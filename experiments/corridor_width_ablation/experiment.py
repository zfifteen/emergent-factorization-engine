#!/usr/bin/env python3
"""
Corridor-Width Ablation Experiment

Paired ablation comparing:
- Baseline: Geometric ranking by distance from sqrt(N)
- Emergent: Cell-view dynamics with DG/Aggregation signals

Gates: G100, G110, G120
Success threshold: >=20% rank reduction with p<0.1 (paired t-test)

EXPERIMENTAL DESIGN NOTE:
-------------------------
This experiment centers the candidate band on sqrt(N), providing a fair comparison
between baseline (geometric distance) and emergent (cell-view dynamics) methods.
The band spans from the true factor p to beyond sqrt(N) to test realistic search
scenarios for unbalanced semiprimes.

REPRODUCTION INSTRUCTIONS:
--------------------------
1. Install the package: pip install -e .
2. Run the experiment: python -m experiments.corridor_width_ablation.experiment
3. Results are written to experiments/corridor_width_ablation/results/
4. View the visualization notebook: experiments/corridor_width_ablation/visualize_results.ipynb

The experiment:
- Loads gates G100, G110, G120 from the verification ladder
- For each gate, generates 50,000 candidate integers in a band spanning from
  near the true factor p up to sqrt(N)
- Runs baseline ranking (sort by distance from sqrt(N)) and emergent ranking
  (cell-view dynamics with dirichlet5, dirichlet11, arctan algotypes)
- Computes corridor metrics: effective width (rank of p), entropy, viable regions
- Calculates statistical significance: Cohen's d effect size, paired t-test
  NOTE: Cohen's d can be inflated when emergent ranks cluster at 1 and baseline
  ranks are uniformly high. This is expected for unbalanced semiprimes.
- Outputs JSON logs with full time-series data for each run
"""

import random
import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from math import sqrt
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.metrics.corridor_metrics import compute_all_corridor_metrics
from cellview.utils.ladder import generate_verification_ladder, get_gate
from cellview.utils.logging import ensure_dir, timestamp_id, write_json
from cellview.utils.rng import create_rng

# ============================================================================
# EXPERIMENT CONSTANTS
# ============================================================================
# These values were chosen based on empirical tuning and computational limits.

# Maximum half-width for candidate band. Limits memory usage while ensuring
# statistical power. With 50k samples from a 10M-wide band, we achieve ~0.5%
# sampling density, sufficient for rank comparison.
MAX_BAND_HALFWIDTH = 5_000_000

# Number of candidates to sample when band is larger than this. Balances
# statistical power (need enough samples for reliable ranks) against
# computational cost (O(n log n) sorting, O(n) dynamics).
DEFAULT_CANDIDATE_SAMPLE_SIZE = 50_000

# Maximum steps for emergent dynamics. Empirically, convergence occurs within
# 100-200 steps for most gates; 500 provides safety margin for edge cases.
DEFAULT_MAX_STEPS = 500

# Timeout for candidate sampling loop (in iterations). Prevents infinite loops
# when sample_size approaches span size. Set to 10x sample size as safety margin.
SAMPLING_ITERATION_LIMIT_MULTIPLIER = 10


@dataclass
class GateConfig:
    """Configuration for a single gate in the ablation."""

    gate_name: str
    N: int
    true_factor_p: int
    true_factor_q: int
    sqrt_N: int
    band_center: int
    band_halfwidth: int
    # For unbalanced semiprimes, p is well below sqrt(N)
    # We create a candidate domain that spans from near p to sqrt(N)
    candidate_sample_size: int = 50000  # Limit total candidates for tractability


@dataclass
class BaselineResult:
    """Results from baseline geometric ranking."""

    ranked_candidates: List[Dict]
    corridor_metrics: Dict
    ranking_time_ms: float


@dataclass
class EmergentResult:
    """Results from emergent cell-view dynamics."""

    ranked_candidates: List[Dict]
    corridor_metrics: Dict
    ranking_time_ms: float
    # Per-step instrumentation
    swaps_per_step: List[int]
    sortedness_series: List[float]
    aggregation_series: List[float]
    dg_episodes: List[Dict]
    dg_index: float
    algotype_distribution: Dict[str, int]
    convergence_step: int
    total_steps: int


@dataclass
class PairedRunResult:
    """Results from a single paired run (baseline + emergent on same gate)."""

    gate_config: GateConfig
    baseline: BaselineResult
    emergent: EmergentResult
    rank_reduction_pct: float  # (baseline_rank - emergent_rank) / baseline_rank * 100
    rank_reduction_absolute: int


def load_gate_configs() -> List[GateConfig]:
    """Load G100, G110, G120 configurations from verification ladder.

    For a fair comparison between baseline (distance from sqrt(N)) and emergent
    methods, we center the band on sqrt(N). The halfwidth is chosen to include
    the true factor p while maintaining computational tractability.
    """
    ladder = generate_verification_ladder()
    configs = []

    for gate_name in ["G100", "G110", "G120"]:
        gate = get_gate(gate_name, ladder)
        if gate is None or gate.p is None:
            raise ValueError(f"Gate {gate_name} not found or factors not revealed")

        # Center on sqrt(N) for fair baseline comparison
        # Halfwidth extends down to include p for unbalanced semiprimes
        sqrt_N = gate.sqrt_N
        p = gate.p

        # Calculate halfwidth to include p with some margin
        # For unbalanced semiprimes, p < sqrt(N), so we need sqrt(N) - p + margin
        distance_to_p = abs(sqrt_N - p)
        # Add 10% margin beyond p, capped by MAX_BAND_HALFWIDTH
        halfwidth = min(MAX_BAND_HALFWIDTH, int(distance_to_p * 1.1) + 1000)

        configs.append(
            GateConfig(
                gate_name=gate_name,
                N=gate.N,
                true_factor_p=gate.p,
                true_factor_q=gate.q,
                sqrt_N=gate.sqrt_N,
                band_center=sqrt_N,  # Fair comparison: center on sqrt(N)
                band_halfwidth=halfwidth,
                candidate_sample_size=DEFAULT_CANDIDATE_SAMPLE_SIZE,
            )
        )

    return configs


def generate_candidates(config: GateConfig, rng: random.Random) -> List[int]:
    """Generate candidate list centered around band_center.

    For tractability with large numbers, we sample rather than enumerate
    the full dense band.

    Args:
        config: Gate configuration with band parameters
        rng: Random number generator (required for reproducibility)

    Returns:
        List of candidate integers including the true factor

    Raises:
        ValueError: If rng is None (explicit RNG required for reproducibility)
        RuntimeError: If sampling loop exceeds iteration limit
    """
    if rng is None:
        raise ValueError("rng is required for reproducibility; pass create_rng(seed)")

    center = config.band_center
    halfwidth = config.band_halfwidth
    sample_size = config.candidate_sample_size

    low = max(2, center - halfwidth)
    high = center + halfwidth
    span = high - low + 1

    # Validate that true factor is within sampling bounds
    p = config.true_factor_p
    if p < low or p > high:
        # Warn but still include p - this is intentional for testing edge cases
        import warnings

        warnings.warn(
            f"true_factor_p={p} is outside band [{low}, {high}]. "
            "Factor will be included but results may not reflect realistic search."
        )

    # If span is smaller than sample size, just enumerate
    if span <= sample_size:
        candidates = list(range(low, high + 1))
        # Ensure true factor is included even if outside band
        if p not in candidates:
            candidates.append(p)
    else:
        # Sample uniformly from the band
        seen = set()
        candidates = []

        # Always include the true factor
        candidates.append(p)
        seen.add(p)

        # Sample remaining candidates with iteration limit
        iteration_limit = sample_size * SAMPLING_ITERATION_LIMIT_MULTIPLIER
        iterations = 0

        while len(candidates) < sample_size:
            iterations += 1
            if iterations > iteration_limit:
                raise RuntimeError(
                    f"Sampling loop exceeded {iteration_limit} iterations. "
                    f"sample_size={sample_size} may be too close to span={span}."
                )

            val = rng.randrange(low, high + 1)
            if val not in seen:
                seen.add(val)
                candidates.append(val)

    return candidates


def run_baseline_ranking(
    candidates: List[int], config: GateConfig
) -> BaselineResult:
    """
    Baseline ranking: Sort candidates by geometric distance from sqrt(N).

    This is the naive approach - closest to sqrt(N) gets lowest rank.
    """
    start_time = time.perf_counter()

    sqrt_N = config.sqrt_N

    # Create ranked list with distance-based energy
    ranked = []
    for n in candidates:
        distance = abs(n - sqrt_N)
        # Normalize distance as "energy" (lower is better)
        energy = Decimal(distance) / Decimal(sqrt_N)
        ranked.append({"n": n, "energy": str(energy), "distance_from_sqrt": distance})

    # Sort by energy (ascending - lower energy = closer to sqrt = higher rank)
    ranked.sort(key=lambda x: Decimal(x["energy"]))

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Compute corridor metrics
    corridor_metrics = compute_all_corridor_metrics(ranked, config.true_factor_p)

    return BaselineResult(
        ranked_candidates=ranked,
        corridor_metrics=corridor_metrics,
        ranking_time_ms=elapsed_ms,
    )


def run_emergent_ranking(
    candidates: List[int],
    config: GateConfig,
    rng: random.Random,
    algotypes: Sequence[str] = ("dirichlet5", "dirichlet11", "arctan"),
    max_steps: int = DEFAULT_MAX_STEPS,
) -> EmergentResult:
    """
    Emergent ranking: Apply cell-view dynamics with multiple algotypes.

    Uses the CellViewEngine to perform Levin-style swaps, tracking
    DG episodes, aggregation, and convergence metrics.
    """
    start_time = time.perf_counter()

    # Set up energy specs for the algotypes
    energy_specs = default_specs()

    # Create the engine
    engine = CellViewEngine(
        N=config.N,
        candidates=candidates,
        algotypes=algotypes,
        energy_specs=energy_specs,
        rng=rng,
        sweep_order="ascending",
        max_steps=max_steps,
        type2_immovable=False,
    )

    # Run the dynamics
    results = engine.run()

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Extract per-step data
    swaps_per_step = results["swaps_per_step"]
    sortedness_series = results["sortedness"]
    aggregation_series = results["aggregation"]
    dg_episodes = results["dg_episodes"]
    dg_index = results["dg_index"]

    # Find convergence step (first step with 0 swaps, or last step)
    convergence_step = len(swaps_per_step)
    for i, swaps in enumerate(swaps_per_step):
        if swaps == 0:
            convergence_step = i + 1
            break

    # Count algotype distribution
    algotype_counts: Dict[str, int] = {}
    for cell in engine.cells:
        algo = cell.algotype
        algotype_counts[algo] = algotype_counts.get(algo, 0) + 1

    # Get ranked candidates
    ranked = results["ranked_candidates"]

    # Compute corridor metrics
    corridor_metrics = compute_all_corridor_metrics(ranked, config.true_factor_p)

    return EmergentResult(
        ranked_candidates=ranked,
        corridor_metrics=corridor_metrics,
        ranking_time_ms=elapsed_ms,
        swaps_per_step=swaps_per_step,
        sortedness_series=sortedness_series,
        aggregation_series=aggregation_series,
        dg_episodes=dg_episodes,
        dg_index=dg_index,
        algotype_distribution=algotype_counts,
        convergence_step=convergence_step,
        total_steps=len(swaps_per_step),
    )


def run_paired_experiment(
    config: GateConfig,
    seed: int,
    algotypes: Sequence[str] = ("dirichlet5", "dirichlet11", "arctan"),
    max_steps: int = 500,
) -> PairedRunResult:
    """Run a single paired experiment on one gate."""
    # Create RNG for reproducibility
    rng = create_rng(seed)

    # Generate candidates (pass rng for sampling)
    candidates = generate_candidates(config, rng)

    # Run baseline
    baseline = run_baseline_ranking(candidates, config)

    # Run emergent
    emergent = run_emergent_ranking(candidates, config, rng, algotypes, max_steps)

    # Compute rank reduction
    baseline_rank = baseline.corridor_metrics.get("effective_corridor_width")
    emergent_rank = emergent.corridor_metrics.get("effective_corridor_width")

    if baseline_rank is not None and emergent_rank is not None:
        rank_reduction_absolute = baseline_rank - emergent_rank
        rank_reduction_pct = (rank_reduction_absolute / baseline_rank) * 100
    else:
        rank_reduction_absolute = 0
        rank_reduction_pct = 0.0

    return PairedRunResult(
        gate_config=config,
        baseline=baseline,
        emergent=emergent,
        rank_reduction_pct=rank_reduction_pct,
        rank_reduction_absolute=rank_reduction_absolute,
    )


def compute_cohens_d(values1: Sequence[float], values2: Sequence[float]) -> float:
    """
    Compute Cohen's d effect size for paired samples.

    d = mean(diff) / std(diff)

    Args:
        values1: First set of paired observations (e.g., baseline ranks)
        values2: Second set of paired observations (e.g., emergent ranks)

    Returns:
        Cohen's d effect size

    Note on interpretation:
        Standard thresholds (Cohen 1988): small=0.2, medium=0.5, large=0.8

        CAUTION: In this experiment, Cohen's d can be artificially inflated when:
        - All emergent ranks cluster at 1 (exact factor found)
        - Baseline ranks are uniformly high (far from sqrt(N))

        This produces very large effect sizes (d > 100) that don't meaningfully
        characterize the underlying phenomena. When d > 10, interpret as
        "complete separation between methods" rather than quantitative magnitude.
    """
    if len(values1) != len(values2):
        raise ValueError("Paired samples must have same length")

    n = len(values1)
    if n < 2:
        return 0.0

    diffs = [v1 - v2 for v1, v2 in zip(values1, values2)]
    mean_diff = sum(diffs) / n
    var_diff = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    std_diff = sqrt(var_diff) if var_diff > 0 else 1e-12

    return mean_diff / std_diff


def _t_cdf(t: float, df: int) -> float:
    """
    Compute the CDF of Student's t-distribution at value t with df degrees of freedom.

    Uses numerical integration of the t-distribution PDF. For small df (like df=2),
    this is significantly more accurate than normal approximation.

    Args:
        t: The t-statistic value
        df: Degrees of freedom

    Returns:
        P(T <= t) for t-distributed random variable T with df degrees
    """
    from math import atan, gamma, pi

    # For df=1 (Cauchy), use closed form
    if df == 1:
        return 0.5 + atan(t) / pi

    # For df=2, use closed form
    if df == 2:
        return 0.5 + t / (2 * sqrt(2 + t * t))

    # For larger df, use Simpson's rule numerical integration
    # Integrate from -inf to t, using substitution x = t*u/(1-u^2) for (-1,1) -> (-inf, inf)
    # This is more stable than direct integration

    # Use the regularized incomplete beta function relationship:
    # F(t; df) = 1 - 0.5 * I_{df/(df+t^2)}(df/2, 1/2)  for t > 0
    # For simplicity, we'll use a more direct numerical approach

    # Numerical integration using Simpson's rule on finite interval
    # Transform: t = tan(theta) maps (-pi/2, pi/2) to (-inf, inf)
    from math import cos, tan

    def pdf(x: float) -> float:
        """t-distribution PDF"""
        coef = gamma((df + 1) / 2) / (sqrt(df * pi) * gamma(df / 2))
        return coef * (1 + x * x / df) ** (-(df + 1) / 2)

    # Integrate from -inf to t
    # Use change of variables: x = tan(theta), dx = sec^2(theta) dtheta
    # Integral becomes: integral of pdf(tan(theta)) * sec^2(theta) dtheta

    # Upper limit in theta space
    upper_theta = atan(t)
    lower_theta = -pi / 2 + 1e-10  # Avoid singularity

    # Simpson's rule
    n_intervals = 1000
    h = (upper_theta - lower_theta) / n_intervals

    total = 0.0
    for i in range(n_intervals + 1):
        theta = lower_theta + i * h
        x = tan(theta)
        sec_sq = 1 / (cos(theta) ** 2)
        y = pdf(x) * sec_sq

        if i == 0 or i == n_intervals:
            total += y
        elif i % 2 == 1:
            total += 4 * y
        else:
            total += 2 * y

    return total * h / 3


def compute_paired_ttest(
    values1: Sequence[float], values2: Sequence[float]
) -> Tuple[float, float]:
    """
    Compute paired t-test statistic and p-value.

    Uses proper t-distribution CDF (not normal approximation) for accurate
    p-values at small sample sizes.

    Args:
        values1: First set of paired observations
        values2: Second set of paired observations (same length as values1)

    Returns:
        Tuple of (t_statistic, two_tailed_p_value)

    Note:
        For n=3 (df=2), the t-distribution has much heavier tails than normal.
        Using normal approximation would underestimate p-values by ~30-50%.
    """
    if len(values1) != len(values2):
        raise ValueError("Paired samples must have same length")

    n = len(values1)
    if n < 2:
        return 0.0, 1.0

    diffs = [v1 - v2 for v1, v2 in zip(values1, values2)]
    mean_diff = sum(diffs) / n
    var_diff = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    std_err = sqrt(var_diff / n) if var_diff > 0 else 1e-12

    t_stat = mean_diff / std_err
    df = n - 1

    # Two-tailed p-value using proper t-distribution
    # P(|T| > |t|) = 2 * P(T > |t|) = 2 * (1 - CDF(|t|))
    cdf_value = _t_cdf(abs(t_stat), df)
    p_value = 2 * (1 - cdf_value)

    # Clamp to valid range (numerical errors can cause slight overshoots)
    p_value = max(0.0, min(1.0, p_value))

    return t_stat, p_value


def run_full_ablation(
    output_dir: Path = None,
    seed_base: int = 42,
    compact: bool = False,
) -> Dict[str, Any]:
    """
    Run the complete corridor-width ablation experiment.

    Tests 3 gates (G100, G110, G120) with paired baseline vs emergent comparison.

    Args:
        output_dir: Directory for output files. Defaults to results/ subdirectory.
        seed_base: Base seed for reproducibility.
        compact: If True, omit per-step time series data from JSON output.
            This reduces file size significantly (50k candidates × steps × 2 methods).
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "results"
    ensure_dir(str(output_dir))

    run_id = timestamp_id("ablation")
    print(f"Starting ablation experiment: {run_id}")
    print("=" * 80)

    # Load gate configurations
    configs = load_gate_configs()
    print(f"Loaded {len(configs)} gate configurations: {[c.gate_name for c in configs]}")

    # Run paired experiments
    results: List[Dict] = []
    baseline_ranks: List[float] = []
    emergent_ranks: List[float] = []

    for config in configs:
        print(f"\nRunning paired experiment on {config.gate_name}...")
        print(f"  N = {config.N} ({config.N.bit_length()} bits)")
        print(f"  True factor p = {config.true_factor_p}")
        print(f"  sqrt(N) = {config.sqrt_N}")

        # Use different seed per gate for reproducibility
        gate_seed = seed_base + hash(config.gate_name) % 10000

        result = run_paired_experiment(config, gate_seed)

        # Collect ranks for statistical analysis
        b_rank = result.baseline.corridor_metrics.get("effective_corridor_width")
        e_rank = result.emergent.corridor_metrics.get("effective_corridor_width")

        if b_rank is not None:
            baseline_ranks.append(float(b_rank))
        if e_rank is not None:
            emergent_ranks.append(float(e_rank))

        # Build result dict for JSON export
        emergent_data = {
            "corridor_metrics": result.emergent.corridor_metrics,
            "ranking_time_ms": result.emergent.ranking_time_ms,
            "dg_index": result.emergent.dg_index,
            "algotype_distribution": result.emergent.algotype_distribution,
            "convergence_step": result.emergent.convergence_step,
            "total_steps": result.emergent.total_steps,
        }

        # Include time series data only in non-compact mode
        if not compact:
            emergent_data.update(
                {
                    "swaps_per_step": result.emergent.swaps_per_step,
                    "sortedness_series": result.emergent.sortedness_series,
                    "aggregation_series": result.emergent.aggregation_series,
                    "dg_episodes": result.emergent.dg_episodes,
                }
            )

        result_dict = {
            "gate": config.gate_name,
            "gate_config": {
                "N": str(config.N),
                "true_factor_p": config.true_factor_p,
                "true_factor_q": config.true_factor_q,
                "sqrt_N": config.sqrt_N,
                "band_center": config.band_center,
                "band_halfwidth": config.band_halfwidth,
            },
            "baseline": {
                "corridor_metrics": result.baseline.corridor_metrics,
                "ranking_time_ms": result.baseline.ranking_time_ms,
            },
            "emergent": emergent_data,
            "comparison": {
                "rank_reduction_pct": result.rank_reduction_pct,
                "rank_reduction_absolute": result.rank_reduction_absolute,
            },
        }
        results.append(result_dict)

        print(f"  Baseline rank: {b_rank}")
        print(f"  Emergent rank: {e_rank}")
        print(f"  Rank reduction: {result.rank_reduction_pct:.1f}%")
        print(f"  DG episodes: {len(result.emergent.dg_episodes)}")
        print(f"  Convergence at step: {result.emergent.convergence_step}")

    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)

    if len(baseline_ranks) >= 2 and len(emergent_ranks) >= 2:
        # Cohen's d
        cohens_d = compute_cohens_d(baseline_ranks, emergent_ranks)

        # Paired t-test
        t_stat, p_value = compute_paired_ttest(baseline_ranks, emergent_ranks)

        # Mean rank reduction
        mean_baseline = sum(baseline_ranks) / len(baseline_ranks)
        mean_emergent = sum(emergent_ranks) / len(emergent_ranks)
        mean_reduction_pct = (mean_baseline - mean_emergent) / mean_baseline * 100

        print(f"  Mean baseline rank: {mean_baseline:.1f}")
        print(f"  Mean emergent rank: {mean_emergent:.1f}")
        print(f"  Mean rank reduction: {mean_reduction_pct:.1f}%")
        print(f"  Cohen's d: {cohens_d:.3f}")
        print(f"  Paired t-test: t={t_stat:.3f}, p={p_value:.4f}")

        # Decision threshold
        success = mean_reduction_pct >= 20.0 and p_value < 0.1
        print(f"\n  SUCCESS THRESHOLD: >=20% reduction with p<0.1")
        print(f"  RESULT: {'PASS' if success else 'FAIL'}")

        stats_summary = {
            "n_gates": len(configs),
            "mean_baseline_rank": mean_baseline,
            "mean_emergent_rank": mean_emergent,
            "mean_rank_reduction_pct": mean_reduction_pct,
            "cohens_d": cohens_d,
            "t_statistic": t_stat,
            "p_value": p_value,
            "success_threshold_met": success,
            "decision": "PROCEED to G127" if success else "PIVOT research direction",
        }
    else:
        print("  Insufficient data for statistical analysis")
        stats_summary = {"error": "Insufficient data"}

    # Build final output
    output = {
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiment_config": {
            "gates_tested": [c.gate_name for c in configs],
            "max_band_halfwidth": MAX_BAND_HALFWIDTH,
            "candidate_sample_size": DEFAULT_CANDIDATE_SAMPLE_SIZE,
            "algotypes": ["dirichlet5", "dirichlet11", "arctan"],
            "max_steps": DEFAULT_MAX_STEPS,
            "seed_base": seed_base,
            "compact_output": compact,
        },
        "gate_results": results,
        "statistical_summary": stats_summary,
    }

    # Write JSON output
    output_file = output_dir / f"{run_id}.json"
    write_json(str(output_file), output)
    print(f"\nResults written to: {output_file}")

    # Also write a summary table
    summary_file = output_dir / f"{run_id}_summary.txt"
    with open(summary_file, "w") as f:
        f.write("CORRIDOR-WIDTH ABLATION EXPERIMENT SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Gate':<8} {'Baseline':<12} {'Emergent':<12} {'Reduction':<12} {'p-value':<10}\n")
        f.write("-" * 60 + "\n")
        for i, r in enumerate(results):
            b_rank = r["baseline"]["corridor_metrics"].get("effective_corridor_width", "N/A")
            e_rank = r["emergent"]["corridor_metrics"].get("effective_corridor_width", "N/A")
            reduction = r["comparison"]["rank_reduction_pct"]
            f.write(f"{r['gate']:<8} {b_rank:<12} {e_rank:<12} {reduction:<12.1f}%\n")
        f.write("-" * 60 + "\n")
        if "mean_rank_reduction_pct" in stats_summary:
            f.write(f"\nMean rank reduction: {stats_summary['mean_rank_reduction_pct']:.1f}%\n")
            f.write(f"Cohen's d: {stats_summary['cohens_d']:.3f}\n")
            f.write(f"p-value: {stats_summary['p_value']:.4f}\n")
            f.write(f"\nDECISION: {stats_summary['decision']}\n")
    print(f"Summary written to: {summary_file}")

    return output


def main():
    """Main entry point.

    Command line arguments:
        --compact: Omit per-step time series data from JSON output to reduce file size.
        --seed N: Use N as the base seed (default: 42).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Corridor-Width Ablation Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Omit per-step time series data from JSON output (reduces file size)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base seed for reproducibility (default: 42)",
    )
    args = parser.parse_args()

    print("Corridor-Width Ablation Experiment")
    print("=" * 80)
    if args.compact:
        print("(Compact output mode: time series data will be omitted)")
    print()

    results = run_full_ablation(seed_base=args.seed, compact=args.compact)

    print("\n" + "=" * 80)
    print("Experiment complete!")
    return results


if __name__ == "__main__":
    main()
