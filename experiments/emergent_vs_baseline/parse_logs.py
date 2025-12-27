#!/usr/bin/env python3
"""
Parse ablation logs into CSV summary.
"""
import json
import csv
from pathlib import Path


def main():
    log_dir = Path("logs")
    output_csv = Path("summary.csv")

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "gate",
                "baseline_rank",
                "emergent_rank",
                "delta_rank",
                "baseline_entropy",
                "emergent_entropy",
            ]
        )

        for log_file in log_dir.glob("ablation_G*.json"):
            print(f"Processing {log_file}")
            with open(log_file, "r") as f:
                data = json.load(f)
                gate = data["gate"]
                b_rank = data["baseline"]["metrics"]["rank_of_p"]
                e_rank = data["emergent"]["metrics"]["rank_of_p"]
                delta = b_rank - e_rank
                b_ent = data["baseline"]["metrics"]["corridor_entropy"]
                e_ent = data["emergent"]["metrics"]["corridor_entropy"]
                writer.writerow([gate, b_rank, e_rank, delta, b_ent, e_ent])


if __name__ == "__main__":
    main()
