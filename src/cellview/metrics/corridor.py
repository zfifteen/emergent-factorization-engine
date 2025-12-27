"""
Corridor-width metrics for evaluating factorization search efficiency.
"""

import math
from typing import List, Tuple


def effective_corridor_width(candidates: List[Tuple[int, float]], p_true: int) -> int:
    """
    Return rank of true factor p in sorted candidate list.
    Lower rank = narrower corridor.

    Args:
        candidates: List of (candidate, energy) tuples, sorted by energy ascending
        p_true: The true prime factor

    Returns:
        Rank (1-based index) of p_true in the sorted list
    """
    for rank, (candidate, _) in enumerate(candidates, 1):
        if candidate == p_true:
            return rank
    return len(candidates) + 1  # Not found, worst rank


def corridor_entropy(energy_profile: List[float]) -> float:
    """
    Shannon entropy of energy distribution over candidates.
    Lower entropy = tighter localization.

    Args:
        energy_profile: List of energy values

    Returns:
        Shannon entropy normalized by log(len(energies))
    """
    if not energy_profile:
        return 0.0

    # Normalize to probabilities
    min_energy = min(energy_profile)
    max_energy = max(energy_profile)

    if max_energy == min_energy:
        return 0.0  # All same energy

    # Convert to probabilities (lower energy = higher probability)
    probs = [(max_energy - e) / (max_energy - min_energy) for e in energy_profile]
    total = sum(probs)

    if total == 0:
        return 0.0

    probs = [p / total for p in probs]

    # Compute entropy
    entropy = -sum(p * math.log(p) for p in probs if p > 0)

    # Normalize by maximum possible entropy
    max_entropy = math.log(len(energy_profile))
    return entropy / max_entropy if max_entropy > 0 else 0.0


def viable_region_size(
    candidates: List[Tuple[int, float]], energy_threshold: float
) -> int:
    """
    Count candidates below energy cutoff.
    Fewer = more focused search.

    Args:
        candidates: List of (candidate, energy) tuples
        energy_threshold: Energy cutoff

    Returns:
        Number of candidates with energy <= threshold
    """
    return sum(1 for _, energy in candidates if energy <= energy_threshold)
