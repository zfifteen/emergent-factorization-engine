# Emergent vs Baseline Ablation Results

## Objective
Quantify whether emergent signals reduce search space compared to baseline geometric ranking on gates G100-G110-G120.

## Method
- **Baseline**: Rank by |candidate - √N|
- **Emergent**: Cell-view dynamics with Dirichlet algotype only, 500 swap steps
- **Candidates**: Dense band ±5M around √N, ensuring true factor p is included
- **Metrics**: Rank of true factor p, corridor entropy, viable region size

## Results Summary

| Gate | Baseline Rank | Emergent Rank | Delta Rank | Entropy Reduction | Viable Candidates Reduction |
|------|---------------|---------------|------------|-------------------|-----------------------------|
| G100 | TBD          | TBD          | TBD       | TBD              | TBD                        |
| G110 | TBD          | TBD          | TBD       | TBD              | TBD                        |
| G120 | TBD          | TBD          | TBD       | TBD              | TBD                        |

*Note: Results updated with single algotype for better divisor detection.*

## Statistical Analysis
- **Mean Rank Improvement**: TBD
- **Cohen's d Effect Size**: TBD
- **Paired t-test**: p = TBD
- **Success Criterion (>20% rank reduction)**: TBD / 3 gates

## Interpretation
With single Dirichlet algotype, emergent method should rank true factor p higher due to low energy for divisors.

## Limitations
- Band width may still be insufficient for hypothesis testing
- Single algotype reduces variety but improves consistency

## Decision
Run updated experiment to assess if emergent dynamics narrow corridors.

## Files
- `run_ablation.py`: Updated experiment script
- `visualize_ablation.ipynb`: Analysis notebook
- `logs/ablation_*.json`: Detailed logs
- `figures/`: Plots</content>
<parameter name="filePath">/Users/velocityworks/tmp/grok/emergent-factorization-engine/experiments/emergent_vs_baseline/RESULTS.md