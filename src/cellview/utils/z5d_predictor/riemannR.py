"""
Z5D Riemann R(x) Function Implementation
=========================================

Compute the Riemann prime-counting function R(x) and its derivative R'(x).

The Riemann R function is defined as:
    R(x) = sum_{k=1..∞} μ(k)/k * li(x^{1/k})

where μ(k) is the Möbius function and li is the logarithmic integral.

The derivative is:
    R'(x) = (1/ln x) * sum_{k=1..K} μ(k)/k * x^{1/k - 1}

These functions are fundamental to the Z5D predictor for solving R(x) = n.

@file riemannR.py
@version 1.0
"""

from mpmath import mpf, log, power

from .mobius import mobius
from .li import li


def riemann_R(x: mpf, K: int = 10) -> mpf:
    """
    Compute the Riemann R(x) prime-counting function.

    Uses the series expansion:
        R(x) = sum_{k=1..K} μ(k)/k * li(x^{1/k})

    Parameters
    ----------
    x : mpf
        Input value, must be > 1.
    K : int, optional
        Number of terms in the series. Default is 10 (matching C default).

    Returns
    -------
    mpf
        The value R(x).

    Raises
    ------
    ValueError
        If x <= 1 or K < 1.

    Notes
    -----
    The series converges rapidly since μ(k) = 0 for k with squared factors,
    and the terms decrease as x^{1/k} approaches 1 for larger k.

    Examples
    --------
    >>> from mpmath import mp
    >>> mp.dps = 50
    >>> R = riemann_R(mpf(1000000))
    >>> # R(x) approximates π(x), the prime counting function
    """
    if x <= 1:
        raise ValueError(f"riemann_R requires x > 1, got x = {x}")
    if K < 1:
        raise ValueError(f"riemann_R requires K >= 1, got K = {K}")

    result = mpf(0)

    for k in range(1, K + 1):
        mu = mobius(k)
        if mu == 0:
            continue

        # x^(1/k)
        x_power = power(x, mpf(1) / k)

        # li(x^(1/k))
        li_val = li(x_power)

        # term = μ(k)/k * li(x^(1/k))
        term = mpf(mu) / k * li_val

        # sum += term
        result += term

    return result


def riemann_R_prime(x: mpf, K: int = 10) -> mpf:
    """
    Compute the derivative R'(x) of the Riemann R function.

    Uses the formula:
        R'(x) = (1/ln x) * sum_{k=1..K} μ(k)/k * x^{1/k - 1}

    This is derived by differentiating li(x^{1/k}) with respect to x.

    Parameters
    ----------
    x : mpf
        Input value, must be > 1.
    K : int, optional
        Number of terms in the series. Default is 10.

    Returns
    -------
    mpf
        The value R'(x).

    Raises
    ------
    ValueError
        If x <= 1 or K < 1.

    Notes
    -----
    The derivative is used in Newton's method to solve R(x) = n for x.

    Examples
    --------
    >>> from mpmath import mp
    >>> mp.dps = 50
    >>> R_prime = riemann_R_prime(mpf(1000000))
    """
    if x <= 1:
        raise ValueError(f"riemann_R_prime requires x > 1, got x = {x}")
    if K < 1:
        raise ValueError(f"riemann_R_prime requires K >= 1, got K = {K}")

    ln_x = log(x)

    result = mpf(0)

    for k in range(1, K + 1):
        mu = mobius(k)
        if mu == 0:
            continue

        # exponent = 1/k - 1
        exponent = mpf(1) / k - 1

        # x^(1/k - 1)
        x_power = power(x, exponent)

        # term = μ(k)/k * x^(1/k - 1)
        term = mpf(mu) / k * x_power

        # sum += term
        result += term

    # R'(x) = sum / ln(x)
    return result / ln_x
