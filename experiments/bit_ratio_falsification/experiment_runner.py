#!/usr/bin/env python3
"""
Experiment: Falsification of Larger Bit Ratio Hypothesis

This experiment tests the hypothesis that larger bit ratios (1:4, 1:5 vs current 1:3)
create more effective "narrow search corridors" for factorization.

Hypothesis to falsify:
    Larger bit ratios (making p even smaller relative to sqrt(N)) will create
    narrower, more effective search corridors that stress robustness more effectively.

Experiment Design:
    1. Generate ladders with three different bit ratios: 1:3 (baseline), 1:4, 1:5
    2. For each ladder, compute:
       - p size in bits
       - q size in bits
       - p / sqrt(N) ratio
       - Distance from p to sqrt(N)
       - "Corridor width" metrics
    3. Compare the characteristics across ratios
    4. Document findings with statistical analysis
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cellview.utils.ladder import (
    generate_verification_ladder,
    GateSemiprime,
    BASE_SEED,
)


def analyze_gate(gate: GateSemiprime) -> Dict[str, Any]:
    """Analyze a single gate for corridor properties."""
    if gate.p is None or gate.q is None:
        return None
    
    # Basic properties
    analysis = {
        "gate": gate.gate,
        "target_bits": gate.target_bits,
        "actual_bits": gate.actual_bits,
        "bit_ratio": gate.bit_ratio,
        "p": gate.p,
        "q": gate.q,
        "p_bits": gate.p_bits,
        "q_bits": gate.q_bits,
        "N": gate.N,
        "sqrt_N": gate.sqrt_N,
    }
    
    # Corridor metrics
    analysis["p_distance_from_sqrt"] = gate.sqrt_N - gate.p
    analysis["p_as_fraction_of_sqrt"] = gate.p / gate.sqrt_N if gate.sqrt_N > 0 else 0
    
    # Search space metrics
    # "Corridor width" is the range around p that would need to be searched
    # If p is much smaller, the corridor is narrower in absolute terms
    # but might be relatively wider in terms of percentage of search space
    
    # Absolute corridor metrics
    analysis["absolute_corridor_from_2_to_p"] = gate.p - 2
    analysis["absolute_corridor_p_to_sqrt"] = gate.sqrt_N - gate.p
    
    # Relative corridor metrics (as fraction of full search space [2, sqrt(N)])
    full_space = gate.sqrt_N - 2
    if full_space > 0:
        analysis["relative_position_of_p"] = (gate.p - 2) / full_space
        analysis["relative_corridor_to_sqrt"] = (gate.sqrt_N - gate.p) / full_space
    else:
        analysis["relative_position_of_p"] = 0
        analysis["relative_corridor_to_sqrt"] = 0
    
    # Trial division complexity (number of candidates to check if doing naive sweep)
    # This is the "search burden" - how many candidates before finding p
    analysis["trial_division_burden"] = gate.p - 2
    
    # Bit imbalance (higher = more imbalanced)
    if gate.p_bits and gate.q_bits:
        analysis["bit_imbalance"] = gate.q_bits - gate.p_bits
        analysis["bit_ratio_actual"] = gate.q_bits / gate.p_bits if gate.p_bits > 0 else 0
    
    return analysis


def analyze_ladder(ladder: List[GateSemiprime], bit_ratio: int) -> Dict[str, Any]:
    """Analyze an entire ladder for a given bit ratio."""
    gates_analysis = []
    
    for gate in ladder:
        if gate.gate == "G127":  # Skip challenge gate
            continue
        
        analysis = analyze_gate(gate)
        if analysis:
            gates_analysis.append(analysis)
    
    # Compute aggregate statistics
    if not gates_analysis:
        return {"bit_ratio": bit_ratio, "gates": [], "statistics": {}}
    
    stats = {
        "bit_ratio": f"1:{bit_ratio}",
        "num_gates": len(gates_analysis),
        "avg_p_as_fraction_of_sqrt": sum(g["p_as_fraction_of_sqrt"] for g in gates_analysis) / len(gates_analysis),
        "avg_relative_position_of_p": sum(g["relative_position_of_p"] for g in gates_analysis) / len(gates_analysis),
        "avg_bit_imbalance": sum(g["bit_imbalance"] for g in gates_analysis) / len(gates_analysis),
        "min_p_bits": min(g["p_bits"] for g in gates_analysis),
        "max_p_bits": max(g["p_bits"] for g in gates_analysis),
        "min_q_bits": min(g["q_bits"] for g in gates_analysis),
        "max_q_bits": max(g["q_bits"] for g in gates_analysis),
    }
    
    # Check for specific gates (G030, G060, G090, G120, G130)
    sample_gates = {}
    for target_gate in ["G030", "G060", "G090", "G120", "G130"]:
        gate_data = next((g for g in gates_analysis if g["gate"] == target_gate), None)
        if gate_data:
            sample_gates[target_gate] = {
                "p_bits": gate_data["p_bits"],
                "q_bits": gate_data["q_bits"],
                "p": gate_data["p"],
                "p_as_fraction_of_sqrt": gate_data["p_as_fraction_of_sqrt"],
                "trial_division_burden": gate_data["trial_division_burden"],
            }
    
    return {
        "bit_ratio": f"1:{bit_ratio}",
        "statistics": stats,
        "sample_gates": sample_gates,
        "all_gates": gates_analysis,
    }


def run_experiment() -> Dict[str, Any]:
    """Run the complete experiment comparing bit ratios."""
    print("=" * 80)
    print("BIT RATIO FALSIFICATION EXPERIMENT")
    print("=" * 80)
    print()
    
    bit_ratios = [3, 4, 5]
    results = {}
    
    for bit_ratio in bit_ratios:
        print(f"Generating ladder for bit ratio 1:{bit_ratio}...")
        ladder = generate_verification_ladder(base_seed=BASE_SEED, bit_ratio=bit_ratio)
        
        # Verify generation
        non_g127 = [g for g in ladder if g.gate != "G127"]
        print(f"  Generated {len(non_g127)} gates (excluding G127)")
        
        # Analyze
        analysis = analyze_ladder(ladder, bit_ratio)
        results[f"ratio_1_{bit_ratio}"] = analysis
        
        print(f"  Average p as fraction of sqrt(N): {analysis['statistics']['avg_p_as_fraction_of_sqrt']:.6e}")
        print(f"  Average bit imbalance (q_bits - p_bits): {analysis['statistics']['avg_bit_imbalance']:.1f}")
        print()
    
    # Comparative analysis
    print("=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()
    
    comparison = {
        "experiment_metadata": {
            "base_seed": BASE_SEED,
            "bit_ratios_tested": bit_ratios,
            "gates_per_ladder": 13,  # excluding G127
        },
        "ratio_results": results,
    }
    
    # Print comparison table
    print(f"{'Metric':<40} {'1:3':<15} {'1:4':<15} {'1:5':<15}")
    print("-" * 85)
    
    metrics = [
        ("avg_p_as_fraction_of_sqrt", "Avg p/sqrt(N)"),
        ("avg_relative_position_of_p", "Avg relative position of p"),
        ("avg_bit_imbalance", "Avg bit imbalance"),
        ("min_p_bits", "Min p bits"),
        ("max_p_bits", "Max p bits"),
    ]
    
    for metric_key, metric_label in metrics:
        values = []
        for bit_ratio in bit_ratios:
            value = results[f"ratio_1_{bit_ratio}"]["statistics"][metric_key]
            if isinstance(value, float):
                values.append(f"{value:.6e}")
            else:
                values.append(f"{value}")
        
        print(f"{metric_label:<40} {values[0]:<15} {values[1]:<15} {values[2]:<15}")
    
    print()
    print("=" * 80)
    print("SAMPLE GATES (G130)")
    print("=" * 80)
    print()
    
    for bit_ratio in bit_ratios:
        sample = results[f"ratio_1_{bit_ratio}"]["sample_gates"].get("G130")
        if sample:
            print(f"Ratio 1:{bit_ratio}:")
            print(f"  p = {sample['p']} ({sample['p_bits']} bits)")
            print(f"  q bits = {sample['q_bits']}")
            print(f"  p/sqrt(N) = {sample['p_as_fraction_of_sqrt']:.6e}")
            print(f"  Trial division burden = {sample['trial_division_burden']:,}")
            print()
    
    return comparison


def main():
    """Main entry point for the experiment."""
    print("Starting Bit Ratio Falsification Experiment")
    print()
    
    # Run the experiment
    results = run_experiment()
    
    # Save results
    output_dir = Path(__file__).parent
    output_file = output_dir / "experiment_results.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print()
    print("Experiment complete!")
    
    return results


if __name__ == "__main__":
    main()
