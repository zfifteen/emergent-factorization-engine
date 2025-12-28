"""Tests for corridor metrics used in emergent vs baseline validation.

Validation criterion: Δ > 0 (emergent_rank < baseline_rank)
- effective_corridor_width returns rank (1-based) of true factor in sorted list
- Lower rank = better performance (narrower effective corridor)
- Success: emergent method produces lower rank than geometric baseline
- Percentage reductions are informational, not pass/fail criteria
"""

from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


def test_effective_corridor_width():
    """Test corridor width (rank) calculation.
    
    Success criterion for emergent validation: emergent_rank < baseline_rank
    Lower rank = factor found earlier in sorted list = better performance.
    """
    assert effective_corridor_width([10, 20, 30], 20) == 2
    # 25 is intentionally not in the list; this tests the "not found" behavior
    assert effective_corridor_width([10, 20, 30], 25) == 4
    assert effective_corridor_width([], 1) == 1


def test_corridor_entropy():
    from math import log

    assert abs(corridor_entropy([1, 1]) - log(2)) < 1e-6
    assert corridor_entropy([0, 20]) < 1e-6


def test_viable_region_size():
    cands = [(1, 0.5), (2, 1.5), (3, 0.8)]
    assert viable_region_size(cands, 1.0) == 2
    assert viable_region_size(cands, 0.0) == 0
