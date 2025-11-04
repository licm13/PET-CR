"""
ET Projection and Attribution Module
======================================

This module implements the Budyko framework for ET projection and attribution,
separating climate change impacts from land surface changes.

Author: Sha Zhou
Email: shazhou21@bnu.edu.cn
Date: 2025
"""

import numpy as np
from typing import Union, Dict, Tuple
from scipy.optimize import minimize_scalar


def budyko_et_ratio(
    dryness_index: Union[float, np.ndarray],
    n_parameter: float = 2.0
) -> Union[float, np.ndarray]:
    """
    Calculate ET ratio using the Budyko framework (Choudhury-Yang equation).
    
    使用Budyko框架(Choudhury-Yang方程)计算ET比率
    
    Parameters
    ----------
    dryness_index : float or np.ndarray
        Dryness index (PET/P), dimensionless
        干燥度指数(PET/P),无量纲
    n_parameter : float, optional
        Budyko parameter accounting for land surface characteristics (default: 2.0)
        Budyko参数,考虑陆地表面特征(默认: 2.0)
    
    Returns
    -------
    float or np.ndarray
        ET ratio (ET/P), dimensionless
        ET比率(ET/P),无量纲
    
    Notes
    -----
    The Budyko framework relates ET/P to PET/P:
    
    ET/P = [(PET/P)^(-n) + 1]^(-1/n)
    
    where:
    - ET/P is the evaporative ratio
    - PET/P is the dryness index
    - n is a parameter reflecting land surface characteristics
    
    Budyko框架将ET/P与PET/P联系起来
    
    Reference:
    Yang, H., Yang, D., Lei, Z., & Sun, F. (2008). New analytical derivation
    of the mean annual water-energy balance equation. Water Resources Research,
    44(3), W03410.
    """
    # Ensure dryness_index is positive to avoid numerical issues
    # 确保dryness_index为正以避免数值问题
    dryness_index = np.maximum(dryness_index, 1e-10)
    
    # Calculate ET ratio using Choudhury-Yang equation
    # 使用Choudhury-Yang方程计算ET比率
    et_ratio = (dryness_index**(-n_parameter) + 1.0) ** (-1.0 / n_parameter)
    
    return et_ratio


def calculate_et_from_budyko(
    pet: Union[float, np.ndarray],
    precipitation: Union[float, np.ndarray],
    n_parameter: float = 2.0
) -> Union[float, np.ndarray]:
    """
    Calculate ET using the Budyko framework.
    
    使用Budyko框架计算ET
    
    Parameters
    ----------
    pet : float or np.ndarray
        Potential evapotranspiration (mm/day)
        潜在蒸散发(mm/day)
    precipitation : float or np.ndarray
        Precipitation (mm/day)
        降水(mm/day)
    n_parameter : float, optional
        Budyko parameter (default: 2.0)
        Budyko参数(默认: 2.0)
    
    Returns
    -------
    float or np.ndarray
        Evapotranspiration (mm/day)
        蒸散发(mm/day)
    """
    # Calculate dryness index
    # 计算干燥度指数
    # Avoid division by zero
    # 避免除以零
    precipitation_safe = np.maximum(precipitation, 1e-10)
    dryness_index = pet / precipitation_safe
    
    # Calculate ET ratio
    # 计算ET比率
    et_ratio = budyko_et_ratio(dryness_index, n_parameter)
    
    # Calculate ET
    # 计算ET
    et = precipitation * et_ratio
    
    return et


def calibrate_budyko_parameter(
    et_observed: Union[float, np.ndarray],
    pet: Union[float, np.ndarray],
    precipitation: Union[float, np.ndarray],
    bounds: Tuple[float, float] = (0.1, 10.0)
) -> float:
    """
    Calibrate the Budyko parameter n to match observed ET.
    
    校准Budyko参数n以匹配观测的ET
    
    Parameters
    ----------
    et_observed : float or np.ndarray
        Observed evapotranspiration (mm/day)
        观测的蒸散发(mm/day)
    pet : float or np.ndarray
        Potential evapotranspiration (mm/day)
        潜在蒸散发(mm/day)
    precipitation : float or np.ndarray
        Precipitation (mm/day)
        降水(mm/day)
    bounds : tuple, optional
        Bounds for n parameter (default: (0.1, 10.0))
        n参数的界限(默认: (0.1, 10.0))
    
    Returns
    -------
    float
        Calibrated n parameter
        校准的n参数
    
    Notes
    -----
    The calibration minimizes the squared difference between
    observed and predicted ET:
    
    minimize: (ET_obs - ET_pred)^2
    
    校准最小化观测和预测ET之间的平方差
    """
    # Define objective function
    # 定义目标函数
    def objective(n):
        et_predicted = calculate_et_from_budyko(pet, precipitation, n)
        
        # Calculate mean squared error
        # 计算均方误差
        if isinstance(et_predicted, np.ndarray):
            mse = np.mean((et_observed - et_predicted) ** 2)
        else:
            mse = (et_observed - et_predicted) ** 2
        
        return mse
    
    # Optimize n parameter
    # 优化n参数
    result = minimize_scalar(objective, bounds=bounds, method='bounded')
    
    if not result.success:
        raise RuntimeError(f"Calibration failed: {result.message}")
    
    return result.x


def attribution_analysis(
    et_timeseries: np.ndarray,
    pete_timeseries: np.ndarray,
    pr_timeseries: np.ndarray,
    window_size: int = 30,
    n_parameter: float = None
) -> Dict[str, np.ndarray]:
    """
    Perform attribution analysis to separate climate change and land surface effects.
    
    执行归因分析以分离气候变化和陆地表面效应
    
    Parameters
    ----------
    et_timeseries : np.ndarray
        Time series of observed ET (mm/day), shape (n_years,)
        观测ET的时间序列(mm/day),形状(n_years,)
    pete_timeseries : np.ndarray
        Time series of energy-based PET (mm/day), shape (n_years,)
        能量基础PET的时间序列(mm/day),形状(n_years,)
    pr_timeseries : np.ndarray
        Time series of precipitation (mm/day), shape (n_years,)
        降水的时间序列(mm/day),形状(n_years,)
    window_size : int, optional
        Window size for moving average (default: 30 years)
        滑动平均的窗口大小(默认: 30年)
    n_parameter : float, optional
        Budyko parameter. If None, will be calibrated from first window.
        Budyko参数。如果为None,将从第一个窗口校准。
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'et_total': Total ET changes (mm/day)
        - 'et_climate': Climate change contribution (mm/day)
        - 'et_landsurf': Land surface change contribution (mm/day)
        - 'n_parameter': Calibrated or used Budyko parameter
        - 'time_index': Time indices for the results
        
        包含以下键的字典:
        - 'et_total': 总ET变化(mm/day)
        - 'et_climate': 气候变化贡献(mm/day)
        - 'et_landsurf': 陆地表面变化贡献(mm/day)
        - 'n_parameter': 校准或使用的Budyko参数
        - 'time_index': 结果的时间索引
    
    Notes
    -----
    The attribution separates total ET changes into:
    1. Climate change effect: Changes in PETe and precipitation
    2. Land surface effect: Changes in vegetation, soil properties, etc.
    
    归因将总ET变化分为:
    1. 气候变化效应: PETe和降水的变化
    2. 陆地表面效应: 植被、土壤性质等的变化
    
    Method:
    - Uses moving averages to smooth interannual variability
    - Calibrates n from the first window if not provided
    - Keeps n constant over time to isolate land surface changes
    
    方法:
    - 使用滑动平均来平滑年际变率
    - 如果未提供,从第一个窗口校准n
    - 保持n随时间恒定以隔离陆地表面变化
    """
    n_years = len(et_timeseries)
    n_windows = n_years - window_size + 1
    
    if n_windows <= 0:
        raise ValueError(f"Time series length ({n_years}) must be >= window_size ({window_size})")
    
    # Initialize arrays for results
    # 初始化结果数组
    et_smooth = np.zeros(n_windows)
    pete_smooth = np.zeros(n_windows)
    pr_smooth = np.zeros(n_windows)
    
    # Calculate moving averages
    # 计算滑动平均
    for i in range(n_windows):
        et_smooth[i] = np.mean(et_timeseries[i:i+window_size])
        pete_smooth[i] = np.mean(pete_timeseries[i:i+window_size])
        pr_smooth[i] = np.mean(pr_timeseries[i:i+window_size])
    
    # Calibrate n parameter from the first window if not provided
    # 如果未提供,从第一个窗口校准n参数
    if n_parameter is None:
        n_parameter = calibrate_budyko_parameter(
            et_smooth[0], pete_smooth[0], pr_smooth[0]
        )
    
    # Calculate climate-driven ET using constant n
    # 使用恒定的n计算气候驱动的ET
    et_climate = calculate_et_from_budyko(pete_smooth, pr_smooth, n_parameter)
    
    # Calculate land surface contribution (residual)
    # 计算陆地表面贡献(残差)
    et_landsurf = et_smooth - et_climate
    
    # Calculate changes relative to first period
    # 计算相对于第一个时期的变化
    et_total_change = et_smooth - et_smooth[0]
    et_climate_change = et_climate - et_climate[0]
    et_landsurf_change = et_landsurf - et_landsurf[0]
    
    # Time indices (first year of each window)
    # 时间索引(每个窗口的第一年)
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
    et_1pctCO2rad: np.ndarray = None,
    window_size: int = 30
) -> Dict[str, np.ndarray]:
    """
    Perform ET projection and attribution for 1pctCO2 experiments.
    
    为1pctCO2实验执行ET预估和归因
    
    Parameters
    ----------
    et_data : np.ndarray
        ET from 1pctCO2 experiment (mm/day), shape (n_years,)
        1pctCO2实验的ET(mm/day),形状(n_years,)
    pete_data : np.ndarray
        Energy-based PET from 1pctCO2 (mm/day), shape (n_years,)
        1pctCO2的能量基础PET(mm/day),形状(n_years,)
    pr_data : np.ndarray
        Precipitation from 1pctCO2 (mm/day), shape (n_years,)
        1pctCO2的降水(mm/day),形状(n_years,)
    et_1pctCO2rad : np.ndarray, optional
        ET from 1pctCO2-rad experiment (radiative forcing only)
        If provided, will compare two attribution approaches
        1pctCO2-rad实验的ET(仅辐射强迫)
        如果提供,将比较两种归因方法
    window_size : int, optional
        Window size for moving average (default: 30 years)
        滑动平均的窗口大小(默认: 30年)
    
    Returns
    -------
    dict
        Dictionary containing projection and attribution results
        包含预估和归因结果的字典
    
    Notes
    -----
    The 1pctCO2 experiment increases CO2 by 1% per year, affecting both
    atmosphere (radiative) and land surface (physiological).
    
    The 1pctCO2-rad experiment only includes radiative forcing,
    isolating climate change effects.
    
    1pctCO2实验每年增加1%的CO2,影响大气(辐射)和陆地表面(生理)。
    1pctCO2-rad实验仅包括辐射强迫,隔离气候变化效应。
    """
    # Perform attribution using Budyko framework
    # 使用Budyko框架执行归因
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
    
    # If 1pctCO2-rad data is provided, compare two approaches
    # 如果提供了1pctCO2-rad数据,比较两种方法
    if et_1pctCO2rad is not None:
        n_years = len(et_data)
        n_windows = n_years - window_size + 1
        
        # Calculate moving average for 1pctCO2-rad
        # 计算1pctCO2-rad的滑动平均
        et_rad_smooth = np.zeros(n_windows)
        for i in range(n_windows):
            et_rad_smooth[i] = np.mean(et_1pctCO2rad[i:i+window_size])
        
        # Calculate moving average for 1pctCO2
        # 计算1pctCO2的滑动平均
        et_smooth = np.zeros(n_windows)
        for i in range(n_windows):
            et_smooth[i] = np.mean(et_data[i:i+window_size])
        
        # Calculate changes relative to first period
        # 计算相对于第一个时期的变化
        et_climate_rad = et_rad_smooth - et_rad_smooth[0]
        et_landsurf_rad = (et_smooth - et_smooth[0]) - et_climate_rad
        
        results['et_climate_1pctCO2rad'] = et_climate_rad
        results['et_landsurf_1pctCO2rad'] = et_landsurf_rad
        
        # Calculate differences between two approaches
        # 计算两种方法之间的差异
        results['climate_difference'] = budyko_results['et_climate'] - et_climate_rad
        results['landsurf_difference'] = budyko_results['et_landsurf'] - et_landsurf_rad
    
    return results


if __name__ == "__main__":
    # Example usage
    # 示例用法
    print("ET Projection and Attribution Module")
    print("=" * 60)
    
    # Generate synthetic time series data (140 years)
    # 生成合成时间序列数据(140年)
    np.random.seed(42)
    n_years = 140
    
    # Create increasing trends for climate change
    # 为气候变化创建增加趋势
    time = np.arange(n_years)
    
    # PETe increases with warming
    # PETe随变暖增加
    pete_trend = 3.0 + 0.005 * time + np.random.normal(0, 0.1, n_years)
    
    # Precipitation has slight increase
    # 降水略有增加
    pr_trend = 2.5 + 0.002 * time + np.random.normal(0, 0.15, n_years)
    
    # ET increases with both climate and land surface changes
    # ET随气候和陆地表面变化增加
    et_climate_component = 1.8 + 0.004 * time
    et_landsurf_component = -0.001 * time  # Slight decrease due to CO2 physiological effect
    et_trend = et_climate_component + et_landsurf_component + np.random.normal(0, 0.08, n_years)
    
    # Perform attribution analysis
    # 执行归因分析
    print("\n1. Attribution Analysis (Budyko Framework)")
    print("-" * 60)
    
    results = attribution_analysis(
        et_timeseries=et_trend,
        pete_timeseries=pete_trend,
        pr_timeseries=pr_trend,
        window_size=30
    )
    
    print(f"Calibrated n parameter: {results['n_parameter']:.3f}")
    print(f"Number of 30-year windows: {len(results['time_index'])}")
    
    # Show changes at different time periods
    # 显示不同时期的变化
    periods = [0, len(results['time_index'])//2, len(results['time_index'])-1]
    period_names = ['Initial', 'Middle', 'Final']
    
    print("\nET Changes (mm/day):")
    print(f"{'Period':<15} {'Total':<10} {'Climate':<10} {'Land Surf':<10}")
    print("-" * 50)
    for period, name in zip(periods, period_names):
        print(f"{name:<15} "
              f"{results['et_total'][period]:>9.3f} "
              f"{results['et_climate'][period]:>9.3f} "
              f"{results['et_landsurf'][period]:>9.3f}")
    
    # 2. 1pctCO2 experiment analysis
    # 2. 1pctCO2实验分析
    print("\n2. 1pctCO2 Experiment Analysis")
    print("-" * 60)
    
    # Generate 1pctCO2-rad data (climate change only)
    # 生成1pctCO2-rad数据(仅气候变化)
    et_1pctCO2rad = et_climate_component + np.random.normal(0, 0.08, n_years)
    
    # Perform projection analysis
    # 执行预估分析
    proj_results = projection_1pctCO2(
        et_data=et_trend,
        pete_data=pete_trend,
        pr_data=pr_trend,
        et_1pctCO2rad=et_1pctCO2rad,
        window_size=30
    )
    
    print(f"\nComparison of Two Attribution Approaches:")
    print(f"{'Period':<15} {'Budyko':<12} {'1pctCO2-rad':<12} {'Difference':<12}")
    print("-" * 55)
    
    # Climate change contribution
    # 气候变化贡献
    print("Climate Change Contribution:")
    for period, name in zip(periods, period_names):
        budyko_val = proj_results['et_climate_budyko'][period]
        rad_val = proj_results['et_climate_1pctCO2rad'][period]
        diff = proj_results['climate_difference'][period]
        print(f"{name:<15} {budyko_val:>11.3f} {rad_val:>11.3f} {diff:>11.3f}")
    
    # Land surface contribution
    # 陆地表面贡献
    print("\nLand Surface Contribution:")
    for period, name in zip(periods, period_names):
        budyko_val = proj_results['et_landsurf_budyko'][period]
        rad_val = proj_results['et_landsurf_1pctCO2rad'][period]
        diff = proj_results['landsurf_difference'][period]
        print(f"{name:<15} {budyko_val:>11.3f} {rad_val:>11.3f} {diff:>11.3f}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
