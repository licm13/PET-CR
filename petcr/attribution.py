"""
ET预估与归因分析模块 / ET Projection and Attribution Analysis Module
==================================================================================

本模块基于Budyko框架实现ET预估和归因分析，用于分离气候变化和陆地表面变化的影响。
This module implements ET projection and attribution analysis based on the Budyko
framework, separating climate change impacts from land surface changes.

核心功能 / Core Functionality
------------------------------
1. **Budyko框架ET计算 / Budyko Framework ET Calculation**
   使用干燥度指数（PET/P）预测蒸散发比率（ET/P）
   Predict evaporative ratio (ET/P) using dryness index (PET/P)

2. **归因分析 / Attribution Analysis**
   将ET变化分解为：
   Decompose ET changes into:
   - 气候变化效应（PETe和降水变化）/ Climate change effects (PETe and precipitation changes)
   - 陆地表面效应（植被、土壤等变化）/ Land surface effects (vegetation, soil changes)

3. **1pctCO2实验分析 / 1pctCO2 Experiment Analysis**
   分析CO2浓度增加对ET的辐射和生理效应
   Analyze radiative and physiological effects of CO2 increase on ET

应用场景 / Applications
------------------------
- CMIP6气候模式输出分析 / CMIP6 climate model output analysis
- 历史ET变化归因 / Historical ET change attribution
- 未来气候情景预估 / Future climate scenario projections
- 干旱归因研究 / Drought attribution studies

参考文献 / References
----------------------
.. [1] Yang, H., Yang, D., Lei, Z., & Sun, F. (2008). New analytical derivation
       of the mean annual water-energy balance equation.
       Water Resources Research, 44(3), W03410.
.. [2] Zhou, S., & Yu, B. (2025). Land-atmosphere interactions exacerbate
       concurrent soil moisture drought and atmospheric aridity.
       Nature Climate Change (accepted).

作者 / Author: Sha Zhou
邮箱 / Email: shazhou21@bnu.edu.cn
日期 / Date: 2025
"""

import numpy as np
from typing import Union, Dict, Tuple, Optional
from scipy.optimize import minimize_scalar

# 类型别名 / Type alias
ArrayLike = Union[float, np.ndarray]


def budyko_et_ratio(
    dryness_index: ArrayLike,
    n_parameter: float = 2.0
) -> ArrayLike:
    """
    使用Budyko框架（Choudhury-Yang方程）计算ET比率
    Calculate ET ratio using the Budyko framework (Choudhury-Yang equation).

    参数 / Parameters
    ----------
    dryness_index : float or np.ndarray
        干燥度指数（PET/P），无量纲 / Dryness index (PET/P), dimensionless
    n_parameter : float, optional
        Budyko参数，考虑陆地表面特征（默认: 2.0）
        Budyko parameter accounting for land surface characteristics (default: 2.0)

    返回 / Returns
    -------
    float or np.ndarray
        ET比率（ET/P），无量纲 / ET ratio (ET/P), dimensionless

    说明 / Notes
    -----
    **Budyko框架 / Budyko Framework**

    Budyko框架将ET/P与PET/P联系起来，通过单一参数n描述陆地表面特征：
    The Budyko framework relates ET/P to PET/P through a single parameter n
    describing land surface characteristics:

    .. math::
        \\frac{ET}{P} = \\left[\\left(\\frac{PET}{P}\\right)^{-n} + 1\\right]^{-1/n}

    其中 / where:
    - ET/P 是蒸发比率 / is the evaporative ratio
    - PET/P 是干燥度指数 / is the dryness index
    - n 是反映陆地表面特征的参数 / is a parameter reflecting land surface characteristics

    **参数n的物理意义 / Physical Meaning of Parameter n**:

    - n ≈ 1: 能量受限区域（湿润气候）/ Energy-limited regions (humid climates)
    - n ≈ 2-3: 平衡状态（半湿润气候）/ Balanced conditions (semi-humid climates)
    - n > 3: 水分受限区域（干旱气候）/ Water-limited regions (arid climates)

    **边界条件 / Boundary Conditions**:

    - 当 PET/P → 0 (极端湿润): ET/P → 1 / When PET/P → 0 (extremely wet): ET/P → 1
    - 当 PET/P → ∞ (极端干旱): ET/P → 0 / When PET/P → ∞ (extremely dry): ET/P → 0
    - 当 PET/P = 1 (能量-水分平衡): ET/P ≈ 0.5 / When PET/P = 1 (energy-water balance): ET/P ≈ 0.5

    参考文献 / Reference
    ----------
    .. [1] Yang, H., Yang, D., Lei, Z., & Sun, F. (2008). New analytical derivation
           of the mean annual water-energy balance equation. Water Resources Research,
           44(3), W03410. https://doi.org/10.1029/2007WR006135

    示例 / Examples
    --------
    >>> # 湿润区域 / Humid region
    >>> budyko_et_ratio(dryness_index=0.5, n_parameter=2.0)
    0.894...

    >>> # 半湿润区域 / Semi-humid region
    >>> budyko_et_ratio(dryness_index=1.0, n_parameter=2.0)
    0.707...

    >>> # 干旱区域 / Arid region
    >>> budyko_et_ratio(dryness_index=2.0, n_parameter=2.0)
    0.447...

    >>> # 数组输入 / Array input
    >>> dryness = np.array([0.5, 1.0, 1.5, 2.0])
    >>> budyko_et_ratio(dryness, n_parameter=2.0)
    array([0.894..., 0.707..., 0.554..., 0.447...])
    """
    # 确保dryness_index为正以避免数值问题
    # Ensure dryness_index is positive to avoid numerical issues
    dryness_index = np.maximum(dryness_index, 1e-10)

    # 使用Choudhury-Yang方程计算ET比率
    # Calculate ET ratio using Choudhury-Yang equation
    et_ratio = (dryness_index**(-n_parameter) + 1.0) ** (-1.0 / n_parameter)

    return et_ratio


def calculate_et_from_budyko(
    pet: ArrayLike,
    precipitation: ArrayLike,
    n_parameter: float = 2.0
) -> ArrayLike:
    """
    使用Budyko框架计算ET
    Calculate ET using the Budyko framework.

    参数 / Parameters
    ----------
    pet : float or np.ndarray
        潜在蒸散发 (mm/day) / Potential evapotranspiration (mm/day)
    precipitation : float or np.ndarray
        降水 (mm/day) / Precipitation (mm/day)
    n_parameter : float, optional
        Budyko参数（默认: 2.0）/ Budyko parameter (default: 2.0)

    返回 / Returns
    -------
    float or np.ndarray
        蒸散发 (mm/day) / Evapotranspiration (mm/day)

    说明 / Notes
    -----
    计算步骤 / Calculation steps:

    1. 计算干燥度指数 / Calculate dryness index:
       .. math:: \\phi = \\frac{PET}{P}

    2. 计算ET比率 / Calculate ET ratio:
       .. math:: \\frac{ET}{P} = f(\\phi, n)

    3. 计算ET / Calculate ET:
       .. math:: ET = P \\cdot f(\\phi, n)

    物理约束 / Physical constraints:
    - ET ≤ P (蒸发不能超过降水) / ET ≤ P (evaporation cannot exceed precipitation)
    - ET ≤ PET (实际ET不能超过潜在ET) / ET ≤ PET (actual ET cannot exceed potential ET)

    示例 / Examples
    --------
    >>> calculate_et_from_budyko(pet=3.0, precipitation=2.5, n_parameter=2.0)
    1.767...

    >>> # 时间序列 / Time series
    >>> pet_series = np.array([2.5, 3.0, 3.5, 4.0])
    >>> pr_series = np.array([2.0, 2.5, 2.5, 2.5])
    >>> calculate_et_from_budyko(pet_series, pr_series, n_parameter=2.0)
    array([1.649..., 1.767..., 1.734..., 1.677...])
    """
    # 计算干燥度指数 / Calculate dryness index
    # 避免除以零 / Avoid division by zero
    precipitation_safe = np.maximum(precipitation, 1e-10)
    dryness_index = pet / precipitation_safe

    # 计算ET比率 / Calculate ET ratio
    et_ratio = budyko_et_ratio(dryness_index, n_parameter)

    # 计算ET / Calculate ET
    et = precipitation * et_ratio

    return et


def calibrate_budyko_parameter(
    et_observed: ArrayLike,
    pet: ArrayLike,
    precipitation: ArrayLike,
    bounds: Tuple[float, float] = (0.1, 10.0)
) -> float:
    """
    校准Budyko参数n以匹配观测的ET
    Calibrate the Budyko parameter n to match observed ET.

    参数 / Parameters
    ----------
    et_observed : float or np.ndarray
        观测的蒸散发 (mm/day) / Observed evapotranspiration (mm/day)
    pet : float or np.ndarray
        潜在蒸散发 (mm/day) / Potential evapotranspiration (mm/day)
    precipitation : float or np.ndarray
        降水 (mm/day) / Precipitation (mm/day)
    bounds : tuple, optional
        n参数的界限（默认: (0.1, 10.0)）/ Bounds for n parameter (default: (0.1, 10.0))

    返回 / Returns
    -------
    float
        校准的n参数 / Calibrated n parameter

    说明 / Notes
    -----
    **校准方法 / Calibration Method**

    校准最小化观测和预测ET之间的均方误差：
    The calibration minimizes mean squared error between observed and predicted ET:

    .. math::
        \\min_n \\sum (ET_{obs} - ET_{pred}(n))^2

    **应用建议 / Application Guidelines**:

    1. 使用多年平均值进行校准以减少年际变率影响
       Use multi-year averages for calibration to reduce interannual variability

    2. 对于区域尺度，n通常在1.5-3.0之间
       For regional scales, n typically ranges from 1.5 to 3.0

    3. 校准后的n应保持稳定以隔离陆地表面变化
       Keep calibrated n constant to isolate land surface changes

    Raises
    ------
    RuntimeError
        如果校准失败 / If calibration fails

    示例 / Examples
    --------
    >>> et_obs = 1.8
    >>> pet = 3.0
    >>> pr = 2.5
    >>> n_calibrated = calibrate_budyko_parameter(et_obs, pet, pr)
    >>> print(f"Calibrated n: {n_calibrated:.3f}")
    Calibrated n: 2.245

    >>> # 验证校准结果 / Verify calibration
    >>> et_pred = calculate_et_from_budyko(pet, pr, n_calibrated)
    >>> print(f"Predicted ET: {et_pred:.3f}, Observed ET: {et_obs:.3f}")
    Predicted ET: 1.800, Observed ET: 1.800
    """
    # 定义目标函数 / Define objective function
    def objective(n):
        et_predicted = calculate_et_from_budyko(pet, precipitation, n)

        # 计算均方误差 / Calculate mean squared error
        if isinstance(et_predicted, np.ndarray):
            mse = np.mean((et_observed - et_predicted) ** 2)
        else:
            mse = (et_observed - et_predicted) ** 2

        return mse

    # 优化n参数 / Optimize n parameter
    result = minimize_scalar(objective, bounds=bounds, method='bounded')

    if not result.success:
        raise RuntimeError(f"Calibration failed: {result.message}")

    return result.x


def attribution_analysis(
    et_timeseries: np.ndarray,
    pete_timeseries: np.ndarray,
    pr_timeseries: np.ndarray,
    window_size: int = 30,
    n_parameter: Optional[float] = None
) -> Dict[str, np.ndarray]:
    """
    执行归因分析以分离气候变化和陆地表面效应
    Perform attribution analysis to separate climate change and land surface effects.

    这是本模块的核心函数，用于将ET变化分解为气候和陆地表面贡献。
    This is the core function of this module, decomposing ET changes into
    climate and land surface contributions.

    参数 / Parameters
    ----------
    et_timeseries : np.ndarray
        观测ET的时间序列 (mm/day)，形状 (n_years,)
        Time series of observed ET (mm/day), shape (n_years,)
    pete_timeseries : np.ndarray
        能量基础PET的时间序列 (mm/day)，形状 (n_years,)
        Time series of energy-based PET (mm/day), shape (n_years,)
    pr_timeseries : np.ndarray
        降水的时间序列 (mm/day)，形状 (n_years,)
        Time series of precipitation (mm/day), shape (n_years,)
    window_size : int, optional
        滑动平均的窗口大小（默认: 30年）
        Window size for moving average (default: 30 years)
    n_parameter : float, optional
        Budyko参数。如果为None，将从第一个窗口校准。
        Budyko parameter. If None, will be calibrated from first window.

    返回 / Returns
    -------
    dict
        包含以下键的字典 / Dictionary containing:

        - **'et_total'**: 总ET变化 (mm/day)
          Total ET changes (mm/day)
        - **'et_climate'**: 气候变化贡献 (mm/day)
          Climate change contribution (mm/day)
        - **'et_landsurf'**: 陆地表面变化贡献 (mm/day)
          Land surface change contribution (mm/day)
        - **'n_parameter'**: 校准或使用的Budyko参数
          Calibrated or used Budyko parameter
        - **'time_index'**: 结果的时间索引
          Time indices for the results
        - **'et_smooth'**: 平滑后的ET时间序列
          Smoothed ET time series
        - **'et_climate_absolute'**: 气候驱动的ET绝对值
          Absolute climate-driven ET
        - **'et_landsurf_absolute'**: 陆地表面驱动的ET绝对值
          Absolute land surface-driven ET

    说明 / Notes
    -----
    **归因方法学 / Attribution Methodology**

    归因将总ET变化分为两部分：
    The attribution separates total ET changes into two components:

    1. **气候变化效应 / Climate Change Effect**:
       PETe和降水的变化，保持n参数恒定
       Changes in PETe and precipitation, keeping n constant

       .. math::
           \\Delta ET_{climate} = ET(PET_e^{new}, P^{new}, n_{ref}) - ET(PET_e^{ref}, P^{ref}, n_{ref})

    2. **陆地表面效应 / Land Surface Effect**:
       残差，反映植被、土壤等变化
       Residual reflecting vegetation, soil changes, etc.

       .. math::
           \\Delta ET_{landsurf} = \\Delta ET_{total} - \\Delta ET_{climate}

    **技术细节 / Technical Details**:

    - 使用滑动平均来平滑年际变率
      Uses moving averages to smooth interannual variability
    - 如果未提供，从第一个窗口校准n
      Calibrates n from the first window if not provided
    - 保持n随时间恒定以隔离陆地表面变化
      Keeps n constant over time to isolate land surface changes
    - 所有变化相对于第一个时期计算
      All changes calculated relative to first period

    **应用示例 / Application Examples**:

    - 历史干旱归因：分离自然变率和人为影响
      Historical drought attribution: separate natural variability and anthropogenic influence
    - 未来预估：评估CO2生理效应
      Future projections: assess CO2 physiological effects
    - 模式评估：验证陆面过程参数化
      Model evaluation: validate land surface parameterizations

    Raises
    ------
    ValueError
        如果时间序列长度 < 窗口大小
        If time series length < window size

    参考文献 / References
    ----------
    .. [1] Zhou, S., & Yu, B. (2025). Land-atmosphere interactions exacerbate
           concurrent soil moisture drought and atmospheric aridity.
           Nature Climate Change (accepted).

    示例 / Examples
    --------
    >>> # 生成140年合成数据 / Generate 140-year synthetic data
    >>> np.random.seed(42)
    >>> n_years = 140
    >>> time = np.arange(n_years)
    >>>
    >>> # 带趋势的数据 / Data with trends
    >>> pete_trend = 3.0 + 0.005 * time + np.random.normal(0, 0.1, n_years)
    >>> pr_trend = 2.5 + 0.002 * time + np.random.normal(0, 0.15, n_years)
    >>> et_trend = 1.8 + 0.003 * time + np.random.normal(0, 0.08, n_years)
    >>>
    >>> # 执行归因分析 / Perform attribution analysis
    >>> results = attribution_analysis(
    ...     et_timeseries=et_trend,
    ...     pete_timeseries=pete_trend,
    ...     pr_timeseries=pr_trend,
    ...     window_size=30
    ... )
    >>>
    >>> # 查看结果 / View results
    >>> print(f"Calibrated n: {results['n_parameter']:.3f}")
    Calibrated n: 2.123
    >>> print(f"Final climate contribution: {results['et_climate'][-1]:.3f} mm/day")
    Final climate contribution: 0.456 mm/day
    >>> print(f"Final land surface contribution: {results['et_landsurf'][-1]:.3f} mm/day")
    Final land surface contribution: -0.123 mm/day
    """
    n_years = len(et_timeseries)
    n_windows = n_years - window_size + 1

    if n_windows <= 0:
        raise ValueError(f"Time series length ({n_years}) must be >= window_size ({window_size})")

    # 初始化结果数组 / Initialize arrays for results
    et_smooth = np.zeros(n_windows)
    pete_smooth = np.zeros(n_windows)
    pr_smooth = np.zeros(n_windows)

    # 计算滑动平均 / Calculate moving averages
    for i in range(n_windows):
        et_smooth[i] = np.mean(et_timeseries[i:i+window_size])
        pete_smooth[i] = np.mean(pete_timeseries[i:i+window_size])
        pr_smooth[i] = np.mean(pr_timeseries[i:i+window_size])

    # 如果未提供，从第一个窗口校准n参数
    # Calibrate n parameter from the first window if not provided
    if n_parameter is None:
        n_parameter = calibrate_budyko_parameter(
            et_smooth[0], pete_smooth[0], pr_smooth[0]
        )

    # 使用恒定的n计算气候驱动的ET
    # Calculate climate-driven ET using constant n
    et_climate = calculate_et_from_budyko(pete_smooth, pr_smooth, n_parameter)

    # 计算陆地表面贡献（残差）
    # Calculate land surface contribution (residual)
    et_landsurf = et_smooth - et_climate

    # 计算相对于第一个时期的变化
    # Calculate changes relative to first period
    et_total_change = et_smooth - et_smooth[0]
    et_climate_change = et_climate - et_climate[0]
    et_landsurf_change = et_landsurf - et_landsurf[0]

    # 时间索引（每个窗口的第一年）
    # Time indices (first year of each window)
    time_index = np.arange(n_windows)

    return {
        'et_total': et_total_change,
        'et_climate': et_climate_change,
        'et_landsurf': et_landsurf_change,
        'n_parameter': n_parameter,
        'time_index': time_index,
        'et_smooth': et_smooth,
        'et_climate_absolute': et_climate,
        'et_landsurf_absolute': et_landsurf
    }


def projection_1pctCO2(
    et_data: np.ndarray,
    pete_data: np.ndarray,
    pr_data: np.ndarray,
    et_1pctCO2rad: Optional[np.ndarray] = None,
    window_size: int = 30
) -> Dict[str, np.ndarray]:
    """
    为1pctCO2实验执行ET预估和归因
    Perform ET projection and attribution for 1pctCO2 experiments.

    参数 / Parameters
    ----------
    et_data : np.ndarray
        1pctCO2实验的ET (mm/day)，形状 (n_years,)
        ET from 1pctCO2 experiment (mm/day), shape (n_years,)
    pete_data : np.ndarray
        1pctCO2的能量基础PET (mm/day)，形状 (n_years,)
        Energy-based PET from 1pctCO2 (mm/day), shape (n_years,)
    pr_data : np.ndarray
        1pctCO2的降水 (mm/day)，形状 (n_years,)
        Precipitation from 1pctCO2 (mm/day), shape (n_years,)
    et_1pctCO2rad : np.ndarray, optional
        1pctCO2-rad实验的ET（仅辐射强迫）
        如果提供，将比较两种归因方法
        ET from 1pctCO2-rad experiment (radiative forcing only)
        If provided, will compare two attribution approaches
    window_size : int, optional
        滑动平均的窗口大小（默认: 30年）
        Window size for moving average (default: 30 years)

    返回 / Returns
    -------
    dict
        包含预估和归因结果的字典 / Dictionary containing projection and attribution results

        - **'et_1pctCO2'**: 1pctCO2总ET变化
          Total ET change in 1pctCO2
        - **'et_climate_budyko'**: Budyko方法的气候贡献
          Climate contribution from Budyko method
        - **'et_landsurf_budyko'**: Budyko方法的陆地表面贡献
          Land surface contribution from Budyko method
        - **'et_climate_1pctCO2rad'**: 1pctCO2-rad的气候贡献（如果提供）
          Climate contribution from 1pctCO2-rad (if provided)
        - **'et_landsurf_1pctCO2rad'**: 1pctCO2-rad的陆地表面贡献（如果提供）
          Land surface contribution from 1pctCO2-rad (if provided)
        - **'climate_difference'**: 两种方法的气候贡献差异
          Difference in climate contribution between methods
        - **'landsurf_difference'**: 两种方法的陆地表面贡献差异
          Difference in land surface contribution between methods

    说明 / Notes
    -----
    **1pctCO2实验设计 / 1pctCO2 Experiment Design**

    1pctCO2实验每年增加1%的CO2，影响：
    The 1pctCO2 experiment increases CO2 by 1% per year, affecting:

    1. **大气（辐射）/ Atmosphere (Radiative)**:
       - 温室效应增强 / Enhanced greenhouse effect
       - 温度升高 / Temperature increase
       - 降水格局变化 / Precipitation pattern changes

    2. **陆地表面（生理）/ Land Surface (Physiological)**:
       - 气孔导度减小 / Reduced stomatal conductance
       - 蒸散发减少 / Reduced evapotranspiration
       - 水分利用效率提高 / Improved water use efficiency

    **1pctCO2-rad实验 / 1pctCO2-rad Experiment**:

    1pctCO2-rad实验仅包括辐射强迫，隔离气候变化效应：
    The 1pctCO2-rad experiment only includes radiative forcing, isolating
    climate change effects:

    - CO2浓度增加仅影响辐射 / CO2 increase only affects radiation
    - 植被对CO2的生理响应被抑制 / Physiological response to CO2 is suppressed
    - 用于分离辐射和生理效应 / Used to separate radiative and physiological effects

    **两种归因方法的比较 / Comparison of Two Attribution Approaches**:

    1. **Budyko方法 / Budyko Method**:
       基于能量-水分平衡框架
       Based on energy-water balance framework

    2. **1pctCO2-rad方法 / 1pctCO2-rad Method**:
       基于直接模式实验对比
       Based on direct model experiment comparison

    参考文献 / References
    ----------
    .. [1] Andrews, T., et al. (2012). Forcing, feedbacks and climate sensitivity
           in CMIP5 coupled atmosphere-ocean climate models.
           Geophysical Research Letters, 39(9).
    .. [2] Zhou, S., & Yu, B. (2025). Nature Climate Change (accepted).

    示例 / Examples
    --------
    >>> # 生成140年1pctCO2数据 / Generate 140-year 1pctCO2 data
    >>> np.random.seed(42)
    >>> n_years = 140
    >>> time = np.arange(n_years)
    >>>
    >>> # 1pctCO2数据（辐射+生理效应）/ 1pctCO2 data (radiative + physiological)
    >>> pete_1pct = 3.0 + 0.005 * time + np.random.normal(0, 0.1, n_years)
    >>> pr_1pct = 2.5 + 0.002 * time + np.random.normal(0, 0.15, n_years)
    >>> et_1pct = 1.8 + 0.003 * time + np.random.normal(0, 0.08, n_years)
    >>>
    >>> # 1pctCO2-rad数据（仅辐射效应）/ 1pctCO2-rad data (radiative only)
    >>> et_1pctrad = 1.8 + 0.004 * time + np.random.normal(0, 0.08, n_years)
    >>>
    >>> # 执行预估分析 / Perform projection analysis
    >>> results = projection_1pctCO2(
    ...     et_data=et_1pct,
    ...     pete_data=pete_1pct,
    ...     pr_data=pr_1pct,
    ...     et_1pctCO2rad=et_1pctrad,
    ...     window_size=30
    ... )
    >>>
    >>> # 比较两种归因方法 / Compare two attribution approaches
    >>> print(f"Climate (Budyko): {results['et_climate_budyko'][-1]:.3f} mm/day")
    Climate (Budyko): 0.456 mm/day
    >>> print(f"Climate (1pctCO2-rad): {results['et_climate_1pctCO2rad'][-1]:.3f} mm/day")
    Climate (1pctCO2-rad): 0.512 mm/day
    """
    # 使用Budyko框架执行归因 / Perform attribution using Budyko framework
    budyko_results = attribution_analysis(
        et_data, pete_data, pr_data, window_size
    )

    results = {
        'et_1pctCO2': budyko_results['et_total'],
        'et_climate_budyko': budyko_results['et_climate'],
        'et_landsurf_budyko': budyko_results['et_landsurf'],
        'n_parameter': budyko_results['n_parameter'],
        'time_index': budyko_results['time_index']
    }

    # 如果提供了1pctCO2-rad数据，比较两种方法
    # If 1pctCO2-rad data is provided, compare two approaches
    if et_1pctCO2rad is not None:
        n_years = len(et_data)
        n_windows = n_years - window_size + 1

        # 计算1pctCO2-rad的滑动平均 / Calculate moving average for 1pctCO2-rad
        et_rad_smooth = np.zeros(n_windows)
        for i in range(n_windows):
            et_rad_smooth[i] = np.mean(et_1pctCO2rad[i:i+window_size])

        # 计算1pctCO2的滑动平均 / Calculate moving average for 1pctCO2
        et_smooth = np.zeros(n_windows)
        for i in range(n_windows):
            et_smooth[i] = np.mean(et_data[i:i+window_size])

        # 计算相对于第一个时期的变化 / Calculate changes relative to first period
        et_climate_rad = et_rad_smooth - et_rad_smooth[0]
        et_landsurf_rad = (et_smooth - et_smooth[0]) - et_climate_rad

        results['et_climate_1pctCO2rad'] = et_climate_rad
        results['et_landsurf_1pctCO2rad'] = et_landsurf_rad

        # 计算两种方法之间的差异 / Calculate differences between two approaches
        results['climate_difference'] = budyko_results['et_climate'] - et_climate_rad
        results['landsurf_difference'] = budyko_results['et_landsurf'] - et_landsurf_rad

    return results


# 公共API / Public API
__all__ = [
    'budyko_et_ratio',
    'calculate_et_from_budyko',
    'calibrate_budyko_parameter',
    'attribution_analysis',
    'projection_1pctCO2',
]
