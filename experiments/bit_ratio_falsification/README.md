# Bit Ratio Falsification Experiment

This experiment tests the hypothesis that larger bit ratios (1:4, 1:5 vs current 1:3) create more effective "narrow search corridors" for factorization.

## Files

- **`FINDINGS.md`** - Complete experimental findings with executive summary and detailed analysis
- **`experiment_runner.py`** - Python script to execute the experiment
- **`experiment_results.json`** - Raw experimental data (JSON format)

## Quick Start

To run the experiment:

```bash
python experiments/bit_ratio_falsification/experiment_runner.py
```

## Summary

**Hypothesis:** Larger bit ratios create narrower search corridors by making p smaller.

**Result:** **HYPOTHESIS FALSIFIED** - Larger ratios make p smaller in absolute terms but do NOT create narrower corridors in relative terms. The relative position of p within the search space [2, √N] remains essentially constant (~4.7%) across all tested ratios.

## Key Findings

| Metric | 1:3 | 1:4 | 1:5 |
|--------|-----|-----|-----|
| Avg p/√N | 5.07% | 4.91% | 4.90% |
| Avg relative position | 4.74% | 4.58% | 4.57% |
| G130 p value | 3.66B (32 bits) | 57M (26 bits) | 1.79M (21 bits) |
| Trial division burden (G130) | 3.66B | 57M | 1.79M |

While p becomes exponentially smaller (2048x from 1:3 to 1:5), the relative search corridor width remains constant. This makes the problem easier via brute force, not more challenging.

**Conclusion:** The current 1:3 ratio is appropriate. Larger ratios do not provide the hypothesized benefits.

## Reproducibility

All code changes are minimal and backward-compatible. The experiment can be re-run at any time with:

```bash
python experiments/bit_ratio_falsification/experiment_runner.py
```

Results are deterministic (same seed = same results).

## Testing

New tests added in `tests/test_bit_ratio.py` validate:
- Bit ratio parameter functionality
- Backward compatibility
- Deterministic generation
- Correct bit allocation per ratio

All tests pass:
```bash
pytest tests/test_bit_ratio.py -v
# 14 passed
```
