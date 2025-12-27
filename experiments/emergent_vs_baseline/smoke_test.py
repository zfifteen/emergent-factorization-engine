#!/usr/bin/env python3
"""
Smoke test for corridor-width ablation experiment.
Runs with minimal parameters to verify integration.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cellview.utils.challenge import canonical_N
from cellview.algos.cellview import Cellview
from cellview.energies.dirichlet import dirichlet_energy
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


def test_smoke():
    """Smoke test with small gate."""
    print("Running smoke test with G010...")
    
    # Small gate for quick test
    N = canonical_N("G010")
    if N is None:
        print("ERROR: Cannot resolve G010")
        return False
    
    print(f"N = {N}")
    
    # Small candidate window
    isqrt_N = int(N**0.5)
    halfwidth = 50
    start = isqrt_N - halfwidth
    end = isqrt_N + halfwidth
    candidates_list = list(range(start, end))
    
    print(f"Candidates: {len(candidates_list)} in [{start}, {end})")
    
    # Find factor
    p = None
    for c in candidates_list:
        if c > 1 and N % c == 0:
            p = c
            break
    
    if p is None:
        print(f"ERROR: No factor found in band")
        return False
    
    print(f"True factor p = {p}")
    
    # Test baseline
    baseline_ranked = sorted(candidates_list, key=lambda d: abs(d - isqrt_N))
    baseline_rank = effective_corridor_width(
        [(c, abs(c - isqrt_N)) for c in baseline_ranked], p
    )
    print(f"Baseline rank: {baseline_rank}")
    
    # Test emergent (minimal swaps)
    try:
        cv = Cellview(N, candidates_list, energy_fn=dirichlet_energy)
        cv.run_swaps(10)  # Just 10 swaps for smoke test
        emergent_ranked = cv.get_sorted_candidates()
        emergent_rank = effective_corridor_width(emergent_ranked, p)
        print(f"Emergent rank: {emergent_rank}")
        
        # Verify metrics compute without error
        emergent_energies = [e for _c, e in emergent_ranked]
        entropy = corridor_entropy(emergent_energies)
        viable = viable_region_size(emergent_ranked, 0.5)
        
        print(f"Entropy: {entropy:.6f}")
        print(f"Viable region: {viable}")
        
    except Exception as e:
        print(f"ERROR during emergent test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ Smoke test passed")
    return True


if __name__ == "__main__":
    success = test_smoke()
    sys.exit(0 if success else 1)
