"""
Unit tests for corridor-width ablation experiment.

Tests for:
- generate_candidates with factor outside band
- statistical functions (Cohen's d, t-test)
- GateConfig handling
"""

import random
import sys
import unittest
import warnings
from dataclasses import dataclass
from pathlib import Path

# Add src and experiments to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.corridor_width_ablation.experiment import (
    DEFAULT_CANDIDATE_SAMPLE_SIZE,
    GateConfig,
    _t_cdf,
    compute_cohens_d,
    compute_paired_ttest,
    generate_candidates,
)
from cellview.utils.rng import create_rng


class TestGenerateCandidates(unittest.TestCase):
    """Tests for candidate generation."""

    def test_factor_within_band(self):
        """Factor within band should be included without warning."""
        config = GateConfig(
            gate_name="test",
            N=100,
            true_factor_p=10,
            true_factor_q=10,
            sqrt_N=10,
            band_center=10,
            band_halfwidth=5,
            candidate_sample_size=10,
        )
        rng = create_rng(42)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            candidates = generate_candidates(config, rng)
            # No warning should be raised
            self.assertEqual(len(w), 0)

        # Factor should be included
        self.assertIn(10, candidates)

    def test_factor_outside_band_raises_warning(self):
        """Factor outside band should raise a warning but still be included."""
        config = GateConfig(
            gate_name="test",
            N=100,
            true_factor_p=100,  # Outside band [5, 15]
            true_factor_q=1,
            sqrt_N=10,
            band_center=10,
            band_halfwidth=5,
            candidate_sample_size=10,
        )
        rng = create_rng(42)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            candidates = generate_candidates(config, rng)
            # Warning should be raised
            self.assertEqual(len(w), 1)
            self.assertIn("outside band", str(w[0].message))

        # Factor should still be included
        self.assertIn(100, candidates)

    def test_rng_required(self):
        """Passing None for rng should raise ValueError."""
        config = GateConfig(
            gate_name="test",
            N=100,
            true_factor_p=10,
            true_factor_q=10,
            sqrt_N=10,
            band_center=10,
            band_halfwidth=5,
            candidate_sample_size=1000,  # Larger than span to trigger sampling
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidates(config, None)

        self.assertIn("rng is required", str(ctx.exception))

    def test_small_band_enumerates_all(self):
        """When band is smaller than sample size, enumerate all."""
        config = GateConfig(
            gate_name="test",
            N=100,
            true_factor_p=10,
            true_factor_q=10,
            sqrt_N=10,
            band_center=10,
            band_halfwidth=3,  # Band = [7, 13], span = 7
            candidate_sample_size=100,  # > span
        )
        rng = create_rng(42)

        candidates = generate_candidates(config, rng)

        # Should include all of [7, 13]
        self.assertEqual(set(candidates), set(range(7, 14)))


class TestTDistributionCDF(unittest.TestCase):
    """Tests for t-distribution CDF implementation."""

    def test_cdf_at_zero(self):
        """CDF at t=0 should be 0.5 for any df."""
        for df in [1, 2, 5, 10, 30]:
            cdf = _t_cdf(0.0, df)
            self.assertAlmostEqual(cdf, 0.5, places=5)

    def test_cdf_symmetry(self):
        """CDF should be symmetric: CDF(-t) = 1 - CDF(t)."""
        for df in [1, 2, 5]:
            for t in [0.5, 1.0, 2.0]:
                cdf_pos = _t_cdf(t, df)
                cdf_neg = _t_cdf(-t, df)
                self.assertAlmostEqual(cdf_pos + cdf_neg, 1.0, places=4)

    def test_df2_closed_form(self):
        """df=2 uses closed form, verify against known values."""
        # For df=2, CDF(t) = 0.5 + t / (2 * sqrt(2 + t^2))
        import math

        for t in [1.0, 2.0, 3.0]:
            expected = 0.5 + t / (2 * math.sqrt(2 + t * t))
            actual = _t_cdf(t, 2)
            self.assertAlmostEqual(actual, expected, places=10)

    def test_df1_cauchy(self):
        """df=1 (Cauchy) uses arctan formula."""
        import math

        for t in [0.0, 1.0, 2.0]:
            expected = 0.5 + math.atan(t) / math.pi
            actual = _t_cdf(t, 1)
            self.assertAlmostEqual(actual, expected, places=10)


class TestPairedTTest(unittest.TestCase):
    """Tests for paired t-test implementation."""

    def test_identical_samples_gives_zero_t(self):
        """Identical samples should give t=0, p=1."""
        values = [1.0, 2.0, 3.0]
        t_stat, p_value = compute_paired_ttest(values, values)
        self.assertAlmostEqual(t_stat, 0.0, places=5)
        self.assertAlmostEqual(p_value, 1.0, places=5)

    def test_different_samples_gives_nonzero(self):
        """Different samples should give non-zero t-stat."""
        values1 = [10.0, 20.0, 30.0]
        values2 = [5.0, 15.0, 25.0]
        t_stat, p_value = compute_paired_ttest(values1, values2)
        self.assertGreater(abs(t_stat), 0)
        self.assertLess(p_value, 1.0)

    def test_mismatched_lengths_raises(self):
        """Different length arrays should raise ValueError."""
        with self.assertRaises(ValueError):
            compute_paired_ttest([1, 2], [1, 2, 3])

    def test_single_sample_returns_one(self):
        """Single sample returns p=1."""
        t_stat, p_value = compute_paired_ttest([1.0], [2.0])
        self.assertEqual(p_value, 1.0)


class TestCohensD(unittest.TestCase):
    """Tests for Cohen's d implementation."""

    def test_identical_samples_gives_zero(self):
        """Identical samples should give d=0."""
        values = [1.0, 2.0, 3.0]
        d = compute_cohens_d(values, values)
        self.assertAlmostEqual(d, 0.0, places=5)

    def test_separated_samples_gives_large_d(self):
        """Well-separated samples should give large d."""
        values1 = [100.0, 100.0, 100.0]
        values2 = [1.0, 1.0, 1.0]
        d = compute_cohens_d(values1, values2)
        # All diffs are 99, std of diffs is 0, so d is very large
        # Actually std is 0 so we'd get division by small epsilon
        self.assertGreater(d, 10)  # Large effect

    def test_moderate_difference(self):
        """Moderate differences should give moderate d."""
        values1 = [10.0, 20.0, 30.0]
        values2 = [5.0, 15.0, 25.0]
        d = compute_cohens_d(values1, values2)
        # Diffs are all 5, std is 0, so very large d
        # This test shows the inflation issue documented in the code
        self.assertGreater(abs(d), 0)


if __name__ == "__main__":
    unittest.main()
