#!/usr/bin/env python3
"""
Smoke test for corridor-width ablation experiment.
Runs with minimal parameters to verify integration.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# Test gate
TEST_N = 35  # 5 * 7 (G010)

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.utils.rng import rng_from_hex
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


def test_smoke():
    """Smoke test with small gate."""
    print("Running smoke test with G010...")
    
    # Small gate for quick test
    N = TEST_N
    print(f"N = {N}")
    
    # Small candidate window
    isqrt_N = int(N**0.5)
    halfwidth = 50
    start = max(2, isqrt_N - halfwidth)  # Ensure start >= 2
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
        seed_hex = f"{N:064x}"
        rng = rng_from_hex(seed_hex)
        energy_specs = default_specs()
        
        engine = CellViewEngine(
            N=N,
            candidates=candidates_list,
            algotypes=["dirichlet5"],
            energy_specs=energy_specs,
            rng=rng,
            sweep_order="ascending",
            max_steps=10,  # Just 10 steps for smoke test
        )
        result = engine.run()
        
        emergent_ranked = result["ranked_candidates"]
        emergent_rank = None
        for idx, entry in enumerate(emergent_ranked, start=1):
            if int(entry["n"]) == p:
                emergent_rank = idx
                break
        
        if emergent_rank is None:
            emergent_rank = len(emergent_ranked) + 1
            
        print(f"Emergent rank: {emergent_rank}")
        
        # Verify metrics compute without error
        emergent_energies = [float(entry["energy"]) for entry in emergent_ranked]
        entropy = corridor_entropy(emergent_energies)
        viable = viable_region_size([(int(e["n"]), float(e["energy"])) for e in emergent_ranked], 0.5)
        
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
