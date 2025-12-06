"""
Z5D Möbius Function Implementation
==================================

The Möbius function μ(n) is a number-theoretic function defined as:
- μ(1) = 1
- μ(n) = 0 if n has a squared prime factor
- μ(n) = (-1)^k if n is the product of k distinct primes

Uses a precomputed table for small n (1-15) to match the C implementation,
with fallback to trial division for larger values.

@file mobius.py
@version 1.0
"""

from typing import List

# Precomputed Möbius function values for k=1..15 matching C implementation
# Index 0 is unused (placeholder for n=0)
_MOBIUS_TABLE: List[int] = [
    0, 1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0, -1, 1, 1
]


def mobius(n: int) -> int:
    """
    Compute the Möbius function μ(n).

    The Möbius function is defined as:
    - μ(1) = 1
    - μ(n) = 0 if n has a squared prime factor
    - μ(n) = (-1)^k if n is the product of k distinct primes

    Parameters
    ----------
    n : int
        Positive integer input.

    Returns
    -------
    int
        The value μ(n) ∈ {-1, 0, 1}.

    Raises
    ------
    ValueError
        If n < 1.

    Examples
    --------
    >>> mobius(1)
    1
    >>> mobius(2)
    -1
    >>> mobius(4)
    0
    >>> mobius(6)
    1
    """
    if n < 1:
        raise ValueError(f"Möbius function requires n >= 1, got n = {n}")

    # Use precomputed table for n <= 15
    if n <= 15:
        return _MOBIUS_TABLE[n]

    # Fallback: trial division for n > 15
    if n == 1:
        return 1

    prime_factors = 0
    temp_n = n

    i = 2
    while i * i <= temp_n:
        if temp_n % i == 0:
            prime_factors += 1
            temp_n //= i
            if temp_n % i == 0:
                # n has a squared prime factor
                return 0
        i += 1

    if temp_n > 1:
        prime_factors += 1

    return -1 if (prime_factors % 2) else 1
