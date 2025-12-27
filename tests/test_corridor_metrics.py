import unittest
from cellview.metrics.corridor import effective_corridor_width, corridor_entropy, viable_region_size

class TestCorridorMetrics(unittest.TestCase):
    def test_effective_corridor_width(self):
        # Case 1: List of ints
        candidates = [100, 101, 102, 103, 104]
        self.assertEqual(effective_corridor_width(candidates, 0, 102), 2)
        self.assertEqual(effective_corridor_width(candidates, 0, 100), 0)
        self.assertEqual(effective_corridor_width(candidates, 0, 999), -1)

        # Case 2: List of dicts
        candidates_dicts = [{'n': 100}, {'n': 101}, {'n': 102}]
        self.assertEqual(effective_corridor_width(candidates_dicts, 0, 101), 1)
        
        # Case 3: Empty list
        self.assertEqual(effective_corridor_width([], 0, 101), -1)
        
        # Case 4: Single element
        self.assertEqual(effective_corridor_width([101], 0, 101), 0)

        # Case 5: Duplicate candidates - should return first occurrence
        candidates_dups = [100, 102, 102, 103]
        self.assertEqual(effective_corridor_width(candidates_dups, 0, 102), 1)

    def test_corridor_entropy(self):
        # Case 1: Uniform energies -> Max entropy
        # E = [1, 1] -> Softmax -> [0.5, 0.5] -> H = 1 bit
        # With normalization: rng=0 -> uniform
        energies = [1.0, 1.0]
        self.assertAlmostEqual(corridor_entropy(energies), 1.0)
        
        # Case 2: Highly skewed energies -> Low entropy
        energies = [0.0, 100.0]
        self.assertLess(corridor_entropy(energies), 0.1)
        
        # Case 3: Empty list
        self.assertEqual(corridor_entropy([]), 0.0)
        
        # Case 4: Single element
        self.assertEqual(corridor_entropy([10.0]), 0.0)

    def test_viable_region_size(self):
        candidates = [
            {'n': 1, 'energy': 0.1},
            {'n': 2, 'energy': 0.5},
            {'n': 3, 'energy': 1.0},
            {'n': 4, 'energy': 2.0},
            100  # Plain int should be ignored
        ]
        
        self.assertEqual(viable_region_size(candidates, 0.5), 2)
        self.assertEqual(viable_region_size(candidates, 0.0), 0)
        self.assertEqual(viable_region_size(candidates, 2.0), 4)

if __name__ == '__main__':
    unittest.main()
