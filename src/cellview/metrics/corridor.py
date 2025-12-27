from typing import List, Union, Dict
import math
from decimal import Decimal

def effective_corridor_width(candidates: List[Union[int, Dict]], N: int, p_true: int) -> int:
    """
    Return rank of true factor p in sorted candidate list.
    Lower rank = narrower corridor.
    
    Args:
        candidates: List of candidate integers OR list of dicts with 'n' key. 
                    Must be sorted by the ranking metric (e.g. energy).
        N: The target semi-prime. (Ignored; kept for signature compatibility).
        p_true: The true factor to find.
        
    Returns:
        0-based index of p_true in candidates, or -1 if not found.
    """
    for rank, cand in enumerate(candidates):
        val = cand if isinstance(cand, int) else cand['n']
        if val == p_true:
            return rank
    return -1

def corridor_entropy(energy_profile: List[float]) -> float:
    """
    Shannon entropy of energy distribution over candidates.
    Lower entropy = tighter localization.
    
    Uses a Boltzmann-like distribution (Softmax): P_i = exp(-E_i) / sum(exp(-E_j)).
    This correctly gives higher probability to lower energies.
    
    If all energies are equal (including all-zero), the distribution is uniform.
    Negative energies are supported via shifting by min_e.
    
    Args:
        energy_profile: List of energy values (float or Decimal). 
                        
    Returns:
        Shannon entropy in bits. Returns 0.0 for empty profile.
    """
    if not energy_profile:
        return 0.0
        
    values = [float(e) for e in energy_profile]
    
    # Softmax implementation for stability
    # P_i = exp(-E_i) / sum(exp(-E_j))
    # For numerical stability: P_i = exp(-(E_i - min_E)) / sum(exp(-(E_j - min_E)))
    
    min_e = min(values)
    # If all energies are identical, exps will be all 1.0 (uniform)
    exps = [math.exp(-(v - min_e)) for v in values] # Negate because lower energy = higher probability
    sum_exps = sum(exps)
    
    if sum_exps == 0:
        return 0.0
        
    probs = [e / sum_exps for e in exps]
    
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)
            
    return entropy

def viable_region_size(candidates: List[Union[int, Dict]], energy_threshold: Union[float, Decimal]) -> int:
    """
    Count candidates below energy cutoff.
    Fewer = more focused search.
    
    Args:
        candidates: List of candidate dicts with 'energy' key. 
                    Plain integers in the list are ignored.
        energy_threshold: Maximum energy to be considered "viable".
        
    Returns:
        Count of candidates with energy <= threshold.
    """
    count = 0
    thresh = float(energy_threshold)
    
    for cand in candidates:
        if isinstance(cand, dict) and 'energy' in cand:
            e = float(cand['energy'])
            if e <= thresh:
                count += 1
    return count