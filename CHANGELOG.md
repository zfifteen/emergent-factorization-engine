# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `src/cellview/metrics/corridor.py`: New module for corridor-width metrics (Effective Width, Entropy, Viable Region Size).
- `experiments/emergent_vs_baseline/run_ablation.py`: Paired ablation experiment harness.
- CLI: Added `--ablation-mode` flag to `run_cellview.py`.
- Instrumentation: Added `trace_activity` and `dg_index_series` tracking to `CellViewEngine`.

### Changed
- **BREAKING CHANGE**: `CellViewEngine.step()` now returns a `Tuple[int, List[int]]` instead of a single `int`. The second element contains the values of candidates that were swapped during the step.
- `corridor_entropy` now uses range-based normalization [0, 10] for improved numerical stability and discriminative peaking in Softmax.

### Fixed
- Tracing Memory: Added hard limits to `active_candidates_per_step` and `active_candidates` tracing in `CellViewEngine` to prevent OOM on long runs.
- Robust Error Handling: Added top-level try-except blocks to CLI and robust energy-resolver fallback in the engine to prevent unlogged crashes.
- Scale Guard: Added `MIN_GATE_N = 1e9` to the ablation runner to prevent geometric clustering bias on small semiprimes.
- Corrected search domain centering in ablation results documentation.
