"""
Z5D nth-Prime Predictor Implementation
=======================================

High-precision Python implementation using mpmath to solve R(x) = n
and predict the nth prime.

This module provides configuration and result tracking, encapsulating
the complete Newton-Raphson iteration process.

Matches the algorithm and structure from the C implementation in
z5d_predictor.c.

@file predictor.py
@version 1.0
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from mpmath import mp, mpf

from .dusart import dusart_initializer
from .newton import newton_step


# Library version matching C implementation
Z5D_PREDICTOR_VERSION = "1.0.0"

# Default precision in decimal places (corresponds to ~96 decimal places / 320 bits)
Z5D_DEFAULT_DPS = 96

# Default number of terms in Riemann R series
Z5D_DEFAULT_K = 10


@dataclass
class Z5DConfig:
    """
    Configuration for the Z5D predictor.

    Attributes
    ----------
    dps : int
        Decimal places of precision for mpmath. Default is 96.
    K : int
        Number of terms in the Riemann R(x) series. Default is 10.
    max_iterations : int
        Maximum Newton-Raphson iterations. Default is 10.
    tolerance : mpf
        Convergence tolerance. Default is 1e-50.
    """

    dps: int = Z5D_DEFAULT_DPS
    K: int = Z5D_DEFAULT_K
    max_iterations: int = 10
    tolerance: mpf = field(default_factory=lambda: mpf("1e-50"))


@dataclass
class Z5DResult:
    """
    Result structure for nth prime prediction.

    Attributes
    ----------
    predicted_prime : mpf
        The predicted value of p_n.
    error : mpf
        Estimated error bound (last delta in Newton iteration).
    elapsed_ms : float
        Computation time in milliseconds.
    iterations : int
        Number of Newton-Raphson iterations performed.
    converged : bool
        True if the iteration converged within tolerance.
    """

    predicted_prime: mpf = field(default_factory=lambda: mpf(0))
    error: mpf = field(default_factory=lambda: mpf(0))
    elapsed_ms: float = 0.0
    iterations: int = 0
    converged: bool = False


def get_version() -> str:
    """
    Get the library version string.

    Returns
    -------
    str
        Version string in format "X.Y.Z".
    """
    return Z5D_PREDICTOR_VERSION


def predict_nth_prime(
    n: int, config: Optional[Z5DConfig] = None
) -> Z5DResult:
    """
    Predict the nth prime using the Z5D algorithm.

    Uses Newton-Raphson iteration to solve R(x) = n, where R(x) is the
    Riemann prime-counting function. Starting from the Dusart/Cipolla
    initializer, iterates until convergence or max_iterations is reached.

    Parameters
    ----------
    n : int
        The index of the prime to predict (n >= 1).
    config : Z5DConfig, optional
        Configuration for the predictor. If None, uses default configuration.

    Returns
    -------
    Z5DResult
        Result containing the predicted prime, error estimate, timing,
        iteration count, and convergence status.

    Raises
    ------
    ValueError
        If n < 1.

    Notes
    -----
    For n < ~10, the Riemann R(x) approximation may not be as accurate,
    but the predictor still provides reasonable estimates.

    The prediction is a continuous approximation; the actual nth prime
    is the nearest integer.

    Examples
    --------
    >>> from mpmath import mp
    >>> mp.dps = 96
    >>> result = predict_nth_prime(1000000)
    >>> int(result.predicted_prime)  # doctest: +SKIP
    15485863
    """
    if n < 1:
        raise ValueError(f"predict_nth_prime requires n >= 1, got n = {n}")

    # Use default config if not provided
    if config is None:
        config = Z5DConfig()

    # Set mpmath precision
    mp.dps = config.dps

    # Initialize result
    result = Z5DResult()

    # Start timing
    start_time = time.perf_counter()

    # Convert n to mpf
    n_mpf = mpf(n)

    # Compute Dusart initializer as starting point
    x_current = dusart_initializer(n_mpf)

    # Newton iteration
    x_next = x_current
    delta = mpf(0)

    for iteration in range(config.max_iterations):
        result.iterations = iteration + 1

        # Perform one Newton step
        x_next = newton_step(x_current, n_mpf, config.K)

        # Check convergence: |x_next - x_current| < tolerance
        delta = abs(x_next - x_current)

        if delta < config.tolerance:
            result.converged = True
            result.predicted_prime = x_next
            break

        # Update for next iteration
        x_current = x_next

    # If not converged in loop, still return last value
    if not result.converged:
        result.predicted_prime = x_next

    # Estimate error as last delta
    result.error = delta

    # Record elapsed time
    result.elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return result
