#!/usr/bin/env python3
"""
Ladder Generator for Cell-View Factor Morphospace.

Generates UNBALANCED semiprimes with a 1:3 factor ratio (p gets ~25% of bits).
Uses base seed 42 with per-gate derivation for reproducibility.

Two modes:
    - Verification ladder: factors revealed for regression/testing (default via generate_ladder).
    - Challenge ladder: same Ns, but p/q are withheld (factors_revealed=False) for blind challenges.

Prime Generation:
    Uses a pure-Python Z5D predictor implementation (mpmath-powered).
    Falls back to Miller-Rabin probabilistic primality testing when needed.
    See: https://github.com/velocityworks/emergent-factorization-engine
"""

import random
import json
import yaml
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from importlib import resources
from math import isqrt

from mpmath import mp, mpf

from .z5d_predictor import (
    predict_nth_prime,
    riemann_R,
    Z5DConfig,
    Z5D_DEFAULT_DPS,
    Z5D_DEFAULT_K,
)

# Canonical constants
BASE_SEED = 42
RATIO = 0.25  # small factor gets 25% of bits → 1:3 ratio
CHALLENGE_N = 137524771864208156028430259349934309717
CHALLENGE_BITS = 127


Z5D_CONFIG = Z5DConfig()
FALLBACK_THRESHOLD = 1000


def _miller_rabin(n: int, k: int = 10) -> bool:
    """
    Probabilistic Miller-Rabin primality test.
    """
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _fallback_is_prime(n: int) -> bool:
    """
    Fallback primality probe: trial division for small n, Miller-Rabin otherwise.
    """
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    if n < 1000:
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True
    return _miller_rabin(n, k=10)


def _fallback_next_prime(n: int) -> int:
    """
    Simple brute-force next-prime search using the fallback primality test.
    """
    candidate = max(n, 2)
    if candidate <= 2:
        return 2
    if candidate % 2 == 0:
        candidate += 1
    while not _fallback_is_prime(candidate):
        candidate += 2
    return candidate


def _prime_index_estimate(value: int, K: int = Z5D_DEFAULT_K) -> int:
    """
    Estimate π(value) using the Riemann R(x) approximation.
    """
    mp.dps = Z5D_DEFAULT_DPS
    x = mpf(max(value, 2))
    pi_est = riemann_R(x, K)
    return max(int(pi_est), 1)


def _simple_next_prime(n: int) -> int:
    """
    Estimate the next prime >= n via the Z5D predictor and verify it.
    """
    if n < FALLBACK_THRESHOLD:
        return _fallback_next_prime(n)
    index_estimate = _prime_index_estimate(n)
    target_index = max(index_estimate + 1, 2)
    mp.dps = Z5D_DEFAULT_DPS
    result = predict_nth_prime(target_index, Z5D_CONFIG)
    candidate = max(int(round(result.predicted_prime)), n)
    if candidate % 2 == 0:
        candidate += 1
    while True:
        if _fallback_is_prime(candidate):
            return candidate
        candidate += 2


def _is_prime(n: int) -> bool:
    """
    Deterministic primality test with Miller-Rabin fallback.
    """
    return _fallback_is_prime(n)


@dataclass
class GateSemiprime:
    """Represents a single gate in a ladder."""
    gate: str
    target_bits: int
    actual_bits: Optional[int] = None
    N: Optional[int] = None
    p: Optional[int] = None
    q: Optional[int] = None
    p_bits: Optional[int] = None
    q_bits: Optional[int] = None
    effective_seed: Optional[int] = None
    ratio: Optional[float] = None
    sqrt_N: Optional[int] = None
    p_distance_from_sqrt: Optional[int] = None
    p_as_fraction_of_sqrt: Optional[float] = None
    note: Optional[str] = None
    factors_revealed: bool = True


def get_effective_seed(base_seed: int, bit_size: int) -> int:
    """Derive per-gate seed from base seed + bit size."""
    return base_seed + bit_size


def generate_unbalanced_semiprime(
    bit_size: int,
    seed: int,
    ratio: float = RATIO,
    reveal_factors: bool = True,
) -> GateSemiprime:
    """
    Generate an unbalanced semiprime of the specified bit size.
    
    The small factor p gets ~ratio of the bits (default 25%).
    This places p well below √N, making it a non-trivial search target.
    
    Args:
        bit_size: Target bit length of N
        seed: RNG seed for reproducibility
        ratio: Fraction of bits for smaller factor (default 0.25 = 1:3 ratio)
    
    Returns:
        GateSemiprime with all fields populated
    """
    rng = random.Random(seed)
    
    # Small factor p gets ~ratio of the bits
    p_bits = max(4, int(bit_size * ratio))  # at least 4 bits for meaningful prime
    
    # Generate p (small factor)
    p_min = 1 << (p_bits - 1)  # ensure correct bit length
    p_max = (1 << p_bits) - 1
    p_candidate = rng.randint(p_min, p_max) | 1  # ensure odd
    p = _simple_next_prime(p_candidate)
    
    # Compute required q_bits to hit target N bit size
    # N = p * q, so log2(N) ≈ log2(p) + log2(q)
    q_bits = bit_size - p.bit_length()
    q_bits = max(p.bit_length() + 1, q_bits)  # ensure q > p
    
    q_min = 1 << (q_bits - 1)
    q_max = (1 << q_bits) - 1
    q_candidate = rng.randint(q_min, q_max) | 1  # ensure odd
    q = _simple_next_prime(q_candidate)
    
    # Ensure p < q (p is the small factor)
    if p > q:
        p, q = q, p
    
    N = p * q
    sqrt_N = isqrt(N)
    
    gate = GateSemiprime(
        gate=f"G{bit_size:03d}",
        target_bits=bit_size,
        actual_bits=N.bit_length(),
        N=N,
        p=p if reveal_factors else None,
        q=q if reveal_factors else None,
        p_bits=p.bit_length() if reveal_factors else None,
        q_bits=q.bit_length() if reveal_factors else None,
        effective_seed=seed,
        ratio=ratio,
        sqrt_N=sqrt_N,
        p_distance_from_sqrt=sqrt_N - p if reveal_factors else None,
        p_as_fraction_of_sqrt=(p / sqrt_N) if (sqrt_N > 0 and reveal_factors) else None,
        note=None if reveal_factors else "Factors withheld (challenge ladder)",
        factors_revealed=reveal_factors,
    )

    # Actively scrub prime values when factors are withheld to avoid accidental reuse
    if not reveal_factors:
        p = None
        q = None

    return gate


def _insert_g127(ladder: List[GateSemiprime]) -> List[GateSemiprime]:
    """Insert the canonical challenge gate (factors withheld) into a ladder list."""
    g127_idx = next(i for i, g in enumerate(ladder) if g.target_bits > 127)
    g127 = GateSemiprime(
        gate="G127",
        target_bits=127,
        actual_bits=CHALLENGE_N.bit_length(),
        N=CHALLENGE_N,
        p=None,
        q=None,
        p_bits=None,
        q_bits=None,
        effective_seed=None,
        ratio=None,
        sqrt_N=isqrt(CHALLENGE_N),
        p_distance_from_sqrt=None,
        p_as_fraction_of_sqrt=None,
        note="Canonical challenge - factors unknown",
        factors_revealed=False,
    )
    ladder.insert(g127_idx, g127)
    return ladder


def generate_verification_ladder(
    base_seed: int = BASE_SEED,
    ratio: float = RATIO,
) -> List[GateSemiprime]:
    """Generate a ladder with factors revealed for regression/verification."""
    ladder = []

    for bits in range(10, 131, 10):
        effective_seed = get_effective_seed(base_seed, bits)
        gate = generate_unbalanced_semiprime(bits, effective_seed, ratio, reveal_factors=True)
        ladder.append(gate)

    _insert_g127(ladder)
    return ladder


def generate_challenge_ladder(
    base_seed: int = BASE_SEED,
    ratio: float = RATIO,
) -> List[GateSemiprime]:
    """Generate a ladder with factors withheld (blind challenge set)."""
    ladder = []

    for bits in range(10, 131, 10):
        effective_seed = get_effective_seed(base_seed, bits)
        gate = generate_unbalanced_semiprime(bits, effective_seed, ratio, reveal_factors=False)
        ladder.append(gate)

    _insert_g127(ladder)
    return ladder


# Backward-compatible alias: verification ladder remains the default
def generate_ladder(
    base_seed: int = BASE_SEED,
    ratio: float = RATIO,
) -> List[GateSemiprime]:
    return generate_verification_ladder(base_seed=base_seed, ratio=ratio)


VALIDATION_LADDER_YAML = "validation_ladder.yaml"
CHALLENGE_LADDER_YAML = "challenge_ladder.yaml"


def load_ladder_yaml(path: Union[str, Path] = None, kind: str = "validation") -> Dict[str, Any]:
    """
    Load a ladder definition from YAML.
    
    Args:
        path: Explicit path override (skips packaged selection)
        kind: "validation" (default) or "challenge" when using packaged assets
    
    Returns:
        Parsed YAML as dictionary
    """
    if path is None and kind not in {"validation", "challenge"}:
        raise ValueError("kind must be 'validation' or 'challenge'")

    if path is None:
        filename = VALIDATION_LADDER_YAML if kind == "validation" else CHALLENGE_LADDER_YAML
        resource = resources.files("cellview.data") / filename
        contents = resource.read_text(encoding="utf-8")
        return yaml.safe_load(contents)
    
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_gate(gate_name: str, ladder: List[GateSemiprime] = None) -> Optional[GateSemiprime]:
    """
    Get a specific gate by name (e.g., "G030").
    
    Args:
        gate_name: Gate identifier like "G030" or "G127"
        ladder: Pre-generated ladder (if None, generates fresh)
    
    Returns:
        GateSemiprime or None if not found
    """
    if ladder is None:
        ladder = generate_ladder()
    
    for gate in ladder:
        if gate.gate == gate_name:
            return gate
    return None


def print_ladder_summary(
    ladder: List[GateSemiprime] = None,
    label: str = None,
) -> None:
    """Print a human-readable summary of the ladder."""
    if ladder is None:
        ladder = generate_ladder()

    if label is None:
        # If every non-G127 gate hides factors, call it the challenge ladder
        non_challenge_gates = [g for g in ladder if g.gate != "G127"]
        hidden = all(not g.factors_revealed for g in non_challenge_gates)
        label = "CHALLENGE" if hidden else "VERIFICATION"

    print("=" * 100)
    print(f"{label.upper()} LADDER: Unbalanced Semiprimes (Base Seed: 42, Ratio: 1:3)")
    print("=" * 100)
    print(f"{'Gate':<6} {'Bits':<6} {'p bits':<8} {'q bits':<8} {'p/√N':<12} {'p':>24}")
    print("-" * 100)

    for g in ladder:
        if g.p is None:
            marker = "[CHALLENGE]" if g.gate == "G127" else "[WITHHELD]"
            print(f"{g.gate:<6} {g.target_bits:<6} {'?':<8} {'?':<8} {'?':<12} {marker:>24}")
        else:
            print(f"{g.gate:<6} {g.actual_bits:<6} {g.p_bits:<8} {g.q_bits:<8} "
                  f"{g.p_as_fraction_of_sqrt:<12.6f} {g.p:>24}")

    print("=" * 100)


def export_ladder_json(path: Path = None, ladder: List[GateSemiprime] = None) -> None:
    """
    Export the ladder to JSON format.
    
    Args:
        path: Output path (default: validation_ladder.json in emergence/)
        ladder: Pre-generated ladder (if None, generates fresh)
    """
    if ladder is None:
        ladder = generate_ladder()
    
    if path is None:
        path = Path(__file__).parent.parent.parent / "validation_ladder.json"
    
    data = {
        "base_seed": BASE_SEED,
        "ratio": RATIO,
        "description": "Unbalanced semiprimes for cell-view emergence validation",
        "ladder": [asdict(g) for g in ladder]
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"Ladder exported to {path}")


if __name__ == "__main__":
    ladder = generate_ladder()
    print_ladder_summary(ladder)
    export_ladder_json(ladder=ladder)
