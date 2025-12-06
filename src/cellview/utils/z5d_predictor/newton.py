"""
Z5D Newton Solver Implementation
=================================

Perform Newton iteration steps to solve R(x) = n for x.

Newton's method:
    x_{n+1} = x_n - f(x_n)/f'(x_n)

where f(x) = R(x) - n.

This module implements a single Newton step, which is called iteratively
by the main predictor until convergence.

@file newton.py
@version 1.0
"""

from mpmath import mpf

from .riemannR import riemann_R, riemann_R_prime


def newton_step(x: mpf, n: mpf, K: int = 10) -> mpf:
    """
    Perform one Newton iteration step to solve R(x) = n.

    Uses Newton's method:
        x_{new} = x - f(x)/f'(x)

    where f(x) = R(x) - n.

    Parameters
    ----------
    x : mpf
        Current estimate of x.
    n : mpf
        Target value (prime index).
    K : int, optional
        Number of terms in R(x) series. Default is 10.

    Returns
    -------
    mpf
        The new estimate x_{new}.

    Raises
    ------
    ValueError
        If x <= 1, n < 1, K < 1, or if the derivative R'(x) is zero.

    Notes
    -----
    The Newton step typically converges very quickly (3-5 iterations)
    when starting from a good initial estimate like the Dusart initializer.

    Examples
    --------
    >>> from mpmath import mp
    >>> mp.dps = 50
    >>> x = mpf(15485000)  # Initial guess for the 10^6-th prime
    >>> n = mpf(1000000)
    >>> x_new = newton_step(x, n)
    """
    if x <= 1:
        raise ValueError(f"newton_step requires x > 1, got x = {x}")
    if n < 1:
        raise ValueError(f"newton_step requires n >= 1, got n = {n}")
    if K < 1:
        raise ValueError(f"newton_step requires K >= 1, got K = {K}")

    # Compute R(x)
    R_x = riemann_R(x, K)

    # Compute f(x) = R(x) - n
    f_x = R_x - n

    # Compute R'(x)
    R_prime_x = riemann_R_prime(x, K)

    # Check for zero derivative (would cause division by zero)
    if R_prime_x == 0:
        raise ValueError(
            f"Newton step failed: derivative R'(x) is zero at x = {x}"
        )

    # delta = f(x) / f'(x)
    delta = f_x / R_prime_x

    # x_{new} = x - delta
    return x - delta
