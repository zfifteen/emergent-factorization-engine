import unittest
from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


class TestCorridorMetrics(unittest.TestCase):
    def test_effective_corridor_width_found(self):
        """Test rank when p_true is in candidates."""
        candidates = [(2, 1.0), (3, 0.5), (5, 0.2)]  # sorted by energy ascending
        rank = effective_corridor_width(candidates, 3)
        self.assertEqual(rank, 2)  # 3 is at position 2 (1-based)

    def test_effective_corridor_width_not_found(self):
        """Test rank when p_true not in candidates."""
        candidates = [(2, 1.0), (3, 0.5), (5, 0.2)]
        rank = effective_corridor_width(candidates, 7)
        self.assertEqual(rank, 4)  # len + 1

    def test_corridor_entropy_uniform(self):
        """Test entropy for uniform energies."""
        energies = [1.0, 1.0, 1.0]
        entropy = corridor_entropy(energies)
        self.assertAlmostEqual(entropy, 0.0, places=5)

    def test_corridor_entropy_diverse(self):
        """Test entropy for diverse energies."""
        energies = [1, 2, 3, 10]
        entropy = corridor_entropy(energies)
        # Approximate check; should be >0 and <1
        self.assertGreater(entropy, 0.5)
        self.assertLess(entropy, 1.0)

    def test_corridor_entropy_empty(self):
        """Test entropy for empty list."""
        entropy = corridor_entropy([])
        self.assertEqual(entropy, 0.0)

    def test_viable_region_size_below_threshold(self):
        """Test count below threshold."""
        candidates = [(1, 0.1), (2, 0.5), (3, 1.0)]
        count = viable_region_size(candidates, 0.6)
        self.assertEqual(count, 2)  # 0.1 and 0.5

    def test_viable_region_size_above(self):
        """Test count when all above threshold."""
        candidates = [(1, 0.8), (2, 0.9), (3, 1.0)]
        count = viable_region_size(candidates, 0.5)
        self.assertEqual(count, 0)

    def test_effective_corridor_width_empty(self):
        """Test rank with empty candidate list."""
        candidates = []
        rank = effective_corridor_width(candidates, 5)
        self.assertEqual(rank, 1)  # len(0) + 1

    def test_corridor_entropy_single_element(self):
        """Test entropy for single element."""
        energies = [1.0]
        entropy = corridor_entropy(energies)
        self.assertEqual(entropy, 0.0)

    def test_corridor_entropy_negative_energies(self):
        """Test entropy with negative/zero energies."""
        energies = [0, 0, 0]
        entropy = corridor_entropy(energies)
        self.assertEqual(entropy, 0.0)


if __name__ == "__main__":
    unittest.main()
