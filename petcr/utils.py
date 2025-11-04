"""
数据生成和加载工具模块 / Data Generation and Loading Utilities Module
================================================================================

本模块提供示例数据生成和真实数据加载功能。
This module provides sample data generation and real data loading capabilities.

功能 / Features
----------------
1. **示例数据生成 / Sample Data Generation**
   - 气象变量的随机数据生成
     Random meteorological data generation
   - 气候预估的时间序列生成
     Time series generation for climate projections

2. **数据加载接口 / Data Loading Interfaces**
   - Fluxnet2015站点数据加载
     Fluxnet2015 site data loading
   - CMIP6模式数据加载
     CMIP6 model data loading

用途 / Use Cases
-----------------
- 测试和演示代码功能 / Testing and demonstrating code functionality
- 生成教程示例数据 / Generating tutorial example data
- 提供真实数据加载框架 / Providing framework for real data loading

作者 / Author: Sha Zhou
邮箱 / Email: shazhou21@bnu.edu.cn
日期 / Date: 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, Union, Optional, Tuple
import warnings
from pathlib import Path

# 尝试延迟导入 matplotlib（仅当需要绘图时）/ Lazy import matplotlib only when needed
def setup_chinese_font(preferred: Optional[list] = None) -> Optional[str]:
    """
    配置 Matplotlib 以正确显示中文，并修复负号显示问题。
    Configure Matplotlib for proper Chinese rendering and fix minus sign display.

    Parameters
    ----------
    preferred : list, optional
        优先候选字体名称列表；若未提供将使用常见中文字体候选。

    Returns
    -------
    str or None
        实际使用的字体名称；如果 Matplotlib 未安装则返回 None（静默跳过）。

    Notes
    -----
    - 在 Windows 上通常可用: 'SimHei', 'Microsoft YaHei'
    - 在 macOS 上: 'PingFang SC'
    - 跨平台开源: 'Noto Sans CJK SC', 'Source Han Sans SC'
    """
    try:
        import matplotlib.pyplot as plt  # noqa: F401
        from matplotlib import font_manager
    except Exception:
        # Matplotlib 不可用，直接跳过 / Matplotlib unavailable, skip silently
        return None

    candidates = preferred or [
        'SimHei',
        'Microsoft YaHei',
        'PingFang SC',
        'Noto Sans CJK SC',
        'Source Han Sans SC',
        'WenQuanYi Zen Hei',
        'Arial Unicode MS',
    ]

    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for name in candidates:
        if name in available:
            chosen = name
            break

    # 设置字体与负号 / Set font and minus sign rendering
    import matplotlib as mpl
    if chosen:
        mpl.rcParams['font.sans-serif'] = [chosen]
    else:
        # 仍然设置一个候选列表，部分环境可解析 / set a candidate list anyway
        mpl.rcParams['font.sans-serif'] = candidates
    mpl.rcParams['axes.unicode_minus'] = False

    return chosen

# 类型别名 / Type alias
ArrayDict = Dict[str, np.ndarray]


def generate_sample_data(
    n_samples: int = 100,
    surface_type: str = 'land',
    seed: Optional[int] = None
) -> ArrayDict:
    """
    生成随机示例气象数据
    Generate random sample meteorological data.

    参数 / Parameters
    ----------
    n_samples : int, optional
        要生成的样本数（默认: 100）
        Number of samples to generate (default: 100)
    surface_type : str, optional
        表面类型: 'land'或'ocean'（默认: 'land')
        Type of surface: 'land' or 'ocean' (default: 'land')
    seed : int, optional
        随机种子以实现可重现性
        Random seed for reproducibility

    返回 / Returns
    -------
    dict
        包含气象变量的字典 / Dictionary containing meteorological variables:

        - **'hfls'**: 潜热通量 (W/m²) / Latent heat flux (W/m²)
        - **'hfss'**: 感热通量 (W/m²) / Sensible heat flux (W/m²)
        - **'huss'**: 比湿 (kg/kg) / Specific humidity (kg/kg)
        - **'ps'**: 气压 (Pa) / Air pressure (Pa)
        - **'tas'**: 气温 (K) / Air temperature (K)
        - **'ts'**: 表皮温度 (K) / Skin temperature (K)

    说明 / Notes
    -----
    **陆地表面典型范围 / Land Surface Typical Ranges**:

    - 潜热通量: 60-150 W/m² / Latent heat flux: 60-150 W/m²
    - 感热通量: 30-80 W/m² / Sensible heat flux: 30-80 W/m²
    - 比湿: 0.005-0.015 kg/kg / Specific humidity: 0.005-0.015 kg/kg
    - 气压: 98000-103000 Pa / Air pressure: 98000-103000 Pa
    - 气温: 288-305 K (15-32°C) / Air temperature: 288-305 K (15-32°C)
    - 表皮温度: 290-308 K (17-35°C) / Skin temperature: 290-308 K (17-35°C)

    **海洋表面典型范围 / Ocean Surface Typical Ranges**:

    - 潜热通量: 100-200 W/m² / Latent heat flux: 100-200 W/m²
    - 感热通量: 15-50 W/m² / Sensible heat flux: 15-50 W/m²
    - 比湿: 0.010-0.020 kg/kg / Specific humidity: 0.010-0.020 kg/kg
    - 气压: 100000-102000 Pa / Air pressure: 100000-102000 Pa
    - 气温: 293-303 K (20-30°C) / Air temperature: 293-303 K (20-30°C)
    - 表皮温度: 293-303 K (20-30°C) / Skin temperature: 293-303 K (20-30°C)

    Raises
    ------
    ValueError
        如果surface_type不是'land'或'ocean'
        If surface_type is not 'land' or 'ocean'

    示例 / Examples
    --------
    >>> # 生成陆地表面数据 / Generate land surface data
    >>> data = generate_sample_data(n_samples=50, surface_type='land', seed=42)
    >>> print(data['hfls'].shape)
    (50,)
    >>> print(f"Mean latent heat: {np.mean(data['hfls']):.1f} W/m²")
    Mean latent heat: 105.3 W/m²

    >>> # 生成海洋表面数据 / Generate ocean surface data
    >>> ocean_data = generate_sample_data(n_samples=100, surface_type='ocean', seed=123)
    >>> print(f"Mean specific humidity: {np.mean(ocean_data['huss']):.4f} kg/kg")
    Mean specific humidity: 0.0150 kg/kg

    另见 / See Also
    --------
    generate_timeseries_data : 生成时间序列数据 / Generate time series data
    """
    if seed is not None:
        np.random.seed(seed)

    if surface_type == 'land':
        # 陆地表面典型范围 / Land surface typical ranges
        data = {
            'hfls': np.random.uniform(60, 150, n_samples),     # W/m²
            'hfss': np.random.uniform(30, 80, n_samples),      # W/m²
            'huss': np.random.uniform(0.005, 0.015, n_samples),  # kg/kg
            'ps': np.random.uniform(98000, 103000, n_samples),  # Pa
            'tas': np.random.uniform(288, 305, n_samples),     # K
            'ts': np.random.uniform(290, 308, n_samples)       # K
        }
    elif surface_type == 'ocean':
        # 海洋表面典型范围 / Ocean surface typical ranges
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
) -> ArrayDict:
    """
    生成用于气候预估的时间序列数据
    Generate time series data for climate projections.

    参数 / Parameters
    ----------
    n_years : int, optional
        要生成的年数（默认: 140，用于1pctCO2实验）
        Number of years to generate (default: 140, for 1pctCO2 experiments)
    timestep : str, optional
        时间步长: 'annual'或'monthly'（默认: 'annual')
        Time step: 'annual' or 'monthly' (default: 'annual')
    include_trend : bool, optional
        是否包括变暖趋势（默认: True）
        Whether to include warming trends (default: True)
    seed : int, optional
        随机种子以实现可重现性
        Random seed for reproducibility

    返回 / Returns
    -------
    dict
        包含时间序列的字典 / Dictionary containing time series:

        - **'time'**: 时间数组（年或月）/ Time array (years or months)
        - **'et'**: 蒸散发 (mm/day) / Evapotranspiration (mm/day)
        - **'pete'**: 能量基础PET (mm/day) / Energy-based PET (mm/day)
        - **'pr'**: 降水 (mm/day) / Precipitation (mm/day)
        - **'tas'**: 气温 (K) / Air temperature (K)

    说明 / Notes
    -----
    **趋势设置 / Trend Settings** (when include_trend=True):

    模拟1pctCO2实验（140年，CO2加倍）：
    Simulates 1pctCO2 experiment (140 years, CO2 doubling):

    1. **温度趋势 / Temperature Trend**:
       约2-4°C升温 / About 2-4°C warming
       .. math:: \\Delta T \\approx 0.02 \\cdot \\frac{t}{n_{steps}} \\cdot 100 \\text{ K}

    2. **PETe趋势 / PETe Trend**:
       随温度增加 / Increases with temperature
       .. math:: \\Delta PET_e \\approx 0.004 \\cdot \\frac{t}{n_{steps}} \\cdot 100 \\text{ mm/day}

    3. **降水趋势 / Precipitation Trend**:
       轻微增加 / Slight increase
       .. math:: \\Delta P \\approx 0.002 \\cdot \\frac{t}{n_{steps}} \\cdot 100 \\text{ mm/day}

    4. **ET趋势 / ET Trend**:
       增加但受陆地表面变化调节 / Increases but moderated by land surface changes
       .. math:: \\Delta ET \\approx 0.003 \\cdot \\frac{t}{n_{steps}} \\cdot 100 \\text{ mm/day}

    **噪声水平 / Noise Levels**:

    - 年度数据: 较小噪声 (σ ~ 0.1) / Annual data: smaller noise (σ ~ 0.1)
    - 月度数据: 较大噪声 (σ ~ 0.3) / Monthly data: larger noise (σ ~ 0.3)

    **物理约束 / Physical Constraints**:

    - ET ≤ P (蒸发不能超过降水) / ET ≤ P (evaporation cannot exceed precipitation)
    - 所有变量 ≥ 0 / All variables ≥ 0

    Raises
    ------
    ValueError
        如果timestep不是'annual'或'monthly'
        If timestep is not 'annual' or 'monthly'

    示例 / Examples
    --------
    >>> # 生成140年年度数据，带趋势 / Generate 140-year annual data with trend
    >>> data = generate_timeseries_data(n_years=140, include_trend=True, seed=42)
    >>> print(data['et'].shape)
    (140,)
    >>> print(f"Initial ET: {data['et'][0]:.3f} mm/day")
    Initial ET: 1.734 mm/day
    >>> print(f"Final ET: {data['et'][-1]:.3f} mm/day")
    Final ET: 2.011 mm/day
    >>> print(f"ET change: {data['et'][-1] - data['et'][0]:.3f} mm/day")
    ET change: 0.277 mm/day

    >>> # 生成月度数据，无趋势 / Generate monthly data without trend
    >>> monthly_data = generate_timeseries_data(
    ...     n_years=10,
    ...     timestep='monthly',
    ...     include_trend=False,
    ...     seed=123
    ... )
    >>> print(f"Total time steps: {len(monthly_data['time'])}")
    Total time steps: 120

    另见 / See Also
    --------
    generate_sample_data : 生成单次样本数据 / Generate single sample data
    """
    if seed is not None:
        np.random.seed(seed)

    # 确定时间步数 / Determine number of time steps
    if timestep == 'annual':
        n_steps = n_years
    elif timestep == 'monthly':
        n_steps = n_years * 12
    else:
        raise ValueError(f"Unknown timestep: {timestep}. Use 'annual' or 'monthly'.")

    # 创建时间数组 / Create time array
    time = np.arange(n_steps)

    # 生成趋势 / Generate trends
    if include_trend:
        # 变暖趋势: ~2-4°C over the period
        # Warming trend: ~2-4°C over the period
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

    # 添加噪声 / Add noise
    noise_scale = 0.1 if timestep == 'annual' else 0.3

    data = {
        'time': time,
        'tas': 288.0 + temp_trend + np.random.normal(0, noise_scale * 10, n_steps),
        'pete': 3.0 + pete_trend + np.random.normal(0, noise_scale, n_steps),
        'pr': 2.5 + pr_trend + np.random.normal(0, noise_scale * 1.5, n_steps),
        'et': 1.8 + et_trend + np.random.normal(0, noise_scale * 0.8, n_steps)
    }

    # 确保物理上现实的值 / Ensure physically realistic values
    data['pete'] = np.maximum(data['pete'], 0.5)
    data['pr'] = np.maximum(data['pr'], 0.1)
    data['et'] = np.maximum(data['et'], 0.1)
    data['et'] = np.minimum(data['et'], data['pr'])  # ET不能超过降水 / ET cannot exceed precipitation

    return data


def load_fluxnet_data(
    filepath: str,
    variables: Optional[list] = None
) -> pd.DataFrame:
    """
    从CSV文件加载Fluxnet2015数据
    Load Fluxnet2015 data from CSV file.

    参数 / Parameters
    ----------
    filepath : str
        Fluxnet CSV文件的路径
        Path to the Fluxnet CSV file
    variables : list, optional
        要加载的变量列表。如果为None，加载所有可用变量。
        List of variables to load. If None, load all available.

    返回 / Returns
    -------
    pd.DataFrame
        包含Fluxnet数据的DataFrame
        DataFrame containing Fluxnet data

    说明 / Notes
    -----
    **Fluxnet2015数据中预期的变量 / Expected Variables in Fluxnet2015 Data**:

    - **LE**: 潜热通量 (W/m²) / Latent heat flux (W/m²)
    - **H**: 感热通量 (W/m²) / Sensible heat flux (W/m²)
    - **TA**: 气温 (°C) / Air temperature (°C)
    - **TS**: 地表温度 (°C) / Surface temperature (°C)
    - **PA**: 大气压强 (kPa) / Atmospheric pressure (kPa)
    - **VPD**: 饱和水汽压差 (hPa) / Vapor pressure deficit (hPa)
    - **NETRAD**: 净辐射 (W/m²) / Net radiation (W/m²)
    - **G**: 土壤热通量 (W/m²) / Ground heat flux (W/m²)

    **数据来源 / Data Source**:

    Fluxnet2015数据可从以下网址下载：
    Fluxnet2015 data can be downloaded from:
    https://fluxnet.org/data/fluxnet2015-dataset/

    **回退行为 / Fallback Behavior**:

    如果文件未找到，函数将生成示例数据并发出警告
    If file not found, function will generate sample data with warning

    Warnings
    --------
    UserWarning
        如果文件未找到，将生成示例数据
        If file not found, sample data will be generated

    示例 / Examples
    --------
    >>> # 加载真实Fluxnet数据（当文件可用时）
    >>> # Load real Fluxnet data (when file is available)
    >>> # df = load_fluxnet_data('data/input/fluxnet_site.csv')
    >>> # print(df.head())
    >>>
    >>> # 如果文件不存在，将生成示例数据
    >>> # If file doesn't exist, sample data will be generated
    >>> df = load_fluxnet_data('nonexistent_file.csv')
    >>> print(df.columns.tolist())
    ['LE', 'H', 'TA', 'TS', 'PA', 'QA']

    另见 / See Also
    --------
    load_cmip6_data : 加载CMIP6数据 / Load CMIP6 data
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
        warnings.warn(
            f"File not found: {filepath}\n"
            f"Please download Fluxnet2015 data from: https://fluxnet.org/data/fluxnet2015-dataset/\n"
            f"Generating sample data instead...",
            UserWarning
        )

        # 生成示例数据作为后备 / Generate sample data as fallback
        n_samples = 100
        sample_data = generate_sample_data(n_samples=n_samples, surface_type='land')

        # 转换为类似Fluxnet的DataFrame格式
        # Convert to DataFrame format similar to Fluxnet
        df = pd.DataFrame({
            'LE': sample_data['hfls'],
            'H': sample_data['hfss'],
            'TA': sample_data['tas'] - 273.15,  # 转换为°C / Convert to °C
            'TS': sample_data['ts'] - 273.15,
            'PA': sample_data['ps'] / 1000.0,  # 转换为kPa / Convert to kPa
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
    从NetCDF文件加载CMIP6模式数据
    Load CMIP6 model data from NetCDF files.

    参数 / Parameters
    ----------
    model : str
        CMIP6模式名称（例如：'ACCESS-CM2', 'CanESM5')
        CMIP6 model name (e.g., 'ACCESS-CM2', 'CanESM5')
    experiment : str
        实验名称（例如：'historical', 'ssp585', '1pctCO2')
        Experiment name (e.g., 'historical', 'ssp585', '1pctCO2')
    variable : str
        变量名称（例如：'hfls', 'hfss', 'tas', 'pr')
        Variable name (e.g., 'hfls', 'hfss', 'tas', 'pr')
    path : str
        CMIP6数据目录的路径
        Path to CMIP6 data directory

    返回 / Returns
    -------
    np.ndarray or None
        包含请求数据的数组，如果找不到文件则为None
        Array containing the requested data, or None if file not found

    说明 / Notes
    -----
    **CMIP6数据来源 / CMIP6 Data Source**:

    CMIP6数据应从以下网址下载：
    CMIP6 data should be downloaded from:
    https://esgf-node.llnl.gov/search/cmip6/

    **预期文件命名约定 / Expected File Naming Convention**:

    {variable}_{model}_{experiment}_*.nc

    例如 / Example:
    hfls_ACCESS-CM2_1pctCO2_r1i1p1f1_gn_185001-198912.nc

    **变量名称 / Variable Names**:

    常用CMIP6变量 / Common CMIP6 variables:
    - hfls: 地表潜热通量 / Surface latent heat flux
    - hfss: 地表感热通量 / Surface sensible heat flux
    - tas: 近地表气温 / Near-surface air temperature
    - ts: 地表温度 / Surface temperature
    - pr: 降水 / Precipitation
    - ps: 地表气压 / Surface air pressure

    **回退行为 / Fallback Behavior**:

    如果目录或文件未找到，或netCDF4包未安装，
    函数将生成示例时间序列数据并发出警告
    If directory or file not found, or netCDF4 not installed,
    function will generate sample time series data with warning

    Warnings
    --------
    UserWarning
        如果目录/文件未找到或netCDF4未安装
        If directory/file not found or netCDF4 not installed

    示例 / Examples
    --------
    >>> # 加载真实CMIP6数据（当文件可用时）
    >>> # Load real CMIP6 data (when file is available)
    >>> # data = load_cmip6_data(
    >>> #     model='ACCESS-CM2',
    >>> #     experiment='1pctCO2',
    >>> #     variable='hfls',
    >>> #     path='data/input/cmip6/'
    >>> # )
    >>> # print(f"Data shape: {data.shape}")
    >>>
    >>> # 如果文件不存在，将生成示例数据
    >>> # If file doesn't exist, sample data will be generated
    >>> data = load_cmip6_data(
    ...     model='TEST-MODEL',
    ...     experiment='1pctCO2',
    ...     variable='hfls',
    ...     path='nonexistent_path/'
    ... )
    >>> print(f"Generated data length: {len(data)}")
    Generated data length: 140

    另见 / See Also
    --------
    load_fluxnet_data : 加载Fluxnet数据 / Load Fluxnet data
    """
    import os

    # 构造文件名模式 / Construct filename pattern
    filename_pattern = f"{variable}_{model}_{experiment}"

    # 检查目录是否存在 / Check if directory exists
    if not os.path.exists(path):
        warnings.warn(
            f"Directory not found: {path}\n"
            f"Please download CMIP6 data from: https://esgf-node.llnl.gov/search/cmip6/\n"
            f"Generating sample time series data instead...",
            UserWarning
        )

        # 生成示例时间序列数据作为后备
        # Generate sample time series data as fallback
        sample_data = generate_timeseries_data(n_years=140, seed=42)

        # 将变量名映射到示例数据 / Map variable name to sample data
        variable_map = {
            'hfls': 'et',  # 使用ET作为潜热的代理 / Use ET as proxy for latent heat
            'hfss': 'et',  # 使用ET缩放为感热 / Use ET scaled for sensible heat
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

        # 查找匹配的文件 / Find matching file
        files = [f for f in os.listdir(path) if f.startswith(filename_pattern)]

        if not files:
            raise FileNotFoundError(f"No file found matching pattern: {filename_pattern}")

        # 加载第一个匹配的文件 / Load first matching file
        filepath = os.path.join(path, files[0])
        dataset = nc.Dataset(filepath, 'r')

        # 提取变量 / Extract variable
        data = dataset.variables[variable][:]

        dataset.close()

        return np.array(data)

    except ImportError:
        warnings.warn(
            "netCDF4 package not installed. Install with: pip install netCDF4\n"
            "Generating sample data instead...",
            UserWarning
        )
        return generate_timeseries_data(n_years=140, seed=42)['et']

    except Exception as e:
        warnings.warn(
            f"Error loading CMIP6 data: {e}\n"
            f"Generating sample data instead...",
            UserWarning
        )
        return generate_timeseries_data(n_years=140, seed=42)['et']


# 公共API / Public API
__all__ = [
    'generate_sample_data',
    'generate_timeseries_data',
    'load_fluxnet_data',
    'load_cmip6_data',
]
