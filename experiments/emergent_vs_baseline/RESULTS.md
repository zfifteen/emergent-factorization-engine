# Emergent vs Baseline Ablation Results

## Validation Criterion

### Primary Criterion: Δ > 0
- **Pass condition**: Emergent rank < Baseline rank (Δ > 0) on all tested gates
- **Δ definition**: Baseline_rank - Emergent_rank (positive = emergent improvement)

### Rationale
This experiment validates a novel emergent ranking method. The success criterion is:

> **Δ > 0**: Emergent ranking must consistently outperform geometric baseline.

No minimum percentage threshold is applied because:
1. No prior literature establishes expected improvement magnitudes for emergent cell-view dynamics on factorization problems
2. Arbitrary percentage thresholds conflate statistical significance with practical utility
3. For novel methods, *consistent* improvement is the appropriate scientific validation criterion

**Percentage improvements and effect sizes are computed for analysis but are not pass/fail criteria.**

## Status
- Results pending. Run `run_ablation.py` to populate this report.

## Summary (Planned)
- Gate(s): TBD
- Dense band widths: TBD
- Emergent metrics: corridor width (rank), entropy, viable region size
- Baseline metrics: corridor width (rank), entropy, viable region size
- **Success metric**: Δ > 0 for each gate

## Expected Results Format

| Gate | Baseline Rank | Emergent Rank | Δ (improvement) | Status |
|------|--------------|---------------|-----------------|--------|
| G100 | TBD | TBD | TBD | ✅/❌ Δ > 0 |
| G110 | TBD | TBD | TBD | ✅/❌ Δ > 0 |
| G120 | TBD | TBD | TBD | ✅/❌ Δ > 0 |

**Hypothesis validated if all gates satisfy Δ > 0.**

## Findings (Planned)
- TBD

## Artifacts (Planned)
- results.json
- summary.json
- results.csv
- figures/
