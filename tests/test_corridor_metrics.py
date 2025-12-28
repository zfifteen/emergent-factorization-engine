"""
Unit tests for corridor metrics.

Tests for:
- effective_corridor_width
- corridor_entropy
- viable_region_size
- compute_all_corridor_metrics
"""

import unittest
from decimal import Decimal

from cellview.metrics.corridor_metrics import (
    compute_all_corridor_metrics,
    corridor_entropy,
    effective_corridor_width,
    viable_region_contains_factor,
    viable_region_size,
)


class TestEffectiveCorridorWidth(unittest.TestCase):
    """Tests for effective_corridor_width metric."""

    def test_factor_at_first_position(self):
        """Factor at rank 1 should return 1."""
        ranked = [
            {"n": 17, "energy": "0.01"},
            {"n": 23, "energy": "0.02"},
            {"n": 29, "energy": "0.03"},
        ]
        self.assertEqual(effective_corridor_width(ranked, 17), 1)

    def test_factor_at_middle_position(self):
        """Factor at rank 2 should return 2."""
        ranked = [
            {"n": 17, "energy": "0.01"},
            {"n": 23, "energy": "0.02"},
            {"n": 29, "energy": "0.03"},
        ]
        self.assertEqual(effective_corridor_width(ranked, 23), 2)

    def test_factor_at_last_position(self):
        """Factor at last position should return correct rank."""
        ranked = [
            {"n": 17, "energy": "0.01"},
            {"n": 23, "energy": "0.02"},
            {"n": 29, "energy": "0.03"},
        ]
        self.assertEqual(effective_corridor_width(ranked, 29), 3)

    def test_factor_not_in_candidates(self):
        """Factor not in candidates should return None."""
        ranked = [
            {"n": 17, "energy": "0.01"},
            {"n": 23, "energy": "0.02"},
        ]
        self.assertIsNone(effective_corridor_width(ranked, 99))

    def test_empty_candidates(self):
        """Empty candidate list should return None."""
        self.assertIsNone(effective_corridor_width([], 17))

    def test_tie_handling_returns_average_rank(self):
        """Factor in tie group should return average rank of group."""
        # Candidates at ranks 2, 3, 4 all have same energy
        ranked = [
            {"n": 10, "energy": "0.01"},  # rank 1
            {"n": 20, "energy": "0.05"},  # rank 2 (tie)
            {"n": 30, "energy": "0.05"},  # rank 3 (tie) - factor
            {"n": 40, "energy": "0.05"},  # rank 4 (tie)
            {"n": 50, "energy": "0.09"},  # rank 5
        ]
        # Average of ranks 2, 3, 4 = 3
        result = effective_corridor_width(ranked, 30, handle_ties=True)
        self.assertEqual(result, 3)

    def test_tie_handling_disabled(self):
        """With handle_ties=False, return actual position."""
        ranked = [
            {"n": 10, "energy": "0.05"},
            {"n": 20, "energy": "0.05"},  # factor at position 2
            {"n": 30, "energy": "0.05"},
        ]
        result = effective_corridor_width(ranked, 20, handle_ties=False)
        self.assertEqual(result, 2)

    def test_no_energy_field(self):
        """Candidates without energy field should use position."""
        ranked = [{"n": 10}, {"n": 20}, {"n": 30}]
        result = effective_corridor_width(ranked, 20, handle_ties=True)
        self.assertEqual(result, 2)


class TestCorridorEntropy(unittest.TestCase):
    """Tests for corridor_entropy metric."""

    def test_uniform_energies_high_entropy(self):
        """Uniform energies should produce high normalized entropy."""
        energies = [Decimal("0.5"), Decimal("0.5"), Decimal("0.5"), Decimal("0.5")]
        entropy = corridor_entropy(energies, normalize=True)
        # Uniform distribution = max entropy = 1.0 (normalized)
        self.assertAlmostEqual(entropy, 1.0, places=5)

    def test_concentrated_energies_low_entropy(self):
        """One very low energy vs many high should produce lower entropy."""
        # One candidate has much lower energy (better rank)
        energies = [Decimal("0.01"), Decimal("0.99"), Decimal("0.99"), Decimal("0.99")]
        entropy = corridor_entropy(energies, normalize=True)
        # Should be lower than uniform (less than 1.0)
        self.assertLess(entropy, 1.0)

    def test_single_candidate_zero_entropy(self):
        """Single candidate should return 0 entropy."""
        energies = [Decimal("0.5")]
        entropy = corridor_entropy(energies, normalize=True)
        self.assertEqual(entropy, 0.0)

    def test_empty_list_zero_entropy(self):
        """Empty list should return 0 entropy."""
        entropy = corridor_entropy([], normalize=True)
        self.assertEqual(entropy, 0.0)

    def test_two_different_energies(self):
        """Two different energies should have entropy between 0 and 1."""
        energies = [Decimal("0.1"), Decimal("0.9")]
        entropy = corridor_entropy(energies, normalize=True)
        self.assertGreater(entropy, 0.0)
        self.assertLess(entropy, 1.0)

    def test_near_zero_energy_differences(self):
        """Near-zero energy differences should return max entropy."""
        # All energies differ by less than default threshold (1e-12)
        base = Decimal("0.5")
        energies = [base, base + Decimal("1e-15"), base - Decimal("1e-15")]
        entropy = corridor_entropy(energies, normalize=True)
        # Should be max entropy since differences are negligible
        self.assertAlmostEqual(entropy, 1.0, places=5)

    def test_custom_near_zero_threshold(self):
        """Custom threshold should affect near-zero detection."""
        energies = [Decimal("0.1"), Decimal("0.2"), Decimal("0.3")]
        # With normal threshold, these are different
        entropy_normal = corridor_entropy(energies, normalize=True)
        self.assertLess(entropy_normal, 1.0)

        # With very large threshold, treated as equal
        entropy_high_thresh = corridor_entropy(
            energies, normalize=True, near_zero_threshold=1.0
        )
        self.assertAlmostEqual(entropy_high_thresh, 1.0, places=5)

    def test_zero_energies(self):
        """Zero and near-zero energies should be handled gracefully."""
        energies = [Decimal("0"), Decimal("0.001"), Decimal("0.01")]
        entropy = corridor_entropy(energies, normalize=True)
        # Should not raise, should return valid entropy
        self.assertGreaterEqual(entropy, 0.0)
        self.assertLessEqual(entropy, 1.0)

    def test_negative_energies(self):
        """Negative energies should be handled gracefully."""
        # This shouldn't happen in practice, but test robustness
        energies = [Decimal("-0.1"), Decimal("0.0"), Decimal("0.1")]
        entropy = corridor_entropy(energies, normalize=True)
        self.assertGreaterEqual(entropy, 0.0)
        self.assertLessEqual(entropy, 1.0)


class TestViableRegion(unittest.TestCase):
    """Tests for viable_region_size and viable_region_contains_factor."""

    def test_viable_region_size_10_percent(self):
        """10% of 100 candidates should be 10."""
        ranked = [{"n": i, "energy": str(i)} for i in range(100)]
        self.assertEqual(viable_region_size(ranked, 10.0), 10)

    def test_viable_region_size_minimum_one(self):
        """Should always return at least 1."""
        ranked = [{"n": 1, "energy": "0.1"}]
        self.assertEqual(viable_region_size(ranked, 10.0), 1)

    def test_viable_region_empty(self):
        """Empty list should return 0."""
        self.assertEqual(viable_region_size([], 10.0), 0)

    def test_contains_factor_in_region(self):
        """Factor in top 10% should return True."""
        ranked = [{"n": i, "energy": str(i)} for i in range(100)]
        # Factor 5 is in top 10 (indices 0-9)
        self.assertTrue(viable_region_contains_factor(ranked, 5, 10.0))

    def test_contains_factor_outside_region(self):
        """Factor outside top 10% should return False."""
        ranked = [{"n": i, "energy": str(i)} for i in range(100)]
        # Factor 50 is NOT in top 10
        self.assertFalse(viable_region_contains_factor(ranked, 50, 10.0))

    def test_contains_factor_at_boundary(self):
        """Factor at exact boundary of viable region."""
        ranked = [{"n": i, "energy": str(i)} for i in range(100)]
        # Top 10% = indices 0-9 (10 candidates)
        # Factor at index 9 should be in region
        self.assertTrue(viable_region_contains_factor(ranked, 9, 10.0))


class TestComputeAllMetrics(unittest.TestCase):
    """Tests for compute_all_corridor_metrics."""

    def test_complete_metrics_output(self):
        """Should return all expected keys."""
        ranked = [
            {"n": 10, "energy": "0.1"},
            {"n": 20, "energy": "0.2"},
            {"n": 30, "energy": "0.3"},
            {"n": 40, "energy": "0.4"},
            {"n": 50, "energy": "0.5"},
        ]
        metrics = compute_all_corridor_metrics(ranked, true_factor=20)

        # Check all expected keys exist
        self.assertIn("effective_corridor_width", metrics)
        self.assertIn("relative_rank", metrics)
        self.assertIn("rank_reduction_vs_random_pct", metrics)
        self.assertIn("corridor_entropy_bits", metrics)
        self.assertIn("corridor_entropy_normalized", metrics)
        self.assertIn("total_candidates", metrics)
        self.assertIn("viable_regions", metrics)
        self.assertIn("factor_found", metrics)

    def test_factor_found_true(self):
        """Factor in list should set factor_found to True."""
        ranked = [{"n": 17, "energy": "0.1"}, {"n": 23, "energy": "0.2"}]
        metrics = compute_all_corridor_metrics(ranked, true_factor=17)
        self.assertTrue(metrics["factor_found"])

    def test_factor_found_false(self):
        """Factor not in list should set factor_found to False."""
        ranked = [{"n": 17, "energy": "0.1"}, {"n": 23, "energy": "0.2"}]
        metrics = compute_all_corridor_metrics(ranked, true_factor=99)
        self.assertFalse(metrics["factor_found"])

    def test_rank_reduction_calculation(self):
        """Rank reduction should be calculated correctly."""
        # 10 candidates, factor at rank 2
        ranked = [{"n": i, "energy": str(i / 10)} for i in range(10)]
        # True factor is 1 (at rank 2, 0-indexed position 1)
        metrics = compute_all_corridor_metrics(ranked, true_factor=1)

        # Random baseline = 10/2 = 5
        # Actual rank = 2
        # Reduction = (5 - 2) / 5 * 100 = 60%
        self.assertAlmostEqual(metrics["rank_reduction_vs_random_pct"], 60.0, places=1)

    def test_viable_regions_multiple_thresholds(self):
        """Should compute viable regions for default thresholds."""
        ranked = [{"n": i, "energy": str(i / 100)} for i in range(100)]
        metrics = compute_all_corridor_metrics(ranked, true_factor=50)

        # Check default thresholds (5%, 10%, 20%)
        self.assertIn("viable_p5", metrics["viable_regions"])
        self.assertIn("viable_p10", metrics["viable_regions"])
        self.assertIn("viable_p20", metrics["viable_regions"])


class TestToyExample(unittest.TestCase):
    """Integration test with a toy factorization example."""

    def test_toy_semiprime(self):
        """Test with a simple semiprime N = 77 = 7 * 11."""
        # N = 77, p = 7, q = 11
        p = 7
        sqrt_N = 8  # isqrt(77) = 8

        # Simulate candidates around sqrt(N)
        candidates = list(range(2, 15))

        # Create ranked list by geometric distance (baseline)
        baseline_ranked = []
        for n in candidates:
            distance = abs(n - sqrt_N)
            baseline_ranked.append({"n": n, "energy": str(distance)})
        baseline_ranked.sort(key=lambda x: int(x["energy"]))

        # Compute metrics
        metrics = compute_all_corridor_metrics(baseline_ranked, true_factor=p)

        # Verify factor was found
        self.assertTrue(metrics["factor_found"])

        # Verify the rank is correct
        # Distance from sqrt(8) to p=7 is 1
        # Candidates 7, 8, 9 all have distance 0 or 1
        # 8 has distance 0, 7 and 9 have distance 1
        # So 7 should be at rank 2 or 3
        self.assertIsNotNone(metrics["effective_corridor_width"])
        self.assertLessEqual(metrics["effective_corridor_width"], 5)


if __name__ == "__main__":
    unittest.main()
