# Emergent Factorization Engine

Research artifacts and tooling for the Emergence cell-view engine, reorganized into a standard Python project layout for reproducible factorization experiments.

## What’s inside
- `src/cellview/` – core package (engine, heuristics, utilities, CLI, experiments).
- `src/cellview/data/validation_ladder.yaml` – canonical validation gates and progression criteria.
- `src/cellview/data/challenge_ladder.yaml` – factor-free challenge set (Ns only, no p/q leakage).
- `src/cellview/utils/z5d_predictor/` – pure-Python Z5D nth-prime predictor (mpmath-powered) that feeds the ladder generator.
- `tests/` – deterministic unit/regression tests for the engine, ladder, metrics, and predictor.
- `docs/` – mission goals, implementation notes, experiment write-ups, and integration guidance.
- `logs/` – runtime JSON outputs from `cellview.cli.run_cellview` (ignored).

## Getting started

1. Create an isolated environment: `python -m venv .venv && source .venv/bin/activate`.
2. Install the package: `pip install -e .`.
3. Inspect the CLI: `python -m cellview.cli.run_cellview --help`.
4. Run the test suite: `python -m pytest`.

## Highlights
- **Dual ladders** – Verification ladder (default) reveals factors for regression; challenge ladder withholds factors (G010–G130 including G127) for blind factoring exercises. Both use the same seeds/ratio and live under `cellview.utils.ladder`.
- **Canonical challenge pipeline** – The CLI ties together deterministic RNG, geometric heuristics, cell-view dynamics, DG/aggregation metrics, and JSON logging for the 127-bit semiprime.
- **Pure-Python Z5D predictor** – The ladder generator calls `predict_nth_prime` (mpmath) and verifies outputs with Miller-Rabin for reproducible semiprime construction.
- **Documentation-first experiments** – `docs/` includes the mission goal, implementation codex, METAcells proposal, simulation findings, and Z5D integration notes so you can understand the rationale without running anything first.

## Levin et al. (2023) concepts applied
- **Distributed “cell-view” sorting** – Arrays sort bottom-up: each element (cell) runs its algotype locally (bubble/selection variants), matching the paper’s decentralization and absence of a top-down controller.
- **Unreliable substrate** – Frozen/immovable cells are supported to mirror damaged cells in the study; robustness is evaluated under these perturbations.
- **Chimeric algotypes & aggregation** – Mixed algotypes in one run let us track clustering via the `aggregation` metric, reflecting the paper’s chimeric arrays and emergent grouping behaviors.
- **Delayed gratification detector** – `metrics.detect_dg` scores peak–valley–higher-peak episodes, capturing the paper’s “move away to get closer later” competency.
- **Goal-tracking via sortedness** – `sortedness` measures local monotonicity as the proxy for reaching the anatomical target line, aligning with the paper’s axis-order objective.
- **Reproducible perturbation experiments** – Seeds and ladder gates give fixed scenarios to test how the decentralized system copes with errors, paralleling the paper’s emphasis on robustness and emergent competencies.

## Ladders: verification vs. challenge
- Call `generate_verification_ladder()` (or legacy `generate_ladder()`) to get reproducible gates with `p`/`q` present. Used by tests and CI.
- Call `generate_challenge_ladder()` for the blind set: same Ns, no factors retained, `factors_revealed=False` per gate. The packaged metadata is `src/cellview/data/challenge_ladder.yaml`.
- YAML loader: `load_ladder_yaml(kind="validation" | "challenge")` to pick the packaged asset; pass a `path` to load custom ladders.
- Printing: `print_ladder_summary(generate_challenge_ladder())` shows the same progression with factors redacted.

## Testing & verification

- `python -m pytest tests/test_ladder.py tests/test_z5d_predictor.py tests/test_metrics.py tests/test_guardrails.py` – covers the ladder generator, Z5D predictor, emergent metrics, and guardrails.
- Tests exercise the verification ladder; challenge ladder coverage ensures factors stay hidden but does not expose them in fixtures or outputs.

## Logs

Logs are written to `logs/` (ignored by git). Each run records the config, RNG seed, swap counts, metrics, final lattice, ranked candidates, and certification output for auditing or visualization tools.
