# Emergent Factorization Engine

## Abstract
This project is a whitebox testbed for emergent factorization and morphogenetic search. It pairs a pure-Python prime generator (Z5D-based) with a decentralised “cell-view” engine inspired by Levin et al. (2023) on autonomous sorting. The system intentionally stresses unreliable substrates, mixed behavioral types, and delayed-gratification dynamics while producing deterministic ladders of unbalanced semiprimes for both verification and blind challenges.

## Method Deep Dive (Levin-inspired & novel elements)
- **Distributed cell-view agents**: Each integer “cell” executes its algotype locally (bubble/selection variants), mirroring the paper’s bottom-up control with no omniscient coordinator.
- **Unreliable substrate**: Frozen and immovable cells simulate damaged tissue; robustness is evaluated as the engine sorts despite execution failures.
- **Chimeric populations & aggregation**: Mixed algotypes run together; the `aggregation` metric tracks spontaneous clustering, echoing chimeric arrays in the paper.
- **Delayed-gratification detector**: `metrics.detect_dg` flags peak–valley–higher-peak episodes, quantifying the “step back to leap forward” competency highlighted by Levin et al.
- **Goal tracking via sortedness**: `sortedness` measures local monotonicity as a proxy for reaching the anatomical target line (ordered axis), aligning with morphogenesis analogies.
- **Deterministic yet perturbable experiments**: RNG seeds and ladder gates yield reproducible setups; perturbations (frozen cells, noisy candidates) reveal emergent resilience rather than baked-in shortcuts.
- **Unbalanced semiprimes as stimuli**: The ladder builds 1:3 factor-ratio semiprimes where p ≪ √N, creating search corridors that reward intelligent navigation over brute-force symmetry.
- **Prime supply chain**: `_simple_next_prime` uses the pure-Python Z5D predictor plus Miller–Rabin verification; tiny n fall back to trial division to stay robust when predictors are overkill.

## Ladders (Verification vs Challenge)
- **Verification ladder**: `generate_verification_ladder()` (alias `generate_ladder()`) reveals p/q for regression and CI. Packaged at `src/cellview/data/validation_ladder.yaml`.
- **Challenge ladder**: `generate_challenge_ladder()` withholds p/q (factors_revealed=False) but keeps identical Ns/seeds; packaged at `src/cellview/data/challenge_ladder.yaml`. Use it for blind factoring runs.
- **YAML loader**: `load_ladder_yaml(kind="validation" | "challenge")` or pass a custom `path`. `print_ladder_summary(...)` auto-labels the ladder and redacts factors when appropriate.

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
