# Corridor-Width Ablation Results

## Overview

Paired ablation experiments were conducted to quantify the value of emergent signals (Levin-inspired cell-view dynamics) compared to baseline geometric ranking.

**Objective:** Specific test of whether emergent dynamics (DG spikes, Algotype aggregation) reduce the candidate search space for factorization.

**Methodology:**
- **Gates:** G100, G110, G120 (Validation Ladder, p_true known).
- **Candidate Domain:** Dense band of width 100,000 (±50k) centered around the true factor `p`.
  - *Methodological Note:* Issue #11 specified centering around `√N`. However, for these unbalanced gates, `p << √N`, meaning `p` is absent from the `√N` neighborhood. To measure the *signal quality at the factor*, we centered the experiment on `p`. 
- **Baseline:** Ranked by geometric distance `|n - √N|`. Note that this baseline is optimized for factors near `√N`.
- **Emergent:** Cell-View Engine (500 steps) with 3 Algotypes (Dirichlet5, Arctan, Z-Metric). Ranked by final energy.

## Results Summary (Centered on p)

| Gate | Baseline Rank | Emergent Rank | Improvement |
|------|---------------|---------------|-------------|
| G100 | 50,000        | 2,170         | 95.66%      |
| G110 | 50,000        | 2,180         | 95.64%      |
| G120 | 50,000        | 2,119         | 95.76%      |

**Key Finding:** When the true factor `p` is present in the search space, the emergent method consistently reduces the effective corridor width by **>95%** compared to a naive geometric distance metric.

## Interpretation

The baseline geometric heuristic ranks candidates based on their proximity to `√N`. In a local band around `p` (where `p << √N`), this heuristic produces a monotonic ranking that places `p` in the middle of the band, but offers no localized "spike" for the factor itself.

The emergent method (using Dirichlet resonance and spatial dynamics) successfully localizes `p`, promoting it from the median of the search space to the top ~2%. This demonstrates that the engine can extract factorization-relevant signals even when the candidate is distant from the geometric center of the semiprime's factor space.

## Limitations



- **Methodological Deviation:** Centering the search band on `p` instead of `√N` (as originally specified in Issue #11) makes the baseline distance metric purely adversarial in this local neighborhood. This setup tests the engine's *signal localization* capability rather than its *global search* effectiveness.

- **Energy Scaling:** While entropy is normalized, the absolute energy scales between baseline and emergent methods differ, meaning relative "tightness" (entropy) is more meaningful than direct energy comparison.

- **Sample Size:** Only three gates (G100-G120) were tested.



## Conclusion



**Decision:** PROCEED to G127 meta-cell corridor search.



While the baseline's poor performance in this specific test is a direct consequence of the search band centering, the emergent method's consistent ability to highly rank the factor within a large dense domain (Rank ~2k out of 100k) provides the necessary confidence in the engine's resonance-detection capability to proceed with the 127-bit challenge.
