from typing import List, Union, Dict
import math
from decimal import Decimal

# Softmax scale range to allow significant peaking. 
# Higher range = lower entropy for the same relative spread.
ENTROPY_SCALE_RANGE = 10.0

def effective_corridor_width(candidates: List[Union[int, Dict]], N: int, p_true: int) -> int:
    """
    Return rank of true factor p in sorted candidate list.
    Lower rank = narrower corridor.
    """
    for rank, cand in enumerate(candidates):
        val = cand if isinstance(cand, int) else cand['n']
        if val == p_true:
            return rank
    return -1

def corridor_entropy(energy_profile: List[float], scale_range: float = ENTROPY_SCALE_RANGE) -> float:
    """
    Shannon entropy of energy distribution over candidates.
    Lower entropy = tighter localization.
    
    Uses Softmax: P_i = exp(-E_i / T) / sum(exp(-E_j / T)).
    
    Normalization: We map energies to [0, scale_range] to ensure the Softmax 
    can actually "peak" even if original energy scales were small. 
    Without this, Softmax on [0, 1] range is quite flat (H ~ log2(N)).
    """
    if not energy_profile:
        return 0.0
    if len(energy_profile) == 1:
        return 0.0
        
    values = [float(e) for e in energy_profile]
    min_v = min(values)
    max_v = max(values)
    rng = max_v - min_v
    
    if rng < 1e-12:
        return math.log2(len(values))
        
    # Map to [0, scale_range] to allow significant peaking in the exp() call
    scaled = [scale_range * (v - min_v) / rng for v in values]
    
    exps = [math.exp(-s) for s in scaled]
    sum_exps = sum(exps)
    
    if sum_exps == 0:
        return math.log2(len(values))
        
    probs = [e / sum_exps for e in exps]
    
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log2(p)
            
    return entropy

def viable_region_size(candidates: List[Union[int, Dict]], energy_threshold: Union[float, Decimal]) -> int:
    """Count candidates below energy cutoff."""
    count = 0
    thresh = float(energy_threshold)
    for cand in candidates:
        if isinstance(cand, dict) and 'energy' in cand:
            if float(cand['energy']) <= thresh:
                count += 1
    return count
