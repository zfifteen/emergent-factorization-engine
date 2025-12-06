"""
Z5D nth-Prime Predictor
=======================

High-precision Python implementation of the Z5D nth-prime predictor using
mpmath for arbitrary precision arithmetic.

This module provides functions to predict the nth prime by solving R(x) = n,
where R(x) is the Riemann prime-counting function.

Components:
- mobius: Möbius function μ(n) with precomputed table
- li: Logarithmic integral li(x) using series expansion
- dusart: Dusart/Cipolla 3-term initializer for nth prime
- riemannR: Riemann R(x) function and its derivative R'(x)
- newton: Newton iteration solver for R(x) = n
- predictor: Main predictor with configuration and result tracking

Usage
-----
>>> from mpmath import mp
>>> mp.dps = 96  # Set precision
>>> from z5d_predictor import predict_nth_prime
>>> result = predict_nth_prime(1000000)
>>> int(result.predicted_prime)  # doctest: +SKIP
15485863

@package z5d_predictor
@version 1.0.0
"""

from .mobius import mobius
from .li import li
from .dusart import dusart_initializer
from .riemannR import riemann_R, riemann_R_prime
from .newton import newton_step
from .predictor import (
    Z5DConfig,
    Z5DResult,
    Z5D_PREDICTOR_VERSION,
    Z5D_DEFAULT_DPS,
    Z5D_DEFAULT_K,
    get_version,
    predict_nth_prime,
)

__version__ = Z5D_PREDICTOR_VERSION

__all__ = [
    # Core mathematical functions
    "mobius",
    "li",
    "dusart_initializer",
    "riemann_R",
    "riemann_R_prime",
    "newton_step",
    # Predictor
    "Z5DConfig",
    "Z5DResult",
    "predict_nth_prime",
    "get_version",
    # Constants
    "Z5D_PREDICTOR_VERSION",
    "Z5D_DEFAULT_DPS",
    "Z5D_DEFAULT_K",
]
