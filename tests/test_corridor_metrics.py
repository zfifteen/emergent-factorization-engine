import pytest

from cellview.metrics.corridor import (
    effective_corridor_width,
    corridor_entropy,
    viable_region_size,
)


def test_effective_corridor_width():
    assert effective_corridor_width([10, 20, 30], 20) == 2
    assert effective_corridor_width([10, 20, 30], 25) == 4


def test_corridor_entropy():
    import math

    assert abs(corridor_entropy([1, 1]) - math.log(2)) < 1e-6
    assert corridor_entropy([0, 20]) < 1e-6


def test_viable_region_size():
    cands = [(1, 0.5), (2, 1.5), (3, 0.8)]
    assert viable_region_size(cands, 1.0) == 2
    assert viable_region_size(cands, 0.0) == 0
