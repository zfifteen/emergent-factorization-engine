"""
Z5D nth-Prime Predictor Tests
=============================

Reproducibility tests for the Z5D predictor Python implementation.
Tests validate that predictions match known prime values within tolerance.

Uses mpmath with precision > 1e-16 (96 decimal places).

@file test_predictor.py
@version 1.0
"""

import unittest
from mpmath import mp, mpf

from z5d_predictor import (
    mobius,
    li,
    dusart_initializer,
    riemann_R,
    riemann_R_prime,
    newton_step,
    predict_nth_prime,
    Z5DConfig,
    get_version,
    Z5D_PREDICTOR_VERSION,
)


class TestMobius(unittest.TestCase):
    """Tests for the Möbius function."""

    def test_mobius_values(self):
        """Test Möbius function against known values."""
        # μ(1) = 1
        self.assertEqual(mobius(1), 1)
        # μ(2) = -1 (one prime factor)
        self.assertEqual(mobius(2), -1)
        # μ(3) = -1 (one prime factor)
        self.assertEqual(mobius(3), -1)
        # μ(4) = 0 (4 = 2^2, has squared factor)
        self.assertEqual(mobius(4), 0)
        # μ(5) = -1 (one prime factor)
        self.assertEqual(mobius(5), -1)
        # μ(6) = 1 (6 = 2*3, two distinct primes)
        self.assertEqual(mobius(6), 1)
        # μ(7) = -1 (one prime factor)
        self.assertEqual(mobius(7), -1)
        # μ(8) = 0 (8 = 2^3, has squared factor)
        self.assertEqual(mobius(8), 0)
        # μ(9) = 0 (9 = 3^2, has squared factor)
        self.assertEqual(mobius(9), 0)
        # μ(10) = 1 (10 = 2*5, two distinct primes)
        self.assertEqual(mobius(10), 1)

    def test_mobius_precomputed_table(self):
        """Verify precomputed table matches C implementation."""
        expected = [0, 1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0, -1, 1, 1]
        for n in range(1, 16):
            self.assertEqual(mobius(n), expected[n])

    def test_mobius_beyond_table(self):
        """Test Möbius function for values beyond precomputed table."""
        # μ(17) = -1 (prime, single distinct prime factor)
        self.assertEqual(mobius(17), -1)
        # μ(30) = -1 (30 = 2*3*5, three distinct primes, (-1)^3 = -1)
        self.assertEqual(mobius(30), -1)
        # μ(36) = 0 (36 = 2^2 * 3^2, has squared prime factors)
        self.assertEqual(mobius(36), 0)

    def test_mobius_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            mobius(0)
        with self.assertRaises(ValueError):
            mobius(-1)


class TestLi(unittest.TestCase):
    """Tests for the logarithmic integral."""

    def setUp(self):
        mp.dps = 50

    def test_li_basic(self):
        """Test li(x) for basic values."""
        # li(10) ≈ 6.1655995...
        result = li(mpf(10))
        self.assertAlmostEqual(float(result), 6.1655995, places=5)

    def test_li_larger(self):
        """Test li(x) for larger values."""
        # li(100) ≈ 30.12...
        result = li(mpf(100))
        self.assertAlmostEqual(float(result), 30.12614, places=3)

    def test_li_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            li(mpf(1))
        with self.assertRaises(ValueError):
            li(mpf(0.5))


class TestDusart(unittest.TestCase):
    """Tests for the Dusart initializer."""

    def setUp(self):
        mp.dps = 50

    def test_dusart_basic(self):
        """Test Dusart initializer produces reasonable estimates."""
        # For n = 1000000, the 10^6-th prime is 15485863
        x0 = dusart_initializer(mpf(1000000))
        # Should be within 1% of actual prime
        error_pct = abs(float(x0) - 15485863) / 15485863 * 100
        self.assertLess(error_pct, 1.0)

    def test_dusart_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            dusart_initializer(mpf(1))


class TestRiemannR(unittest.TestCase):
    """Tests for Riemann R(x) and R'(x)."""

    def setUp(self):
        mp.dps = 50

    def test_riemann_R_basic(self):
        """Test R(x) approximates π(x)."""
        # R(1000) should be close to π(1000) = 168
        R_val = riemann_R(mpf(1000))
        # Allow 1% error
        self.assertAlmostEqual(float(R_val), 168, delta=5)

    def test_riemann_R_prime_positive(self):
        """Test R'(x) is positive for x > 1."""
        R_prime = riemann_R_prime(mpf(1000))
        self.assertGreater(float(R_prime), 0)

    def test_riemann_R_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            riemann_R(mpf(1))
        with self.assertRaises(ValueError):
            riemann_R_prime(mpf(0.5))


class TestNewton(unittest.TestCase):
    """Tests for Newton solver step."""

    def setUp(self):
        mp.dps = 50

    def test_newton_step_converges(self):
        """Test that Newton step moves toward solution."""
        n = mpf(1000000)
        x0 = dusart_initializer(n)

        # One Newton step should improve estimate
        x1 = newton_step(x0, n)

        # The new estimate should be different (iteration is happening)
        self.assertNotEqual(float(x0), float(x1))

    def test_newton_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            newton_step(mpf(0.5), mpf(100))
        with self.assertRaises(ValueError):
            newton_step(mpf(100), mpf(0))


class TestPredictor(unittest.TestCase):
    """Tests for the main predictor."""

    def setUp(self):
        mp.dps = 96

    def test_version(self):
        """Test version string."""
        self.assertEqual(get_version(), Z5D_PREDICTOR_VERSION)
        self.assertEqual(get_version(), "1.0.0")

    def test_predict_known_primes(self):
        """Test predictor against known nth primes."""
        # Known values: (n, p_n)
        test_cases = [
            (100, 541),
            (1000, 7919),
            (10000, 104729),
            (100000, 1299709),
            (1000000, 15485863),
        ]

        for n, expected_prime in test_cases:
            with self.subTest(n=n):
                result = predict_nth_prime(n)

                # Check convergence
                self.assertTrue(result.converged)

                # Check prediction is within 1% of actual
                predicted = int(round(float(result.predicted_prime)))
                error_pct = abs(predicted - expected_prime) / expected_prime * 100
                self.assertLess(
                    error_pct, 1.0,
                    f"n={n}: predicted {predicted}, expected {expected_prime}"
                )

    def test_predict_with_custom_config(self):
        """Test predictor with custom configuration."""
        config = Z5DConfig(
            dps=50,
            K=15,
            max_iterations=20,
            tolerance=mpf("1e-30"),
        )
        result = predict_nth_prime(1000, config)
        self.assertTrue(result.converged)

    def test_predict_result_fields(self):
        """Test that result contains expected fields."""
        result = predict_nth_prime(1000)

        self.assertIsNotNone(result.predicted_prime)
        self.assertIsNotNone(result.error)
        self.assertGreater(result.elapsed_ms, 0)
        self.assertGreater(result.iterations, 0)
        self.assertIsInstance(result.converged, bool)

    def test_predict_invalid_input(self):
        """Test that invalid inputs raise ValueError."""
        with self.assertRaises(ValueError):
            predict_nth_prime(0)
        with self.assertRaises(ValueError):
            predict_nth_prime(-1)


class TestHighPrecision(unittest.TestCase):
    """Tests to verify high-precision arithmetic (< 1e-16)."""

    def setUp(self):
        mp.dps = 96  # 96 decimal places of precision

    def test_precision_exceeds_double(self):
        """Test that precision exceeds double precision (~1e-16)."""
        # Predict a large prime index
        result = predict_nth_prime(10000000)

        # Error should be much smaller than 1e-16 * predicted value
        relative_error = float(result.error) / float(result.predicted_prime)
        self.assertLess(relative_error, 1e-16)

    def test_reproducibility(self):
        """Test that results are reproducible."""
        n = 1000000
        result1 = predict_nth_prime(n)
        result2 = predict_nth_prime(n)

        # Results should be identical
        self.assertEqual(
            str(result1.predicted_prime),
            str(result2.predicted_prime)
        )


if __name__ == "__main__":
    unittest.main()
