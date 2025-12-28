"""
Corridor-width metrics for ablation experiments.

These metrics quantify search efficiency by measuring how well a ranking
method concentrates probability mass near the true factor.

Metrics:
    - effective_corridor_width: Rank position of true factor (lower is better)
    - corridor_entropy: Shannon entropy of energy distribution (lower = more concentrated)
    - viable_region_size: Count of candidates below energy threshold
"""

from decimal import Decimal
from math import log2
from typing import Dict, List, Optional, Sequence, Tuple


def effective_corridor_width(
    ranked_candidates: Sequence[Dict],
    true_factor: int,
) -> Optional[int]:
    """
    Compute the rank position of the true factor in a ranked candidate list.

    This is the primary metric for corridor efficiency - lower rank means
    the ranking method places the true factor closer to the top.

    Args:
        ranked_candidates: List of dicts with 'n' key, ordered by rank (best first)
        true_factor: The actual factor p we're searching for

    Returns:
        1-indexed rank of true factor, or None if not in candidates
    """
    for idx, candidate in enumerate(ranked_candidates):
        if candidate.get("n") == true_factor:
            return idx + 1  # 1-indexed rank
    return None


def corridor_entropy(
    energies: Sequence[Decimal],
    normalize: bool = True,
) -> float:
    """
    Compute Shannon entropy of the energy distribution.

    Lower entropy means the ranking is more decisive (concentrated mass).
    Higher entropy means the ranking is more uniform (less discriminating).

    Args:
        energies: List of energy values (Decimal or float-like)
        normalize: If True, normalize to [0, 1] range based on max entropy

    Returns:
        Entropy value (bits). If normalized, 0 = perfectly concentrated, 1 = uniform
    """
    if len(energies) < 2:
        return 0.0

    # Convert energies to probabilities via softmax-like transformation
    # We invert energies first since lower energy = better
    float_energies = [float(e) for e in energies]

    # Avoid numerical issues - shift to have max at 0
    max_e = max(float_energies)
    if max_e == 0:
        max_e = 1.0

    # Convert to "quality" scores (higher is better for probability)
    # Use 1 - normalized_energy as quality
    min_e = min(float_energies)
    range_e = max_e - min_e
    if range_e < 1e-12:
        # All energies equal - maximum entropy
        return 1.0 if normalize else log2(len(energies))

    qualities = [(max_e - e) / range_e + 1e-12 for e in float_energies]
    total = sum(qualities)
    probs = [q / total for q in qualities]

    # Shannon entropy
    entropy = -sum(p * log2(p) for p in probs if p > 0)

    if normalize:
        max_entropy = log2(len(energies))
        if max_entropy > 0:
            return entropy / max_entropy
        return 0.0

    return entropy


def viable_region_size(
    ranked_candidates: Sequence[Dict],
    threshold_percentile: float = 10.0,
) -> int:
    """
    Count candidates in the "viable region" (below energy threshold).

    This measures the effective search space after applying the ranking -
    how many candidates need to be checked before reaching the given
    quality threshold?

    Args:
        ranked_candidates: List of dicts with 'energy' key, ordered by rank
        threshold_percentile: Top X% of candidates to consider viable

    Returns:
        Number of candidates in the viable region
    """
    if not ranked_candidates:
        return 0

    count = max(1, int(len(ranked_candidates) * threshold_percentile / 100))
    return count


def viable_region_contains_factor(
    ranked_candidates: Sequence[Dict],
    true_factor: int,
    threshold_percentile: float = 10.0,
) -> bool:
    """
    Check if the true factor is within the viable region.

    Args:
        ranked_candidates: List of dicts with 'n' key, ordered by rank
        true_factor: The actual factor p we're searching for
        threshold_percentile: Top X% of candidates to consider viable

    Returns:
        True if factor is in viable region
    """
    viable_size = viable_region_size(ranked_candidates, threshold_percentile)

    for idx, candidate in enumerate(ranked_candidates):
        if idx >= viable_size:
            break
        if candidate.get("n") == true_factor:
            return True

    return False


def compute_all_corridor_metrics(
    ranked_candidates: Sequence[Dict],
    true_factor: int,
    threshold_percentiles: Sequence[float] = (5.0, 10.0, 20.0),
) -> Dict:
    """
    Compute all corridor metrics for a single run.

    Args:
        ranked_candidates: List of dicts with 'n' and 'energy' keys
        true_factor: The actual factor p
        threshold_percentiles: Percentiles for viable region computation

    Returns:
        Dictionary with all computed metrics
    """
    # Effective corridor width (rank of true factor)
    ecw = effective_corridor_width(ranked_candidates, true_factor)

    # Extract energies for entropy computation
    energies = [Decimal(c.get("energy", "0")) for c in ranked_candidates]

    # Corridor entropy
    entropy_raw = corridor_entropy(energies, normalize=False)
    entropy_normalized = corridor_entropy(energies, normalize=True)

    # Viable region metrics for each threshold
    viable_metrics = {}
    for pct in threshold_percentiles:
        size = viable_region_size(ranked_candidates, pct)
        contains = viable_region_contains_factor(ranked_candidates, true_factor, pct)
        viable_metrics[f"viable_p{int(pct)}"] = {
            "size": size,
            "contains_factor": contains,
        }

    # Relative rank (as fraction of total candidates)
    total = len(ranked_candidates)
    relative_rank = ecw / total if ecw and total > 0 else None

    # Rank reduction vs random baseline
    # Random baseline would place factor at position ~total/2 on average
    random_baseline_rank = total / 2
    rank_reduction_pct = None
    if ecw is not None and random_baseline_rank > 0:
        rank_reduction_pct = (random_baseline_rank - ecw) / random_baseline_rank * 100

    return {
        "effective_corridor_width": ecw,
        "relative_rank": relative_rank,
        "rank_reduction_vs_random_pct": rank_reduction_pct,
        "corridor_entropy_bits": entropy_raw,
        "corridor_entropy_normalized": entropy_normalized,
        "total_candidates": total,
        "viable_regions": viable_metrics,
        "factor_found": ecw is not None,
    }


__all__ = [
    "effective_corridor_width",
    "corridor_entropy",
    "viable_region_size",
    "viable_region_contains_factor",
    "compute_all_corridor_metrics",
]
