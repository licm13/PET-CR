"""
PET-CR: Complementary Relationship Evapotranspiration Library

A Python library for estimating actual evapotranspiration (Ea) using 
Complementary Relationship (CR) theory.

This package provides:
- Core CR models (Sigmoid, Polynomial, Rescaled Power, Bouchet, A-A)
- Physical calculations (Penman, Priestley-Taylor, VPD)
- Standardized SI unit inputs
- Well-documented implementations with literature references

Authors: PET-CR Contributors
License: MIT
"""

__version__ = "0.1.0"

from .models import (
    sigmoid_cr,
    polynomial_cr,
    rescaled_power_cr,
    bouchet_cr,
    aa_cr
)

from .physics import (
    penman_potential_et,
    priestley_taylor_et,
    vapor_pressure_deficit,
    calculate_psychrometric_constant,
    calculate_saturation_vapor_pressure,
    calculate_slope_svp
)

__all__ = [
    # Models
    'sigmoid_cr',
    'polynomial_cr',
    'rescaled_power_cr',
    'bouchet_cr',
    'aa_cr',
    # Physics
    'penman_potential_et',
    'priestley_taylor_et',
    'vapor_pressure_deficit',
    'calculate_psychrometric_constant',
    'calculate_saturation_vapor_pressure',
    'calculate_slope_svp',
]
