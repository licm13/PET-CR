"""
PET-CR: 互补关系蒸散发库 / Complementary Relationship Evapotranspiration Library
==================================================================================

一个用于使用互补关系（CR）理论估算实际蒸散发（Ea）的Python库。
A Python library for estimating actual evapotranspiration (Ea) using
Complementary Relationship (CR) theory.

本包提供两种主要方法 / This package provides two main approaches
-----------------------------------------------------------

**方法1: 传统CR模型 / Method 1: Traditional CR Models**
    适用于拥有预计算的Ep（Penman）和Ew（Priestley-Taylor）的用户
    For users who have pre-calculated Ep (Penman) and Ew (Priestley-Taylor)

    - Sigmoid CR (Han & Tian, 2018)
    - Polynomial CR (Brutsaert, 2015)
    - Rescaled Power CR (Szilagyi et al., 2017)
    - Bouchet CR (1963)
    - Advection-Aridity CR

**方法2: 陆地-大气框架 / Method 2: Land-Atmosphere Framework**
    基于Zhou & Yu (2025)的Nature Climate Change论文
    Based on Zhou & Yu (2025) Nature Climate Change paper

    适用于拥有通量数据（LH/SH）并希望执行高级PETe/PETa分析和归因的用户
    For users who have flux data (LH/SH) and want to perform advanced
    PETe/PETa analysis and attribution

    - PETe/PETa估算 / PETe/PETa estimation
    - 湿润/干燥条件分析 / Wet/dry conditions analysis
    - Budyko框架归因 / Budyko framework attribution
    - 气候变化影响分离 / Climate change impact separation

主要特性 / Key Features
------------------------
- 标准化的SI单位输入 / Standardized SI unit inputs
- 文献参考的完善实现 / Well-documented implementations with literature references
- 双语文档（英文/中文）/ Bilingual documentation (English/Chinese)
- 核心CR模型 / Core CR models
- 物理计算（Penman, Priestley-Taylor, VPD）/ Physical calculations
- 数据生成和加载工具 / Data generation and loading utilities

模块 / Modules
--------------
- **models**: 传统CR模型 / Traditional CR models
- **physics**: 物理计算 / Physical calculations
- **land_atmosphere**: 陆地-大气PET估算 / Land-atmosphere PET estimation
- **attribution**: ET归因分析 / ET attribution analysis
- **utils**: 工具函数 / Utility functions

快速开始 / Quick Start
-----------------------

**示例1: 传统CR模型 / Example 1: Traditional CR Model**::

    import petcr

    # 使用Sigmoid CR模型 / Using Sigmoid CR model
    ea = petcr.sigmoid_cr(ep=400.0, ew=350.0, beta=0.5)
    print(f"Actual ET: {ea:.2f} W/m²")

**示例2: 陆地-大气框架 / Example 2: Land-Atmosphere Framework**::

    import petcr

    # 计算PETe和PETa / Calculate PETe and PETa
    results = petcr.calculate_pet_land(
        latent_heat=100.0,
        sensible_heat=50.0,
        specific_humidity=0.01,
        air_pressure=101325.0,
        air_temperature=298.15,
        skin_temperature=300.15
    )
    print(f"PETe: {results['pete']:.2f} mm/day")
    print(f"PETa: {results['peta']:.2f} mm/day")

**示例3: 归因分析 / Example 3: Attribution Analysis**::

    import petcr
    import numpy as np

    # 生成时间序列数据 / Generate time series data
    data = petcr.generate_timeseries_data(n_years=140, include_trend=True, seed=42)

    # 执行归因分析 / Perform attribution analysis
    results = petcr.attribution_analysis(
        et_timeseries=data['et'],
        pete_timeseries=data['pete'],
        pr_timeseries=data['pr'],
        window_size=30
    )
    print(f"Climate contribution: {results['et_climate'][-1]:.3f} mm/day")
    print(f"Land surface contribution: {results['et_landsurf'][-1]:.3f} mm/day")

引用 / Citation
----------------
如果您在研究中使用本库，请引用：
If you use this library in your research, please cite:

Zhou, S., & Yu, B. (2025). Land-atmosphere interactions exacerbate
concurrent soil moisture drought and atmospheric aridity.
Nature Climate Change (accepted).

作者 / Authors: PET-CR Contributors
许可证 / License: MIT
版本 / Version: 0.2.0
"""

__version__ = "0.2.0"

# ============================================================================
# 传统CR模型 / Traditional CR Models
# ============================================================================
from .models import (
    sigmoid_cr,
    polynomial_cr,
    rescaled_power_cr,
    bouchet_cr,
    aa_cr
)

# ============================================================================
# 物理计算 / Physical Calculations
# ============================================================================
from .physics import (
    penman_potential_et,
    priestley_taylor_et,
    vapor_pressure_deficit,
    calculate_psychrometric_constant,
    calculate_saturation_vapor_pressure,
    calculate_slope_svp
)

# ============================================================================
# 陆地-大气框架 / Land-Atmosphere Framework
# ============================================================================
from .land_atmosphere import (
    calculate_pet_land,
    calculate_pet_ocean,
    batch_calculate_pet,
    calculate_wet_bowen_ratio,
    calculate_latent_heat_vaporization,
    calculate_saturation_vapor_pressure_tetens,
    calculate_actual_vapor_pressure,
    calculate_psychrometric_constant_land,
    calculate_slope_saturation_curve,
)

# ============================================================================
# 归因分析 / Attribution Analysis
# ============================================================================
from .attribution import (
    budyko_et_ratio,
    calculate_et_from_budyko,
    calibrate_budyko_parameter,
    attribution_analysis,
    projection_1pctCO2,
)

# ============================================================================
# 工具函数 / Utility Functions
# ============================================================================
from .utils import (
    generate_sample_data,
    generate_timeseries_data,
    load_fluxnet_data,
    load_cmip6_data,
    setup_chinese_font,
)

# ============================================================================
# 公共API / Public API
# ============================================================================
__all__ = [
    # 版本 / Version
    '__version__',

    # 传统CR模型 / Traditional CR Models
    'sigmoid_cr',
    'polynomial_cr',
    'rescaled_power_cr',
    'bouchet_cr',
    'aa_cr',

    # 物理计算 / Physical Calculations
    'penman_potential_et',
    'priestley_taylor_et',
    'vapor_pressure_deficit',
    'calculate_psychrometric_constant',
    'calculate_saturation_vapor_pressure',
    'calculate_slope_svp',

    # 陆地-大气框架 / Land-Atmosphere Framework
    'calculate_pet_land',
    'calculate_pet_ocean',
    'batch_calculate_pet',
    'calculate_wet_bowen_ratio',
    'calculate_latent_heat_vaporization',
    'calculate_saturation_vapor_pressure_tetens',
    'calculate_actual_vapor_pressure',
    'calculate_psychrometric_constant_land',
    'calculate_slope_saturation_curve',

    # 归因分析 / Attribution Analysis
    'budyko_et_ratio',
    'calculate_et_from_budyko',
    'calibrate_budyko_parameter',
    'attribution_analysis',
    'projection_1pctCO2',

    # 工具函数 / Utility Functions
    'generate_sample_data',
    'generate_timeseries_data',
    'load_fluxnet_data',
    'load_cmip6_data',
    'setup_chinese_font',
]
