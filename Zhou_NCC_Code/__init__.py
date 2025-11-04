"""
Land-Atmosphere Feedback in ET Projections
============================================

A Python package for analyzing land-atmosphere feedbacks in 
evapotranspiration projections using energy-based and aerodynamics-based
potential evapotranspiration estimators.

Author: Sha Zhou
Email: shazhou21@bnu.edu.cn
Institution: Beijing Normal University
Date: 2025

Based on the paper:
Zhou, S., & Yu, B. (2025). Neglecting land–atmosphere feedbacks overestimates 
climate-driven increases in evapotranspiration. Nature Climate Change.
"""

__version__ = "1.0.0"
__author__ = "Sha Zhou"
__email__ = "shazhou21@bnu.edu.cn"

# Import main functions
from .pet_estimation import (
    calculate_pet_land,
    batch_calculate_pet,
    calculate_wet_bowen_ratio,
    calculate_latent_heat_vaporization,
    calculate_saturation_vapor_pressure,
    calculate_actual_vapor_pressure
)

from .wet_dry_conditions import (
    calculate_pet_ocean,
    calculate_pet_sensitivity
)

from .et_attribution import (
    attribution_analysis,
    projection_1pctCO2,
    calculate_et_from_budyko,
    calibrate_budyko_parameter,
    budyko_et_ratio
)

from .data_generator import (
    generate_sample_data,
    generate_timeseries_data,
    load_fluxnet_data,
    load_cmip6_data
)

__all__ = [
    # PET estimation
    'calculate_pet_land',
    'batch_calculate_pet',
    'calculate_wet_bowen_ratio',
    'calculate_latent_heat_vaporization',
    'calculate_saturation_vapor_pressure',
    'calculate_actual_vapor_pressure',
    
    # Wet/dry conditions
    'calculate_pet_ocean',
    'calculate_pet_sensitivity',
    
    # Attribution analysis
    'attribution_analysis',
    'projection_1pctCO2',
    'calculate_et_from_budyko',
    'calibrate_budyko_parameter',
    'budyko_et_ratio',
    
    # Data generation and loading
    'generate_sample_data',
    'generate_timeseries_data',
    'load_fluxnet_data',
    'load_cmip6_data',
]
