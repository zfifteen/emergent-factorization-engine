# Emergent Factorization Engine

## Abstract
This repository is a whitebox exploration of emergent problem-solving framed as integer factorization. Drawing on Levin et al. (2023) about decentralized “cell-view” sorting, we model factors as autonomous cells that rearrange themselves in an unreliable substrate, exhibit clustering, and occasionally step away from the goal before converging. A pure-Python Z5D prime predictor supplies unbalanced semiprime ladders (1:3 p:q bit ratio) that expose narrow search corridors; the engine measures how mixed algotypes, noise, and frozen cells influence convergence on both small and 127-bit challenges. The emphasis is explanatory, not cryptanalytic: we instrument the dynamics of emergence under controlled seeds and perturbations, then report DG (delayed gratification), aggregation (clustering), and sortedness as proxies for competence.

## Method Deep Dive (Levin-inspired synthesis)
The engine instantiates Levin’s decentralization by assigning every integer “cell” a local algotype (bubble or selection variant) that decides swaps with only neighbor knowledge; no global controller exists. Hardware unreliability is explicit: frozen and immovable cells force the swarm to route around defects, stressing robustness. Chimeric populations mix algotypes in one lattice; the `aggregation` metric quantifies spontaneous clustering and segregation that mirrors the paper’s chimeric-array behaviors. Time-series analysis includes `detect_dg` to surface delayed-gratification episodes—temporary regressions that lead to higher later progress—and `sortedness` to score approach to the target anatomical line (ordered array). Factorization stimuli are unbalanced semiprimes, chosen because p ≪ √N makes naive corridor searches brittle, rewarding emergent navigation instead. The prime supply chain uses `_simple_next_prime`, which couples the pure-Python Z5D predictor with Miller–Rabin verification and a tiny-n fallback to keep correctness independent of predictor error. Experiments remain reproducible via fixed seeds and packaged ladders but are perturbable to reveal competencies rather than encode them. 

This is not a practical competitor to GNFS / deployed RSA.

## Ladders (Verification vs Challenge)
- **Verification ladder**: `generate_verification_ladder()` (alias `generate_ladder()`) reveals p/q for regression and CI. Packaged at `src/cellview/data/validation_ladder.yaml`.
- **Challenge ladder**: `generate_challenge_ladder()` withholds p/q (factors_revealed=False) but keeps identical Ns/seeds; packaged at `src/cellview/data/challenge_ladder.yaml`. Use it for blind factoring runs.
- **YAML loader**: `load_ladder_yaml(kind="validation" | "challenge")` or pass a custom `path`. `print_ladder_summary(...)` auto-labels the ladder and redacts factors when appropriate.

**Disclaimer**: This project is not a practical attack on deployed RSA and does not compete with GNFS-class algorithms; it is an experimental search/measurement harness on small and 127-bit test cases.

## Repository Layout
- `src/cellview/` – engine, heuristics, utilities, CLI, experiments.
- `src/cellview/utils/z5d_predictor/` – pure-Python Z5D nth-prime predictor (mpmath) feeding the ladder.
- `src/cellview/data/validation_ladder.yaml` – factor-revealing verification gates.
- `src/cellview/data/challenge_ladder.yaml` – factor-free challenge gates (Ns only).
- `tests/` – regression for ladder, predictor, metrics, guardrails; verbose ladder reports are printed under pytest `-s`.
- `docs/` – goal statement, implementation codex, METAcells proposal, simulation findings, Z5D notes, and the source paper PDF (`docs/2401.05375v1.pdf`).
- `logs/` – JSON outputs from `cellview.cli.run_cellview` (git-ignored).

## Getting Started
1) `python -m venv .venv && source .venv/bin/activate`
2) `pip install -e .`
3) Inspect CLI: `python -m cellview.cli.run_cellview --help`
4) Run tests: `python -m pytest`

## Testing & Verification
- Core suite: `python -m pytest tests/test_ladder.py tests/test_z5d_predictor.py tests/test_metrics.py tests/test_guardrails.py`
- CI uses the verification ladder; a separate test asserts the challenge ladder never exposes factors.

## CLI in Brief
- Entry: `python -m cellview.cli.run_cellview`
- Modes: `--mode challenge` (canonical 127-bit N) or `--mode validation` with `--override-n` for small Ns.
- Candidate domains: corridor/dense bands, validation full-domain, or file-based candidates.
- Outputs: JSON log with ranked candidates, DG/aggregation traces, certification results.

## Logs
Written to `logs/` with run config, RNG seed, swap counts, metrics over time, ranked candidates, and certification payloads for audit or visualization.
