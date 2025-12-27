#!/usr/bin/env python3
"""
Corridor-Width Ablation Experiment

Tests whether emergent signals (DG spikes, Algotype aggregation) reduce
search space compared to baseline geometric ranking on gates G100-G110-G120.

Hypothesis: Emergent dynamics narrow the corridor width by >20% vs. naive |d - √N| ranking.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)
from cellview.utils.ladder import generate_verification_ladder, get_gate


def generate_candidates(
    center: int, half_width: int = 5000000, density: int = 100, must_include: int = None
) -> List[int]:
    """
    Generate dense candidate band around center ± half_width.

    Args:
        center: Center point
        half_width: Half-width of the band
        density: Step size (smaller = denser)
        must_include: Ensure this value is in the list

    Returns:
        List of candidate integers
    """
    start = max(2, center - half_width)
    end = center + half_width
    candidates = list(range(start, end + 1, density))
    if must_include and must_include not in candidates:
        candidates.append(must_include)
        candidates.sort()
    return candidates


def baseline_ranking(candidates: List[int], sqrt_N: int) -> List[Tuple[int, float]]:
    """
    Baseline: Rank by geometric distance |d - sqrt_N|

    Returns:
        Sorted list of (candidate, energy) tuples, energy = distance
    """
    candidates_with_energy = [(c, abs(c - sqrt_N)) for c in candidates]
    return sorted(candidates_with_energy, key=lambda x: x[1])


def emergent_ranking(
    N: int,
    sqrt_N: int,
    candidates: List[int],
    algotypes: List[str],
    max_steps: int = 500,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Emergent ranking using cell-view dynamics.

    Returns:
        Full results dict from CellViewEngine.run()
    """
    rng = random.Random(seed)
    energy_specs = default_specs()
    # Update specs to use the gate's sqrt_N
    for spec in energy_specs.values():
        if "sqrtN" in spec.params:
            spec.params["sqrtN"] = sqrt_N

    engine = CellViewEngine(
        N=N,
        candidates=candidates,
        algotypes=algotypes,
        energy_specs=energy_specs,
        rng=rng,
        max_steps=max_steps,
    )

    return engine.run()


def compute_corridor_metrics(
    ranked_candidates: List[Tuple[int, float]],
    p_true: int,
    energy_threshold: float = None,
) -> Dict[str, Any]:
    """
    Compute corridor metrics for a ranked candidate list.

    Args:
        ranked_candidates: List of (candidate, energy) sorted by energy
        p_true: True prime factor
        energy_threshold: Threshold for viable region (if None, use median energy)

    Returns:
        Metrics dict
    """
    energies = [e for _, e in ranked_candidates]

    if energy_threshold is None:
        # Use median energy as threshold
        sorted_energies = sorted(energies)
        energy_threshold = sorted_energies[len(sorted_energies) // 2]

    rank = effective_corridor_width(ranked_candidates, p_true)
    entropy = corridor_entropy(energies)
    viable_count = viable_region_size(ranked_candidates, energy_threshold)

    return {
        "rank_of_p": rank,
        "corridor_entropy": float(entropy),
        "viable_candidates": viable_count,
        "total_candidates": len(ranked_candidates),
        "energy_threshold": energy_threshold,
    }


def run_single_gate_ablation(
    gate_name: str, half_width: int = 5000000, max_steps: int = 500
) -> Dict[str, Any]:
    """
    Run ablation for a single gate.

    Args:
        gate_name: e.g., "G100"
        half_width: Candidate band half-width
        max_steps: Max steps for emergent dynamics

    Returns:
        Results dict
    """
    print(f"Running ablation for {gate_name}...")

    # Get gate
    ladder = generate_verification_ladder()
    gate = get_gate(gate_name, ladder)
    if not gate or not gate.p:
        raise ValueError(f"Gate {gate_name} not found or factors not revealed")

    N, p_true, sqrt_N = gate.N, gate.p, gate.sqrt_N  # p is the true factor

    # Generate candidates
    candidates = generate_candidates(sqrt_N, half_width, must_include=p_true)
    print(f"  Generated {len(candidates)} candidates around {sqrt_N}")

    # Fixed seed from gate N for reproducibility
    seed = abs(hash(gate_name + str(N))) % (2**32)

    results = {
        "gate": gate_name,
        "N": N,
        "p_true": p_true,
        "sqrt_N": sqrt_N,
        "candidate_count": len(candidates),
        "half_width": half_width,
        "seed": seed,
    }

    # Baseline method
    print("  Running baseline ranking...")
    baseline_ranked = baseline_ranking(candidates, sqrt_N)
    baseline_metrics = compute_corridor_metrics(baseline_ranked, p_true)
    results["baseline"] = {
        "ranked_candidates": baseline_ranked,
        "metrics": baseline_metrics,
    }

    # Emergent method
    print("  Running emergent dynamics...")
    algotypes = ["dirichlet5"]  # Single algotype for consistent divisor detection
    emergent_results = emergent_ranking(
        N, sqrt_N, candidates, algotypes, max_steps, seed
    )

    # Extract ranked candidates from emergent results
    emergent_ranked = [
        (int(c["n"]), float(c["energy"])) for c in emergent_results["ranked_candidates"]
    ]
    emergent_metrics = compute_corridor_metrics(emergent_ranked, p_true)

    results["emergent"] = {
        "ranked_candidates": emergent_ranked,
        "metrics": emergent_metrics,
        "time_series": {
            "sortedness": emergent_results["sortedness"],
            "aggregation": emergent_results["aggregation"],
            "dg_index": emergent_results["dg_index"],
            "dg_episodes": emergent_results["dg_episodes"],
        },
        "final_state": emergent_results["final_state"],
    }

    print(f"  Baseline rank: {baseline_metrics['rank_of_p']}")
    print(f"  Emergent rank: {emergent_metrics['rank_of_p']}")

    return results


def run_ablation_experiment(
    gates: List[str] = None,
    half_width: int = 5000000,
    max_steps: int = 500,
    output_dir: str = "logs",
) -> Dict[str, Any]:
    """
    Run the complete ablation experiment.

    Args:
        gates: List of gate names (default: ["G100", "G110", "G120"])
        half_width: Candidate band half-width
        max_steps: Max steps for dynamics
        output_dir: Output directory

    Returns:
        Summary results
    """
    if gates is None:
        gates = ["G100", "G110", "G120"]

    Path(output_dir).mkdir(exist_ok=True)

    all_results = {}
    summary = {
        "experiment_config": {
            "gates": gates,
            "half_width": half_width,
            "max_steps": max_steps,
            "output_dir": output_dir,
        },
        "gate_results": {},
    }

    for gate_name in gates:
        results = run_single_gate_ablation(gate_name, half_width, max_steps)
        all_results[gate_name] = results

        # Save individual log
        log_file = Path(output_dir) / f"ablation_{gate_name}.json"
        with open(log_file, "w") as f:
            json.dump(results, f, indent=2)

        # Add to summary
        summary["gate_results"][gate_name] = {
            "baseline_rank": results["baseline"]["metrics"]["rank_of_p"],
            "emergent_rank": results["emergent"]["metrics"]["rank_of_p"],
            "rank_delta": results["baseline"]["metrics"]["rank_of_p"]
            - results["emergent"]["metrics"]["rank_of_p"],
            "baseline_entropy": results["baseline"]["metrics"]["corridor_entropy"],
            "emergent_entropy": results["emergent"]["metrics"]["corridor_entropy"],
            "baseline_viable": results["baseline"]["metrics"]["viable_candidates"],
            "emergent_viable": results["emergent"]["metrics"]["viable_candidates"],
        }

    # Save summary
    summary_file = Path(output_dir) / "ablation_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run corridor-width ablation experiment"
    )
    parser.add_argument(
        "--gates", nargs="+", default=["G100", "G110", "G120"], help="Gates to test"
    )
    parser.add_argument(
        "--candidate-halfwidth",
        type=int,
        default=5000000,
        help="Half-width of candidate band around sqrt(N)",
    )
    parser.add_argument(
        "--swap-steps", type=int, default=500, help="Max steps for emergent dynamics"
    )
    parser.add_argument(
        "--output-dir", type=str, default="logs", help="Output directory for logs"
    )

    args = parser.parse_args()

    print("Starting Corridor-Width Ablation Experiment")
    print(f"Gates: {args.gates}")
    print(f"Candidate half-width: {args.candidate_halfwidth}")
    print(f"Max swap steps: {args.swap_steps}")
    print(f"Output dir: {args.output_dir}")
    print()

    summary = run_ablation_experiment(
        gates=args.gates,
        half_width=args.candidate_halfwidth,
        max_steps=args.swap_steps,
        output_dir=args.output_dir,
    )

    print("\nExperiment complete!")
    print("Summary:")
    for gate, res in summary["gate_results"].items():
        print(
            f"  {gate}: Baseline rank {res['baseline_rank']}, Emergent rank {res['emergent_rank']} "
            f"(delta: {res['rank_delta']})"
        )


if __name__ == "__main__":
    main()
