# Emergent vs Baseline Ablation Results

## Objective
Quantify whether emergent signals reduce search space compared to baseline geometric ranking on scale-representative balanced semiprimes (N ≈ 10¹²).

## Method
- **Baseline**: Rank by |candidate - √N|
- **Emergent**: Cell-view dynamics with Dirichlet algotype only, 500 swap steps
- **Candidates**: Dense band ±5000 around √N (10,000 candidates total), ensuring true factor p is included
- **Gates**: G020_BAL, G025_BAL, G030_BAL (balanced semiprimes with N ≥ 10⁶)
- **Metrics**: Rank of true factor p, corridor entropy, viable region size

## Results Summary

| Gate     | Baseline Rank | Emergent Rank | Delta Rank | Baseline Entropy | Emergent Entropy |
|----------|---------------|---------------|------------|------------------|------------------|
| G020_BAL | 8             | 1             | 7          | 0.979            | 0.990            |
| G025_BAL | 72            | 1             | 71         | 0.979            | 0.976            |
| G030_BAL | 4             | 1             | 3          | 0.979            | 0.913            |

**Average Delta Rank**: 27 (71+7+3)/3  
**Success Rate (>20% improvement)**: 3/3 gates

*Results from actual experiment runs with 500 swap steps per gate (Dirichlet-only).*

## Statistical Analysis
- **Mean Rank Improvement**: 27 positions
- **Median Delta Rank**: 7
- **Best Case**: G025_BAL with 98.6% rank reduction (72 → 1)
- **Success Criterion (>20% rank reduction)**: 3 / 3 gates

## Key Findings

### Emergent Ranking Consistently Improves Balanced Gates

All three balanced gates see emergent ranking place the true factor at **rank #1**, while baseline geometric ranking ranges from **#4 to #72**. This shows the Dirichlet energy surrogate provides a consistent ranking advantage even when the factor remains inside a tight ±5000 corridor.

### Entropy Analysis

Entropy behavior is mixed: G030_BAL shows a sharp **entropy drop** (0.979 → 0.913), while G020_BAL rises slightly and G025_BAL stays near baseline. This indicates the Dirichlet kernel sometimes concentrates energy around the factor but is not uniformly discriminative across all balanced gates.

## Interpretation
With single Dirichlet algotype, results show **strong success on balanced scale-representative gates**:
- Emergent method **outperforms baseline** in every gate (never worse)
- Improvements range from modest (rank 4 → 1) to dramatic (72 → 1)

These results validate that the emergent ranking infrastructure scales to N ≈ 10¹² and can yield meaningful ranking improvements even within a narrow corridor.

## Limitations
- Only balanced gates tested; unbalanced cases (p far below √N) remain unvalidated
- 500 swap steps may be insufficient for full convergence on larger candidate sets
- Single algotype reduces diversity but improves consistency

## Decision
**Validated for balanced gates at N ≈ 10¹²**: emergent ranking consistently improves over geometric baseline in scale-representative, tight-corridor settings.

**Open question**: unbalanced gates (where p is far below √N) have not been tested yet. Results there will determine whether emergent ranking provides advantage beyond geometric proximity.

## Files
- `run_ablation.py`: Experiment script
- `visualize_ablation.ipynb`: Analysis notebook
- `tests/logs/ablation_*.json`: Detailed logs with full results
- `tests/summary.csv`: Parsed results
- `figures/`: Plots (generated from notebook)
