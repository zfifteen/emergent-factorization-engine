import argparse
import json
import math
from typing import Dict, List
import yaml
from mpmath import mp, mpf, sqrt as mp_sqrt
from decimal import Decimal
from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)
import random

# Known factors for gates where available (add for lower gates if known)
known_factors = {
    # 'G010': 13,  # example
    # add more
}


def main():
    parser = argparse.ArgumentParser(
        description="Run ablation experiments for emergent vs baseline ranking"
    )
    parser.add_argument("--gates", nargs="+", default=["G100", "G110", "G120"])
    parser.add_argument("--candidate_halfwidth", type=int, default=5000000)
    parser.add_argument("--swap_steps", type=int, default=500)
    parser.add_argument("--output_dir", default="logs/ablation")
    args = parser.parse_args()

    ladder = load_ladder("src/cellview/data/challenge_ladder.yaml")
    summary = []
    os.makedirs(args.output_dir, exist_ok=True)

    for gate in args.gates:
        item = next(i for i in ladder if i["gate"] == gate)
        N = item["N"]
        effective_seed = item["effective_seed"]
        p_true = known_factors.get(gate, None)

        candidates = generate_candidates(N, args.candidate_halfwidth)

        # Baseline geometric ranking
        sqrt_n = float(mp_sqrt(N))
        sorted_baseline = sorted(candidates, key=lambda d: abs(d - sqrt_n))
        baseline_energies = [abs(d - sqrt_n) for d in sorted_baseline]
        baseline_rank = (
            effective_corridor_width(sorted_baseline, p_true)
            if p_true and p_true in set(sorted_baseline)
            else None
        )
        baseline_entropy = corridor_entropy(baseline_energies)
        baseline_viable = viable_region_size(
            [(d, e) for d, e in zip(sorted_baseline, baseline_energies)],
            threshold=1000.0,
        )

        # Emergent method
        algotypes = [
            "dirichlet5",
            "arctan_geodesic",
            "z5d",
        ]  # Adjust based on available heuristics
        rng = random.Random(effective_seed)
        energy_specs = default_specs()
        engine = CellViewEngine(
            N,
            candidates,
            algotypes,
            energy_specs,
            rng,
            max_steps=args.swap_steps,
            ablation_mode=True,
            gate_id=gate,
        )
        result = engine.run()
        ranked_emergent = [item["n"] for item in result["ranked_candidates"]]
        energies_emergent = [
            Decimal(item["energy"]) for item in result["ranked_candidates"]
        ]
        emergent_rank = (
            effective_corridor_width(ranked_emergent, p_true)
            if p_true and p_true in set(ranked_emergent)
            else None
        )
        emergent_entropy = corridor_entropy(energies_emergent)
        emergent_viable = viable_region_size(
            [
                (item["n"], Decimal(item["energy"]))
                for item in result["ranked_candidates"]
            ],
            threshold=Decimal("1"),
        )

        summary.append(
            {
                "gate": gate,
                "N": N,
                "num_candidates": len(candidates),
                "baseline_rank": baseline_rank,
                "emergent_rank": emergent_rank,
                "baseline_entropy": baseline_entropy,
                "emergent_entropy": emergent_entropy,
                "baseline_viable": baseline_viable,
                "emergent_viable": emergent_viable,
                "dg_index": result.get("dg_index", 0),
                "max_aggregation": max(result["aggregation"])
                if result["aggregation"]
                else 0,
                "json_log": f"{args.output_dir}/gate_{gate}.json",
            }
        )

        # Save per-gate json if not already from engine
        gate_data = {
            "gate": gate,
            "baseline": {
                "sorted_candidates": sorted_baseline,
                "energies": baseline_energies,
                "rank": baseline_rank,
                "entropy": baseline_entropy,
                "viable": baseline_viable,
            },
            "emergent": {
                "result": result,
                "rank": emergent_rank,
                "entropy": emergent_entropy,
                "viable": emergent_viable,
            },
        }
        with open(f"{args.output_dir}/gate_{gate}.json", "w") as f:
            json.dump(gate_data, f, indent=2)

    # Save summary
    with open(f"{args.output_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Ablation experiments completed. Summary saved to summary.json")


def load_ladder(path: str) -> List[Dict]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return data["ladder"]


def generate_candidates(N: int, halfwidth: int) -> List[int]:
    mp.dps = 50
    sqrt_n = mp.sqrt(N)
    candidates = []
    for offset in range(-halfwidth, halfwidth + 1):
        cand = int(sqrt_n + offset)
        if cand > 1:
            candidates.append(cand)
    return candidates


if __name__ == "__main__":
    main()
