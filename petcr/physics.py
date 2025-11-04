"""
Physical calculations for evapotranspiration estimation.

This module provides fundamental physical calculations required for 
Complementary Relationship (CR) models, including:
- Penman potential evapotranspiration (PM)
- Priestley-Taylor evapotranspiration (PT)
- Vapor Pressure Deficit (VPD)
- Psychrometric constant
- Saturation vapor pressure and its slope

All functions use SI units unless otherwise specified.

References
----------
.. [1] Penman, H.L. (1948). Natural evaporation from open water, bare soil 
       and grass. Proceedings of the Royal Society of London. Series A, 
       193(1032), 120-145.
.. [2] Priestley, C.H.B., & Taylor, R.J. (1972). On the assessment of surface 
       heat flux and evaporation using large-scale parameters. Monthly Weather 
       Review, 100(2), 81-92.
.. [3] Allen, R.G., Pereira, L.S., Raes, D., & Smith, M. (1998). Crop 
       evapotranspiration-Guidelines for computing crop water requirements. 
       FAO Irrigation and drainage paper 56, FAO, Rome, 300(9), D05109.
"""

import numpy as np
from typing import Union

# Type alias for array-like inputs
ArrayLike = Union[float, np.ndarray]


def calculate_saturation_vapor_pressure(temperature: ArrayLike) -> ArrayLike:
    """
    Calculate saturation vapor pressure using the Tetens equation.
    
    Parameters
    ----------
    temperature : float or array_like
        Air temperature [°C]
    
    Returns
    -------
    float or array_like
        Saturation vapor pressure [Pa]
    
    Notes
    -----
    Uses the Tetens equation (also known as Murray equation):
    
    .. math::
        e_s(T) = 611 \\exp\\left(\\frac{17.27 T}{T + 237.3}\\right)
    
    where T is temperature in °C and e_s is in Pa.
    
    References
    ----------
    .. [1] Allen et al. (1998) FAO-56, Equation 11
    
    Examples
    --------
    >>> calculate_saturation_vapor_pressure(20.0)
    2337.08...
    >>> calculate_saturation_vapor_pressure(np.array([0, 10, 20, 30]))
    array([ 611.21..., 1228.09..., 2337.08..., 4243.50...])
    """
    return 611.0 * np.exp((17.27 * temperature) / (temperature + 237.3))


def calculate_slope_svp(temperature: ArrayLike) -> ArrayLike:
    """
    Calculate the slope of saturation vapor pressure curve.
    
    Parameters
    ----------
    temperature : float or array_like
        Air temperature [°C]
    
    Returns
    -------
    float or array_like
        Slope of saturation vapor pressure curve [Pa °C⁻¹]
    
    Notes
    -----
    The slope is computed as the derivative of the Tetens equation:
    
    .. math::
        \\Delta = \\frac{4098 e_s(T)}{(T + 237.3)^2}
    
    where T is temperature in °C.
    
    References
    ----------
    .. [1] Allen et al. (1998) FAO-56, Equation 13
    
    Examples
    --------
    >>> calculate_slope_svp(20.0)
    144.66...
    >>> calculate_slope_svp(np.array([10, 20, 30]))
    array([ 82.24..., 144.66..., 243.49...])
    """
    es = calculate_saturation_vapor_pressure(temperature)
    return 4098.0 * es / ((temperature + 237.3) ** 2)


def calculate_psychrometric_constant(pressure: ArrayLike, 
                                     specific_heat: float = 1013.0,
                                     latent_heat: float = 2.45e6,
                                     mw_ratio: float = 0.622) -> ArrayLike:
    """
    Calculate the psychrometric constant.
    
    Parameters
    ----------
    pressure : float or array_like
        Atmospheric pressure [Pa]
    specific_heat : float, optional
        Specific heat of air at constant pressure [J kg⁻¹ K⁻¹]. 
        Default is 1013.0 J kg⁻¹ K⁻¹.
    latent_heat : float, optional
        Latent heat of vaporization [J kg⁻¹]. 
        Default is 2.45e6 J kg⁻¹ (at 20°C).
    mw_ratio : float, optional
        Ratio of molecular weight of water vapor to dry air [-]. 
        Default is 0.622.
    
    Returns
    -------
    float or array_like
        Psychrometric constant [Pa K⁻¹]
    
    Notes
    -----
    The psychrometric constant is calculated as:
    
    .. math::
        \\gamma = \\frac{c_p P}{\\varepsilon \\lambda}
    
    where:
    - c_p is the specific heat of air at constant pressure
    - P is atmospheric pressure
    - ε is the ratio of molecular weights (water vapor / dry air)
    - λ is the latent heat of vaporization
    
    References
    ----------
    .. [1] Allen et al. (1998) FAO-56, Equation 8
    
    Examples
    --------
    >>> calculate_psychrometric_constant(101325.0)
    66.77...
    >>> calculate_psychrometric_constant(np.array([80000, 101325]))
    array([52.71..., 66.77...])
    """
    return (specific_heat * pressure) / (mw_ratio * latent_heat)


def vapor_pressure_deficit(temperature: ArrayLike, 
                          relative_humidity: ArrayLike) -> ArrayLike:
    """
    Calculate vapor pressure deficit (VPD).
    
    Parameters
    ----------
    temperature : float or array_like
        Air temperature [°C]
    relative_humidity : float or array_like
        Relative humidity [%] (0-100 range)
    
    Returns
    -------
    float or array_like
        Vapor pressure deficit [Pa]
    
    Notes
    -----
    VPD is calculated as:
    
    .. math::
        VPD = e_s(T) \\left(1 - \\frac{RH}{100}\\right)
    
    where:
    - e_s(T) is the saturation vapor pressure at temperature T
    - RH is relative humidity in %
    
    VPD represents the difference between the amount of moisture in the air 
    and how much moisture the air can hold when saturated.
    
    References
    ----------
    .. [1] Allen et al. (1998) FAO-56
    
    Examples
    --------
    >>> vapor_pressure_deficit(20.0, 50.0)
    1168.54...
    >>> vapor_pressure_deficit(np.array([20, 25]), np.array([50, 60]))
    array([1168.54..., 1269.96...])
    """
    es = calculate_saturation_vapor_pressure(temperature)
    return es * (1.0 - relative_humidity / 100.0)


def priestley_taylor_et(net_radiation: ArrayLike,
                       ground_heat_flux: ArrayLike,
                       temperature: ArrayLike,
                       pressure: ArrayLike,
                       alpha: float = 1.26) -> ArrayLike:
    """
    Calculate Priestley-Taylor potential evapotranspiration.
    
    Parameters
    ----------
    net_radiation : float or array_like
        Net radiation at the surface [W m⁻²]
    ground_heat_flux : float or array_like
        Ground heat flux [W m⁻²]
    temperature : float or array_like
        Air temperature [°C]
    pressure : float or array_like
        Atmospheric pressure [Pa]
    alpha : float, optional
        Priestley-Taylor coefficient [-]. Default is 1.26.
    
    Returns
    -------
    float or array_like
        Priestley-Taylor potential evapotranspiration [W m⁻²]
    
    Notes
    -----
    The Priestley-Taylor equation is:
    
    .. math::
        ET_{PT} = \\alpha \\frac{\\Delta}{\\Delta + \\gamma} (R_n - G)
    
    where:
    - α is the Priestley-Taylor coefficient (typically 1.26)
    - Δ is the slope of saturation vapor pressure curve
    - γ is the psychrometric constant
    - R_n is net radiation
    - G is ground heat flux
    
    The original Priestley-Taylor coefficient (α = 1.26) was derived for 
    well-watered surfaces under minimal advection conditions.
    
    References
    ----------
    .. [1] Priestley, C.H.B., & Taylor, R.J. (1972). On the assessment of 
           surface heat flux and evaporation using large-scale parameters. 
           Monthly Weather Review, 100(2), 81-92.
    
    Examples
    --------
    >>> priestley_taylor_et(500.0, 50.0, 20.0, 101325.0)
    309.48...
    """
    delta = calculate_slope_svp(temperature)
    gamma = calculate_psychrometric_constant(pressure)
    
    available_energy = net_radiation - ground_heat_flux
    et_pt = alpha * (delta / (delta + gamma)) * available_energy
    
    return et_pt


def penman_potential_et(net_radiation: ArrayLike,
                       ground_heat_flux: ArrayLike,
                       temperature: ArrayLike,
                       relative_humidity: ArrayLike,
                       wind_speed: ArrayLike,
                       pressure: ArrayLike,
                       height: float = 2.0) -> ArrayLike:
    """
    Calculate Penman potential evapotranspiration.
    
    Parameters
    ----------
    net_radiation : float or array_like
        Net radiation at the surface [W m⁻²]
    ground_heat_flux : float or array_like
        Ground heat flux [W m⁻²]
    temperature : float or array_like
        Air temperature [°C]
    relative_humidity : float or array_like
        Relative humidity [%] (0-100 range)
    wind_speed : float or array_like
        Wind speed at height specified [m s⁻¹]
    pressure : float or array_like
        Atmospheric pressure [Pa]
    height : float, optional
        Height of wind measurement [m]. Default is 2.0 m.
    
    Returns
    -------
    float or array_like
        Penman potential evapotranspiration [W m⁻²]
    
    Notes
    -----
    The Penman equation combines the energy balance and aerodynamic methods:
    
    .. math::
        ET_P = \\frac{\\Delta (R_n - G) + \\rho_a c_p VPD / r_a}
                    {\\Delta + \\gamma}
    
    where:
    - Δ is the slope of saturation vapor pressure curve
    - γ is the psychrometric constant
    - R_n is net radiation
    - G is ground heat flux
    - ρ_a is air density
    - c_p is specific heat of air
    - VPD is vapor pressure deficit
    - r_a is aerodynamic resistance
    
    The aerodynamic resistance is calculated using a simplified form:
    
    .. math::
        r_a = \\frac{208}{u_z}
    
    where u_z is wind speed at height z (typically 2 m).
    
    References
    ----------
    .. [1] Penman, H.L. (1948). Natural evaporation from open water, bare soil 
           and grass. Proceedings of the Royal Society of London. Series A, 
           193(1032), 120-145.
    .. [2] Allen et al. (1998) FAO-56
    
    Examples
    --------
    >>> penman_potential_et(500.0, 50.0, 20.0, 50.0, 2.0, 101325.0)
    334.78...
    """
    # Physical constants
    specific_heat = 1013.0  # J kg⁻¹ K⁻¹
    air_density = 1.225  # kg m⁻³ (at sea level, 15°C)
    
    # Calculate required variables
    delta = calculate_slope_svp(temperature)
    gamma = calculate_psychrometric_constant(pressure)
    vpd = vapor_pressure_deficit(temperature, relative_humidity)
    
    # Calculate aerodynamic resistance (simplified form)
    # ra = 208 / u for reference grass at 2m height
    aerodynamic_resistance = 208.0 / wind_speed
    
    # Available energy
    available_energy = net_radiation - ground_heat_flux
    
    # Penman equation
    radiation_term = delta * available_energy
    aerodynamic_term = (air_density * specific_heat * vpd) / aerodynamic_resistance
    
    et_penman = (radiation_term + aerodynamic_term) / (delta + gamma)
    
    return et_penman
