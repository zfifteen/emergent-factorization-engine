import unittest
from mpmath import mp, mpf

from cellview.utils.z5d_predictor import (
    mobius,
    li,
    riemann_R,
    riemann_R_prime,
    newton_step,
    predict_nth_prime,
    Z5DConfig,
    get_version,
    Z5D_PREDICTOR_VERSION,
)


class TestMobius(unittest.TestCase):
    def test_known_values(self):
        expected = {
            1: 1,
            2: -1,
            3: -1,
            4: 0,
            5: -1,
            6: 1,
            7: -1,
            8: 0,
            9: 0,
            10: 1,
        }
        for k, v in expected.items():
            self.assertEqual(mobius(k), v)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            mobius(0)
        with self.assertRaises(ValueError):
            mobius(-5)


class TestLiFunction(unittest.TestCase):
    def setUp(self):
        mp.dps = 50

    def test_li_basic(self):
        value = li(mpf(100))
        self.assertAlmostEqual(float(value), 30.12614, places=3)

    def test_li_invalid(self):
        with self.assertRaises(ValueError):
            li(mpf(1))


class TestRiemannR(unittest.TestCase):
    def setUp(self):
        mp.dps = 50

    def test_riemann_approx_pi(self):
        approx = riemann_R(mpf(1000))
        self.assertAlmostEqual(float(approx), 168, delta=5)

    def test_derivative_positive(self):
        self.assertGreater(float(riemann_R_prime(mpf(1000))), 0)


class TestNewtonStep(unittest.TestCase):
    def setUp(self):
        mp.dps = 50

    def test_newton_changes_estimate(self):
        n = mpf(1000000)
        x0 = mpf(15485000)
        x1 = newton_step(x0, n)
        self.assertNotEqual(float(x0), float(x1))

    def test_newton_invalid(self):
        with self.assertRaises(ValueError):
            newton_step(mpf(0.5), mpf(100))


class TestPredictor(unittest.TestCase):
    def setUp(self):
        mp.dps = 96

    def test_version(self):
        self.assertEqual(get_version(), Z5D_PREDICTOR_VERSION)

    def test_predict_known_primes(self):
        cases = [(100, 541), (1000, 7919), (10000, 104729)]
        for idx, expected in cases:
            result = predict_nth_prime(idx)
            self.assertTrue(result.converged)
            predicted = int(round(float(result.predicted_prime)))
            error_pct = abs(predicted - expected) / expected * 100
            self.assertLess(error_pct, 1.0)

    def test_custom_config(self):
        config = Z5DConfig(dps=64, K=12, max_iterations=15, tolerance=mpf("1e-30"))
        result = predict_nth_prime(1000, config)
        self.assertTrue(result.converged)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            predict_nth_prime(0)


if __name__ == "__main__":
    unittest.main()
