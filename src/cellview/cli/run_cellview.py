from math import isqrt
import argparse
import json
import os
from typing import Dict

from cellview.cert.certify import certify_top_m
from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import EnergySpec, default_specs, resolve_energy
from cellview.utils import candidates as cand_utils
from cellview.utils.corridors import (
    default_range_for,
    expand_corridors_to_candidates,
    generate_corridors,
    levin_sort_corridors,
    score_corridor,
)
from cellview.utils.challenge import CHALLENGE
from cellview.utils.logging import ensure_dir, timestamp_id, write_json
from cellview.utils.rng import rng_from_hex
from cellview.metrics.corridor import effective_corridor_width, corridor_entropy
from cellview.utils.ladder import generate_verification_ladder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emergence cell-view search engine (geofac)")
    parser.add_argument("--mode", choices=["challenge", "validation"], default="challenge")
    parser.add_argument("--override-n", type=int, help="Optional override modulus (for validation)")
    parser.add_argument("--samples", type=int, default=50_000, help="Samples for corridor mode")
    parser.add_argument("--window", type=int, default=cand_utils.DEFAULT_WINDOW, help="Window around sqrt(N)")
    parser.add_argument("--bands", type=str, help="Optional multiband spec center:window:samples,... (sparse)")
    parser.add_argument(
        "--dense-window",
        type=int,
        help="Use dense contiguous band of +/- dense_window around sqrt(N) (challenge mode only).",
    )
    parser.add_argument(
        "--dense-bands",
        type=str,
        help="Dense bands spec center:halfwidth,... (challenge mode only), full coverage per band.",
    )
    parser.add_argument("--algotypes", type=str, default="dirichlet5", help="Comma-separated algotypes")
    parser.add_argument("--sweep-order", choices=["ascending", "random"], default="ascending")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--top-m", type=int, default=50, help="Number of candidates to certify")
    parser.add_argument("--seed-hex", type=str, help="Override seed hex")
    parser.add_argument("--candidates-file", type=str, help="Optional file with newline-separated candidates")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to store JSON logs")
    
    parser.add_argument("--ablation-mode", action="store_true", help="Run baseline comparison and log ablation metrics")
    parser.add_argument("--trace-activity", action="store_true", help="Trace active candidates per step (memory intensive)")

    # Stage-1 meta-cell (corridor) mode
    parser.add_argument("--corridor-mode", action="store_true", help="Two-stage corridor meta-cell pipeline")
    parser.add_argument("--corridor-count", type=int, default=20_000, help="Number of coarse corridors to rank")
    parser.add_argument(
        "--corridor-halfwidth", type=int, default=1_000_000, help="Half-width of each corridor (integer radius)"
    )
    parser.add_argument(
        "--corridor-samples",
        type=int,
        default=256,
        help="Samples per corridor to estimate resonance energy",
    )
    parser.add_argument(
        "--corridor-topk",
        type=int,
        default=8,
        help="Top-ranked corridors to expand into dense candidates",
    )
    parser.add_argument(
        "--corridor-agg",
        type=str,
        default="p5",
        help="Energy aggregator for corridors: 'min' or percentile like 'p5'",
    )
    parser.add_argument(
        "--corridor-range",
        type=str,
        help="Optional start:end for corridor centers (defaults to challenge-biased window or [2, sqrt(N)])",
    )
    return parser.parse_args()


def load_candidates(args, N, rng):
    if args.candidates_file:
        with open(args.candidates_file, "r", encoding="utf-8") as f:
            vals = [int(line.strip()) for line in f if line.strip()]
        return vals

    # Dense contiguous options (challenge mode)
    if args.dense_window:
        center = int((N ** 0.5))
        half = args.dense_window
        return cand_utils.dense_band(center, half)
    if args.dense_bands:
        bands_spec = []
        for token in args.dense_bands.split(","):
            center, half = token.split(":")
            bands_spec.append((int(center), int(half)))
        return cand_utils.dense_bands(bands_spec)

    if args.mode == "validation":
        if N > 10**12:
            raise ValueError("Validation mode expects small N; override N accordingly.")
        return cand_utils.validation_full_domain(N)

    # Small-N shortcut even in challenge mode to avoid absurd corridors
    if args.mode == "challenge" and N < 10**8:
        return cand_utils.validation_full_domain(N)

    # challenge mode corridors
    if args.bands:
        bands_spec = []
        for token in args.bands.split(","):
            center, window, samples = token.split(":")
            bands_spec.append((int(center), int(window), int(samples)))
        return cand_utils.multiband_corridors(N, rng, bands_spec)

    return cand_utils.corridor_around_sqrt(N, rng, samples=args.samples, window=args.window)


def main():
    args = parse_args()
    N = args.override_n or CHALLENGE.n
    run_id = timestamp_id("run")
    ensure_dir(args.log_dir)

    try:
        algotypes = [a.strip() for a in args.algotypes.split(",") if a.strip()]
        energy_specs: Dict[str, any] = default_specs()
        rng = rng_from_hex(args.seed_hex)

        stage1_corridor_info = None

        if args.corridor_mode:
            # Stage 1: corridor generation and ranking
            range_start, range_end = default_range_for(
                N,
                *([int(x) for x in args.corridor_range.split(":")] if args.corridor_range else (None, None)),
            )

            corridors = generate_corridors(
                range_start=range_start,
                range_end=range_end,
                half_width=args.corridor_halfwidth,
                num_corridors=args.corridor_count,
                rng=rng,
            )

            # Use the first algotype (or default) for corridor energy scoring
            algo_key = algotypes[0] if algotypes else "dirichlet5"
            energy_spec = energy_specs.get(algo_key) or default_specs().get(algo_key)
            if energy_spec is None:
                energy_fn = resolve_energy(algo_key)
                energy_spec = EnergySpec(algo_key, energy_fn, {})
                energy_specs[algo_key] = energy_spec

            cache: Dict[tuple, any] = {}
            for c in corridors:
                score_corridor(
                    corridor=c,
                    N=N,
                    energy_spec=energy_spec,
                    samples=args.corridor_samples,
                    rng=rng,
                    aggregator=args.corridor_agg,
                    energy_cache=cache,
                )

            corridor_sort = levin_sort_corridors(corridors, max_steps=args.max_steps)
            ranked_corridors = sorted(corridors, key=lambda c: c.energy)
            top_corridors = ranked_corridors[: args.corridor_topk]

            candidates = expand_corridors_to_candidates(top_corridors)

            stage1_corridor_info = {
                "range_start": range_start,
                "range_end": range_end,
                "corridor_count": len(corridors),
                "corridor_halfwidth": args.corridor_halfwidth,
                "corridor_samples": args.corridor_samples,
                "corridor_agg": args.corridor_agg,
                "top_corridor_count": len(top_corridors),
                "top_corridors": [
                    {"center": c.center, "low": c.low, "high": c.high, "energy": str(c.energy)}
                    for c in top_corridors
                ],
                "levin_metrics": corridor_sort,
            }

            print(
                f"Corridor mode: ranked {len(corridors)} corridors across [{range_start}, {range_end}] "
                f"→ top {len(top_corridors)} expanded to {len(candidates)} candidates"
            )
        else:
            candidates = load_candidates(args, N, rng)

        if args.mode == "challenge":
            cand_utils.guard_dense_domain_for_challenge(len(candidates), n=N)

        # --- Ablation Mode: Metrics & Baseline setup ---
        ablation_baseline = None
        p_true = None
        if args.ablation_mode:
            # Attempt to find p_true from validation ladder
            try:
                ladder = generate_verification_ladder()
                for g in ladder:
                    if g.N == N:
                        p_true = g.p
                        break
            except Exception:
                pass

            sqrt_N = isqrt(N)
            base_cands = [{'n': c, 'energy': abs(c - sqrt_N)} for c in candidates]
            base_cands.sort(key=lambda x: x['energy'])
            
            ablation_baseline = {
                "entropy": corridor_entropy([x['energy'] for x in base_cands])
            }
            if p_true:
                ablation_baseline["rank"] = effective_corridor_width(base_cands, N, p_true)

        engine = CellViewEngine(
            N=N,
            candidates=candidates,
            algotypes=algotypes,
            energy_specs=energy_specs,
            rng=rng,
            sweep_order=args.sweep_order,
            max_steps=args.max_steps,
            trace_activity=args.trace_activity,
        )
        run_results = engine.run()

        cert_results = certify_top_m(run_results["ranked_candidates"], N, m=args.top_m)

        payload = {
            "config": vars(args),
            "N": str(N),
            "seed_hex": args.seed_hex or CHALLENGE.seed_hex,
            "candidate_count": len(candidates),
            "results": run_results,
            "certification": cert_results,
        }

        if stage1_corridor_info:
            payload["stage1_corridors"] = stage1_corridor_info

        if args.ablation_mode:
            payload["ablation_baseline"] = ablation_baseline
            # Emergent metrics
            emergent_cands = run_results["ranked_candidates"]
            emergent_metrics = {
                "entropy": corridor_entropy([float(x['energy']) for x in emergent_cands])
            }
            if p_true:
                emergent_metrics["rank"] = effective_corridor_width(emergent_cands, N, p_true)
            payload["ablation_emergent"] = emergent_metrics

        log_path = os.path.join(args.log_dir, f"{run_id}.json")
        write_json(log_path, payload)

        print(f"Run complete. Candidates: {len(candidates)}. Log: {log_path}")
        print(f"Top-{args.top_m} certified (showing first 5):")
        for row in cert_results[:5]:
            print(json.dumps(row, default=str))

    except Exception as e:
        error_payload = {
            "config": vars(args),
            "error": str(e),
            "type": type(e).__name__,
            "status": "failed"
        }
        error_path = os.path.join(args.log_dir, f"{run_id}_error.json")
        write_json(error_path, error_payload)
        print(f"CRITICAL ERROR: {e}. Diagnostics saved to {error_path}")
        raise



if __name__ == "__main__":
    main()