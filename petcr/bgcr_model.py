# -*- coding: utf-8 -*-
"""
BGCR-Budyko Model / BGCR-Budyko 模型
===================================

This module integrates the BGCR (Budyko-Generalized Complementary Relationship)
model into the PET-CR library. The BGCR model combines the long-term Budyko
framework with the short-term generalized complementary relationship (GCR).

本模块将 BGCR（Budyko-广义互补关系）模型集成到 PET-CR 库中。
BGCR 模型将长期 Budyko 框架与短期广义互补关系（GCR）相结合。

Key Features / 主要特性
-----------------------
- Monthly evapotranspiration estimation / 月尺度蒸散发估算
- Distributed Budyko parameter (w) schemes / 分布式 Budyko 参数 (w) 方案
- Integration with standard meteorological variables / 与标准气象变量集成
- Handles spatial heterogeneity / 处理空间异质性

Mathematical Framework / 数学框架
---------------------------------
The BGCR model uses:
1. Apparent potential evaporation: Epa = Erad + Eaero
2. Budyko framework: E/Epa = f(P/Epa, w)
3. Distributed w parameter: w = f(SI, ALB)

Where:
- Erad: Radiation component from Penman equation / Penman 方程的辐射分量
- Eaero: Aerodynamic component / 空气动力学分量
- P: Precipitation / 降水
- SI: Seasonality index / 季节性指数
- ALB: Surface albedo / 地表反照率
- w: Budyko parameter / Budyko 参数

References / 参考文献
---------------------
- Yang, D., et al. (2006). Interpreting the complementary relationship in
  non-humid environments based on the Budyko and Penman hypotheses.
  Geophysical Research Letters, 33(18).

- Zhang, L., et al. (2016). A rational function approach for estimating
  mean annual evapotranspiration. Water Resources Research, 52(12),
  9456-9472.

Authors / 作者
--------------
PET-CR Contributors

Version / 版本: 0.3.0 (2025-01-XX)
"""

import numpy as np
from typing import Union, Dict, Tuple, Optional

# ============================================================================
# Mathematical Utilities / 数学工具函数
# ============================================================================

def _clamp(x: np.ndarray, lo: Optional[float] = None,
           hi: Optional[float] = None) -> np.ndarray:
    """
    Clamp array values to range [lo, hi].

    将数组值限制在 [lo, hi] 范围内。

    Parameters
    ----------
    x : np.ndarray
        Input array / 输入数组
    lo : float, optional
        Lower bound / 下界
    hi : float, optional
        Upper bound / 上界

    Returns
    -------
    np.ndarray
        Clamped array / 限制后的数组
    """
    if lo is not None:
        x = np.maximum(x, lo)
    if hi is not None:
        x = np.minimum(x, hi)
    return x


def _safe_div(a: np.ndarray, b: np.ndarray,
              eps: float = 1e-12) -> np.ndarray:
    """
    Safe division with small epsilon to avoid division by zero.

    安全除法，使用小的 epsilon 避免除零错误。

    Parameters
    ----------
    a : np.ndarray
        Numerator / 分子
    b : np.ndarray
        Denominator / 分母
    eps : float, default=1e-12
        Small value to add to denominator / 添加到分母的小值

    Returns
    -------
    np.ndarray
        Result of division / 除法结果
    """
    return a / (b + eps)


def _cubic_root_trig(z: np.ndarray) -> np.ndarray:
    """
    Solve depressed cubic equation: x³ - 2x² + z = 0 using trigonometric form.

    使用三角形式求解简化三次方程：x³ - 2x² + z = 0。

    This is the mathematical core of the BGCR model, derived from combining
    the Budyko and complementary relationship frameworks.

    这是 BGCR 模型的数学核心，源自 Budyko 和互补关系框架的结合。

    Parameters
    ----------
    z : np.ndarray
        Coefficient in cubic equation / 三次方程中的系数

    Returns
    -------
    np.ndarray
        Solution x in physically relevant range [0, 2] / 物理相关范围 [0, 2] 中的解 x

    Notes
    -----
    The cubic equation arises from eliminating E/Epa between the Budyko
    curve and the generalized complementary relationship.

    三次方程来自于在 Budyko 曲线和广义互补关系之间消除 E/Epa。
    """
    z = np.asarray(z, dtype=float)
    p = -4.0 / 3.0
    q = -16.0 / 27.0 + z

    # Trigonometric solution ensuring principal branch
    # 三角解法确保主分支
    tmp = 3 * np.sqrt(3) / 2.0 * q / np.power(-p, 1.5)
    tmp = np.clip(tmp, -1.0, 1.0)
    theta = (1.0 / 3.0) * np.arcsin(tmp)
    x = 2.0 / np.sqrt(3.0) * np.sin(theta) + 2.0 / 3.0

    return _clamp(x, 0.0, 2.0)


# ============================================================================
# Penman Components / Penman 分量计算
# ============================================================================

def _slope_svpc(temperature: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate slope of saturation vapor pressure curve (Δ).

    计算饱和水汽压曲线斜率（Δ）。

    Uses Tetens equation derivative approximation.
    使用 Tetens 方程导数近似。

    Parameters
    ----------
    temperature : float or np.ndarray
        Air temperature [°C] / 气温 [°C]

    Returns
    -------
    float or np.ndarray
        Slope Δ [kPa/°C] / 斜率 Δ [kPa/°C]

    References
    ----------
    Allen, R. G., et al. (1998). Crop evapotranspiration - Guidelines for
    computing crop water requirements. FAO Irrigation and drainage paper 56.
    """
    T = np.asarray(temperature, dtype=float)
    # Saturation vapor pressure using Tetens equation
    # 使用 Tetens 方程计算饱和水汽压
    es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
    # Derivative (slope)
    # 导数（斜率）
    delta = 4098 * es / (T + 237.3)**2
    return delta


def calculate_penman_components(
    net_radiation: Union[float, np.ndarray],
    ground_heat_flux: Union[float, np.ndarray],
    temperature: Union[float, np.ndarray],
    wind_speed: Union[float, np.ndarray],
    actual_vapor_pressure: Union[float, np.ndarray],
    saturation_vapor_pressure: Union[float, np.ndarray],
    psychrometric_constant: float = 0.066,
    latent_heat_vaporization: float = 2.45e6
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate Penman equation components: radiation term (Erad) and
    aerodynamic term (Eaero).

    计算 Penman 方程分量：辐射项（Erad）和空气动力学项（Eaero）。

    Epa = Erad + Eaero, where:
    - Erad = Δ/(Δ+γ) × (Rn - G) / Le
    - Eaero = γ/(Δ+γ) × f(U2) × (es - ea)

    Parameters
    ----------
    net_radiation : float or np.ndarray
        Net radiation [W/m²] / 净辐射 [W/m²]
    ground_heat_flux : float or np.ndarray
        Ground heat flux [W/m²] (typically ~0 for monthly) / 地表热通量 [W/m²]
    temperature : float or np.ndarray
        Air temperature [°C] / 气温 [°C]
    wind_speed : float or np.ndarray
        Wind speed at 2m height [m/s] / 2米高处风速 [m/s]
    actual_vapor_pressure : float or np.ndarray
        Actual vapor pressure [kPa] / 实际水汽压 [kPa]
    saturation_vapor_pressure : float or np.ndarray
        Saturation vapor pressure [kPa] / 饱和水汽压 [kPa]
    psychrometric_constant : float, default=0.066
        Psychrometric constant [kPa/°C] / 干湿表常数 [kPa/°C]
    latent_heat_vaporization : float, default=2.45e6
        Latent heat of vaporization [J/kg] / 汽化潜热 [J/kg]

    Returns
    -------
    Erad : np.ndarray
        Radiation component [mm/day] / 辐射分量 [mm/day]
    Eaero : np.ndarray
        Aerodynamic component [mm/day] / 空气动力学分量 [mm/day]

    Notes
    -----
    Units conversion:
    - W/m² to mm/day: multiply by 86400 / (Le × ρw)
    - Where Le = 2.45e6 J/kg, ρw = 1000 kg/m³

    单位转换：
    - W/m² 转 mm/day：乘以 86400 / (Le × ρw)
    - 其中 Le = 2.45e6 J/kg，ρw = 1000 kg/m³

    References
    ----------
    Penman, H. L. (1948). Natural evaporation from open water, bare soil
    and grass. Proceedings of the Royal Society of London. Series A.
    """
    # Convert inputs to arrays
    # 将输入转换为数组
    T = np.asarray(temperature, dtype=float)
    U2 = np.asarray(wind_speed, dtype=float)
    ea = np.asarray(actual_vapor_pressure, dtype=float)
    es = np.asarray(saturation_vapor_pressure, dtype=float)
    Rn = np.asarray(net_radiation, dtype=float)
    G = np.asarray(ground_heat_flux, dtype=float)

    # Calculate slope of saturation vapor pressure curve
    # 计算饱和水汽压曲线斜率
    Delta = _slope_svpc(T)

    # Penman wind function (empirical)
    # Penman 风速函数（经验公式）
    f_U = 2.6 * (1.0 + 0.54 * U2)

    # Available energy converted to mm/day equivalent
    # 可用能量转换为 mm/day 当量
    Qne = (Rn - G) / latent_heat_vaporization * 86400 / 1000  # mm/day

    # Radiation component
    # 辐射分量
    Erad = Delta / (Delta + psychrometric_constant) * Qne

    # Aerodynamic component
    # 空气动力学分量
    Eaero = (psychrometric_constant / (Delta + psychrometric_constant) *
             f_U * (es - ea))

    return Erad, Eaero


# ============================================================================
# Budyko Parameter Schemes / Budyko 参数方案
# ============================================================================

def calculate_seasonality_index(
    precipitation_monthly: np.ndarray
) -> np.ndarray:
    """
    Compute seasonality index (SI) from monthly precipitation.

    从月降水量计算季节性指数（SI）。

    SI measures the temporal variability of precipitation within a year.
    Higher values indicate stronger seasonality.

    SI 衡量一年内降水的时间变异性。值越高表示季节性越强。

    Parameters
    ----------
    precipitation_monthly : np.ndarray
        Monthly precipitation with shape (n_years, 12, ...)
        月降水量，形状为 (n_years, 12, ...)

    Returns
    -------
    np.ndarray
        Seasonality index (scalar or spatial field) / 季节性指数（标量或空间场）

    Notes
    -----
    SI = (1/Pa) × Σ|Pi - Pa/12|
    where Pa is annual precipitation, Pi is monthly precipitation.

    SI = (1/Pa) × Σ|Pi - Pa/12|
    其中 Pa 是年降水量，Pi 是月降水量。

    References
    ----------
    Walsh, R. P. D., & Lawler, D. M. (1981). Rainfall seasonality:
    description, spatial patterns and change through time. Weather, 36(7).
    """
    P_monthly = np.asarray(precipitation_monthly, dtype=float)

    if P_monthly.shape[1] != 12:
        raise ValueError("Second dimension must be 12 (months). "
                        "Expected shape: (n_years, 12, ...)")

    n_years = P_monthly.shape[0]

    # Annual total for each year
    # 每年的年总降水量
    P_annual = np.sum(P_monthly, axis=1, keepdims=True)

    # Expected monthly mean if uniform distribution
    # 如果均匀分布的预期月平均值
    P_mean_month = P_annual / 12.0

    # SI per year
    # 每年的 SI
    diff = np.abs(P_monthly - P_mean_month)
    with np.errstate(divide='ignore', invalid='ignore'):
        SI_year = np.where(
            P_annual > 0,
            np.sum(diff, axis=1) / P_annual.squeeze(1),
            0.0
        )

    # Final SI is mean over years
    # 最终 SI 是多年平均
    return np.mean(SI_year, axis=0)


def calculate_budyko_w_from_SI(
    seasonality_index: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate Budyko parameter w from seasonality index (BGCR-1 scheme).

    从季节性指数计算 Budyko 参数 w（BGCR-1 方案）。

    This single-variable regionalization scheme relates the Budyko parameter
    to precipitation seasonality.

    该单变量区域化方案将 Budyko 参数与降水季节性相关联。

    Parameters
    ----------
    seasonality_index : float or np.ndarray
        Precipitation seasonality index (dimensionless) / 降水季节性指数（无量纲）

    Returns
    -------
    float or np.ndarray
        Budyko parameter w / Budyko 参数 w

    Notes
    -----
    w = 0.214 - 0.651×SI + 7.350×SI²

    This empirical relationship was calibrated across diverse catchments.
    该经验关系在不同流域进行了校准。

    References
    ----------
    Yang, D., et al. (2016). Regional parameterization of the Budyko
    parameter. Hydrological Processes, 30(26), 4663-4673.
    """
    SI = np.asarray(seasonality_index, dtype=float)
    return 0.214 - 0.651 * SI + 7.350 * np.square(SI)


def calculate_budyko_w_from_SI_albedo(
    seasonality_index: Union[float, np.ndarray],
    albedo: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate Budyko parameter w from SI and albedo (BGCR-2 scheme).

    从 SI 和反照率计算 Budyko 参数 w（BGCR-2 方案）。

    This dual-variable regionalization scheme incorporates both temporal
    (seasonality) and spatial (albedo) heterogeneity.

    该双变量区域化方案同时考虑时间（季节性）和空间（反照率）异质性。

    Parameters
    ----------
    seasonality_index : float or np.ndarray
        Precipitation seasonality index (dimensionless) / 降水季节性指数（无量纲）
    albedo : float or np.ndarray
        Surface albedo [0-1] / 地表反照率 [0-1]

    Returns
    -------
    float or np.ndarray
        Budyko parameter w / Budyko 参数 w

    Notes
    -----
    w = 0.5931 + 7.0871×SI³ + 0.0175/ALB²

    Albedo is clipped to [0.001, 1.0] to avoid division issues.
    反照率被限制在 [0.001, 1.0] 以避免除法问题。

    References
    ----------
    Yang, D., et al. (2016). Regional parameterization of the Budyko
    parameter. Hydrological Processes, 30(26), 4663-4673.
    """
    SI = np.asarray(seasonality_index, dtype=float)
    ALB = np.asarray(albedo, dtype=float)

    # Clip albedo to avoid division by zero
    # 限制反照率以避免除零
    ALB = np.clip(ALB, 1e-3, 1.0)

    return 0.5931 + 7.0871 * np.power(SI, 3) + 0.0175 / np.square(ALB)


# ============================================================================
# Core BGCR Model / 核心 BGCR 模型
# ============================================================================

def _budyko_tixeront_fu_ratio(
    precipitation: np.ndarray,
    epa: np.ndarray,
    w: np.ndarray
) -> np.ndarray:
    """
    Calculate E/Epa ratio using Tixeront-Fu form of Budyko curve.

    使用 Budyko 曲线的 Tixeront-Fu 形式计算 E/Epa 比值。

    y = 1 + (P/Epa) - [1 + (P/Epa)^w]^(1/w)

    Parameters
    ----------
    precipitation : np.ndarray
        Precipitation [mm] / 降水 [mm]
    epa : np.ndarray
        Apparent potential evaporation [mm] / 表观潜在蒸发 [mm]
    w : np.ndarray
        Budyko parameter / Budyko 参数

    Returns
    -------
    np.ndarray
        Evaporation ratio E/Epa [0-1] / 蒸发比率 E/Epa [0-1]
    """
    Phi = _safe_div(precipitation, epa)
    term = np.power(1.0 + np.power(Phi, w), 1.0 / w)
    y = 1.0 + Phi - term
    return _clamp(y, 0.0, 1.0)


def bgcr_monthly(
    precipitation: Union[float, np.ndarray],
    epa: Union[float, np.ndarray],
    erad: Union[float, np.ndarray],
    w: Union[float, np.ndarray]
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Compute monthly evapotranspiration using BGCR model.

    使用 BGCR 模型计算月蒸散发。

    The BGCR model combines:
    1. Long-term Budyko framework for E/Epa relationship
    2. Short-term generalized complementary relationship
    3. Cubic equation solution to eliminate β_c

    BGCR 模型结合：
    1. 长期 Budyko 框架用于 E/Epa 关系
    2. 短期广义互补关系
    3. 三次方程解以消除 β_c

    Parameters
    ----------
    precipitation : float or np.ndarray
        Monthly precipitation [mm] / 月降水 [mm]
    epa : float or np.ndarray
        Apparent potential evaporation [mm] / 表观潜在蒸发 [mm]
    erad : float or np.ndarray
        Radiation component [mm] / 辐射分量 [mm]
    w : float or np.ndarray
        Budyko parameter (can be spatially distributed) /
        Budyko 参数（可以空间分布）

    Returns
    -------
    E : np.ndarray
        Estimated evapotranspiration [mm] / 估算的蒸散发 [mm]
    diagnostics : dict
        Dictionary containing:
        - 'beta_c': Complementary coefficient / 互补系数
        - 'x': Cubic equation solution / 三次方程解
        - 'ratio': E/Epa ratio / E/Epa 比率

    Notes
    -----
    The cubic equation x³ - 2x² + z = 0 arises from:
    - Budyko: E/Epa = f(P/Epa, w)
    - GCR: E/Epo = g(Epa/Epo) where Epo = β_c × Erad
    - Solution: x = β_c × Erad / Epa

    三次方程 x³ - 2x² + z = 0 来自：
    - Budyko：E/Epa = f(P/Epa, w)
    - GCR：E/Epo = g(Epa/Epo) 其中 Epo = β_c × Erad
    - 解：x = β_c × Erad / Epa

    Examples
    --------
    >>> P = 100.0  # mm
    >>> Epa = 120.0  # mm
    >>> Erad = 80.0  # mm
    >>> w = 2.0
    >>> E, diag = bgcr_monthly(P, Epa, Erad, w)
    >>> print(f"ET: {E:.2f} mm")
    >>> print(f"Complementary coefficient: {diag['beta_c']:.3f}")

    References
    ----------
    Yang, D., et al. (2006). Interpreting the complementary relationship in
    non-humid environments based on the Budyko and Penman hypotheses.
    Geophysical Research Letters, 33(18).
    """
    # Convert inputs to arrays
    # 将输入转换为数组
    P = np.asarray(precipitation, dtype=float)
    Epa = np.asarray(epa, dtype=float)
    Erad = np.asarray(erad, dtype=float)
    w = np.asarray(w, dtype=float)

    # Calculate β_c using cubic solution
    # 使用三次方程解计算 β_c
    Phi = _safe_div(P, Epa)
    z = 1.0 + Phi - np.power(1.0 + np.power(Phi, w), 1.0 / w)
    x = _cubic_root_trig(z)
    beta_c = _safe_div(Epa, Erad) * x

    # Calculate E/Epa from Budyko curve
    # 从 Budyko 曲线计算 E/Epa
    y = _budyko_tixeront_fu_ratio(P, Epa, w)

    # Actual evapotranspiration
    # 实际蒸散发
    E = y * Epa

    # Diagnostics
    # 诊断信息
    diagnostics = {
        'beta_c': beta_c,
        'x': x,
        'ratio': y
    }

    return E, diagnostics


# ============================================================================
# High-Level API / 高级 API
# ============================================================================

def calculate_bgcr_et(
    net_radiation: Union[float, np.ndarray],
    temperature: Union[float, np.ndarray],
    wind_speed: Union[float, np.ndarray],
    actual_vapor_pressure: Union[float, np.ndarray],
    saturation_vapor_pressure: Union[float, np.ndarray],
    precipitation: Union[float, np.ndarray],
    seasonality_index: Union[float, np.ndarray],
    albedo: Optional[Union[float, np.ndarray]] = None,
    ground_heat_flux: Union[float, np.ndarray] = 0.0,
    psychrometric_constant: float = 0.066,
    use_dual_scheme: bool = True
) -> Dict[str, np.ndarray]:
    """
    High-level function to calculate actual ET using BGCR model.

    使用 BGCR 模型计算实际蒸散发的高级函数。

    This function integrates all components of the BGCR model:
    1. Calculates Penman components (Erad, Eaero)
    2. Computes distributed Budyko parameter w
    3. Applies BGCR monthly model

    此函数集成了 BGCR 模型的所有组件：
    1. 计算 Penman 分量（Erad、Eaero）
    2. 计算分布式 Budyko 参数 w
    3. 应用 BGCR 月模型

    Parameters
    ----------
    net_radiation : float or np.ndarray
        Net radiation [W/m²] / 净辐射 [W/m²]
    temperature : float or np.ndarray
        Air temperature [°C] / 气温 [°C]
    wind_speed : float or np.ndarray
        Wind speed at 2m [m/s] / 2米高处风速 [m/s]
    actual_vapor_pressure : float or np.ndarray
        Actual vapor pressure [kPa] / 实际水汽压 [kPa]
    saturation_vapor_pressure : float or np.ndarray
        Saturation vapor pressure [kPa] / 饱和水汽压 [kPa]
    precipitation : float or np.ndarray
        Monthly precipitation [mm] / 月降水 [mm]
    seasonality_index : float or np.ndarray
        Precipitation seasonality index / 降水季节性指数
    albedo : float or np.ndarray, optional
        Surface albedo [0-1]. Required if use_dual_scheme=True /
        地表反照率 [0-1]。如果 use_dual_scheme=True 则必需
    ground_heat_flux : float or np.ndarray, default=0.0
        Ground heat flux [W/m²] / 地表热通量 [W/m²]
    psychrometric_constant : float, default=0.066
        Psychrometric constant [kPa/°C] / 干湿表常数 [kPa/°C]
    use_dual_scheme : bool, default=True
        Use dual-variable (SI+albedo) scheme for w. If False, uses single-variable (SI only) /
        使用双变量（SI+反照率）方案计算 w。如果为 False，使用单变量（仅 SI）

    Returns
    -------
    dict
        Dictionary containing:
        - 'et': Actual evapotranspiration [mm/month] / 实际蒸散发 [mm/月]
        - 'epa': Apparent potential evaporation [mm/month] / 表观潜在蒸发 [mm/月]
        - 'erad': Radiation component [mm/month] / 辐射分量 [mm/月]
        - 'eaero': Aerodynamic component [mm/month] / 空气动力学分量 [mm/月]
        - 'w': Budyko parameter / Budyko 参数
        - 'beta_c': Complementary coefficient / 互补系数
        - 'et_ratio': E/Epa ratio / E/Epa 比率

    Raises
    ------
    ValueError
        If use_dual_scheme=True but albedo is not provided /
        如果 use_dual_scheme=True 但未提供反照率

    Examples
    --------
    >>> # Monthly data for a catchment
    >>> # 流域的月数据
    >>> results = calculate_bgcr_et(
    ...     net_radiation=150.0,
    ...     temperature=20.0,
    ...     wind_speed=2.0,
    ...     actual_vapor_pressure=1.5,
    ...     saturation_vapor_pressure=2.3,
    ...     precipitation=80.0,
    ...     seasonality_index=0.5,
    ...     albedo=0.2
    ... )
    >>> print(f"Monthly ET: {results['et']:.2f} mm")
    >>> print(f"Budyko w: {results['w']:.3f}")

    Notes
    -----
    For gridded applications, ensure all inputs have compatible shapes
    that can be broadcast together.

    对于网格应用，确保所有输入具有可以一起广播的兼容形状。

    Time scale: This function is designed for monthly calculations.
    时间尺度：此函数设计用于月尺度计算。

    See Also
    --------
    bgcr_monthly : Core BGCR model / 核心 BGCR 模型
    calculate_penman_components : Penman equation components / Penman 方程分量
    calculate_budyko_w_from_SI_albedo : Budyko parameter schemes / Budyko 参数方案
    """
    # Step 1: Calculate Penman components
    # 步骤1：计算 Penman 分量
    Erad, Eaero = calculate_penman_components(
        net_radiation=net_radiation,
        ground_heat_flux=ground_heat_flux,
        temperature=temperature,
        wind_speed=wind_speed,
        actual_vapor_pressure=actual_vapor_pressure,
        saturation_vapor_pressure=saturation_vapor_pressure,
        psychrometric_constant=psychrometric_constant
    )

    # Apparent potential evaporation
    # 表观潜在蒸发
    Epa = Erad + Eaero

    # Step 2: Calculate Budyko parameter w
    # 步骤2：计算 Budyko 参数 w
    if use_dual_scheme:
        if albedo is None:
            raise ValueError(
                "albedo is required when use_dual_scheme=True. "
                "Provide albedo or set use_dual_scheme=False."
            )
        w = calculate_budyko_w_from_SI_albedo(seasonality_index, albedo)
    else:
        w = calculate_budyko_w_from_SI(seasonality_index)

    # Step 3: Apply BGCR monthly model
    # 步骤3：应用 BGCR 月模型
    ET, diagnostics = bgcr_monthly(
        precipitation=precipitation,
        epa=Epa,
        erad=Erad,
        w=w
    )

    # Compile results
    # 整合结果
    results = {
        'et': ET,
        'epa': Epa,
        'erad': Erad,
        'eaero': Eaero,
        'w': w,
        'beta_c': diagnostics['beta_c'],
        'et_ratio': diagnostics['ratio']
    }

    return results


# ============================================================================
# Module Exports / 模块导出
# ============================================================================

__all__ = [
    # Core BGCR model / 核心 BGCR 模型
    'bgcr_monthly',
    'calculate_bgcr_et',

    # Penman components / Penman 分量
    'calculate_penman_components',

    # Budyko parameter schemes / Budyko 参数方案
    'calculate_seasonality_index',
    'calculate_budyko_w_from_SI',
    'calculate_budyko_w_from_SI_albedo',
]
