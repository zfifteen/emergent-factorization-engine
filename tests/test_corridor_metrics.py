import unittest
from decimal import Decimal
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

    def test_corridor_entropy(self):
        # Case 1: Uniform energies -> Max entropy
        # E = [1, 1] -> P ~ [exp(-1), exp(-1)] -> P = [0.5, 0.5] -> H = 1 bit
        energies = [1.0, 1.0]
        self.assertAlmostEqual(corridor_entropy(energies), 1.0)
        
        # Case 2: One much lower energy -> Low entropy
        # E = [0, 100] -> P ~ [1, ~0] -> H ~ 0
        energies = [0.0, 100.0]
        self.assertLess(corridor_entropy(energies), 0.1)

    def test_viable_region_size(self):
        candidates = [
            {'n': 1, 'energy': '0.1'},
            {'n': 2, 'energy': '0.5'},
            {'n': 3, 'energy': '1.0'},
            {'n': 4, 'energy': '2.0'}
        ]
        
        self.assertEqual(viable_region_size(candidates, 0.5), 2)
        self.assertEqual(viable_region_size(candidates, 0.0), 0)
        self.assertEqual(viable_region_size(candidates, 2.0), 4)

if __name__ == '__main__':
    unittest.main()
