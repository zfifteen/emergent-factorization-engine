"""Corridor-width metrics for ablation experiments."""

from math import exp, log
from typing import List, Tuple


def effective_corridor_width(sorted_candidates: List[int], p_true: int) -> int:
    """Return 1-based rank of true factor p in sorted candidate list.
    Lower rank = narrower corridor."""
    for rank, candidate in enumerate(sorted_candidates, 1):
        if candidate == p_true:
            return rank
    return len(sorted_candidates) + 1  # not found


def corridor_entropy(energies: List[float]) -> float:
    """Shannon entropy of softmax-normalized energies over candidates.
    Lower entropy = tighter localization."""
    if not energies:
        return 0.0
    max_e = max(energies)
    probs_raw = [exp(-(e - max_e)) for e in energies]
    total = sum(probs_raw)
    if total == 0:
        return 0.0
    probs = [p / total for p in probs_raw]
    return -sum(p * log(p) for p in probs if p > 0)


def viable_region_size(
    candidates: List[Tuple[int, float]], energy_threshold: float
) -> int:
    """Count candidates with energy below threshold.
    Fewer = more focused search."""
    return sum(1 for _, energy in candidates if energy < energy_threshold)
