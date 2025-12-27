#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
from math import isqrt
from decimal import Decimal
import sys

# Ensure src is in path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "src"))

from cellview.utils.ladder import generate_verification_ladder, GateSemiprime
from cellview.engine.engine import CellViewEngine
from cellview.metrics.corridor import effective_corridor_width, corridor_entropy, viable_region_size
from cellview.heuristics.core import EnergySpec, dirichlet_energy, arctan_geodesic_energy, z_metric_energy

def run_experiment(args):
    # 1. Setup Output Directory
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Get Gates
    ladder = generate_verification_ladder()
    target_gates = set(args.gates)
    gates_to_run = [g for g in ladder if g.gate in target_gates]
    
    if not gates_to_run:
        print(f"No gates found matching {target_gates}")
        return

    results_summary = []

    for gate in gates_to_run:
        print(f"Running ablation for {gate.gate} (N={gate.N})...")
        
        N = gate.N
        p_true = gate.p
        sqrt_N = isqrt(N)
        
        # 3. Generate Candidate Domain
        # Issue text says "dense band ±5M around √N", but G-series gates are unbalanced (p << √N).
        # We center the band around p_true to validate signal in its corridor.
        
        half_width = args.candidate_halfwidth
        center = p_true
        start = center - half_width
        end = center + half_width
        start = max(2, start)
        
        # Assertion to ensure p_true is actually in the search band
        assert start <= p_true <= end, f"p_true ({p_true}) is not in band [{start}, {end}]"
        
        print(f"  Generating candidates around p_true ({center}) [{start}, {end}]...")
        candidates = list(range(start, end + 1))
        print(f"  Generated {len(candidates)} candidates.")
        
        # --- Baseline Method ---
        print("  Running Baseline (Geometric)...")
        t0 = time.time()
        # Rank by |d - sqrt(N)|. 
        baseline_candidates = []
        for c in candidates:
            dist = abs(c - sqrt_N)
            baseline_candidates.append({'n': c, 'energy': dist})
        
        baseline_candidates.sort(key=lambda x: x['energy'])
        t_baseline = time.time() - t0
        print(f"  Baseline finished in {t_baseline:.2f}s")
        
        # Metrics
        rank_base = effective_corridor_width(baseline_candidates, N, p_true)
        energies_base = [x['energy'] for x in baseline_candidates]
        ent_base = corridor_entropy(energies_base)
        viable_base = viable_region_size(baseline_candidates, args.energy_threshold)
        
        print(f"  Baseline Rank: {rank_base}")
        
        # --- Emergent Method ---
        print("  Running Emergent (CellView)...")
        t1 = time.time()
        
        energy_specs = {
            "dirichlet5": EnergySpec("dirichlet5", dirichlet_energy, {"j": 5, "normalize": True, "invert": True}),
            "arctan_geodesic": EnergySpec("arctan_geodesic", arctan_geodesic_energy, {"sqrtN": sqrt_N, "scale": 2.0}),
            "z_metric": EnergySpec("z_metric", z_metric_energy, {"sqrtN": sqrt_N, "alpha": 0.2, "beta": 1.0})
        }
        
        algotypes = ["dirichlet5", "arctan_geodesic", "z_metric"]
        
        engine = CellViewEngine(
            N=N,
            candidates=candidates,
            algotypes=algotypes,
            energy_specs=energy_specs,
            rng=None, 
            max_steps=args.swap_steps,
            trace_activity=True # Ablation harness wants to trace activity
        )
        
        emergent_result = engine.run()
        t_emergent = time.time() - t1
        print(f"  Emergent finished in {t_emergent:.2f}s")
        
        emergent_candidates = emergent_result['ranked_candidates']
        
        # Metrics
        rank_emergent = effective_corridor_width(emergent_candidates, N, p_true)
        energies_emergent = [float(x['energy']) for x in emergent_candidates]
        ent_emergent = corridor_entropy(energies_emergent)
        viable_emergent = viable_region_size(emergent_candidates, args.energy_threshold)
        
        print(f"  Emergent Rank: {rank_emergent}")
        
        # Save logs
        log_data = {
            "gate": gate.gate,
            "N": str(N),
            "p_true": str(p_true),
            "baseline": {
                "rank": rank_base,
                "entropy": ent_base,
                "viable_count": viable_base,
                "time": t_baseline
            },
            "emergent": {
                "rank": rank_emergent,
                "entropy": ent_emergent,
                "viable_count": viable_emergent,
                "time": t_emergent,
                "metrics_series": {
                    "sortedness": emergent_result["sortedness"],
                    "aggregation": emergent_result["aggregation"],
                    "dg_index": emergent_result["dg_index_series"]
                },
                "dg_episodes": emergent_result["dg_episodes"],
                "active_candidates_per_step": emergent_result.get("active_candidates_per_step", [])
            }
        }
        
        log_file = out_dir / f"ablation_{gate.gate}.json"
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
        print(f"  Saved logs to {log_file}")
        
        # Add to summary
        if rank_base > 0:
            improvement = (rank_base - rank_emergent) / rank_base
        else:
            improvement = 0.0
            
        results_summary.append({
            "gate": gate.gate,
            "baseline_rank": rank_base,
            "emergent_rank": rank_emergent,
            "improvement": improvement
        })

    # Save summary CSV
    csv_file = out_dir / "summary.csv"
    with open(csv_file, 'w') as f:
        f.write("gate,baseline_rank,emergent_rank,improvement\n")
        for r in results_summary:
            f.write(f"{r['gate']},{r['baseline_rank']},{r['emergent_rank']},{r['improvement']:.4f}\n")
    print(f"Saved summary to {csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run corridor-width ablation experiments.")
    parser.add_argument("--gates", nargs="+", default=["G100", "G110", "G120"], help="Gates to test")
    parser.add_argument("--candidate_halfwidth", type=int, default=50000, help="Half-width of candidate band")
    parser.add_argument("--swap_steps", type=int, default=500, help="Number of swap steps")
    parser.add_argument("--output_dir", default="logs/ablation/", help="Output directory")
    parser.add_argument("--energy_threshold", type=float, default=1.0, help="Energy threshold for viable region count")
    
    args = parser.parse_args()
    run_experiment(args)