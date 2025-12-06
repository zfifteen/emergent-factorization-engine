"""
Corridor (meta-cell) generation and ranking utilities.

Stage-1 of the meta-cell pipeline ranks *ranges* (corridors) by a
geometric energy surrogate before expanding the top corridors into
atomic integer candidates for the regular Levin sorter.

This keeps the search global-but-cheap for 127-bit scale numbers.
"""

from dataclasses import dataclass
from decimal import Decimal
from math import isqrt
from typing import Dict, Iterable, List, Sequence, Tuple

from cellview.heuristics.core import EnergySpec, resolve_energy


@dataclass
class Corridor:
    center: int
    low: int
    high: int
    energy: Decimal | None = None

    @property
    def span(self) -> int:
        return self.high - self.low + 1


def _percentile(values: Sequence[Decimal], p: float) -> Decimal:
    assert 0 <= p <= 100
    if not values:
        return Decimal(0)
    idx = max(0, min(len(values) - 1, int(len(values) * p / 100)))
    return sorted(values)[idx]


def generate_corridors(
    range_start: int,
    range_end: int,
    half_width: int,
    num_corridors: int,
    rng,
) -> List[Corridor]:
    """
    Evenly sweep [range_start, range_end] with num_corridors centers and small jitter.
    Corridors are clamped to [2, range_end].
    """

    if num_corridors <= 0:
        raise ValueError("num_corridors must be positive")
    if range_end <= range_start:
        raise ValueError("range_end must exceed range_start")

    span = range_end - range_start
    step = max(1, span // max(1, num_corridors - 1))
    centers: List[int] = []
    for i in range(num_corridors):
        base = range_start + i * step
        jitter_cap = max(1, min(half_width // 2, step // 2))
        jitter = rng.randint(-jitter_cap, jitter_cap)
        center = max(range_start, min(range_end, base + jitter))
        centers.append(center)

    corridors: List[Corridor] = []
    for center in centers:
        low = max(2, center - half_width)
        high = min(range_end, center + half_width)
        if low > high:
            continue
        corridors.append(Corridor(center=center, low=low, high=high))
    return corridors


def score_corridor(
    corridor: Corridor,
    N: int,
    energy_spec: EnergySpec,
    samples: int,
    rng,
    aggregator: str = "p5",
    energy_cache: Dict[tuple, Decimal] | None = None,
) -> Decimal:
    """
    Compute a scalar energy for a corridor by sampling integer cells inside it.
    aggregator: "min" or "p{percent}" (e.g. "p5" for 5th percentile).
    """

    energy_cache = energy_cache or {}
    span = corridor.span
    count = span if samples >= span else samples

    seen = set()
    energies: List[Decimal] = []
    while len(energies) < count:
        val = rng.randrange(corridor.low, corridor.high + 1)
        if val in seen:
            continue
        seen.add(val)
        cache_key = (energy_spec.name, val)
        if cache_key in energy_cache:
            e_val = energy_cache[cache_key]
        else:
            e_val = energy_spec.fn(val, N, energy_spec.params)
            energy_cache[cache_key] = e_val
        energies.append(e_val)

    if aggregator == "min":
        agg = min(energies)
    elif aggregator.startswith("p"):
        try:
            pct = float(aggregator[1:])
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Bad percentile aggregator '{aggregator}'") from exc
        agg = _percentile(energies, pct)
    else:  # pragma: no cover - defensive
        raise ValueError(f"Unknown aggregator '{aggregator}'")

    corridor.energy = agg
    return agg


def levin_sort_corridors(corridors: List[Corridor], max_steps: int = 10) -> Dict:
    """
    Levin-style neighbor swap sort on corridors using their precomputed energy.
    Returns metrics mirroring the main engine shape.
    """

    swaps_per_step: List[int] = []
    for _ in range(max_steps):
        swaps = 0
        for i in range(len(corridors) - 1):
            a = corridors[i]
            b = corridors[i + 1]
            if a.energy is None or b.energy is None:
                raise ValueError("Corridor energies must be precomputed before sorting")
            if a.energy > b.energy:
                corridors[i], corridors[i + 1] = corridors[i + 1], corridors[i]
                swaps += 1
        swaps_per_step.append(swaps)
        if swaps == 0:
            break

    final_state = [
        {"index": idx, "center": c.center, "low": c.low, "high": c.high, "energy": str(c.energy)}
        for idx, c in enumerate(corridors)
    ]

    ranked = sorted(final_state, key=lambda x: Decimal(x["energy"]))
    return {
        "swaps_per_step": swaps_per_step,
        "final_state": final_state,
        "ranked_corridors": ranked,
    }


def expand_corridors_to_candidates(corridors: Sequence[Corridor]) -> List[int]:
    """
    Expand corridors into dense integer candidate list, deduped and ordered by corridor rank.
    """

    seen = set()
    out: List[int] = []
    for c in corridors:
        for val in range(c.low, c.high + 1):
            if val not in seen:
                seen.add(val)
                out.append(val)
    return out


def default_range_for(N: int, start: int | None, end: int | None) -> Tuple[int, int]:
    """Fallback corridor search window.

    If explicit start/end provided, honor them.
    For the canonical 127-bit challenge we bias to the 2^31..5e9 window
    where prior resonance points cluster; otherwise default to [2, sqrt(N)].
    """

    if start and end:
        return start, end

    sqrt_n = isqrt(N)

    if N > 10**30:  # heuristic cue for the 127-bit scale
        return 1_000_000_000, 5_000_000_000

    return 2, sqrt_n


__all__ = [
    "Corridor",
    "generate_corridors",
    "score_corridor",
    "levin_sort_corridors",
    "expand_corridors_to_candidates",
    "default_range_for",
]
