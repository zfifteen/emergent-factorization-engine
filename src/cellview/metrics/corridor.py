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
        N: The target semi-prime (unused in rank calculation but kept for signature compliance)
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
    
    Args:
        energy_profile: List of energy values (float or Decimal). 
                        Will be normalized to a probability distribution.
                        
    Returns:
        Shannon entropy in bits.
    """
    if not energy_profile:
        return 0.0
        
    # Convert to float and handle negative energies if any (though energies usually >= 0)
    # If energies are "cost" (lower is better), we might need to invert them to get probabilities?
    # But usually entropy of the "energy landscape" implies distribution of values.
    # However, to treat it as a probability distribution for entropy, we usually do softmax or normalize.
    # The issue says "Shannon entropy of energy distribution". 
    # If energy is directly proportional to probability (Boltzmann), then P ~ exp(-E/T).
    # If energy is just a value, maybe we normalize the values themselves?
    # Given the context of "search efficiency", a flatter distribution means higher entropy (harder search).
    # A peaked distribution means lower entropy.
    # I will assume simple normalization of values if they are positive, or softmax if not.
    # Let's assume these are "energies" where lower is better, but for entropy we usually talk about the distribution of states.
    # If we just want entropy of the values:
    
    values = [float(e) for e in energy_profile]
    total = sum(values)
    
    # If total is 0 or values are negative, we might have issues.
    # Assuming positive energies.
    if total <= 0:
        # If all zero, uniform? Or just return 0?
        # If we have negative energies, we should shift them?
        # Let's assume standard probability distribution derived from energy?
        # "distribution over candidates" usually implies P(candidate).
        # If we don't have a conversion to P, maybe we treat the normalized energy profile as P?
        # But high energy = bad candidate?
        # Let's try softmax: P_i = exp(-E_i) / Z. This is standard in physics.
        # But if the energies are large, this might underflow/overflow.
        
        # Simpler interpretation: Just normalize the energy values themselves to sum to 1.
        # But then high energy (bad) has high probability (contribution to entropy).
        # Usually we want entropy of the *probability* of finding the target.
        # If we assume we sample based on energy (Boltzmann), then P(x) ~ exp(-E(x)).
        
        # Let's stick to Softmax as it handles "lower is better" correctly by giving it higher probability.
        # And it works for any energy range.
        pass

    # Softmax implementation for stability
    # P_i = exp(-E_i) / sum(exp(-E_j))
    # For numerical stability: P_i = exp(-(E_i - min_E)) / sum(exp(-(E_j - min_E)))
    
    min_e = min(values)
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
        energy_threshold: Maximum energy to be considered "viable".
        
    Returns:
        Count of candidates with energy <= threshold.
    """
    count = 0
    thresh = float(energy_threshold)
    
    for cand in candidates:
        # If candidates are just ints, we can't check energy. 
        # Assume they are dicts from the engine output.
        if isinstance(cand, dict) and 'energy' in cand:
            e = float(cand['energy'])
            if e <= thresh:
                count += 1
    return count
