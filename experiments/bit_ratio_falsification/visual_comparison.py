#!/usr/bin/env python3
"""
Visual demonstration of bit ratio differences.

This script generates a side-by-side comparison of ladders with different bit ratios
to visualize the impact of changing from 1:3 to 1:4 to 1:5.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cellview.utils.ladder import (
    generate_verification_ladder,
    print_ladder_summary,
    BASE_SEED,
)


def main():
    """Generate and display ladders for visual comparison."""
    
    print("\n" + "=" * 100)
    print("BIT RATIO VISUAL COMPARISON")
    print("=" * 100)
    print()
    
    # Generate ladders
    print("Generating ladders with different bit ratios...")
    print()
    
    ladder_1_3 = generate_verification_ladder(base_seed=BASE_SEED, bit_ratio=3)
    ladder_1_4 = generate_verification_ladder(base_seed=BASE_SEED, bit_ratio=4)
    ladder_1_5 = generate_verification_ladder(base_seed=BASE_SEED, bit_ratio=5)
    
    # Display each ladder
    print_ladder_summary(ladder_1_3, label="1:3 Ratio (Baseline)")
    print()
    
    print_ladder_summary(ladder_1_4, label="1:4 Ratio")
    print()
    
    print_ladder_summary(ladder_1_5, label="1:5 Ratio")
    print()
    
    # Print comparison for key gates
    print("=" * 100)
    print("DIRECT COMPARISON - KEY GATES")
    print("=" * 100)
    print()
    
    key_gates = ["G030", "G060", "G090", "G120", "G130"]
    
    for gate_name in key_gates:
        g3 = next(g for g in ladder_1_3 if g.gate == gate_name)
        g4 = next(g for g in ladder_1_4 if g.gate == gate_name)
        g5 = next(g for g in ladder_1_5 if g.gate == gate_name)
        
        print(f"{gate_name} ({g3.target_bits} bits):")
        print(f"  1:3 → p = {g3.p:,} ({g3.p_bits} bits), q = {g3.q_bits} bits, p/√N = {g3.p_as_fraction_of_sqrt:.6e}")
        print(f"  1:4 → p = {g4.p:,} ({g4.p_bits} bits), q = {g4.q_bits} bits, p/√N = {g4.p_as_fraction_of_sqrt:.6e}")
        print(f"  1:5 → p = {g5.p:,} ({g5.p_bits} bits), q = {g5.q_bits} bits, p/√N = {g5.p_as_fraction_of_sqrt:.6e}")
        
        # Show relative change
        p_reduction_4 = g3.p / g4.p
        p_reduction_5 = g3.p / g5.p
        print(f"  → p reduction: {p_reduction_4:.1f}x (1:4), {p_reduction_5:.1f}x (1:5)")
        
        # Show relative corridor position change
        rel_pos_3 = (g3.p - 2) / (g3.sqrt_N - 2)
        rel_pos_4 = (g4.p - 2) / (g4.sqrt_N - 2)
        rel_pos_5 = (g5.p - 2) / (g5.sqrt_N - 2)
        print(f"  → Relative position in [2,√N]: {rel_pos_3:.6f} (1:3), {rel_pos_4:.6f} (1:4), {rel_pos_5:.6f} (1:5)")
        print(f"  → Change: {abs(rel_pos_3 - rel_pos_5):.6f} ({abs(rel_pos_3 - rel_pos_5)/rel_pos_3*100:.2f}%)")
        print()
    
    print("=" * 100)
    print("INSIGHT: While p becomes exponentially smaller in absolute terms,")
    print("         the relative position in search space changes minimally.")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()
