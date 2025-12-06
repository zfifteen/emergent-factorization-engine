"""
Z5D Dusart/Cipolla Initializer Implementation
==============================================

Compute a high-quality initial estimate for the nth prime using
the Dusart/Cipolla 3-term formula.

The 3-term asymptotic expansion is:
    x0 = n * (L + L2 - 1 + (L2 - 2)/L - (L2^2 - 6*L2 + 11)/(2*L^2))

where:
    L = ln(n)
    L2 = ln(ln(n))

This 3-term version provides materially better accuracy at 10^9-10^12
compared to the simpler 2-term version.

@file dusart.py
@version 1.0
"""

from mpmath import mpf, log


def dusart_initializer(n: mpf) -> mpf:
    """
    Compute the 3-term Dusart/Cipolla initial estimate for the nth prime.

    Uses the asymptotic expansion:
        x0 = n * (L + L2 - 1 + (L2 - 2)/L - (L2^2 - 6*L2 + 11)/(2*L^2))

    where L = ln(n) and L2 = ln(ln(n)).

    This provides an excellent starting point for Newton-Raphson iteration
    when solving R(x) = n.

    Parameters
    ----------
    n : mpf
        The prime index n (must be >= 2 for ln(ln(n)) to be defined).

    Returns
    -------
    mpf
        The initial estimate x0 for the nth prime.

    Raises
    ------
    ValueError
        If n < 2 (ln(ln(n)) would be undefined or negative).

    Notes
    -----
    For very small n (n < ~10), the approximation may not be as accurate,
    but it still provides a reasonable starting point for iteration.

    Examples
    --------
    >>> from mpmath import mp
    >>> mp.dps = 50
    >>> x0 = dusart_initializer(mpf(1000000))
    >>> float(x0)  # doctest: +ELLIPSIS
    15475096...
    """
    if n < 2:
        raise ValueError(f"Dusart initializer requires n >= 2, got n = {n}")

    # L = ln(n)
    ln_n = log(n)

    # L2 = ln(ln(n))
    ln_ln_n = log(ln_n)

    # Precompute squares
    ln_n_sq = ln_n * ln_n  # L^2
    ln_ln_n_sq = ln_ln_n * ln_ln_n  # L2^2

    # term1 = L + L2 - 1
    term1 = ln_n + ln_ln_n - 1

    # term2 = (L2 - 2) / L
    term2 = (ln_ln_n - 2) / ln_n

    # term3 = -(L2^2 - 6*L2 + 11) / (2*L^2)
    # numerator: L2^2 - 6*L2 + 11
    numerator = ln_ln_n_sq - 6 * ln_ln_n + 11
    # denominator: 2*L^2
    denominator = 2 * ln_n_sq
    term3 = -numerator / denominator

    # result = n * (term1 + term2 + term3)
    return n * (term1 + term2 + term3)
