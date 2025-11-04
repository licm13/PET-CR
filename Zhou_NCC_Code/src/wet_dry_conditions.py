"""
PET Estimation Under Wet and Driest Conditions (Ocean Surfaces)
==================================================================

This module calculates PETe and PETa under wet (ocean) and hypothetically
driest conditions to assess sensitivity to surface moisture changes.

Author: Sha Zhou
Email: shazhou21@bnu.edu.cn
Date: 2025
"""

import numpy as np
from typing import Union, Dict
from .pet_estimation import (
    calculate_latent_heat_vaporization,
    calculate_saturation_vapor_pressure,
    calculate_actual_vapor_pressure,
    calculate_psychrometric_constant
)


def calculate_pet_ocean(
    latent_heat: Union[float, np.ndarray],
    sensible_heat: Union[float, np.ndarray],
    specific_humidity: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray],
    air_temperature: Union[float, np.ndarray],
    skin_temperature: Union[float, np.ndarray]
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate PETe and PETa under wet and driest conditions for ocean surfaces.
    
    计算海洋表面在湿润和最干条件下的PETe和PETa
    
    This function estimates how PETe and PETa change when surface moisture
    transitions from wet (ocean) to hypothetically driest conditions, while
    maintaining constant moist enthalpy.
    
    此函数估计当地表湿度从湿润(海洋)过渡到假设的最干条件时,
    PETe和PETa如何变化,同时保持湿焓不变。
    
    Parameters
    ----------
    latent_heat : float or np.ndarray
        Latent heat flux in W/m²
        潜热通量,单位W/m²
    sensible_heat : float or np.ndarray
        Sensible heat flux in W/m²
        感热通量,单位W/m²
    specific_humidity : float or np.ndarray
        Specific humidity in kg/kg
        比湿,单位kg/kg
    air_pressure : float or np.ndarray
        Air pressure in Pa
        气压,单位Pa
    air_temperature : float or np.ndarray
        Air temperature in K
        气温,单位K
    skin_temperature : float or np.ndarray
        Surface skin temperature in K
        地表表皮温度,单位K
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'et': Actual ET over ocean (mm/day)
        - 'beta': Bowen ratio over ocean
        - 'beta_w_wet': Wet Bowen ratio under wet conditions
        - 'beta_w_driest': Wet Bowen ratio under driest conditions
        - 'pete_wet': PETe under wet conditions (mm/day)
        - 'peta_wet': PETa under wet conditions (mm/day)
        - 'pete_driest': PETe under driest conditions (mm/day)
        - 'peta_driest': PETa under driest conditions (mm/day)
        - 'temp_diff': Temperature difference from wet to driest (K)
        
        包含以下键的字典:
        - 'et': 海洋上的实际ET (mm/day)
        - 'beta': 海洋上的波文比
        - 'beta_w_wet': 湿润条件下的湿润波文比
        - 'beta_w_driest': 最干条件下的湿润波文比
        - 'pete_wet': 湿润条件下的PETe (mm/day)
        - 'peta_wet': 湿润条件下的PETa (mm/day)
        - 'pete_driest': 最干条件下的PETe (mm/day)
        - 'peta_driest': 最干条件下的PETa (mm/day)
        - 'temp_diff': 从湿润到最干的温度差异 (K)
    
    Notes
    -----
    The calculation assumes:
    1. Constant moist enthalpy: T + e/γ = constant
    2. Under driest conditions: vapor pressure → 0
    3. Energy balance: Rn = sensible heat + latent heat
    
    计算假设:
    1. 恒定湿焓: T + e/γ = 常数
    2. 最干条件下: 水汽压 → 0
    3. 能量平衡: Rn = 感热 + 潜热
    
    Reference:
    Zhou, S., & Yu, B. (2024). Physical basis of the potential evapotranspiration
    and its estimation over land. Journal of Hydrology, 641, 131825.
    """
    # Convert heat fluxes from W/m² to mm/day
    # 将热通量从W/m²转换为mm/day
    CONVERSION_FACTOR = 0.0864
    hfls_mmday = latent_heat * CONVERSION_FACTOR
    hfss_mmday = sensible_heat * CONVERSION_FACTOR
    
    # Calculate latent heat of vaporization
    # 计算汽化潜热
    lv = calculate_latent_heat_vaporization(air_temperature)
    
    # Calculate vapor pressures
    # 计算水汽压
    vp_sat_air = calculate_saturation_vapor_pressure(air_temperature)
    vp_sat_surface = calculate_saturation_vapor_pressure(skin_temperature)
    vp_actual = calculate_actual_vapor_pressure(specific_humidity, air_pressure)
    
    # Calculate psychrometric constant
    # 计算干湿表常数
    gamma = calculate_psychrometric_constant(lv, air_pressure)
    
    # ========================================
    # Under driest conditions (vapor pressure → 0)
    # 最干条件下(水汽压 → 0)
    # ========================================
    
    # Temperature under driest conditions (assuming constant moist enthalpy)
    # 最干条件下的温度(假设恒定湿焓)
    # T_driest = T + e/γ (since e_driest → 0)
    air_temp_driest = air_temperature + vp_actual / gamma
    surface_temp_driest = skin_temperature + vp_sat_surface / gamma
    
    # Saturation vapor pressure at driest surface temperature
    # 最干条件下地表温度的饱和水汽压
    vp_sat_surface_driest = calculate_saturation_vapor_pressure(surface_temp_driest)
    
    # ========================================
    # Bowen ratios
    # 波文比
    # ========================================
    
    # Actual Bowen ratio over ocean
    # 海洋上的实际波文比
    beta_actual = sensible_heat / latent_heat
    
    # Wet Bowen ratio under wet conditions (ocean surface)
    # 湿润条件下的湿润波文比(海洋表面)
    beta_w_wet = gamma * (skin_temperature - air_temperature) / \
                 (vp_sat_surface - vp_actual)
    
    # Wet Bowen ratio under driest conditions
    # 最干条件下的湿润波文比
    beta_w_driest = gamma * (surface_temp_driest - air_temp_driest) / \
                    vp_sat_surface_driest
    
    # ========================================
    # Calculate ET and fluxes
    # 计算ET和通量
    # ========================================
    
    # Convert heat fluxes to equivalent water depth
    # 将热通量转换为等效水深
    lh = hfls_mmday / lv
    sh = hfss_mmday / lv
    
    # Net radiation (sum of latent and sensible heat)
    # 净辐射(潜热和感热之和)
    rn = sh + lh
    
    # ========================================
    # PET under wet conditions
    # 湿润条件下的PET
    # ========================================
    
    # PETe under wet conditions
    # 湿润条件下的PETe
    pete_wet = rn / (1.0 + beta_w_wet)
    
    # PETa under wet conditions
    # 湿润条件下的PETa
    peta_wet = sh / beta_w_wet
    
    # ========================================
    # PET under driest conditions
    # 最干条件下的PET
    # ========================================
    
    # PETe under driest conditions
    # 最干条件下的PETe
    pete_driest = rn / (1.0 + beta_w_driest)
    
    # PETa under driest conditions
    # 最干条件下的PETa
    # Note: Under driest conditions, latent heat → 0, so all Rn → sensible heat
    # 注意: 最干条件下,潜热 → 0,所以所有Rn → 感热
    peta_driest = rn / beta_w_driest
    
    # ========================================
    # Temperature difference
    # 温度差异
    # ========================================
    
    # Mean temperature difference from wet to driest conditions
    # 从湿润到最干条件的平均温度差异
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


def calculate_pet_sensitivity(
    latent_heat: Union[float, np.ndarray],
    sensible_heat: Union[float, np.ndarray],
    specific_humidity: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray],
    air_temperature: Union[float, np.ndarray],
    skin_temperature: Union[float, np.ndarray]
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate sensitivity of PETe and PETa to surface moisture changes.
    
    计算PETe和PETa对地表湿度变化的敏感性
    
    Parameters
    ----------
    Similar to calculate_pet_ocean()
    与calculate_pet_ocean()相同
    
    Returns
    -------
    dict
        Dictionary containing sensitivity metrics:
        - 'dpete_dt': Sensitivity of PETe to temperature (mm/day/K)
        - 'dpeta_dt': Sensitivity of PETa to temperature (mm/day/K)
        - 'relative_pete_change': Relative change in PETe (%)
        - 'relative_peta_change': Relative change in PETa (%)
        
        包含敏感性指标的字典:
        - 'dpete_dt': PETe对温度的敏感性 (mm/day/K)
        - 'dpeta_dt': PETa对温度的敏感性 (mm/day/K)
        - 'relative_pete_change': PETe的相对变化 (%)
        - 'relative_peta_change': PETa的相对变化 (%)
    
    Notes
    -----
    Sensitivity is calculated as the ratio of changes in PET to changes
    in mean temperature between wet and driest conditions.
    
    敏感性计算为PET变化与湿润和最干条件之间平均温度变化的比率。
    """
    # Calculate PET under wet and driest conditions
    # 计算湿润和最干条件下的PET
    results = calculate_pet_ocean(
        latent_heat, sensible_heat, specific_humidity,
        air_pressure, air_temperature, skin_temperature
    )
    
    # Extract values
    # 提取值
    pete_wet = results['pete_wet']
    peta_wet = results['peta_wet']
    pete_driest = results['pete_driest']
    peta_driest = results['peta_driest']
    temp_diff = results['temp_diff']
    
    # Calculate sensitivities (change per degree K)
    # 计算敏感性(每K的变化)
    # Avoid division by zero
    # 避免除以零
    temp_diff_safe = np.where(np.abs(temp_diff) < 1e-10, np.nan, temp_diff)
    
    dpete_dt = (pete_driest - pete_wet) / temp_diff_safe
    dpeta_dt = (peta_driest - peta_wet) / temp_diff_safe
    
    # Calculate relative changes (%)
    # 计算相对变化(%)
    pete_wet_safe = np.where(np.abs(pete_wet) < 1e-10, np.nan, pete_wet)
    peta_wet_safe = np.where(np.abs(peta_wet) < 1e-10, np.nan, peta_wet)
    
    relative_pete_change = (pete_driest - pete_wet) / pete_wet_safe * 100.0
    relative_peta_change = (peta_driest - peta_wet) / peta_wet_safe * 100.0
    
    return {
        'dpete_dt': dpete_dt,
        'dpeta_dt': dpeta_dt,
        'relative_pete_change': relative_pete_change,
        'relative_peta_change': relative_peta_change,
        **results  # Include all ocean calculation results
    }


if __name__ == "__main__":
    # Example usage
    # 示例用法
    print("PET Under Wet and Driest Conditions")
    print("=" * 50)
    
    # Single calculation for ocean surface
    # 海洋表面的单次计算
    print("\nOcean surface example:")
    results = calculate_pet_ocean(
        latent_heat=150.0,
        sensible_heat=30.0,
        specific_humidity=0.015,
        air_pressure=101325.0,
        air_temperature=298.15,
        skin_temperature=299.15
    )
    
    print(f"\nUnder wet conditions:")
    print(f"  PETe: {results['pete_wet']:.2f} mm/day")
    print(f"  PETa: {results['peta_wet']:.2f} mm/day")
    print(f"  Wet Bowen ratio: {results['beta_w_wet']:.3f}")
    
    print(f"\nUnder driest conditions:")
    print(f"  PETe: {results['pete_driest']:.2f} mm/day")
    print(f"  PETa: {results['peta_driest']:.2f} mm/day")
    print(f"  Wet Bowen ratio: {results['beta_w_driest']:.3f}")
    
    print(f"\nTemperature difference: {results['temp_diff']:.2f} K")
    print(f"Actual ET: {results['et']:.2f} mm/day")
    print(f"Actual Bowen ratio: {results['beta']:.3f}")
    
    # Sensitivity analysis
    # 敏感性分析
    print("\n" + "=" * 50)
    print("Sensitivity Analysis")
    print("=" * 50)
    
    sensitivity = calculate_pet_sensitivity(
        latent_heat=150.0,
        sensible_heat=30.0,
        specific_humidity=0.015,
        air_pressure=101325.0,
        air_temperature=298.15,
        skin_temperature=299.15
    )
    
    print(f"\nSensitivity to temperature:")
    print(f"  dPETe/dT: {sensitivity['dpete_dt']:.4f} mm/day/K")
    print(f"  dPETa/dT: {sensitivity['dpeta_dt']:.4f} mm/day/K")
    
    print(f"\nRelative changes:")
    print(f"  PETe change: {sensitivity['relative_pete_change']:.2f}%")
    print(f"  PETa change: {sensitivity['relative_peta_change']:.2f}%")
    
    # Batch calculation
    # 批量计算
    print("\n" + "=" * 50)
    print("Batch Calculation Example")
    print("=" * 50)
    
    n_samples = 10
    batch_results = calculate_pet_ocean(
        latent_heat=np.random.uniform(140, 160, n_samples),
        sensible_heat=np.random.uniform(25, 35, n_samples),
        specific_humidity=np.random.uniform(0.013, 0.017, n_samples),
        air_pressure=np.random.uniform(100000, 102000, n_samples),
        air_temperature=np.random.uniform(297, 300, n_samples),
        skin_temperature=np.random.uniform(298, 301, n_samples)
    )
    
    print(f"\nMean PETe (wet): {np.mean(batch_results['pete_wet']):.2f} mm/day")
    print(f"Mean PETa (wet): {np.mean(batch_results['peta_wet']):.2f} mm/day")
    print(f"Mean PETe (driest): {np.mean(batch_results['pete_driest']):.2f} mm/day")
    print(f"Mean PETa (driest): {np.mean(batch_results['peta_driest']):.2f} mm/day")
