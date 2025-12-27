import math


def effective_corridor_width(candidates, p_true):
    """
    Return 1-based rank of p_true in candidates (sorted by energy ascending).
    If p_true not found, returns len(candidates) + 1.
    """
    for idx, (cand, _energy) in enumerate(candidates, start=1):
        if cand == p_true:
            return idx
    return len(candidates) + 1


def corridor_entropy(energies):
    """
    Shannon entropy of normalized energies (higher = more spread).
    Returns 0.0 for empty or uniform distributions.
    """
    if not energies:
        return 0.0

    total = sum(energies)
    if total == 0:
        return 0.0

    probs = [e / total for e in energies]
    
    # Check if uniform (all probabilities equal)
    if len(set(probs)) == 1:
        return 0.0
    
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)

    max_entropy = math.log2(len(energies)) if len(energies) > 1 else 1.0
    if max_entropy == 0:
        return 0.0

    return entropy / max_entropy


def viable_region_size(candidates, threshold=0.5):
    """
    Count candidates with energy below threshold.
    """
    return sum(1 for _cand, energy in candidates if energy < threshold)
