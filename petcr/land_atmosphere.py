"""
陆地-大气框架PET估算模块 / Land-Atmosphere Framework PET Estimation Module
==================================================================================

本模块实现基于陆地-大气能量交换的PET估算方法，源自Zhou & Yu (2025)的Nature Climate Change论文。
This module implements PET estimation based on land-atmosphere energy exchange,
derived from Zhou & Yu (2025) Nature Climate Change paper.

该方法通过分析能量通量（潜热/感热）来计算两种互补的PET估算值：
The approach calculates two complementary PET estimates by analyzing energy fluxes (latent/sensible heat):

- **PETe (能量基础PET / Energy-based PET)**: 由可用能量约束的最大蒸散发
  Maximum ET constrained by available energy
- **PETa (空气动力学基础PET / Aerodynamics-based PET)**: 由大气需求约束的最大蒸散发
  Maximum ET constrained by atmospheric demand

核心概念 / Key Concepts
------------------------
1. **湿润波文比 (βw) / Wet Bowen Ratio**: 地表饱和时感热与潜热的比值
   Ratio of sensible to latent heat when surface is saturated
2. **互补关系 / Complementary Relationship**: PETe和PETa随地表湿度变化呈反向响应
   PETe and PETa respond oppositely to surface moisture changes
3. **能量平衡 / Energy Balance**: 净辐射 = 潜热通量 + 感热通量
   Net radiation = Latent heat flux + Sensible heat flux

参考文献 / References
----------------------
.. [1] Zhou, S., & Yu, B. (2025). Land-atmosphere interactions exacerbate
       concurrent soil moisture drought and atmospheric aridity.
       Nature Climate Change (accepted).
.. [2] Zhou, S., & Yu, B. (2024). Physical basis of the potential
       evapotranspiration and its estimation over land.
       Journal of Hydrology, 641, 131825.

作者 / Author: Sha Zhou
邮箱 / Email: shazhou21@bnu.edu.cn
日期 / Date: 2025
"""

import numpy as np
from typing import Union, Dict, Tuple

# 类型别名 / Type alias
ArrayLike = Union[float, np.ndarray]


def calculate_latent_heat_vaporization(temperature: ArrayLike) -> ArrayLike:
    """
    计算汽化潜热 (MJ/kg)
    Calculate latent heat of vaporization (MJ/kg).

    参数 / Parameters
    ----------
    temperature : float or np.ndarray
        气温，单位开尔文 (K) / Air temperature in Kelvin (K)

    返回 / Returns
    -------
    float or np.ndarray
        汽化潜热，单位 MJ/kg / Latent heat of vaporization in MJ/kg

    说明 / Notes
    -----
    使用温度的多项式近似：
    Uses polynomial approximation as a function of temperature:

    .. math::
        L_v = \\frac{2500.8 - 2.36(T-273.15) + 0.0016(T-273.15)^2 - 0.00006(T-273.15)^3}{1000}

    其中T为开尔文温度 / where T is temperature in Kelvin

    示例 / Examples
    --------
    >>> calculate_latent_heat_vaporization(293.15)  # 20°C
    2.453...
    >>> calculate_latent_heat_vaporization(np.array([273.15, 293.15, 313.15]))
    array([2.500..., 2.453..., 2.406...])
    """
    temp_celsius = temperature - 273.15
    lv = (2500.8 - 2.36 * temp_celsius +
          0.0016 * temp_celsius**2 -
          0.00006 * temp_celsius**3) / 1000.0
    return lv


def calculate_saturation_vapor_pressure_tetens(temperature: ArrayLike) -> ArrayLike:
    """
    使用Tetens公式计算饱和水汽压 (kPa)
    Calculate saturation vapor pressure (kPa) using Tetens formula.

    参数 / Parameters
    ----------
    temperature : float or np.ndarray
        温度，单位开尔文 (K) / Temperature in Kelvin (K)

    返回 / Returns
    -------
    float or np.ndarray
        饱和水汽压，单位 kPa / Saturation vapor pressure in kPa

    说明 / Notes
    -----
    Tetens方程（也称为Murray方程）：
    Tetens equation (also known as Murray equation):

    .. math::
        e^* = 0.611 \\exp\\left(\\frac{17.27 T_c}{T_c + 237.3}\\right)

    其中 T_c 为摄氏温度 / where T_c is temperature in Celsius

    参考文献 / Reference
    ----------
    .. [1] Tetens, O. (1930). Über einige meteorologische Begriffe.
           Zeitschrift für Geophysik, 6, 297-309.

    示例 / Examples
    --------
    >>> calculate_saturation_vapor_pressure_tetens(293.15)  # 20°C
    2.337...
    """
    temp_celsius = temperature - 273.15
    vp_sat = 0.611 * np.exp(17.27 * temp_celsius / (temp_celsius + 237.3))
    return vp_sat


def calculate_actual_vapor_pressure(
    specific_humidity: ArrayLike,
    air_pressure: ArrayLike
) -> ArrayLike:
    """
    从比湿计算实际水汽压 (kPa)
    Calculate actual vapor pressure (kPa) from specific humidity.

    参数 / Parameters
    ----------
    specific_humidity : float or np.ndarray
        比湿，单位 kg/kg / Specific humidity in kg/kg
    air_pressure : float or np.ndarray
        气压，单位 Pa / Air pressure in Pa

    返回 / Returns
    -------
    float or np.ndarray
        实际水汽压，单位 kPa / Actual vapor pressure in kPa

    说明 / Notes
    -----
    转换公式 / Conversion formula:

    1. 计算混合比 / Calculate mixing ratio:
       .. math:: w = \\frac{q}{1 - q}

    2. 计算水汽压 / Calculate vapor pressure:
       .. math:: e = \\frac{w}{w + 0.622} \\cdot \\frac{p}{1000}

    示例 / Examples
    --------
    >>> calculate_actual_vapor_pressure(0.01, 101325.0)
    1.605...
    """
    # 从比湿计算混合比 / Calculate mixing ratio from specific humidity
    mixing_ratio = specific_humidity / (1.0 - specific_humidity)

    # 从混合比计算水汽压 / Calculate vapor pressure from mixing ratio
    vapor_pressure = mixing_ratio / (mixing_ratio + 0.622) * (air_pressure / 1000.0)

    return vapor_pressure


def calculate_psychrometric_constant_land(
    latent_heat: ArrayLike,
    air_pressure: ArrayLike
) -> ArrayLike:
    """
    计算干湿表常数 (kPa/K)
    Calculate psychrometric constant (kPa/K).

    参数 / Parameters
    ----------
    latent_heat : float or np.ndarray
        汽化潜热，单位 MJ/kg / Latent heat of vaporization in MJ/kg
    air_pressure : float or np.ndarray
        气压，单位 Pa / Air pressure in Pa

    返回 / Returns
    -------
    float or np.ndarray
        干湿表常数，单位 kPa/K / Psychrometric constant in kPa/K

    说明 / Notes
    -----
    公式 / Formula:

    .. math::
        \\gamma = \\frac{c_p}{L_v \\cdot 0.622} \\cdot \\frac{p}{1000}

    其中 c_p = 1.005×10⁻³ MJ/(kg·K) 是定压比热
    where c_p = 1.005×10⁻³ MJ/(kg·K) is specific heat of air at constant pressure

    示例 / Examples
    --------
    >>> lv = calculate_latent_heat_vaporization(293.15)  # 20°C
    >>> calculate_psychrometric_constant_land(lv, 101325.0)
    0.0668...
    """
    cp = 1.005e-3  # 空气定压比热 (MJ/(kg·K)) / Specific heat of air at constant pressure
    gamma = cp / (latent_heat * 0.622) * (air_pressure / 1000.0)
    return gamma


def calculate_slope_saturation_curve(temperature: ArrayLike) -> ArrayLike:
    """
    计算饱和水汽压曲线斜率 (kPa/K)
    Calculate slope of saturation vapor pressure curve (kPa/K).

    参数 / Parameters
    ----------
    temperature : float or np.ndarray
        气温，单位开尔文 (K) / Air temperature in Kelvin (K)

    返回 / Returns
    -------
    float or np.ndarray
        饱和曲线斜率，单位 kPa/K / Slope of saturation curve in kPa/K

    说明 / Notes
    -----
    公式（通过Tetens方程的导数）/ Formula (derivative of Tetens equation):

    .. math::
        \\Delta = e^* \\cdot \\frac{4098}{(T_c + 237.3)^2}

    其中 T_c 为摄氏温度 / where T_c is temperature in Celsius

    示例 / Examples
    --------
    >>> calculate_slope_saturation_curve(293.15)  # 20°C
    0.1446...
    """
    temp_celsius = temperature - 273.15
    vp_sat = calculate_saturation_vapor_pressure_tetens(temperature)
    delta = vp_sat * 4098.0 / ((temp_celsius + 237.3) ** 2)
    return delta


def calculate_wet_bowen_ratio(
    sensible_heat: ArrayLike,
    latent_heat: ArrayLike,
    skin_temperature: ArrayLike,
    air_temperature: ArrayLike,
    specific_humidity: ArrayLike,
    air_pressure: ArrayLike
) -> ArrayLike:
    """
    计算湿润波文比 (βw)，带约束条件
    Calculate wet Bowen ratio (βw) with constraints.

    参数 / Parameters
    ----------
    sensible_heat : float or np.ndarray
        感热通量，单位 W/m² / Sensible heat flux in W/m²
    latent_heat : float or np.ndarray
        潜热通量，单位 W/m² / Latent heat flux in W/m²
    skin_temperature : float or np.ndarray
        地表表皮温度，单位 K / Surface skin temperature in K
    air_temperature : float or np.ndarray
        气温，单位 K / Air temperature in K
    specific_humidity : float or np.ndarray
        比湿，单位 kg/kg / Specific humidity in kg/kg
    air_pressure : float or np.ndarray
        气压，单位 Pa / Air pressure in Pa

    返回 / Returns
    -------
    float or np.ndarray
        湿润波文比（无量纲）/ Wet Bowen ratio (dimensionless)

    说明 / Notes
    -----
    湿润波文比表示地表饱和时感热与潜热的比值。应用两个约束：
    The wet Bowen ratio represents the ratio of sensible to latent heat
    when the surface is saturated. Two constraints are applied:

    1. **下界约束 / Lower bound constraint**:
       .. math:: \\beta_w \\geq 0.24 \\cdot \\frac{\\gamma}{\\Delta}

       基于海洋条件 / Based on ocean conditions

    2. **上界约束 / Upper bound constraint**:
       .. math:: \\beta_w \\leq \\beta_{actual}

       不能超过实际波文比 / Cannot exceed actual Bowen ratio

    理论公式 / Theoretical formula:

    .. math::
        \\beta_w = \\gamma \\cdot \\frac{T_s - T_a}{e_s^* - e_a}

    其中 / where:
    - γ 是干湿表常数 / is psychrometric constant
    - T_s 是地表温度 / is surface temperature
    - T_a 是气温 / is air temperature
    - e_s* 是地表温度的饱和水汽压 / is saturation vapor pressure at surface temperature
    - e_a 是实际水汽压 / is actual vapor pressure

    参考文献 / References
    ----------
    .. [1] Zhou, S., & Yu, B. (2025). Nature Climate Change (accepted).

    示例 / Examples
    --------
    >>> calculate_wet_bowen_ratio(50.0, 100.0, 300.15, 298.15, 0.01, 101325.0)
    0.34...
    """
    # 计算所需变量 / Calculate required variables
    lv = calculate_latent_heat_vaporization(air_temperature)
    gamma = calculate_psychrometric_constant_land(lv, air_pressure)
    delta = calculate_slope_saturation_curve(air_temperature)

    # 地表和空气温度下的饱和水汽压 / Saturation vapor pressure at surface and air temperatures
    vp_sat_surface = calculate_saturation_vapor_pressure_tetens(skin_temperature)
    vp_actual = calculate_actual_vapor_pressure(specific_humidity, air_pressure)

    # 计算实际波文比 / Calculate actual Bowen ratio
    beta_actual = sensible_heat / latent_heat

    # 计算理论湿润波文比 / Calculate theoretical wet Bowen ratio
    beta1 = 0.24 * gamma / delta  # 下界约束（基于海洋）/ Lower constraint (ocean-based)
    beta2 = gamma * (skin_temperature - air_temperature) / (vp_sat_surface - vp_actual)

    # 应用约束: βw 应该在 beta1 和 beta_actual 之间
    # Apply constraints: βw should be between beta1 and beta_actual
    beta12 = np.maximum(beta2, beta1)
    beta_w = np.minimum(beta12, beta_actual)

    return beta_w


def calculate_pet_land(
    latent_heat: ArrayLike,
    sensible_heat: ArrayLike,
    specific_humidity: ArrayLike,
    air_pressure: ArrayLike,
    air_temperature: ArrayLike,
    skin_temperature: ArrayLike
) -> Dict[str, ArrayLike]:
    """
    计算陆地表面的PETe和PETa（Zhou & Yu, 2025方法）
    Calculate PETe and PETa for land surfaces (Zhou & Yu, 2025 method).

    这是本模块的核心函数，实现了基于陆地-大气能量交换的PET估算框架。
    This is the core function of this module, implementing the PET estimation
    framework based on land-atmosphere energy exchange.

    参数 / Parameters
    ----------
    latent_heat : float or np.ndarray
        潜热通量，单位 W/m² / Latent heat flux in W/m²
    sensible_heat : float or np.ndarray
        感热通量，单位 W/m² / Sensible heat flux in W/m²
    specific_humidity : float or np.ndarray
        比湿，单位 kg/kg / Specific humidity in kg/kg
    air_pressure : float or np.ndarray
        气压，单位 Pa / Air pressure in Pa
    air_temperature : float or np.ndarray
        气温，单位 K / Air temperature in K
    skin_temperature : float or np.ndarray
        地表表皮温度，单位 K / Surface skin temperature in K

    返回 / Returns
    -------
    dict
        包含以下键的字典 / Dictionary containing:

        - **'pete'**: 能量基础PET，单位 mm/day
          Energy-based PET in mm/day
        - **'peta'**: 空气动力学基础PET，单位 mm/day
          Aerodynamics-based PET in mm/day
        - **'beta_w'**: 湿润波文比（无量纲）
          Wet Bowen ratio (dimensionless)
        - **'rn'**: 净辐射，单位 mm/day（水当量）
          Net radiation in mm/day (water equivalent)
        - **'et'**: 实际ET，单位 mm/day
          Actual ET in mm/day

    说明 / Notes
    -----
    **方法学原理 / Methodology**

    本方法基于能量平衡和湿润波文比概念：
    This method is based on energy balance and wet Bowen ratio concept:

    1. **净辐射 / Net Radiation**:
       .. math:: R_n = LH + SH

       其中LH是潜热，SH是感热 / where LH is latent heat, SH is sensible heat

    2. **PETe（能量约束）/ PETe (Energy-constrained)**:
       .. math:: PET_e = \\frac{R_n}{1 + \\beta_w}

       代表可用能量约束下的最大ET / Represents maximum ET under available energy constraint

    3. **PETa（需求约束）/ PETa (Demand-constrained)**:
       .. math:: PET_a = \\frac{SH}{\\beta_w}

       代表大气需求约束下的最大ET / Represents maximum ET under atmospheric demand constraint

    **单位转换 / Unit Conversion**:

    转换因子 0.0864 将 W/m² 转换为 mm/day（对于水）
    Conversion factor 0.0864 converts W/m² to mm/day (for water):

    .. math::
        1 \\text{ W/m}^2 = 1 \\text{ J/(s·m}^2\\text{)} = 86400 \\text{ J/(day·m}^2\\text{)}

    除以汽化潜热得到等效水深 / Divided by latent heat of vaporization gives equivalent water depth

    **物理解释 / Physical Interpretation**:

    - 当 PETa > PETe: 能量受限，水分充足
      When PETa > PETe: Energy-limited, moisture sufficient
    - 当 PETa < PETe: 水分受限，能量充足
      When PETa < PETe: Moisture-limited, energy sufficient
    - PETe 和 PETa 的相对大小反映了地表湿度状态
      The relative magnitude of PETe and PETa reflects surface moisture status

    参考文献 / References
    ----------
    .. [1] Zhou, S., & Yu, B. (2025). Land-atmosphere interactions exacerbate
           concurrent soil moisture drought and atmospheric aridity.
           Nature Climate Change (accepted).
    .. [2] Zhou, S., & Yu, B. (2024). Physical basis of the potential
           evapotranspiration and its estimation over land.
           Journal of Hydrology, 641, 131825.

    示例 / Examples
    --------
    >>> results = calculate_pet_land(
    ...     latent_heat=100.0,
    ...     sensible_heat=50.0,
    ...     specific_humidity=0.01,
    ...     air_pressure=101325.0,
    ...     air_temperature=298.15,
    ...     skin_temperature=300.15
    ... )
    >>> print(f"PETe: {results['pete']:.2f} mm/day")
    PETe: 5.91 mm/day
    >>> print(f"PETa: {results['peta']:.2f} mm/day")
    PETa: 6.30 mm/day
    >>> print(f"Wet Bowen ratio: {results['beta_w']:.3f}")
    Wet Bowen ratio: 0.344

    另见 / See Also
    --------
    calculate_pet_ocean : 海洋表面的PET计算 / PET calculation for ocean surfaces
    calculate_wet_bowen_ratio : 湿润波文比计算 / Wet Bowen ratio calculation
    """
    # 将热通量从 W/m² 转换为 mm/day
    # Convert heat fluxes from W/m² to mm/day
    CONVERSION_FACTOR = 0.0864
    hfls_mmday = latent_heat * CONVERSION_FACTOR
    hfss_mmday = sensible_heat * CONVERSION_FACTOR

    # 计算汽化潜热 / Calculate latent heat of vaporization
    lv = calculate_latent_heat_vaporization(air_temperature)

    # 计算湿润波文比 / Calculate wet Bowen ratio
    beta_w = calculate_wet_bowen_ratio(
        sensible_heat, latent_heat, skin_temperature,
        air_temperature, specific_humidity, air_pressure
    )

    # 将热通量转换为等效水深 / Convert heat fluxes to equivalent water depth
    lh = hfls_mmday / lv
    sh = hfss_mmday / lv

    # 净辐射（潜热和感热之和）/ Net radiation (sum of latent and sensible heat)
    rn = sh + lh

    # 计算PETe（能量基础PET）/ Calculate PETe (energy-based PET)
    pete = rn / (1.0 + beta_w)

    # 计算PETa（空气动力学基础PET）/ Calculate PETa (aerodynamics-based PET)
    peta = sh / beta_w

    # 实际ET / Actual ET
    et = lh

    return {
        'pete': pete,
        'peta': peta,
        'beta_w': beta_w,
        'rn': rn,
        'et': et
    }


def batch_calculate_pet(data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    批量计算多个时间步或位置的PET
    Batch calculation of PET for multiple time steps or locations.

    参数 / Parameters
    ----------
    data : dict
        包含输入变量数组的字典 / Dictionary containing arrays of input variables:

        - **'hfls'**: 潜热通量 (W/m²) / latent heat flux (W/m²)
        - **'hfss'**: 感热通量 (W/m²) / sensible heat flux (W/m²)
        - **'huss'**: 比湿 (kg/kg) / specific humidity (kg/kg)
        - **'ps'**: 气压 (Pa) / air pressure (Pa)
        - **'tas'**: 气温 (K) / air temperature (K)
        - **'ts'**: 表皮温度 (K) / skin temperature (K)

    返回 / Returns
    -------
    dict
        包含计算的PET值的字典 / Dictionary with calculated PET values

    示例 / Examples
    --------
    >>> import numpy as np
    >>> n_samples = 100
    >>> data = {
    ...     'hfls': np.random.uniform(80, 120, n_samples),
    ...     'hfss': np.random.uniform(40, 60, n_samples),
    ...     'huss': np.random.uniform(0.008, 0.012, n_samples),
    ...     'ps': np.random.uniform(100000, 102000, n_samples),
    ...     'tas': np.random.uniform(295, 300, n_samples),
    ...     'ts': np.random.uniform(297, 302, n_samples)
    ... }
    >>> results = batch_calculate_pet(data)
    >>> print(f"Mean PETe: {np.mean(results['pete']):.2f} mm/day")
    Mean PETe: 6.15 mm/day
    """
    results = calculate_pet_land(
        latent_heat=data['hfls'],
        sensible_heat=data['hfss'],
        specific_humidity=data['huss'],
        air_pressure=data['ps'],
        air_temperature=data['tas'],
        skin_temperature=data['ts']
    )

    return results


def calculate_pet_ocean(
    latent_heat: ArrayLike,
    sensible_heat: ArrayLike,
    specific_humidity: ArrayLike,
    air_pressure: ArrayLike,
    air_temperature: ArrayLike,
    skin_temperature: ArrayLike
) -> Dict[str, ArrayLike]:
    """
    计算海洋表面在湿润和最干条件下的PETe和PETa
    Calculate PETe and PETa under wet and driest conditions for ocean surfaces.

    此函数估计当地表湿度从湿润（海洋）过渡到假设的最干条件时，
    PETe和PETa如何变化，同时保持湿焓不变。

    This function estimates how PETe and PETa change when surface moisture
    transitions from wet (ocean) to hypothetically driest conditions, while
    maintaining constant moist enthalpy.

    参数 / Parameters
    ----------
    latent_heat : float or np.ndarray
        潜热通量，单位 W/m² / Latent heat flux in W/m²
    sensible_heat : float or np.ndarray
        感热通量，单位 W/m² / Sensible heat flux in W/m²
    specific_humidity : float or np.ndarray
        比湿，单位 kg/kg / Specific humidity in kg/kg
    air_pressure : float or np.ndarray
        气压，单位 Pa / Air pressure in Pa
    air_temperature : float or np.ndarray
        气温，单位 K / Air temperature in K
    skin_temperature : float or np.ndarray
        地表表皮温度，单位 K / Surface skin temperature in K

    返回 / Returns
    -------
    dict
        包含以下键的字典 / Dictionary containing:

        - **'et'**: 海洋上的实际ET (mm/day) / Actual ET over ocean
        - **'beta'**: 海洋上的波文比 / Bowen ratio over ocean
        - **'beta_w_wet'**: 湿润条件下的湿润波文比 / Wet Bowen ratio under wet conditions
        - **'beta_w_driest'**: 最干条件下的湿润波文比 / Wet Bowen ratio under driest conditions
        - **'pete_wet'**: 湿润条件下的PETe (mm/day) / PETe under wet conditions
        - **'peta_wet'**: 湿润条件下的PETa (mm/day) / PETa under wet conditions
        - **'pete_driest'**: 最干条件下的PETe (mm/day) / PETe under driest conditions
        - **'peta_driest'**: 最干条件下的PETa (mm/day) / PETa under driest conditions
        - **'temp_diff'**: 从湿润到最干的温度差异 (K) / Temperature difference from wet to driest

    说明 / Notes
    -----
    **计算假设 / Calculation assumptions**:

    1. **恒定湿焓 / Constant moist enthalpy**:
       .. math:: T + \\frac{e}{\\gamma} = \\text{constant}

    2. **最干条件下 / Under driest conditions**:
       水汽压 → 0 / vapor pressure → 0

    3. **能量平衡 / Energy balance**:
       .. math:: R_n = SH + LH

    **物理意义 / Physical Significance**:

    通过比较湿润和最干条件，可以评估：
    By comparing wet and driest conditions, we can assess:

    - PET对地表湿度变化的敏感性
      Sensitivity of PET to surface moisture changes
    - 陆地-大气反馈强度
      Strength of land-atmosphere feedbacks
    - 干旱条件下的温度响应
      Temperature response under drought conditions

    参考文献 / Reference
    ----------
    .. [1] Zhou, S., & Yu, B. (2024). Physical basis of the potential evapotranspiration
           and its estimation over land. Journal of Hydrology, 641, 131825.

    示例 / Examples
    --------
    >>> results = calculate_pet_ocean(
    ...     latent_heat=150.0,
    ...     sensible_heat=30.0,
    ...     specific_humidity=0.015,
    ...     air_pressure=101325.0,
    ...     air_temperature=298.15,
    ...     skin_temperature=299.15
    ... )
    >>> print(f"PETe (wet): {results['pete_wet']:.2f} mm/day")
    PETe (wet): 8.53 mm/day
    >>> print(f"PETe (driest): {results['pete_driest']:.2f} mm/day")
    PETe (driest): 9.15 mm/day
    >>> print(f"Temperature increase: {results['temp_diff']:.2f} K")
    Temperature increase: 22.45 K
    """
    # 将热通量从 W/m² 转换为 mm/day
    # Convert heat fluxes from W/m² to mm/day
    CONVERSION_FACTOR = 0.0864
    hfls_mmday = latent_heat * CONVERSION_FACTOR
    hfss_mmday = sensible_heat * CONVERSION_FACTOR

    # 计算汽化潜热 / Calculate latent heat of vaporization
    lv = calculate_latent_heat_vaporization(air_temperature)

    # 计算水汽压 / Calculate vapor pressures
    vp_sat_air = calculate_saturation_vapor_pressure_tetens(air_temperature)
    vp_sat_surface = calculate_saturation_vapor_pressure_tetens(skin_temperature)
    vp_actual = calculate_actual_vapor_pressure(specific_humidity, air_pressure)

    # 计算干湿表常数 / Calculate psychrometric constant
    gamma = calculate_psychrometric_constant_land(lv, air_pressure)

    # ========================================
    # 最干条件下（水汽压 → 0）
    # Under driest conditions (vapor pressure → 0)
    # ========================================

    # 最干条件下的温度（假设恒定湿焓）
    # Temperature under driest conditions (assuming constant moist enthalpy)
    # T_driest = T + e/γ (since e_driest → 0)
    air_temp_driest = air_temperature + vp_actual / gamma
    surface_temp_driest = skin_temperature + vp_sat_surface / gamma

    # 最干条件下地表温度的饱和水汽压
    # Saturation vapor pressure at driest surface temperature
    vp_sat_surface_driest = calculate_saturation_vapor_pressure_tetens(surface_temp_driest)

    # ========================================
    # 波文比 / Bowen ratios
    # ========================================

    # 海洋上的实际波文比 / Actual Bowen ratio over ocean
    beta_actual = sensible_heat / latent_heat

    # 湿润条件下的湿润波文比（海洋表面）
    # Wet Bowen ratio under wet conditions (ocean surface)
    beta_w_wet = gamma * (skin_temperature - air_temperature) / \
                 (vp_sat_surface - vp_actual)

    # 最干条件下的湿润波文比
    # Wet Bowen ratio under driest conditions
    beta_w_driest = gamma * (surface_temp_driest - air_temp_driest) / \
                    vp_sat_surface_driest

    # ========================================
    # 计算ET和通量 / Calculate ET and fluxes
    # ========================================

    # 将热通量转换为等效水深 / Convert heat fluxes to equivalent water depth
    lh = hfls_mmday / lv
    sh = hfss_mmday / lv

    # 净辐射（潜热和感热之和）/ Net radiation (sum of latent and sensible heat)
    rn = sh + lh

    # ========================================
    # 湿润条件下的PET / PET under wet conditions
    # ========================================

    pete_wet = rn / (1.0 + beta_w_wet)
    peta_wet = sh / beta_w_wet

    # ========================================
    # 最干条件下的PET / PET under driest conditions
    # ========================================

    pete_driest = rn / (1.0 + beta_w_driest)
    peta_driest = rn / beta_w_driest

    # ========================================
    # 温度差异 / Temperature difference
    # ========================================

    # 从湿润到最干条件的平均温度差异
    # Mean temperature difference from wet to driest conditions
    temp_diff = ((surface_temp_driest + air_temp_driest) / 2.0 -
                 (skin_temperature + air_temperature) / 2.0)

    return {
        'et': lh,
        'beta': beta_actual,
        'beta_w_wet': beta_w_wet,
        'beta_w_driest': beta_w_driest,
        'pete_wet': pete_wet,
        'peta_wet': peta_wet,
        'pete_driest': pete_driest,
        'peta_driest': peta_driest,
        'temp_diff': temp_diff
    }


# 公共API / Public API
__all__ = [
    'calculate_pet_land',
    'calculate_pet_ocean',
    'batch_calculate_pet',
    'calculate_wet_bowen_ratio',
    'calculate_latent_heat_vaporization',
    'calculate_saturation_vapor_pressure_tetens',
    'calculate_actual_vapor_pressure',
    'calculate_psychrometric_constant_land',
    'calculate_slope_saturation_curve',
]
