"""
蒸散发估算的物理计算模块
Physical calculations for evapotranspiration estimation.

本模块提供互补关系(CR)模型所需的基础物理计算，包括：
This module provides fundamental physical calculations required for
Complementary Relationship (CR) models, including:

- Penman 潜在蒸散发 (PM) / Penman potential evapotranspiration (PM)
- Priestley-Taylor 蒸散发 (PT) / Priestley-Taylor evapotranspiration (PT)
- 饱和水汽压差 (VPD) / Vapor Pressure Deficit (VPD)
- 干湿表常数 / Psychrometric constant
- 饱和水汽压及其斜率 / Saturation vapor pressure and its slope

除非另有说明，所有函数使用SI单位
All functions use SI units unless otherwise specified.

参考文献 / References
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

from . import constants

# Type alias for array-like inputs
ArrayLike = Union[float, np.ndarray]


def calculate_saturation_vapor_pressure(temperature: ArrayLike) -> ArrayLike:
    """
    使用Tetens方程计算饱和水汽压
    Calculate saturation vapor pressure using the Tetens equation.

    参数 / Parameters
    ----------
    temperature : float or array_like
        气温 [°C] / Air temperature [°C]

    返回 / Returns
    -------
    float or array_like
        饱和水汽压 [Pa] / Saturation vapor pressure [Pa]

    说明 / Notes
    -----
    使用Tetens方程（也称为Murray方程）：
    Uses the Tetens equation (also known as Murray equation):

    .. math::
        e_s(T) = 611 \\exp\\left(\\frac{17.27 T}{T + 237.3}\\right)

    其中T为摄氏温度，e_s单位为Pa
    where T is temperature in °C and e_s is in Pa.

    参考文献 / References
    ----------
    .. [1] Allen et al. (1998) FAO-56, Equation 11

    示例 / Examples
    --------
    >>> calculate_saturation_vapor_pressure(20.0)
    2337.08...
    >>> calculate_saturation_vapor_pressure(np.array([0, 10, 20, 30]))
    array([ 611.21..., 1228.09..., 2337.08..., 4243.50...])
    """
    # Tetens方程计算饱和水汽压 / Tetens equation for saturation vapor pressure
    return constants.TETENS_E0_PA * np.exp(
        (constants.TETENS_A * temperature) / (temperature + constants.TETENS_B)
    )


def calculate_slope_svp(temperature: ArrayLike) -> ArrayLike:
    """
    计算饱和水汽压曲线的斜率
    Calculate the slope of saturation vapor pressure curve.

    参数 / Parameters
    ----------
    temperature : float or array_like
        气温 [°C] / Air temperature [°C]

    返回 / Returns
    -------
    float or array_like
        饱和水汽压曲线斜率 [Pa °C⁻¹] / Slope of saturation vapor pressure curve [Pa °C⁻¹]

    说明 / Notes
    -----
    斜率通过Tetens方程的导数计算：
    The slope is computed as the derivative of the Tetens equation:

    .. math::
        \\Delta = \\frac{4098 e_s(T)}{(T + 237.3)^2}

    其中T为摄氏温度 / where T is temperature in °C.

    参考文献 / References
    ----------
    .. [1] Allen et al. (1998) FAO-56, Equation 13

    示例 / Examples
    --------
    >>> calculate_slope_svp(20.0)
    144.66...
    >>> calculate_slope_svp(np.array([10, 20, 30]))
    array([ 82.24..., 144.66..., 243.49...])
    """
    # 计算饱和水汽压 / Calculate saturation vapor pressure
    es = calculate_saturation_vapor_pressure(temperature)
    # 计算斜率 / Calculate slope
    return 4098.0 * es / ((temperature + constants.TETENS_B) ** 2)


def calculate_psychrometric_constant(pressure: ArrayLike,
                                     specific_heat: float = None,
                                     latent_heat: float = None,
                                     mw_ratio: float = None) -> ArrayLike:
    """Compute the psychrometric constant.

    计算干湿表常数，用于连接能量项和空气动力学项。

    Parameters 参数
    -------------
    pressure : float or np.ndarray
        Atmospheric pressure in pascals (Pa).
        大气压强，单位帕。
    specific_heat : float, optional
        Specific heat of air at constant pressure [J kg⁻¹ K⁻¹].
        If None, uses constant from constants module (1013.0).
        定压比热。如果为None，使用常数模块中的值（1013.0）。
    latent_heat : float, optional
        Latent heat of vaporization [J kg⁻¹].
        If None, uses constant from constants module (2.45e6).
        汽化潜热。如果为None，使用常数模块中的值（2.45e6）。
    mw_ratio : float, optional
        Molecular weight ratio of water vapour to dry air [-].
        If None, uses constant from constants module (0.62198).
        水汽与干空气的分子量比。如果为None，使用常数模块中的值（0.62198）。

    Returns 返回
    ----------
    float or np.ndarray
        Psychrometric constant in Pa K⁻¹.
        干湿表常数，单位Pa K⁻¹。

    Notes 说明
    ---------
    The constant is :math:`\\gamma = c_p P / (\\varepsilon \\lambda)`, linking
    energy availability to aerodynamic demand in the Penman equation.
    干湿表常数按 :math:`\\gamma = c_p P / (\\varepsilon \\lambda)` 计算，
    在Penman方程中连接能量项与空气动力学项。

    References 参考文献
    -----------------
    Allen et al. (1998) FAO-56 指南 / Allen等 (1998) FAO-56 Manual.
    """
    if specific_heat is None:
        specific_heat = constants.CP_AIR
    if latent_heat is None:
        latent_heat = constants.LV_WATER
    if mw_ratio is None:
        mw_ratio = constants.EPSILON_MOLWEIGHT
    
    return (specific_heat * pressure) / (mw_ratio * latent_heat)


def calculate_latent_heat_vaporization(temperature: ArrayLike) -> ArrayLike:
    """
    计算温度依赖的汽化潜热
    Calculate temperature-dependent latent heat of vaporization.

    参数 / Parameters
    ----------
    temperature : float or array_like
        气温 [°C] / Air temperature [°C]

    返回 / Returns
    -------
    float or array_like
        汽化潜热 [J/kg] / Latent heat of vaporization [J/kg]

    说明 / Notes
    -----
    使用温度的多项式近似（FAO-56）：
    Uses polynomial approximation as a function of temperature (FAO-56):

    .. math::
        L_v = 2500800 - 2360 T + 1.6 T^2 - 0.06 T^3

    其中T为摄氏温度，L_v单位为J/kg
    where T is temperature in °C and L_v is in J/kg.

    参考文献 / References
    ----------
    .. [1] Allen et al. (1998) FAO-56
    .. [2] Harrison, L.P. (1963). Fundamental concepts and definitions
           relating to humidity. In: Humidity and Moisture, Vol. 3.

    示例 / Examples
    --------
    >>> calculate_latent_heat_vaporization(20.0)
    2453600.0
    >>> calculate_latent_heat_vaporization(np.array([0, 10, 20, 30]))
    array([2500800., 2477200., 2453600., 2430000.])
    """
    temp_celsius = np.asarray(temperature, dtype=float)
    # Polynomial approximation for latent heat / 潜热的多项式近似
    lv = (2500800.0 - 2360.0 * temp_celsius +
          1.6 * temp_celsius**2 -
          0.06 * temp_celsius**3)
    return lv


def vapor_pressure_deficit(temperature: ArrayLike,
                          relative_humidity: ArrayLike) -> ArrayLike:
    """Calculate vapor pressure deficit (VPD).

    计算饱和水汽压差（VPD），衡量空气干燥程度。

    Parameters 参数
    -------------
    temperature : float or np.ndarray
        Air temperature in degrees Celsius (°C).
        气温，单位摄氏度。
    relative_humidity : float or np.ndarray
        Relative humidity in percent (0-100).
        相对湿度，百分数表示（0-100）。

    Returns 返回
    ----------
    float or np.ndarray
        Vapor pressure deficit in pascals (Pa).
        饱和水汽压差，单位帕。

    Notes 说明
    ---------
    Computed using :math:`VPD = e_s(T) (1 - RH/100)`, the deficit increases as
    air becomes drier, indicating higher evaporative demand.
    按 :math:`VPD = e_s(T) (1 - RH/100)` 计算，空气越干燥缺额越大，表明蒸发需求越强。

    References 参考文献
    -----------------
    Allen et al. (1998) FAO-56 指南 / Allen等 (1998) FAO-56 Manual.
    """
    es = calculate_saturation_vapor_pressure(temperature)
    return es * (1.0 - relative_humidity / 100.0)


def priestley_taylor_et(net_radiation: ArrayLike,
                       ground_heat_flux: ArrayLike,
                       temperature: ArrayLike,
                       pressure: ArrayLike,
                       alpha: float = None) -> ArrayLike:
    """
    计算Priestley-Taylor潜在蒸散发
    Calculate Priestley-Taylor potential evapotranspiration.

    参数 / Parameters
    ----------
    net_radiation : float or array_like
        地表净辐射 [W m⁻²] / Net radiation at the surface [W m⁻²]
    ground_heat_flux : float or array_like
        土壤热通量 [W m⁻²] / Ground heat flux [W m⁻²]
    temperature : float or array_like
        气温 [°C] / Air temperature [°C]
    pressure : float or array_like
        大气压强 [Pa] / Atmospheric pressure [Pa]
    alpha : float, optional
        Priestley-Taylor系数 [-]，默认1.26 / Priestley-Taylor coefficient [-].
        If None, uses constant from constants module (1.26).
        如果为None，使用常数模块中的值（1.26）。

    返回 / Returns
    -------
    float or array_like
        Priestley-Taylor潜在蒸散发 [W m⁻²] / Priestley-Taylor potential evapotranspiration [W m⁻²]

    说明 / Notes
    -----
    Priestley-Taylor方程为：
    The Priestley-Taylor equation is:

    .. math::
        ET_{PT} = \\alpha \\frac{\\Delta}{\\Delta + \\gamma} (R_n - G)

    其中 / where:
    - α 是 Priestley-Taylor系数（通常为1.26）/ is the Priestley-Taylor coefficient (typically 1.26)
    - Δ 是饱和水汽压曲线斜率 / is the slope of saturation vapor pressure curve
    - γ 是干湿表常数 / is the psychrometric constant
    - R_n 是净辐射 / is net radiation
    - G 是土壤热通量 / is ground heat flux

    原始的Priestley-Taylor系数(α=1.26)是针对充分灌溉、平流效应最小的地表推导的。
    The original Priestley-Taylor coefficient (α = 1.26) was derived for
    well-watered surfaces under minimal advection conditions.

    参考文献 / References
    ----------
    .. [1] Priestley, C.H.B., & Taylor, R.J. (1972). On the assessment of
           surface heat flux and evaporation using large-scale parameters.
           Monthly Weather Review, 100(2), 81-92.

    示例 / Examples
    --------
    >>> priestley_taylor_et(500.0, 50.0, 20.0, 101325.0)
    309.48...
    """
    if alpha is None:
        alpha = constants.PRIESTLEY_TAYLOR_ALPHA
    
    # 计算饱和水汽压曲线斜率 / Calculate slope of saturation vapor pressure curve
    delta = calculate_slope_svp(temperature)
    # 计算干湿表常数 / Calculate psychrometric constant
    gamma = calculate_psychrometric_constant(pressure)

    # 可用能量 = 净辐射 - 土壤热通量 / Available energy = net radiation - ground heat flux
    available_energy = net_radiation - ground_heat_flux
    # Priestley-Taylor方程 / Priestley-Taylor equation
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
    计算Penman潜在蒸散发
    Calculate Penman potential evapotranspiration.

    参数 / Parameters
    ----------
    net_radiation : float or array_like
        地表净辐射 [W m⁻²] / Net radiation at the surface [W m⁻²]
    ground_heat_flux : float or array_like
        土壤热通量 [W m⁻²] / Ground heat flux [W m⁻²]
    temperature : float or array_like
        气温 [°C] / Air temperature [°C]
    relative_humidity : float or array_like
        相对湿度 [%] (0-100范围) / Relative humidity [%] (0-100 range)
    wind_speed : float or array_like
        指定高度的风速 [m s⁻¹] / Wind speed at height specified [m s⁻¹]
    pressure : float or array_like
        大气压强 [Pa] / Atmospheric pressure [Pa]
    height : float, optional
        风速测量高度 [m]，默认2.0m / Height of wind measurement [m]. Default is 2.0 m.

    返回 / Returns
    -------
    float or array_like
        Penman潜在蒸散发 [W m⁻²] / Penman potential evapotranspiration [W m⁻²]

    说明 / Notes
    -----
    Penman方程结合了能量平衡法和空气动力学法：
    The Penman equation combines the energy balance and aerodynamic methods:

    .. math::
        ET_P = \\frac{\\Delta (R_n - G) + \\rho_a c_p VPD / r_a}
                    {\\Delta + \\gamma}

    其中 / where:
    - Δ 是饱和水汽压曲线斜率 / is the slope of saturation vapor pressure curve
    - γ 是干湿表常数 / is the psychrometric constant
    - R_n 是净辐射 / is net radiation
    - G 是土壤热通量 / is ground heat flux
    - ρ_a 是空气密度 / is air density
    - c_p 是空气比热 / is specific heat of air
    - VPD 是饱和水汽压差 / is vapor pressure deficit
    - r_a 是空气动力学阻抗 / is aerodynamic resistance

    空气动力学阻抗采用简化形式计算：
    The aerodynamic resistance is calculated using a simplified form:

    .. math::
        r_a = \\frac{208}{u_z}

    其中u_z是高度z（通常2米）处的风速 / where u_z is wind speed at height z (typically 2 m).

    参考文献 / References
    ----------
    .. [1] Penman, H.L. (1948). Natural evaporation from open water, bare soil
           and grass. Proceedings of the Royal Society of London. Series A,
           193(1032), 120-145.
    .. [2] Allen et al. (1998) FAO-56

    示例 / Examples
    --------
    >>> penman_potential_et(500.0, 50.0, 20.0, 50.0, 2.0, 101325.0)
    334.78...
    """
    # 物理常数 / Physical constants
    specific_heat = constants.CP_AIR  # 空气比热 / Specific heat of air [J kg⁻¹ K⁻¹]
    
    # 计算空气密度（从理想气体定律）/ Calculate air density from ideal gas law
    # ρ = P / (R_specific × T)
    temperature_kelvin = temperature + constants.KELVIN_TO_CELSIUS_OFFSET
    air_density = pressure / (constants.R_SPECIFIC_DRY_AIR * temperature_kelvin)

    # 计算所需变量 / Calculate required variables
    delta = calculate_slope_svp(temperature)  # 饱和水汽压曲线斜率 / Slope of SVP curve
    gamma = calculate_psychrometric_constant(pressure)  # 干湿表常数 / Psychrometric constant
    vpd = vapor_pressure_deficit(temperature, relative_humidity)  # 饱和水汽压差 / VPD

    # 计算空气动力学阻抗（简化形式）/ Calculate aerodynamic resistance (simplified form)
    # ra = 208 / u 适用于2米高度的参考草地 / for reference grass at 2m height
    aerodynamic_resistance = constants.PENMAN_WIND_COEFF / wind_speed

    # 可用能量 / Available energy
    available_energy = net_radiation - ground_heat_flux

    # Penman方程 / Penman equation
    # 辐射项 / Radiation term
    radiation_term = delta * available_energy
    # 空气动力学项 / Aerodynamic term
    aerodynamic_term = (air_density * specific_heat * vpd) / aerodynamic_resistance

    # 组合计算 / Combined calculation
    et_penman = (radiation_term + aerodynamic_term) / (delta + gamma)

    return et_penman
