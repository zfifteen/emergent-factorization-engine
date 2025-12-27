#!/usr/bin/env python3
"""
Ablation experiment: emergent vs baseline ranking on test gates.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.utils.rng import rng_from_hex
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


# Test gates (small semiprimes for validation)
TEST_GATES = {
    "G010": 35,  # 5 * 7
    "G100": 10403,  # 101 * 103
    "G110": 11663,  # 107 * 109
    "G120": 14279,  # 113 * 127
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run corridor-width ablation")
    parser.add_argument(
        "--gates", nargs="+", required=True, help="Gate names (e.g., G100 G110 G120)"
    )
    parser.add_argument(
        "--candidate-halfwidth", type=int, default=5000, help="±halfwidth around √N"
    )
    parser.add_argument("--swap-steps", type=int, default=500, help="Swap steps")
    parser.add_argument("--output-dir", type=Path, default="logs", help="Output dir")
    return parser.parse_args()


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for gate in args.gates:
        N = TEST_GATES.get(gate)
        if N is None:
            print(f"Unknown gate {gate}, skipping")
            continue

        isqrt_N = int(N**0.5)
        start = max(2, isqrt_N - args.candidate_halfwidth)  # Ensure start >= 2
        end = isqrt_N + args.candidate_halfwidth
        candidates_list = list(range(start, end))

        # Find true factor
        p = None
        for c in candidates_list:
            if c > 1 and N % c == 0:
                p = c
                break

        if p is None:
            print(f"{gate}: No factor in band [{start}, {end}), skipping")
            continue

        # Validate p is within bounds (defensive check)
        if p < start or p >= end:
            print(f"WARNING: {gate} factor p={p} outside band [{start}, {end})")
            continue

        # Baseline: geometric rank
        baseline_ranked = sorted(candidates_list, key=lambda d: abs(d - isqrt_N))
        baseline_rank = effective_corridor_width(
            [(c, abs(c - isqrt_N)) for c in baseline_ranked], p
        )
        baseline_energies = [abs(c - isqrt_N) for c in baseline_ranked]
        baseline_entropy = corridor_entropy(baseline_energies)

        # Emergent: Dirichlet only
        seed_hex = f"{N:064x}"  # Deterministic seed from N
        rng = rng_from_hex(seed_hex)
        energy_specs = default_specs()
        
        engine = CellViewEngine(
            N=N,
            candidates=candidates_list,
            algotypes=["dirichlet5"],
            energy_specs=energy_specs,
            rng=rng,
            sweep_order="ascending",
            max_steps=args.swap_steps,
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
        
        emergent_energies = [float(entry["energy"]) for entry in emergent_ranked]
        emergent_entropy = corridor_entropy(emergent_energies)

        # Record
        result = {
            "gate": gate,
            "N": str(N),
            "p": p,
            "baseline": {
                "metrics": {
                    "rank_of_p": baseline_rank,
                    "corridor_entropy": baseline_entropy,
                }
            },
            "emergent": {
                "metrics": {
                    "rank_of_p": emergent_rank,
                    "corridor_entropy": emergent_entropy,
                }
            },
        }

        out_file = args.output_dir / f"ablation_{gate}.json"
        with open(out_file, "w") as f:
            json.dump(result, f, indent=2)

        print(
            f"{gate}: baseline_rank={baseline_rank}, emergent_rank={emergent_rank}, delta={baseline_rank - emergent_rank}"
        )


if __name__ == "__main__":
    main()
