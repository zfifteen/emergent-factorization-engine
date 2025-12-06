# Bit Ratio Exploratory Analysis

This exploratory analysis examines whether larger bit ratios (1:4, 1:5 vs current 1:3) create more effective "narrow search corridors" for factorization.

## Files

- **`FINDINGS.md`** - Complete analysis with executive summary, limitations, and detailed results
- **`experiment_runner.py`** - Python script to execute the experiment
- **`experiment_results.json`** - Raw experimental data (JSON format)
- **`visual_comparison.py`** - Visual demonstration tool

## Quick Start

To run the experiment:

```bash
python experiments/bit_ratio_falsification/experiment_runner.py
```

## Summary

**Hypothesis:** Larger bit ratios create narrower search corridors by making p smaller.

**Result:** **PRELIMINARY EVIDENCE AGAINST HYPOTHESIS** - This exploratory analysis suggests that larger ratios make p smaller in absolute terms but do NOT create observably narrower corridors in the tested relative position metrics. 

**Important:** This is not a rigorous falsification. See FINDINGS.md for methodological limitations.

## Key Findings

| Metric | 1:3 | 1:4 | 1:5 |
|--------|-----|-----|-----|
| Avg p/√N | 5.07% | 4.91% | 4.90% |
| Avg relative position | 4.74% | 4.58% | 4.57% |
| G130 p value | 3.66B (32 bits) | 57M (26 bits) | 1.79M (21 bits) |
| Trial division burden (G130) | 3.66B | 57M | 1.79M |

While p becomes exponentially smaller (2048x from 1:3 to 1:5), the measured relative position changes minimally.

## Limitations

This analysis has important methodological limitations:
- No operational corridor metric (corridor width is inferred, not directly measured)
- Confounding factors (bit-ratio entangled with Z5D predictor behavior)
- No paired experiments with controlled Z5D conditions
- No attack-model validation with concrete factorization procedure

See FINDINGS.md "Methodological Limitations and Future Work" section for details.

**Preliminary Conclusion:** Based on examined metrics, the current 1:3 ratio appears reasonable. A rigorous falsification would require the improvements outlined in FINDINGS.md.

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
