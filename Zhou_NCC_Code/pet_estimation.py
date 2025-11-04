"""
PET Estimation Module for Land Surface
=========================================

This module implements the calculation of energy-based PET (PETe) and 
aerodynamics-based PET (PETa) for land surfaces.

Author: Sha Zhou
Email: shazhou21@bnu.edu.cn
Date: 2025
"""

import numpy as np
from typing import Union, Dict, Tuple


def calculate_latent_heat_vaporization(temperature: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate latent heat of vaporization (MJ/kg).
    
    计算汽化潜热(MJ/kg)
    
    Parameters
    ----------
    temperature : float or np.ndarray
        Air temperature in Kelvin (K)
        气温,单位开尔文(K)
    
    Returns
    -------
    float or np.ndarray
        Latent heat of vaporization in MJ/kg
        汽化潜热,单位MJ/kg
    
    Notes
    -----
    Uses polynomial approximation as a function of temperature.
    使用温度的多项式近似。
    
    Formula:
    Lv = (2500.8 - 2.36*(T-273.15) + 0.0016*(T-273.15)^2 - 0.00006*(T-273.15)^3) / 1000
    """
    temp_celsius = temperature - 273.15
    lv = (2500.8 - 2.36 * temp_celsius + 
          0.0016 * temp_celsius**2 - 
          0.00006 * temp_celsius**3) / 1000.0
    return lv


def calculate_saturation_vapor_pressure(temperature: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate saturation vapor pressure (kPa) using Tetens formula.
    
    使用Tetens公式计算饱和水汽压(kPa)
    
    Parameters
    ----------
    temperature : float or np.ndarray
        Temperature in Kelvin (K)
        温度,单位开尔文(K)
    
    Returns
    -------
    float or np.ndarray
        Saturation vapor pressure in kPa
        饱和水汽压,单位kPa
    
    Notes
    -----
    Formula: e* = 0.611 * exp(17.27 * T_c / (T_c + 237.3))
    where T_c is temperature in Celsius
    
    Reference:
    Tetens, O. (1930). Über einige meteorologische Begriffe. 
    Zeitschrift für Geophysik, 6, 297-309.
    """
    temp_celsius = temperature - 273.15
    vp_sat = 0.611 * np.exp(17.27 * temp_celsius / (temp_celsius + 237.3))
    return vp_sat


def calculate_actual_vapor_pressure(
    specific_humidity: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate actual vapor pressure (kPa) from specific humidity.
    
    从比湿计算实际水汽压(kPa)
    
    Parameters
    ----------
    specific_humidity : float or np.ndarray
        Specific humidity in kg/kg
        比湿,单位kg/kg
    air_pressure : float or np.ndarray
        Air pressure in Pa
        气压,单位Pa
    
    Returns
    -------
    float or np.ndarray
        Actual vapor pressure in kPa
        实际水汽压,单位kPa
    
    Notes
    -----
    Conversion formula:
    w = q / (1 - q)  # mixing ratio
    e = w / (w + 0.622) * (p / 1000)  # vapor pressure in kPa
    """
    # Calculate mixing ratio from specific humidity
    # 从比湿计算混合比
    mixing_ratio = specific_humidity / (1.0 - specific_humidity)
    
    # Calculate vapor pressure from mixing ratio
    # 从混合比计算水汽压
    vapor_pressure = mixing_ratio / (mixing_ratio + 0.622) * (air_pressure / 1000.0)
    
    return vapor_pressure


def calculate_psychrometric_constant(
    latent_heat: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate psychrometric constant (kPa/K).
    
    计算干湿表常数(kPa/K)
    
    Parameters
    ----------
    latent_heat : float or np.ndarray
        Latent heat of vaporization in MJ/kg
        汽化潜热,单位MJ/kg
    air_pressure : float or np.ndarray
        Air pressure in Pa
        气压,单位Pa
    
    Returns
    -------
    float or np.ndarray
        Psychrometric constant in kPa/K
        干湿表常数,单位kPa/K
    
    Notes
    -----
    Formula: γ = cp / (Lv * 0.622) * (p / 1000)
    where cp = 1.005e-3 MJ/(kg·K) is specific heat of air at constant pressure
    """
    cp = 1.005e-3  # Specific heat of air at constant pressure (MJ/(kg·K))
    gamma = cp / (latent_heat * 0.622) * (air_pressure / 1000.0)
    return gamma


def calculate_slope_saturation_curve(
    temperature: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate slope of saturation vapor pressure curve (kPa/K).
    
    计算饱和水汽压曲线斜率(kPa/K)
    
    Parameters
    ----------
    temperature : float or np.ndarray
        Air temperature in Kelvin (K)
        气温,单位开尔文(K)
    
    Returns
    -------
    float or np.ndarray
        Slope of saturation curve in kPa/K
        饱和曲线斜率,单位kPa/K
    
    Notes
    -----
    Formula: Δ = e* × 4098 / (T_c + 237.3)^2
    where T_c is temperature in Celsius
    """
    temp_celsius = temperature - 273.15
    vp_sat = calculate_saturation_vapor_pressure(temperature)
    delta = vp_sat * 4098.0 / ((temp_celsius + 237.3) ** 2)
    return delta


def calculate_wet_bowen_ratio(
    sensible_heat: Union[float, np.ndarray],
    latent_heat: Union[float, np.ndarray],
    skin_temperature: Union[float, np.ndarray],
    air_temperature: Union[float, np.ndarray],
    specific_humidity: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Calculate wet Bowen ratio (βw) with constraints.
    
    计算湿润波文比(βw),带约束条件
    
    Parameters
    ----------
    sensible_heat : float or np.ndarray
        Sensible heat flux in W/m²
        感热通量,单位W/m²
    latent_heat : float or np.ndarray
        Latent heat flux in W/m²
        潜热通量,单位W/m²
    skin_temperature : float or np.ndarray
        Surface skin temperature in K
        地表表皮温度,单位K
    air_temperature : float or np.ndarray
        Air temperature in K
        气温,单位K
    specific_humidity : float or np.ndarray
        Specific humidity in kg/kg
        比湿,单位kg/kg
    air_pressure : float or np.ndarray
        Air pressure in Pa
        气压,单位Pa
    
    Returns
    -------
    float or np.ndarray
        Wet Bowen ratio (dimensionless)
        湿润波文比(无量纲)
    
    Notes
    -----
    The wet Bowen ratio represents the ratio of sensible to latent heat
    when the surface is saturated. Two constraints are applied:
    1. βw >= 0.24 * γ / Δ (lower bound based on ocean conditions)
    2. βw <= β (cannot exceed actual Bowen ratio)
    
    湿润波文比表示地表饱和时感热与潜热的比值。应用两个约束:
    1. βw >= 0.24 * γ / Δ (基于海洋条件的下界)
    2. βw <= β (不能超过实际波文比)
    
    Formula:
    βw = γ × (Ts - Ta) / (e*s - ea)
    """
    # Calculate required variables
    # 计算所需变量
    lv = calculate_latent_heat_vaporization(air_temperature)
    gamma = calculate_psychrometric_constant(lv, air_pressure)
    delta = calculate_slope_saturation_curve(air_temperature)
    
    # Saturation vapor pressure at surface and air temperatures
    # 地表和空气温度下的饱和水汽压
    vp_sat_surface = calculate_saturation_vapor_pressure(skin_temperature)
    vp_actual = calculate_actual_vapor_pressure(specific_humidity, air_pressure)
    
    # Calculate actual Bowen ratio
    # 计算实际波文比
    beta_actual = sensible_heat / latent_heat
    
    # Calculate theoretical wet Bowen ratio
    # 计算理论湿润波文比
    beta1 = 0.24 * gamma / delta  # Lower constraint (ocean-based)
    beta2 = gamma * (skin_temperature - air_temperature) / (vp_sat_surface - vp_actual)
    
    # Apply constraints: βw should be between beta1 and beta_actual
    # 应用约束: βw应该在beta1和beta_actual之间
    beta12 = np.maximum(beta2, beta1)
    beta_w = np.minimum(beta12, beta_actual)
    
    return beta_w


def calculate_pet_land(
    latent_heat: Union[float, np.ndarray],
    sensible_heat: Union[float, np.ndarray],
    specific_humidity: Union[float, np.ndarray],
    air_pressure: Union[float, np.ndarray],
    air_temperature: Union[float, np.ndarray],
    skin_temperature: Union[float, np.ndarray]
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate PETe and PETa for land surfaces.
    
    计算陆地表面的PETe和PETa
    
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
        - 'pete': Energy-based PET in mm/day
        - 'peta': Aerodynamics-based PET in mm/day
        - 'beta_w': Wet Bowen ratio (dimensionless)
        - 'rn': Net radiation in W/m²
        - 'et': Actual ET in mm/day
        
        包含以下键的字典:
        - 'pete': 能量基础PET,单位mm/day
        - 'peta': 空气动力学基础PET,单位mm/day
        - 'beta_w': 湿润波文比(无量纲)
        - 'rn': 净辐射,单位W/m²
        - 'et': 实际ET,单位mm/day
    
    Examples
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
    >>> print(f"PETa: {results['peta']:.2f} mm/day")
    
    Notes
    -----
    Conversion factor: 0.0864 converts W/m² to mm/day (for water)
    1 W/m² = 1 J/(s·m²) = 86400 J/(day·m²)
    For water: 1 mm = 1 kg/m² = 2.45 MJ heat (at 20°C)
    Therefore: 86400 J/(day·m²) / (2.45e6 J/kg) ≈ 0.0353 mm/day
    But using Lv variation: 0.0864 is commonly used
    
    转换因子: 0.0864将W/m²转换为mm/day(对于水)
    """
    # Convert heat fluxes from W/m² to mm/day
    # 将热通量从W/m²转换为mm/day
    CONVERSION_FACTOR = 0.0864
    hfls_mmday = latent_heat * CONVERSION_FACTOR
    hfss_mmday = sensible_heat * CONVERSION_FACTOR
    
    # Calculate latent heat of vaporization
    # 计算汽化潜热
    lv = calculate_latent_heat_vaporization(air_temperature)
    
    # Calculate wet Bowen ratio
    # 计算湿润波文比
    beta_w = calculate_wet_bowen_ratio(
        sensible_heat, latent_heat, skin_temperature,
        air_temperature, specific_humidity, air_pressure
    )
    
    # Convert heat fluxes to equivalent water depth
    # 将热通量转换为等效水深
    lh = hfls_mmday / lv
    sh = hfss_mmday / lv
    
    # Net radiation (sum of latent and sensible heat)
    # 净辐射(潜热和感热之和)
    rn = sh + lh
    
    # Calculate PETe (energy-based PET)
    # 计算PETe(能量基础PET)
    pete = rn / (1.0 + beta_w)
    
    # Calculate PETa (aerodynamics-based PET)
    # 计算PETa(空气动力学基础PET)
    peta = sh / beta_w
    
    # Actual ET
    # 实际ET
    et = lh
    
    return {
        'pete': pete,
        'peta': peta,
        'beta_w': beta_w,
        'rn': rn,
        'et': et
    }


def batch_calculate_pet(
    data: Dict[str, np.ndarray]
) -> Dict[str, np.ndarray]:
    """
    Batch calculation of PET for multiple time steps or locations.
    
    批量计算多个时间步或位置的PET
    
    Parameters
    ----------
    data : dict
        Dictionary containing arrays of input variables:
        - 'hfls': latent heat flux (W/m²)
        - 'hfss': sensible heat flux (W/m²)
        - 'huss': specific humidity (kg/kg)
        - 'ps': air pressure (Pa)
        - 'tas': air temperature (K)
        - 'ts': skin temperature (K)
        
        包含输入变量数组的字典
    
    Returns
    -------
    dict
        Dictionary with calculated PET values
        包含计算的PET值的字典
    
    Examples
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


if __name__ == "__main__":
    # Example usage
    # 示例用法
    print("PET Estimation Module")
    print("=" * 50)
    
    # Single calculation
    # 单次计算
    print("\nSingle calculation example:")
    results = calculate_pet_land(
        latent_heat=100.0,
        sensible_heat=50.0,
        specific_humidity=0.01,
        air_pressure=101325.0,
        air_temperature=298.15,
        skin_temperature=300.15
    )
    
    print(f"PETe: {results['pete']:.2f} mm/day")
    print(f"PETa: {results['peta']:.2f} mm/day")
    print(f"Wet Bowen ratio: {results['beta_w']:.3f}")
    print(f"Net radiation: {results['rn']:.2f} mm/day (water equivalent)")
    print(f"Actual ET: {results['et']:.2f} mm/day")
    
    # Batch calculation
    # 批量计算
    print("\nBatch calculation example:")
    n_samples = 10
    data = {
        'hfls': np.random.uniform(80, 120, n_samples),
        'hfss': np.random.uniform(40, 60, n_samples),
        'huss': np.random.uniform(0.008, 0.012, n_samples),
        'ps': np.random.uniform(100000, 102000, n_samples),
        'tas': np.random.uniform(295, 300, n_samples),
        'ts': np.random.uniform(297, 302, n_samples)
    }
    
    batch_results = batch_calculate_pet(data)
    print(f"Mean PETe: {np.mean(batch_results['pete']):.2f} mm/day")
    print(f"Mean PETa: {np.mean(batch_results['peta']):.2f} mm/day")
    print(f"Mean Wet Bowen ratio: {np.mean(batch_results['beta_w']):.3f}")
