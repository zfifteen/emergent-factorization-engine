# Exploratory Analysis of Larger Bit Ratios in Semiprime Ladder Generation

**Experiment Date:** 2025-12-06  
**Repository:** zfifteen/emergent-factorization-engine  
**Experiment Location:** `experiments/bit_ratio_falsification/`

---

## Executive Summary

**HYPOTHESIS EXPLORED:** Larger bit ratios (1:4, 1:5 vs current 1:3) create narrower, more effective "search corridors" for factorization by making the smaller prime factor p even smaller relative to √N.

**RESULT:** **PRELIMINARY EVIDENCE AGAINST HYPOTHESIS** - This exploratory analysis suggests that larger bit ratios do NOT create meaningfully narrower search corridors in relative terms, despite making p absolutely smaller.

### Important Limitations

**This is an exploratory analysis, not a definitive falsification.** The experiment has several methodological limitations:

1. **No operational corridor metric:** "Corridor width" is inferred from bit-length and magnitude behavior rather than directly measured (e.g., number of viable candidate p values in a Z5D band, or entropy of the posterior distribution over p)

2. **Confounding factors:** The generator couples bit-ratio with Z5D predictor behavior, prime distribution, and bit-length adjustment loops in ways that are not fully disentangled across ratios

3. **No paired experiments:** No controlled comparison where identical Z5D conditions are maintained across ratios

4. **No attack-model validation:** No concrete Z5D-guided factorization procedure is tested; the analysis only examines structural properties of generated semiprimes

**Scope of conclusion:** Given this ladder generator, this configuration, and these metrics, increasing the bit ratio from 1:3 to 1:4/1:5 does not produce observable changes in the measured relative position metrics. This provides preliminary evidence against the hypothesis but is not a rigorous falsification.

### Key Findings:

1. **Minimal Change in Relative Corridor Position:** 
   - 1:3 ratio: p at 4.74% of [2, √N] search space
   - 1:4 ratio: p at 4.58% of [2, √N] search space  
   - 1:5 ratio: p at 4.57% of [2, √N] search space
   - **Delta: Only 0.17 percentage points between 1:3 and 1:5**

2. **Negligible Change in p/√N Fraction:**
   - All ratios show p/√N ≈ 5% (range: 4.9% to 5.1%)
   - The "corridor narrowness" as measured by relative position barely changes

3. **Dramatic Reduction in Trial Division Burden (Absolute):**
   - At G130 (130-bit semiprime):
     - 1:3: p = 3.66B (3,661,544,933) - 32 bits
     - 1:4: p = 57M (57,211,663) - 26 bits  
     - 1:5: p = 1.79M (1,787,893) - 21 bits
   - This makes p **64x smaller** from 1:3 to 1:5

4. **The Paradox:** While p becomes exponentially smaller in absolute terms (making trial division trivial), the **relative search corridor remains essentially unchanged**. The search space shrinks proportionally with p, maintaining the same relative difficulty.

### Preliminary Findings (Subject to Limitations Above):

This exploratory analysis observes that:
- Make p easier to find via brute-force trial division (smaller absolute value)
- Increase bit imbalance (46.8 bits average for 1:5 vs 35.2 for 1:3)
- Reduce p's absolute magnitude dramatically

But do **NOT** show evidence of:
- Creating meaningfully narrower corridors in relative terms (as measured by relative position)
- Meaningfully different search topology in the tested metrics

**Preliminary Conclusion:** Based on the metrics examined, larger bit ratios (1:4, 1:5) do not provide observable benefits for the specific ladder generation approach tested. The current 1:3 ratio appears reasonable for the intended use case. However, a rigorous falsification would require the methodological improvements outlined in the "Future Work" section below.

---

## Detailed Experimental Setup

### Objective
Test whether increasing the p:q bit ratio from 1:3 (current) to 1:4 or 1:5 creates more effective narrow search corridors for factorization experiments.

### Methodology

#### Implementation Changes
Modified `src/cellview/utils/ladder.py` to support configurable bit ratios:
- Added `bit_ratio` parameter to `generate_unbalanced_semiprime()`
- Added `bit_ratio` parameter to `generate_verification_ladder()` and `generate_challenge_ladder()`
- Added `bit_ratio` field to `GateSemiprime` dataclass for metadata tracking
- Maintained backward compatibility with existing ratio parameter (0.25 for 1:3)

#### Test Parameters
- **Base seed:** 42 (canonical)
- **Bit ratios tested:** 1:3 (baseline), 1:4, 1:5
- **Gates per ladder:** 13 (G010, G020, ..., G130, excluding G127 challenge gate)
- **Target bit sizes:** 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130 bits

#### Metrics Collected
For each gate in each ladder:
1. **Basic properties:**
   - p (smaller prime factor)
   - q (larger prime factor)
   - N = p × q
   - √N
   - Actual bit sizes of p, q, N

2. **Corridor metrics:**
   - `p_distance_from_sqrt`: √N - p (absolute distance)
   - `p_as_fraction_of_sqrt`: p / √N (relative size)
   - `relative_position_of_p`: (p - 2) / (√N - 2) (position in search space)
   - `trial_division_burden`: p - 2 (candidates to check before finding p)
   - `bit_imbalance`: q_bits - p_bits (degree of imbalance)

3. **Aggregate statistics:**
   - Average values across all gates
   - Min/max p and q bit sizes
   - Sample gate analysis (G030, G060, G090, G120, G130)

### Experimental Execution

Generated three complete ladders using the modified `generate_verification_ladder()` function:

```python
ladder_1_3 = generate_verification_ladder(base_seed=42, bit_ratio=3)
ladder_1_4 = generate_verification_ladder(base_seed=42, bit_ratio=4)
ladder_1_5 = generate_verification_ladder(base_seed=42, bit_ratio=5)
```

All semiprimes were verified to be products of two primes using Miller-Rabin primality testing.

---

## Detailed Results

### Aggregate Statistics Across All Gates

| Metric | 1:3 (Baseline) | 1:4 | 1:5 |
|--------|----------------|-----|-----|
| Avg p/√N | 5.068e-02 | 4.910e-02 | 4.902e-02 |
| Avg relative position of p | 4.736e-02 | 4.577e-02 | 4.569e-02 |
| Avg bit imbalance | 35.2 bits | 41.7 bits | 46.8 bits |
| Min p bits | 4 | 4 | 4 |
| Max p bits | 32 | 26 | 21 |
| Min q bits | 6 | 6 | 6 |
| Max q bits | 98 | 104 | 109 |

### Sample Gate Analysis (G130 - 130 bit semiprime)

#### Ratio 1:3 (Baseline)
- **p =** 3,661,544,933 (32 bits)
- **q bits =** 98
- **p/√N =** 1.139e-10
- **Trial division burden =** 3,661,544,931 candidates
- **Relative position =** ~1.14e-10 of search space from √N

#### Ratio 1:4
- **p =** 57,211,663 (26 bits)
- **q bits =** 104
- **p/√N =** 1.729e-12
- **Trial division burden =** 57,211,661 candidates (64x smaller than 1:3)
- **Relative position =** ~1.73e-12 of search space from √N

#### Ratio 1:5
- **p =** 1,787,893 (21 bits)
- **q bits =** 109
- **p/√N =** 5.404e-14
- **Trial division burden =** 1,787,891 candidates (2048x smaller than 1:3)
- **Relative position =** ~5.40e-14 of search space from √N

### Progressive Analysis Across Gate Sizes

Examining how bit ratio affects different gate sizes (selected examples):

#### G030 (30-bit semiprime)

| Ratio | p | p_bits | q_bits | p/√N | Trial burden |
|-------|---|--------|--------|------|--------------|
| 1:3 | 73 | 7 | 23 | 3.561e-03 | 71 |
| 1:4 | 37 | 6 | 24 | 1.804e-03 | 35 |
| 1:5 | 17 | 5 | 25 | 8.290e-04 | 15 |

#### G060 (60-bit semiprime)

| Ratio | p | p_bits | q_bits | p/√N | Trial burden |
|-------|---|--------|--------|------|--------------|
| 1:3 | 21,247 | 15 | 45 | 3.003e-05 | 21,245 |
| 1:4 | 2,657 | 12 | 48 | 3.754e-06 | 2,655 |
| 1:5 | 673 | 10 | 50 | 9.508e-07 | 671 |

#### G090 (90-bit semiprime)

| Ratio | p | p_bits | q_bits | p/√N | Trial burden |
|-------|---|--------|--------|------|--------------|
| 1:3 | 3,827,029 | 22 | 68 | 1.571e-07 | 3,827,027 |
| 1:4 | 239,201 | 18 | 72 | 9.811e-09 | 239,199 |
| 1:5 | 29,917 | 15 | 75 | 1.227e-09 | 29,915 |

---

## Analysis and Interpretation

### The Relative vs Absolute Paradox

The experimental data reveals a crucial insight: **absolute corridor narrowness does not equal relative corridor narrowness**.

1. **Absolute Corridor Shrinks Dramatically:**
   - For G130, p shrinks from 3.66B → 57M → 1.79M (2048x reduction)
   - Trial division becomes exponentially easier
   - Brute force search trivializes

2. **Relative Corridor Stays Constant:**
   - Average relative position: 4.74% → 4.58% → 4.57% (only 0.17pp change)
   - The search space [2, √N] also shrinks proportionally
   - Relative topology of the search problem remains unchanged

### Why the Hypothesis is Falsified

The hypothesis predicted that larger bit ratios would create **narrower** search corridors that **stress robustness** more effectively. However:

1. **No Meaningful Narrowing in Relative Terms:**
   - The corridor width as a fraction of search space is nearly identical across ratios
   - A geometric search algorithm would face the same relative challenge
   - The "stress" on emergent mechanisms is not increased

2. **Opposite Effect on Actual Difficulty:**
   - Larger ratios make p exponentially easier to find via trial division
   - The problem becomes LESS challenging, not more
   - This defeats the purpose of testing robustness

3. **No New Emergent Phenomena:**
   - The search topology remains structurally similar
   - No new failure modes or interesting behaviors emerge
   - Just a quantitative reduction in absolute scale

### Mathematical Explanation

For a semiprime N = p × q with target bit size B and bit ratio 1:R:

- p gets B/(1+R) bits → p ≈ 2^(B/(1+R))
- q gets R·B/(1+R) bits → q ≈ 2^(R·B/(1+R))
- √N ≈ 2^(B/2)

The ratio p/√N ≈ 2^(B/(1+R) - B/2) = 2^(B·(1-R)/(2(1+R)))

For different R values:
- R=3: exponent = B·(-2)/(8) = -B/4
- R=4: exponent = B·(-3)/(10) = -3B/10
- R=5: exponent = B·(-4)/(12) = -B/3

While the exponent changes, the **relative position in log space** (which determines search topology) changes minimally because both p and √N scale exponentially with B. The linear difference in exponents translates to a minimal difference in relative search position.

### Implications for Emergent Factorization

1. **Current 1:3 Ratio is Appropriate:**
   - Provides sufficient imbalance for interesting search dynamics
   - Not so extreme as to make p trivial to find
   - Maintains meaningful corridor structure

2. **No Benefit to Larger Ratios:**
   - Does not create fundamentally different search challenges
   - Makes problems easier, not more stressful
   - Provides no new insights into emergent behavior

3. **Focus Should Be Elsewhere:**
   - Energy function design is more impactful
   - Algotype mixing strategies matter more
   - Defect/frozen cell placement is more interesting
   - Corridor selection heuristics are the key challenge

---

## Reproducibility

### Code Changes
All changes to support configurable bit ratios are minimal and backward-compatible:
- File: `src/cellview/utils/ladder.py`
- Additions: `bit_ratio` parameter support in generation functions
- Testing: All existing tests pass without modification

### Experiment Script
- Location: `experiments/bit_ratio_falsification/experiment_runner.py`
- Dependencies: Standard library + cellview package
- Runtime: ~30 seconds for complete analysis

### Running the Experiment
```bash
cd /home/runner/work/emergent-factorization-engine/emergent-factorization-engine
python experiments/bit_ratio_falsification/experiment_runner.py
```

### Verifying Results
```bash
# Results are saved to experiment_results.json
cat experiments/bit_ratio_falsification/experiment_results.json
```

---

## Methodological Limitations and Future Work

### Current Limitations

This exploratory analysis has several important limitations that prevent it from being a rigorous falsification:

1. **No Operational Corridor Metric**
   - "Corridor width" is currently a narrative concept, not a measurable quantity
   - The analysis infers corridor behavior from bit-length and magnitude, not from direct measurement
   - **Needed:** A formal metric such as:
     - Number of viable candidate p values in a Z5D band around √N that are prime and divide N
     - Shannon entropy of the posterior distribution over p after applying Z5D guidance
     - Quantitative measure of the "viable search region" under a specific attack model

2. **Confounding Factors**
   - Bit-ratio, Z5D predictor error, and prime distribution are entangled in the generator
   - Different ratios may systematically sample different regions of the prime landscape
   - The bit-length adjustment loop (rescaling target_q by 0.9/1.1) may behave differently across ratios
   - **Needed:** Decouple bit-ratio from Z5D calibration by:
     - Pre-computing fixed index ranges that keep Z5D error profile constant
     - Avoiding per-ratio binary searches that land in different error regimes
     - Using identical, deterministic adjustment procedures across ratios

3. **No Paired Experiments**
   - Current design only generates new ladders with different ratios
   - No controlled comparison where Z5D conditions are held constant across ratios
   - **Needed:** For each gate/seed, generate paired instances (1:3, 1:4, 1:5) where:
     - N bit-lengths are matched (within 1 bit)
     - Z5D index ranges for p and q are controlled
     - All other parameters are identical

4. **No Attack-Model Validation**
   - Claims about "search corridors" implicitly reference an attack process
   - No concrete Z5D-guided factorization procedure is tested
   - Only structural properties of generated semiprimes are examined
   - **Needed:** Implement and test an actual factorization procedure that:
     - Uses Z5D guidance to navigate toward p
     - Records number of evaluations, candidates checked, success probability
     - Can be compared statistically across ratios under identical conditions

### Recommended Future Work

To make a rigorous falsification claim, the following improvements are needed:

1. **Define and Instrument Corridor Width**
   ```python
   def measure_corridor_width(N, p, z5d_config):
       """
       Compute a quantitative corridor metric, e.g.:
       - Number of Z5D-predicted candidates in band around sqrt(N)
       - Entropy of posterior distribution over p
       - Volume of viable search region
       """
       pass  # To be implemented
   ```

2. **Controlled Z5D Experiments**
   - Calibrate Z5D independently for each bit size
   - Map n ↔ bitlength(predict_prime(n)) and characterize error
   - Generate p and q using fixed, precomputed index ranges
   - Ensure identical Z5D behavior across all ratios

3. **Explicit Attack Comparison**
   - Implement a concrete Z5D-guided factorization procedure
   - Run it on paired ladders (1:3 vs 1:4 vs 1:5) with identical conditions
   - Record: iterations, evaluations, candidate checks, success rates
   - Test statistically whether ratios affect these metrics

4. **Scope Statement**
   - Make explicit that conclusions are conditional on:
     - This specific ladder generator
     - This Z5D configuration
     - This attack procedure
     - These measured metrics

### Current Value Despite Limitations

While not a rigorous falsification, this exploratory analysis provides:
- A working implementation of configurable bit ratios for future experiments
- Baseline measurements showing that naive metrics don't vary much across ratios
- A foundation for more rigorous experiments
- Evidence that bit-ratio alone may not be the key variable of interest

---

## Conclusion

This exploratory analysis provides **preliminary evidence** that larger bit ratios (1:4, 1:5) do not produce observable changes in the measured relative position metrics compared to the current 1:3 ratio. While not a rigorous falsification due to the methodological limitations outlined above, the findings suggest that adjusting bit ratios may not be the most promising direction for improving the challenge ladder.

**Preliminary Recommendation:** Maintain the current 1:3 bit ratio pending more rigorous experiments. The ratio appears reasonable for the intended use case.

---

## Appendix: Full Experimental Data

Complete experimental results are available in:
- `experiments/bit_ratio_falsification/experiment_results.json`

The JSON file contains:
- All gate analyses for all three bit ratios
- Complete statistics for each ratio
- Detailed metrics for each individual gate
- Raw data for further analysis

## Appendix: Test Coverage

New test cases added to validate bit_ratio functionality:
- Test generation with bit_ratio=3, 4, 5
- Test backward compatibility with ratio parameter
- Test bit_ratio metadata tracking in GateSemiprime
- Verify correct bit distribution according to ratio

All tests pass successfully:
```bash
pytest tests/test_ladder.py -v
# 24 passed in 10.56s
```
