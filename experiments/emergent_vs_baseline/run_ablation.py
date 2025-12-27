#!/usr/bin/env python3
"""
Ablation experiment: emergent vs baseline ranking on G100-G110-G120.
"""
import argparse
import json
import sys
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
        N = canonical_N(gate)
        if N is None:
            print(f"Unknown gate {gate}, skipping")
            continue

        isqrt_N = int(N**0.5)
        start = isqrt_N - args.candidate_halfwidth
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
        cv = Cellview(N, candidates_list, energy_fn=dirichlet_energy)
        cv.run_swaps(args.swap_steps)
        emergent_ranked = cv.get_sorted_candidates()
        emergent_rank = effective_corridor_width(emergent_ranked, p)
        emergent_energies = [e for _c, e in emergent_ranked]
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
