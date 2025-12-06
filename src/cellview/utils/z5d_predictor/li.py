"""
Z5D Logarithmic Integral Implementation
========================================

Compute the logarithmic integral li(x) using high-precision mpmath arithmetic.

The logarithmic integral is defined as:
    li(x) = integral from 0 to x of dt/ln(t)

For x > 1, we use the series expansion:
    li(x) ≈ ln(ln(x)) + γ + sum_{k=1..∞} (ln x)^k / (k * k!)

where γ is the Euler-Mascheroni constant.

This implementation matches the algorithm in z5d_math.c.

@file li.py
@version 1.0
"""

from mpmath import mp, mpf, log, euler


def li(x: mpf, max_terms: int = 100, tolerance: mpf = None) -> mpf:
    """
    Compute the logarithmic integral li(x) using series expansion.

    Uses the Ramanujan series representation:
        li(x) = ln(ln(x)) + γ + sum_{k=1..N} (ln x)^k / (k * k!)

    Parameters
    ----------
    x : mpf
        Input value, must be > 1.
    max_terms : int, optional
        Maximum number of series terms to compute. Default is 100.
    tolerance : mpf, optional
        Convergence tolerance. Default is 10^(-mp.dps + 5).

    Returns
    -------
    mpf
        The value li(x).

    Raises
    ------
    ValueError
        If x <= 1 (logarithm of logarithm is undefined or complex).

    Notes
    -----
    The series converges rapidly for typical inputs. The implementation
    uses mpmath for arbitrary precision arithmetic matching the MPFR
    precision used in the C version.

    Examples
    --------
    >>> mp.dps = 50
    >>> li(mpf(10))  # doctest: +ELLIPSIS
    mpf('6.165599...')
    """
    if x <= 1:
        raise ValueError(f"li(x) requires x > 1, got x = {x}")

    if tolerance is None:
        tolerance = mpf(10) ** (-(mp.dps - 5))

    # ln(x)
    ln_x = log(x)

    # ln(ln(x))
    ln_ln_x = log(ln_x)

    # Euler-Mascheroni constant γ
    gamma_const = euler

    # Start with ln(ln(x)) + γ
    result = ln_ln_x + gamma_const

    # Add series: sum_{k=1..N} (ln x)^k / (k * k!)
    factorial = mpf(1)
    power = ln_x

    for k in range(1, max_terms + 1):
        # power = (ln x)^k
        if k > 1:
            power *= ln_x

        # factorial = k!
        if k > 1:
            factorial *= k

        # term = (ln x)^k / (k * k!)
        term = power / (k * factorial)

        # sum += term
        result += term

        # Check convergence
        if abs(term) < tolerance:
            break

    return result
