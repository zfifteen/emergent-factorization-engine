# Emergent Factorization Engine

Research artifacts and tooling for the Emergence cell-view engine, reorganized into a standard Python project layout for reproducible factorization experiments.

## What’s inside
- `src/cellview/` – core package (engine, heuristics, utilities, CLI, experiments).
- `src/cellview/data/validation_ladder.yaml` – canonical validation gates and progression criteria.
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
- **Canonical challenge pipeline** – The CLI ties together deterministic RNG, geometric heuristics, cell-view dynamics, DG/aggregation metrics, and JSON logging for the 127-bit semiprime.
- **Pure-Python Z5D predictor** – The ladder generator now calls `predict_nth_prime` (mpmath) and verifies outputs with Miller-Rabin for reproducible semiprime construction.
- **Documentation-first experiments** – `docs/` includes the mission goal, implementation codex, METAcells proposal, simulation findings, and Z5D integration notes so you can understand the rationale without running anything first.

## Testing & verification

- `python -m pytest tests/test_ladder.py tests/test_z5d_predictor.py tests/test_metrics.py tests/test_guardrails.py` – covers the ladder generator, Z5D predictor, emergent metrics, and guardrails.

## Logs

Logs are written to `logs/` (ignored by git). Each run records the config, RNG seed, swap counts, metrics, final lattice, ranked candidates, and certification output for auditing or visualization tools.
