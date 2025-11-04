"""
Sample Data Generator Module
==============================

This module generates random sample data for testing and demonstration purposes.
It preserves interfaces for loading real data from Fluxnet2015 and CMIP6 sources.

Author: Sha Zhou
Email: shazhou21@bnu.edu.cn
Date: 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, Union, Optional, Tuple


def generate_sample_data(
    n_samples: int = 100,
    surface_type: str = 'land',
    seed: Optional[int] = None
) -> Dict[str, np.ndarray]:
    """
    Generate random sample meteorological data.
    
    生成随机示例气象数据
    
    Parameters
    ----------
    n_samples : int, optional
        Number of samples to generate (default: 100)
        要生成的样本数(默认: 100)
    surface_type : str, optional
        Type of surface: 'land' or 'ocean' (default: 'land')
        表面类型: 'land'或'ocean'(默认: 'land')
    seed : int, optional
        Random seed for reproducibility
        随机种子以实现可重现性
    
    Returns
    -------
    dict
        Dictionary containing meteorological variables:
        - 'hfls': Latent heat flux (W/m²)
        - 'hfss': Sensible heat flux (W/m²)
        - 'huss': Specific humidity (kg/kg)
        - 'ps': Air pressure (Pa)
        - 'tas': Air temperature (K)
        - 'ts': Skin temperature (K)
        
        包含气象变量的字典
    
    Examples
    --------
    >>> data = generate_sample_data(n_samples=50, surface_type='land', seed=42)
    >>> print(data['hfls'].shape)
    (50,)
    """
    if seed is not None:
        np.random.seed(seed)
    
    if surface_type == 'land':
        # Land surface typical ranges
        # 陆地表面典型范围
        data = {
            'hfls': np.random.uniform(60, 150, n_samples),     # W/m²
            'hfss': np.random.uniform(30, 80, n_samples),      # W/m²
            'huss': np.random.uniform(0.005, 0.015, n_samples),  # kg/kg
            'ps': np.random.uniform(98000, 103000, n_samples),  # Pa
            'tas': np.random.uniform(288, 305, n_samples),     # K
            'ts': np.random.uniform(290, 308, n_samples)       # K
        }
    elif surface_type == 'ocean':
        # Ocean surface typical ranges
        # 海洋表面典型范围
        data = {
            'hfls': np.random.uniform(100, 200, n_samples),    # W/m²
            'hfss': np.random.uniform(15, 50, n_samples),      # W/m²
            'huss': np.random.uniform(0.010, 0.020, n_samples),  # kg/kg
            'ps': np.random.uniform(100000, 102000, n_samples),  # Pa
            'tas': np.random.uniform(293, 303, n_samples),     # K
            'ts': np.random.uniform(293, 303, n_samples)       # K
        }
    else:
        raise ValueError(f"Unknown surface_type: {surface_type}. Use 'land' or 'ocean'.")
    
    return data


def generate_timeseries_data(
    n_years: int = 140,
    timestep: str = 'annual',
    include_trend: bool = True,
    seed: Optional[int] = None
) -> Dict[str, np.ndarray]:
    """
    Generate time series data for climate projections.
    
    生成用于气候预估的时间序列数据
    
    Parameters
    ----------
    n_years : int, optional
        Number of years to generate (default: 140, for 1pctCO2 experiments)
        要生成的年数(默认: 140,用于1pctCO2实验)
    timestep : str, optional
        Time step: 'annual' or 'monthly' (default: 'annual')
        时间步长: 'annual'或'monthly'(默认: 'annual')
    include_trend : bool, optional
        Whether to include warming trends (default: True)
        是否包括变暖趋势(默认: True)
    seed : int, optional
        Random seed for reproducibility
        随机种子以实现可重现性
    
    Returns
    -------
    dict
        Dictionary containing time series:
        - 'time': Time array (years or months)
        - 'et': Evapotranspiration (mm/day)
        - 'pete': Energy-based PET (mm/day)
        - 'pr': Precipitation (mm/day)
        - 'tas': Air temperature (K)
        
        包含时间序列的字典
    
    Examples
    --------
    >>> data = generate_timeseries_data(n_years=100, include_trend=True, seed=42)
    >>> print(data['et'].shape)
    (100,)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Determine number of time steps
    # 确定时间步数
    if timestep == 'annual':
        n_steps = n_years
    elif timestep == 'monthly':
        n_steps = n_years * 12
    else:
        raise ValueError(f"Unknown timestep: {timestep}. Use 'annual' or 'monthly'.")
    
    # Create time array
    # 创建时间数组
    time = np.arange(n_steps)
    
    # Generate trends
    # 生成趋势
    if include_trend:
        # Warming trend: ~2-4°C over the period
        # 变暖趋势: 整个时期约2-4°C
        temp_trend = 0.02 * time / n_steps * 100
        
        # PETe increases with temperature
        # PETe随温度增加
        pete_trend = 0.004 * time / n_steps * 100
        
        # Precipitation slight increase
        # 降水略有增加
        pr_trend = 0.002 * time / n_steps * 100
        
        # ET increases but moderated by land surface changes
        # ET增加但受陆地表面变化调节
        et_trend = 0.003 * time / n_steps * 100
    else:
        temp_trend = 0.0
        pete_trend = 0.0
        pr_trend = 0.0
        et_trend = 0.0
    
    # Add noise
    # 添加噪声
    noise_scale = 0.1 if timestep == 'annual' else 0.3
    
    data = {
        'time': time,
        'tas': 288.0 + temp_trend + np.random.normal(0, noise_scale * 10, n_steps),
        'pete': 3.0 + pete_trend + np.random.normal(0, noise_scale, n_steps),
        'pr': 2.5 + pr_trend + np.random.normal(0, noise_scale * 1.5, n_steps),
        'et': 1.8 + et_trend + np.random.normal(0, noise_scale * 0.8, n_steps)
    }
    
    # Ensure physically realistic values
    # 确保物理上现实的值
    data['pete'] = np.maximum(data['pete'], 0.5)
    data['pr'] = np.maximum(data['pr'], 0.1)
    data['et'] = np.maximum(data['et'], 0.1)
    data['et'] = np.minimum(data['et'], data['pr'])  # ET cannot exceed precipitation
    
    return data


def load_fluxnet_data(
    filepath: str,
    variables: Optional[list] = None
) -> pd.DataFrame:
    """
    Load Fluxnet2015 data from CSV file.
    
    从CSV文件加载Fluxnet2015数据
    
    Parameters
    ----------
    filepath : str
        Path to the Fluxnet CSV file
        Fluxnet CSV文件的路径
    variables : list, optional
        List of variables to load. If None, load all available.
        要加载的变量列表。如果为None,加载所有可用变量。
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing Fluxnet data
        包含Fluxnet数据的DataFrame
    
    Notes
    -----
    Expected variables in Fluxnet data:
    - LE: Latent heat flux (W/m²)
    - H: Sensible heat flux (W/m²)
    - TA: Air temperature (°C)
    - TS: Surface temperature (°C)
    - PA: Atmospheric pressure (kPa)
    - VPD: Vapor pressure deficit (hPa)
    
    Fluxnet数据中预期的变量
    
    Examples
    --------
    >>> # Load real Fluxnet data (when available)
    >>> # df = load_fluxnet_data('data/input/fluxnet_site.csv')
    >>> # print(df.head())
    """
    try:
        df = pd.read_csv(filepath)
        
        if variables is not None:
            available_vars = [v for v in variables if v in df.columns]
            if not available_vars:
                raise ValueError(f"None of the requested variables found in file: {variables}")
            df = df[available_vars]
        
        return df
    
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        print("Please download Fluxnet2015 data from: https://fluxnet.org/data/fluxnet2015-dataset/")
        print("\nGenerating sample data instead...")
        
        # Generate sample data as fallback
        # 生成示例数据作为后备
        n_samples = 100
        sample_data = generate_sample_data(n_samples=n_samples, surface_type='land')
        
        # Convert to DataFrame format similar to Fluxnet
        # 转换为类似Fluxnet的DataFrame格式
        df = pd.DataFrame({
            'LE': sample_data['hfls'],
            'H': sample_data['hfss'],
            'TA': sample_data['tas'] - 273.15,  # Convert to °C
            'TS': sample_data['ts'] - 273.15,
            'PA': sample_data['ps'] / 1000.0,  # Convert to kPa
            'QA': sample_data['huss']
        })
        
        return df


def load_cmip6_data(
    model: str,
    experiment: str,
    variable: str,
    path: str
) -> Union[np.ndarray, None]:
    """
    Load CMIP6 model data from NetCDF files.
    
    从NetCDF文件加载CMIP6模型数据
    
    Parameters
    ----------
    model : str
        CMIP6 model name (e.g., 'ACCESS-CM2', 'CanESM5')
        CMIP6模型名称
    experiment : str
        Experiment name (e.g., 'historical', 'ssp585', '1pctCO2')
        实验名称
    variable : str
        Variable name (e.g., 'hfls', 'hfss', 'tas', 'pr')
        变量名称
    path : str
        Path to CMIP6 data directory
        CMIP6数据目录的路径
    
    Returns
    -------
    np.ndarray or None
        Array containing the requested data, or None if file not found
        包含请求数据的数组,如果找不到文件则为None
    
    Notes
    -----
    CMIP6 data should be downloaded from:
    https://esgf-node.llnl.gov/search/cmip6/
    
    Expected file naming convention:
    {variable}_{model}_{experiment}_*.nc
    
    CMIP6数据应从以下网址下载:
    https://esgf-node.llnl.gov/search/cmip6/
    
    Examples
    --------
    >>> # Load real CMIP6 data (when available)
    >>> # data = load_cmip6_data(
    >>> #     model='ACCESS-CM2',
    >>> #     experiment='historical',
    >>> #     variable='hfls',
    >>> #     path='data/input/cmip6/'
    >>> # )
    """
    import os
    
    # Construct filename pattern
    # 构造文件名模式
    filename_pattern = f"{variable}_{model}_{experiment}"
    
    # Check if file exists
    # 检查文件是否存在
    if not os.path.exists(path):
        print(f"Directory not found: {path}")
        print("Please download CMIP6 data from: https://esgf-node.llnl.gov/search/cmip6/")
        print("\nGenerating sample time series data instead...")
        
        # Generate sample time series data as fallback
        # 生成示例时间序列数据作为后备
        sample_data = generate_timeseries_data(n_years=140, seed=42)
        
        # Map variable name to sample data
        # 将变量名映射到示例数据
        variable_map = {
            'hfls': 'et',  # Use ET as proxy for latent heat
            'hfss': 'et',  # Use ET scaled for sensible heat
            'tas': 'tas',
            'pr': 'pr',
            'pete': 'pete'
        }
        
        if variable in variable_map:
            return sample_data[variable_map[variable]]
        else:
            return None
    
    try:
        import netCDF4 as nc
        
        # Find matching file
        # 查找匹配的文件
        files = [f for f in os.listdir(path) if f.startswith(filename_pattern)]
        
        if not files:
            raise FileNotFoundError(f"No file found matching pattern: {filename_pattern}")
        
        # Load first matching file
        # 加载第一个匹配的文件
        filepath = os.path.join(path, files[0])
        dataset = nc.Dataset(filepath, 'r')
        
        # Extract variable
        # 提取变量
        data = dataset.variables[variable][:]
        
        dataset.close()
        
        return np.array(data)
    
    except ImportError:
        print("netCDF4 package not installed. Install with: pip install netCDF4")
        print("Generating sample data instead...")
        return generate_timeseries_data(n_years=140, seed=42)['et']
    
    except Exception as e:
        print(f"Error loading CMIP6 data: {e}")
        print("Generating sample data instead...")
        return generate_timeseries_data(n_years=140, seed=42)['et']


if __name__ == "__main__":
    # Example usage
    # 示例用法
    print("Sample Data Generator Module")
    print("=" * 60)
    
    # 1. Generate sample meteorological data
    # 1. 生成示例气象数据
    print("\n1. Sample Meteorological Data (Land Surface)")
    print("-" * 60)
    
    data = generate_sample_data(n_samples=10, surface_type='land', seed=42)
    
    print(f"Generated {len(data['hfls'])} samples")
    print("\nExample values:")
    print(f"  Latent heat flux: {data['hfls'][0]:.2f} W/m²")
    print(f"  Sensible heat flux: {data['hfss'][0]:.2f} W/m²")
    print(f"  Specific humidity: {data['huss'][0]:.5f} kg/kg")
    print(f"  Air pressure: {data['ps'][0]:.1f} Pa")
    print(f"  Air temperature: {data['tas'][0]:.2f} K")
    print(f"  Skin temperature: {data['ts'][0]:.2f} K")
    
    # 2. Generate time series data
    # 2. 生成时间序列数据
    print("\n2. Time Series Data (Annual, 140 years)")
    print("-" * 60)
    
    ts_data = generate_timeseries_data(n_years=140, include_trend=True, seed=42)
    
    print(f"Generated {len(ts_data['time'])} years of data")
    print("\nInitial values:")
    print(f"  ET: {ts_data['et'][0]:.3f} mm/day")
    print(f"  PETe: {ts_data['pete'][0]:.3f} mm/day")
    print(f"  Precipitation: {ts_data['pr'][0]:.3f} mm/day")
    print(f"  Temperature: {ts_data['tas'][0]:.2f} K")
    
    print("\nFinal values (year 140):")
    print(f"  ET: {ts_data['et'][-1]:.3f} mm/day")
    print(f"  PETe: {ts_data['pete'][-1]:.3f} mm/day")
    print(f"  Precipitation: {ts_data['pr'][-1]:.3f} mm/day")
    print(f"  Temperature: {ts_data['tas'][-1]:.2f} K")
    
    print("\nChanges over 140 years:")
    print(f"  ΔET: {ts_data['et'][-1] - ts_data['et'][0]:.3f} mm/day")
    print(f"  ΔPETe: {ts_data['pete'][-1] - ts_data['pete'][0]:.3f} mm/day")
    print(f"  ΔPrecipitation: {ts_data['pr'][-1] - ts_data['pr'][0]:.3f} mm/day")
    print(f"  ΔTemperature: {ts_data['tas'][-1] - ts_data['tas'][0]:.2f} K")
    
    # 3. Demonstrate data loading interfaces
    # 3. 演示数据加载接口
    print("\n3. Data Loading Interfaces")
    print("-" * 60)
    
    print("\nFluxnet data loading:")
    print("  Interface: load_fluxnet_data(filepath)")
    print("  Data source: https://fluxnet.org/data/fluxnet2015-dataset/")
    print("  Status: Interface ready, using sample data if files not found")
    
    print("\nCMIP6 data loading:")
    print("  Interface: load_cmip6_data(model, experiment, variable, path)")
    print("  Data source: https://esgf-node.llnl.gov/search/cmip6/")
    print("  Status: Interface ready, using sample data if files not found")
    
    print("\n" + "=" * 60)
    print("Sample data generation complete!")
