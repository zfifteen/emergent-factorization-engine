# Z5D Prime Predictor Integration

## Overview

The validation ladder now ships a **pure-Python Z5D predictor** powered by `mpmath`. It solves Riemann's
prime-counting function to estimate the nth prime and falls back to Miller-Rabin verification for safety.

## Architecture

The current topology is straightforward:

```
ladder.py → z5d_predictor (pure-Python)
```

### Files

- `src/cellview/utils/z5d_predictor/` - Pure-Python predictor implementation and helpers
- `src/cellview/utils/ladder.py` - Consumes the predictor to build the validation ladder
- `tests/test_z5d_predictor.py` - Predictor regression and sanity checks

## Usage

### Automatic (Recommended)

`generate_ladder()` internally calls `_simple_next_prime`, which estimates primes via the predictor and
then verifies them with Miller-Rabin. No further action is required.

### Manual Control

```python
from cellview.utils.z5d_predictor import predict_nth_prime, Z5DConfig

config = Z5DConfig(dps=64, K=12)
result = predict_nth_prime(1000000, config)
prime = int(round(float(result.predicted_prime)))
```

`predict_nth_prime` always returns a `Z5DResult` with convergence metadata so you can inspect precision
and iteration counts.

## Requirements

- `mpmath` (added as a dependency in `pyproject.toml`)
- Pure Python standard library (no native extension required)

## Testing

```bash
python -m pytest tests/test_z5d_predictor.py
python -m pytest tests/test_ladder.py
```

Tests verify:
- Z5D predictor math (mobius, logarithmic integral, Newton solver, etc.)
- Estimation accuracy for known nth primes
- Ladder integration still produces valid semiprimes

## Design Principles

1. **Pure Python:** No compiled binaries, all math lives in `mpmath`.
2. **Determinism:** Same seed and config always produce the same primes.
3. **Modularity:** Predictor is a standalone package that can be reused or replaced.
4. **Verification:** Every estimated prime is checked with Miller-Rabin/ trial division.
5. **Testability:** Packaged tests cover both the predictor and the ladder consumer.

## Notes

- `predict_nth_prime` uses a Dusart initializer + Newton-Raphson on R(x) = n.
- The predictor exposes low-level helpers (mobius, riemann_R, etc.) for advanced diagnostics.
- Precision is configurable via `Z5DConfig`; defaults are 96 decimal places and 10 R-terms.
