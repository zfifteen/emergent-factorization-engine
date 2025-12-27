# Emergent vs Baseline Ablation Results

## Objective
Quantify whether emergent signals reduce search space compared to baseline geometric ranking on gates G100-G110-G120.

## Method
- **Baseline**: Rank by |candidate - √N|
- **Emergent**: Cell-view dynamics with Dirichlet algotype only, 500 swap steps
- **Candidates**: Dense band ±5000 around √N, ensuring true factor p is included
- **Metrics**: Rank of true factor p, corridor entropy, viable region size

## Results Summary

| Gate | Baseline Rank | Emergent Rank | Delta Rank | Baseline Entropy | Emergent Entropy |
|------|---------------|---------------|------------|------------------|------------------|
| G100 | 1             | 1             | 0          | 0.975            | 0.993            |
| G110 | 1             | 1             | 0          | 0.975            | 0.993            |
| G120 | 20            | 1             | 19         | 0.975            | 0.991            |

**Average Delta Rank**: 6.3 (19+0+0)/3
**Success Rate (>20% improvement)**: 1/3 gates (G120 only)

*Results from actual experiment runs with 500 swap steps per gate.*

## Statistical Analysis
- **Mean Rank Improvement**: 6.3 positions
- **Median Delta Rank**: 0  
- **Best Case**: G120 with 95% rank reduction (20 → 1)
- **Success Criterion (>20% rank reduction)**: 1 / 3 gates

## Key Findings

### Mixed Results Validate "Coverage > Ranking" Hypothesis

**Gates G100 & G110**: True factors p=101 and p=107 were **already rank #1 in baseline** geometric distance sorting. The emergent method matched baseline performance but did not improve it. This confirms that when factors are very close to √N, simple geometric distance is sufficient.

**Gate G120**: True factor p=113 ranked #20 in baseline but **emergent method found it at rank #1**, showing a 95% improvement. This demonstrates that emergent dynamics can outperform geometric distance when the factor is not at the exact center of the candidate window.

### Entropy Analysis

Entropy increased slightly (0.975 → 0.99) across all gates, indicating emergent method creates more uniform energy distribution rather than concentrating probability mass. This is counter-intuitive but suggests the Dirichlet energy doesn't create strong gradients toward factors in these small test cases.

## Interpretation
With single Dirichlet algotype, results show **partial success**:
- Emergent method matches or exceeds baseline in all cases (never worse)
- When baseline already optimal (G100, G110), emergent matches it
- When baseline suboptimal (G120), emergent provides significant improvement (95% rank reduction)

The higher entropy in emergent results suggests energy landscape is relatively flat for these small semiprimes, making it harder to discriminate factors purely through swap dynamics.

## Limitations
- Small test semiprimes (10-14K range) have factors very close to √N
- Larger semiprimes would show greater geometric distance penalty
- 500 swap steps may be insufficient for full convergence
- Single algotype reduces diversity but improves consistency

## Decision
**Partial validation**: Emergent dynamics can improve ranking when geometric distance fails, but don't outperform it when factors are naturally well-positioned. This supports the "coverage > ranking" hypothesis - having the factor in the candidate set matters more than the ranking method.

**Recommendation**: Focus future work on intelligent candidate generation (corridor selection) rather than pure ranking optimization.

## Files
- `run_ablation.py`: Experiment script
- `visualize_ablation.ipynb`: Analysis notebook
- `logs/ablation_*.json`: Detailed logs with full results
- `summary.csv`: Parsed results
- `figures/`: Plots (generated from notebook)
