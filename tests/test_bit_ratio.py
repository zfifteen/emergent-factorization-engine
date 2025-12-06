import unittest
from cellview.utils.ladder import (
    generate_ladder,
    generate_verification_ladder,
    generate_challenge_ladder,
    generate_unbalanced_semiprime,
    BASE_SEED,
    BIT_RATIO_DEFAULT,
    _is_prime,
)


class TestBitRatioFunctionality(unittest.TestCase):
    """Test the new bit_ratio parameter functionality."""
    
    def test_generate_with_bit_ratio_3(self):
        """Test generating semiprime with 1:3 bit ratio."""
        gate = generate_unbalanced_semiprime(60, 102, bit_ratio=3)
        
        self.assertEqual(gate.bit_ratio, 3)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
        self.assertEqual(gate.N, gate.p * gate.q)
        
        # For 1:3 ratio, p should get ~1/4 of bits (15 out of 60)
        self.assertGreater(gate.p_bits, 12)
        self.assertLess(gate.p_bits, 18)
    
    def test_generate_with_bit_ratio_4(self):
        """Test generating semiprime with 1:4 bit ratio."""
        gate = generate_unbalanced_semiprime(60, 102, bit_ratio=4)
        
        self.assertEqual(gate.bit_ratio, 4)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
        self.assertEqual(gate.N, gate.p * gate.q)
        
        # For 1:4 ratio, p should get ~1/5 of bits (12 out of 60)
        self.assertGreater(gate.p_bits, 10)
        self.assertLess(gate.p_bits, 15)
    
    def test_generate_with_bit_ratio_5(self):
        """Test generating semiprime with 1:5 bit ratio."""
        gate = generate_unbalanced_semiprime(60, 102, bit_ratio=5)
        
        self.assertEqual(gate.bit_ratio, 5)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
        self.assertEqual(gate.N, gate.p * gate.q)
        
        # For 1:5 ratio, p should get ~1/6 of bits (10 out of 60)
        self.assertGreater(gate.p_bits, 8)
        self.assertLess(gate.p_bits, 13)
    
    def test_bit_ratio_precedence_over_ratio(self):
        """Test that bit_ratio parameter takes precedence over ratio."""
        # Generate with both parameters, bit_ratio should win
        gate1 = generate_unbalanced_semiprime(60, 102, ratio=0.25, bit_ratio=4)
        gate2 = generate_unbalanced_semiprime(60, 102, bit_ratio=4)
        
        # Both should produce the same result (bit_ratio=4)
        self.assertEqual(gate1.bit_ratio, 4)
        self.assertEqual(gate2.bit_ratio, 4)
        self.assertEqual(gate1.N, gate2.N)
    
    def test_backward_compatibility_with_ratio(self):
        """Test that old ratio parameter still works."""
        gate = generate_unbalanced_semiprime(60, 102, ratio=0.25)
        
        # Should calculate bit_ratio from ratio (0.25 = 1:3)
        self.assertEqual(gate.bit_ratio, 3)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
    
    def test_default_parameters(self):
        """Test that default parameters produce 1:3 ratio."""
        gate = generate_unbalanced_semiprime(60, 102)
        
        self.assertEqual(gate.bit_ratio, BIT_RATIO_DEFAULT)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
    
    def test_ladder_with_bit_ratio(self):
        """Test generating full ladder with bit_ratio parameter."""
        ladder = generate_verification_ladder(base_seed=BASE_SEED, bit_ratio=4)
        
        # Check that all non-G127 gates have the correct bit_ratio
        for gate in ladder:
            if gate.gate != "G127":
                self.assertEqual(gate.bit_ratio, 4)
                self.assertIsNotNone(gate.p)
                self.assertIsNotNone(gate.q)
    
    def test_challenge_ladder_with_bit_ratio(self):
        """Test generating challenge ladder with bit_ratio parameter."""
        ladder = generate_challenge_ladder(base_seed=BASE_SEED, bit_ratio=5)
        
        # Check that all non-G127 gates have the correct bit_ratio but hide factors
        for gate in ladder:
            if gate.gate != "G127":
                self.assertEqual(gate.bit_ratio, 5)
                self.assertIsNone(gate.p)
                self.assertIsNone(gate.q)
                self.assertFalse(gate.factors_revealed)
    
    def test_bit_ratio_affects_p_size(self):
        """Test that larger bit_ratio produces smaller p."""
        gate_3 = generate_unbalanced_semiprime(100, 142, bit_ratio=3)
        gate_4 = generate_unbalanced_semiprime(100, 142, bit_ratio=4)
        gate_5 = generate_unbalanced_semiprime(100, 142, bit_ratio=5)
        
        # p should get progressively smaller
        self.assertGreater(gate_3.p_bits, gate_4.p_bits)
        self.assertGreater(gate_4.p_bits, gate_5.p_bits)
        
        # Verify actual values are prime
        self.assertTrue(_is_prime(gate_3.p))
        self.assertTrue(_is_prime(gate_4.p))
        self.assertTrue(_is_prime(gate_5.p))
    
    def test_determinism_with_bit_ratio(self):
        """Test that same seed and bit_ratio produce same results."""
        gate1 = generate_unbalanced_semiprime(50, 92, bit_ratio=4)
        gate2 = generate_unbalanced_semiprime(50, 92, bit_ratio=4)
        
        self.assertEqual(gate1.N, gate2.N)
        self.assertEqual(gate1.p, gate2.p)
        self.assertEqual(gate1.q, gate2.q)
    
    def test_different_bit_ratios_produce_different_results(self):
        """Test that different bit_ratios produce different semiprimes."""
        gate_3 = generate_unbalanced_semiprime(50, 92, bit_ratio=3)
        gate_4 = generate_unbalanced_semiprime(50, 92, bit_ratio=4)
        gate_5 = generate_unbalanced_semiprime(50, 92, bit_ratio=5)
        
        # All should be different due to different bit allocations
        self.assertNotEqual(gate_3.N, gate_4.N)
        self.assertNotEqual(gate_4.N, gate_5.N)
        self.assertNotEqual(gate_3.N, gate_5.N)


class TestBitRatioBackwardCompatibility(unittest.TestCase):
    """Test that existing code without bit_ratio still works."""
    
    def test_generate_ladder_without_params(self):
        """Test generating ladder with no parameters (backward compatible)."""
        ladder = generate_ladder()
        
        # Should generate standard ladder
        self.assertEqual(len(ladder), 14)
        
        # All non-G127 gates should have factors
        for gate in ladder:
            if gate.gate != "G127":
                self.assertIsNotNone(gate.p)
                self.assertIsNotNone(gate.q)
    
    def test_verification_ladder_without_params(self):
        """Test verification ladder with defaults."""
        ladder = generate_verification_ladder()
        
        self.assertEqual(len(ladder), 14)
        for gate in ladder:
            if gate.gate != "G127":
                self.assertTrue(gate.factors_revealed)
    
    def test_challenge_ladder_without_params(self):
        """Test challenge ladder with defaults."""
        ladder = generate_challenge_ladder()
        
        self.assertEqual(len(ladder), 14)
        for gate in ladder:
            self.assertFalse(gate.factors_revealed)


if __name__ == '__main__':
    unittest.main()
