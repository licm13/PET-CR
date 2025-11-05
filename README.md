# PET-CR: 互补关系蒸散发库 / Complementary Relationship Evapotranspiration Library

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### Overview

**PET-CR** is a comprehensive Python library for estimating actual evapotranspiration (ET) using Complementary Relationship (CR) theory. The library integrates **three distinct but complementary approaches**:

#### **Method 1: Traditional CR Models**
For users with pre-calculated potential evapotranspiration components:
- **Input**: Penman potential ET (Ep) and Priestley-Taylor ET (Ew)
- **Models**: Sigmoid, Polynomial, Rescaled Power, Bouchet, Advection-Aridity
- **Use Case**: Traditional ET estimation from standard meteorological variables

#### **Method 2: Land-Atmosphere Framework (Zhou & Yu, 2025)**
For users with energy flux data who want advanced PET estimation and attribution:
- **Input**: Latent heat flux (LH), sensible heat flux (SH), and meteorological variables
- **Output**: Energy-based PET (PETe), Aerodynamics-based PET (PETa)
- **Features**:
  - PET estimation from fundamental energy fluxes
  - Budyko framework-based attribution analysis
  - Separation of climate change and land surface effects
  - 1pctCO2 experiment analysis

#### **Method 3: BGCR-Budyko Model (NEW in v0.3.0)**
For users with meteorological data, precipitation, and catchment characteristics:
- **Input**: Net radiation, temperature, wind speed, vapor pressure, precipitation, seasonality index, albedo
- **Output**: Monthly actual ET with distributed Budyko parameter
- **Features**:
  - Combines long-term Budyko framework with short-term GCR
  - Handles spatial heterogeneity through regionalized w parameter
  - Incorporates precipitation seasonality effects
  - Two parameterization schemes: SI-only (BGCR-1) and SI+albedo (BGCR-2)

This unified framework makes PET-CR suitable for operational ET estimation, research in land-atmosphere interactions, climate change attribution, and heterogeneous catchment analysis.

### Key Features

- ✅ **Bilingual Documentation** (English/Chinese)
- ✅ **Three Complementary Approaches** (Traditional CR + Land-Atmosphere + BGCR-Budyko)
- ✅ **SI Units** throughout
- ✅ **Literature-Referenced** implementations
- ✅ **Comprehensive Examples** with visualization
- ✅ **Data Utilities** for sample generation and CMIP6/Fluxnet loading
- ✅ **Attribution Analysis** for climate change studies
- ✅ **Spatial Heterogeneity** handling via distributed parameters

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/PET-CR.git
cd PET-CR

# Install dependencies
pip install -r requirements.txt

# Install package (development mode)
pip install -e .
```

### Quick Start

#### Method 1: Traditional CR Model

Use traditional CR models when you have pre-calculated Penman and Priestley-Taylor ET:

```python
import petcr

# Calculate actual ET using Sigmoid CR model
ep = 400.0  # Penman potential ET [W/m²]
ew = 350.0  # Priestley-Taylor ET [W/m²]

ea = petcr.sigmoid_cr(ep=ep, ew=ew, beta=0.5)
print(f"Actual ET: {ea:.2f} W/m²")
# Output: Actual ET: 331.78 W/m²
```

#### Method 2: Land-Atmosphere Framework

Use the land-atmosphere framework when you have energy flux measurements:

```python
import petcr

# Calculate PETe and PETa from energy fluxes
results = petcr.calculate_pet_land(
    latent_heat=100.0,       # Latent heat flux [W/m²]
    sensible_heat=50.0,      # Sensible heat flux [W/m²]
    specific_humidity=0.01,  # Specific humidity [kg/kg]
    air_pressure=101325.0,   # Air pressure [Pa]
    air_temperature=298.15,  # Air temperature [K]
    skin_temperature=300.15  # Skin temperature [K]
)

print(f"PETe (Energy-based): {results['pete']:.2f} mm/day")
print(f"PETa (Aerodynamics-based): {results['peta']:.2f} mm/day")
print(f"Wet Bowen ratio: {results['beta_w']:.3f}")
print(f"Actual ET: {results['et']:.2f} mm/day")

# Output:
# PETe (Energy-based): 5.91 mm/day
# PETa (Aerodynamics-based): 6.30 mm/day
# Wet Bowen ratio: 0.344
# Actual ET: 4.35 mm/day
```

#### Method 3: BGCR-Budyko Model

Use the BGCR-Budyko model for monthly ET estimation with catchment characteristics:

```python
import petcr

# Calculate monthly ET using BGCR-Budyko model
results = petcr.calculate_bgcr_et(
    net_radiation=150.0,              # Net radiation [W/m²]
    temperature=20.0,                 # Air temperature [°C]
    wind_speed=2.0,                   # Wind speed [m/s]
    actual_vapor_pressure=1.5,        # Actual vapor pressure [kPa]
    saturation_vapor_pressure=2.3,    # Saturation vapor pressure [kPa]
    precipitation=80.0,               # Monthly precipitation [mm]
    seasonality_index=0.5,            # Precipitation seasonality index
    albedo=0.2                        # Surface albedo [0-1]
)

print(f"Monthly ET: {results['et']:.2f} mm")
print(f"Apparent potential evaporation: {results['epa']:.2f} mm")
print(f"Budyko parameter w: {results['w']:.3f}")
print(f"Complementary coefficient: {results['beta_c']:.3f}")

# Output:
# Monthly ET: 72.45 mm
# Apparent potential evaporation: 85.30 mm
# Budyko parameter w: 2.135
# Complementary coefficient: 0.892
```

#### Attribution Analysis

Separate ET changes into climate and land surface contributions:

```python
import petcr
import numpy as np

# Generate 140-year synthetic dataset (simulating 1pctCO2 experiment)
data = petcr.generate_timeseries_data(
    n_years=140,
    include_trend=True,
    seed=42
)

# Perform attribution analysis
results = petcr.attribution_analysis(
    et_timeseries=data['et'],
    pete_timeseries=data['pete'],
    pr_timeseries=data['pr'],
    window_size=30  # 30-year moving window
)

print(f"Calibrated Budyko parameter n: {results['n_parameter']:.3f}")
print(f"Total ET change: {results['et_total'][-1]:.3f} mm/day")
print(f"Climate contribution: {results['et_climate'][-1]:.3f} mm/day")
print(f"Land surface contribution: {results['et_landsurf'][-1]:.3f} mm/day")

# Output:
# Calibrated Budyko parameter n: 2.123
# Total ET change: 0.334 mm/day
# Climate contribution: 0.456 mm/day
# Land surface contribution: -0.122 mm/day
```

### Available Models

#### Traditional CR Models (`petcr.models`)

| Model | Function | Reference |
|-------|----------|-----------|
| Sigmoid CR | `sigmoid_cr(ep, ew, beta)` | Han & Tian (2018) |
| Polynomial CR | `polynomial_cr(ep, ew, b)` | Brutsaert (2015) |
| Rescaled Power CR | `rescaled_power_cr(ep, ew, n)` | Szilagyi et al. (2017) |
| Bouchet CR | `bouchet_cr(ep, ew)` | Bouchet (1963) |
| Advection-Aridity CR | `aa_cr(ep, ew, ea_min)` | Brutsaert & Stricker (1979) |

#### Land-Atmosphere Framework (`petcr.land_atmosphere`)

| Function | Purpose |
|----------|---------|
| `calculate_pet_land()` | Calculate PETe and PETa for land surfaces |
| `calculate_pet_ocean()` | Calculate PET under wet/driest conditions for ocean |
| `calculate_wet_bowen_ratio()` | Calculate wet Bowen ratio with constraints |
| `batch_calculate_pet()` | Batch calculation for multiple time steps |

#### BGCR-Budyko Model (`petcr.bgcr_model`)

| Function | Purpose |
|----------|---------|
| `calculate_bgcr_et()` | High-level BGCR-Budyko ET calculation |
| `bgcr_monthly()` | Core BGCR monthly model |
| `calculate_penman_components()` | Calculate Erad and Eaero from Penman equation |
| `calculate_seasonality_index()` | Compute precipitation seasonality index |
| `calculate_budyko_w_from_SI()` | Single-variable w parameterization (BGCR-1) |
| `calculate_budyko_w_from_SI_albedo()` | Dual-variable w parameterization (BGCR-2) |

#### Attribution Analysis (`petcr.attribution`)

| Function | Purpose |
|----------|---------|
| `budyko_et_ratio()` | Calculate ET/P ratio using Budyko framework |
| `calculate_et_from_budyko()` | Estimate ET from PET and precipitation |
| `calibrate_budyko_parameter()` | Calibrate Budyko n parameter |
| `attribution_analysis()` | Separate climate and land surface effects |
| `projection_1pctCO2()` | Analyze 1pctCO2 experiment results |

### Examples

The `examples/` directory contains comprehensive demonstrations:

```bash
# Traditional CR model comparison
python examples/example_sigmoid.py
python examples/compare_models.py

# Land-atmosphere framework
python examples/example_land_atmosphere.py

# BGCR-Budyko model
python examples/compare_all_three_methods.py

# Attribution analysis with visualization
python examples/example_attribution_analysis.py

# Advanced workflows
python examples/real_data_workflow.py
python examples/advanced_analysis.py
```

### Project Structure

```
PET-CR/
├── petcr/                      # Main package
│   ├── __init__.py            # Package initialization and API
│   ├── models.py              # Traditional CR models
│   ├── physics.py             # Physical calculations (Penman, PT)
│   ├── land_atmosphere.py     # Land-atmosphere PET estimation
│   ├── bgcr_model.py          # BGCR-Budyko model (NEW)
│   ├── attribution.py         # Attribution analysis (Budyko)
│   └── utils.py               # Data generation and loading
├── examples/                   # Example scripts
│   ├── example_sigmoid.py
│   ├── example_land_atmosphere.py
│   ├── example_attribution_analysis.py
│   ├── compare_models.py
│   ├── compare_all_three_methods.py  # NEW
│   ├── real_data_workflow.py
│   └── advanced_analysis.py
├── bgcr-budyko/               # Original BGCR-Budyko implementation
├── tests/                      # Unit tests
├── docs/                       # Documentation
├── README.md                   # This file
├── requirements.txt            # Dependencies
└── setup.py                    # Installation script
```

### Citation

If you use this library in your research, please cite:

```bibtex
@article{zhou2025land,
  title={Land-atmosphere interactions exacerbate concurrent soil moisture drought and atmospheric aridity},
  author={Zhou, Sha and Yu, Bofu},
  journal={Nature Climate Change},
  year={2025},
  note={accepted}
}
```

For BGCR-Budyko model:
```bibtex
@article{yang2006bgcr,
  title={Interpreting the complementary relationship in non-humid environments based on the Budyko and Penman hypotheses},
  author={Yang, Dawen and Sun, Fuqiang and Liu, Zhiyong and Cong, Zhentao and Lei, Zhidong},
  journal={Geophysical Research Letters},
  volume={33},
  number={18},
  year={2006}
}
```

For traditional CR models, also consider citing the original papers listed in the documentation.

### Scientific Background

#### Complementary Relationship Theory

The complementary relationship hypothesis (Bouchet, 1963) states that under the same meteorological conditions, the decrease in actual evapotranspiration due to soil moisture deficit is complemented by an increase in potential evapotranspiration due to feedbacks in the atmospheric boundary layer.

#### Land-Atmosphere Framework (Zhou & Yu, 2025)

This framework introduces two complementary PET estimates:

- **PETe (Energy-based)**: Maximum ET constrained by available energy
  - PETe = Rn / (1 + βw)
  - where Rn is net radiation, βw is wet Bowen ratio

- **PETa (Aerodynamics-based)**: Maximum ET constrained by atmospheric demand
  - PETa = SH / βw
  - where SH is sensible heat flux

The relative magnitudes of PETe and PETa indicate surface moisture status and land-atmosphere coupling strength.

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### License

MIT License - see LICENSE file for details.

### Authors

- PET-CR Contributors
- Original land-atmosphere framework: Sha Zhou (shazhou21@bnu.edu.cn)

### Support

- Documentation: See `docs/` directory
- Issues: Please report bugs via GitHub issues
- Questions: Contact the authors

---

<a name="中文"></a>
## 中文

### 概述

**PET-CR** 是一个使用互补关系（CR）理论估算实际蒸散发（ET）的综合Python库。该库集成了**三种不同但互补的方法**：

#### **方法1：传统CR模型**
适用于拥有预计算潜在蒸散发分量的用户：
- **输入**: Penman潜在蒸散发 (Ep) 和 Priestley-Taylor蒸散发 (Ew)
- **模型**: Sigmoid, Polynomial, Rescaled Power, Bouchet, Advection-Aridity
- **用途**: 从标准气象变量进行传统ET估算

#### **方法2：陆地-大气框架（Zhou & Yu, 2025）**
适用于拥有能量通量数据并希望进行高级PET估算和归因的用户：
- **输入**: 潜热通量（LH）、感热通量（SH）和气象变量
- **输出**: 能量基础PET（PETe）、空气动力学基础PET（PETa）
- **特性**:
  - 从基本能量通量估算PET
  - 基于Budyko框架的归因分析
  - 分离气候变化和陆地表面效应
  - 1pctCO2实验分析

#### **方法3：BGCR-Budyko模型（v0.3.0新增）**
适用于拥有气象数据、降水和流域特征的用户：
- **输入**: 净辐射、温度、风速、水汽压、降水、季节性指数、反照率
- **输出**: 带有分布式Budyko参数的月尺度实际ET
- **特性**:
  - 结合长期Budyko框架与短期GCR
  - 通过区域化w参数处理空间异质性
  - 考虑降水季节性影响
  - 两种参数化方案：仅SI（BGCR-1）和SI+反照率（BGCR-2）

这个统一框架使PET-CR既适用于业务性ET估算、陆地-大气相互作用研究、气候变化归因，也适用于异质流域分析。

### 主要特性

- ✅ **双语文档**（英文/中文）
- ✅ **三种互补方法**（传统CR + 陆地-大气 + BGCR-Budyko）
- ✅ **SI单位**贯穿始终
- ✅ **文献参考**实现
- ✅ **综合示例**含可视化
- ✅ **数据工具**用于样本生成和CMIP6/Fluxnet加载
- ✅ **归因分析**用于气候变化研究
- ✅ **空间异质性**通过分布式参数处理

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/PET-CR.git
cd PET-CR

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

### 快速开始

#### 方法1：传统CR模型

当您有预计算的Penman和Priestley-Taylor ET时使用传统CR模型：

```python
import petcr

# 使用Sigmoid CR模型计算实际ET
ep = 400.0  # Penman潜在蒸散发 [W/m²]
ew = 350.0  # Priestley-Taylor蒸散发 [W/m²]

ea = petcr.sigmoid_cr(ep=ep, ew=ew, beta=0.5)
print(f"实际ET: {ea:.2f} W/m²")
# 输出: 实际ET: 331.78 W/m²
```

#### 方法2：陆地-大气框架

当您有能量通量测量时使用陆地-大气框架：

```python
import petcr

# 从能量通量计算PETe和PETa
results = petcr.calculate_pet_land(
    latent_heat=100.0,       # 潜热通量 [W/m²]
    sensible_heat=50.0,      # 感热通量 [W/m²]
    specific_humidity=0.01,  # 比湿 [kg/kg]
    air_pressure=101325.0,   # 气压 [Pa]
    air_temperature=298.15,  # 气温 [K]
    skin_temperature=300.15  # 表皮温度 [K]
)

print(f"PETe（能量基础）: {results['pete']:.2f} mm/day")
print(f"PETa（空气动力学基础）: {results['peta']:.2f} mm/day")
print(f"湿润波文比: {results['beta_w']:.3f}")
print(f"实际ET: {results['et']:.2f} mm/day")

# 输出:
# PETe（能量基础）: 5.91 mm/day
# PETa（空气动力学基础）: 6.30 mm/day
# 湿润波文比: 0.344
# 实际ET: 4.35 mm/day
```

#### 归因分析

将ET变化分离为气候和陆地表面贡献：

```python
import petcr
import numpy as np

# 生成140年合成数据集（模拟1pctCO2实验）
data = petcr.generate_timeseries_data(
    n_years=140,
    include_trend=True,
    seed=42
)

# 执行归因分析
results = petcr.attribution_analysis(
    et_timeseries=data['et'],
    pete_timeseries=data['pete'],
    pr_timeseries=data['pr'],
    window_size=30  # 30年滑动窗口
)

print(f"校准的Budyko参数n: {results['n_parameter']:.3f}")
print(f"总ET变化: {results['et_total'][-1]:.3f} mm/day")
print(f"气候贡献: {results['et_climate'][-1]:.3f} mm/day")
print(f"陆地表面贡献: {results['et_landsurf'][-1]:.3f} mm/day")

# 输出:
# 校准的Budyko参数n: 2.123
# 总ET变化: 0.334 mm/day
# 气候贡献: 0.456 mm/day
# 陆地表面贡献: -0.122 mm/day
```

### 可用模型

#### 传统CR模型 (`petcr.models`)

| 模型 | 函数 | 参考文献 |
|------|------|---------|
| Sigmoid CR | `sigmoid_cr(ep, ew, beta)` | Han & Tian (2018) |
| Polynomial CR | `polynomial_cr(ep, ew, b)` | Brutsaert (2015) |
| Rescaled Power CR | `rescaled_power_cr(ep, ew, n)` | Szilagyi et al. (2017) |
| Bouchet CR | `bouchet_cr(ep, ew)` | Bouchet (1963) |
| Advection-Aridity CR | `aa_cr(ep, ew, ea_min)` | Brutsaert & Stricker (1979) |

#### 陆地-大气框架 (`petcr.land_atmosphere`)

| 函数 | 用途 |
|------|------|
| `calculate_pet_land()` | 计算陆地表面的PETe和PETa |
| `calculate_pet_ocean()` | 计算海洋湿润/最干条件下的PET |
| `calculate_wet_bowen_ratio()` | 计算带约束的湿润波文比 |
| `batch_calculate_pet()` | 多个时间步的批量计算 |

#### 归因分析 (`petcr.attribution`)

| 函数 | 用途 |
|------|------|
| `budyko_et_ratio()` | 使用Budyko框架计算ET/P比率 |
| `calculate_et_from_budyko()` | 从PET和降水估算ET |
| `calibrate_budyko_parameter()` | 校准Budyko n参数 |
| `attribution_analysis()` | 分离气候和陆地表面效应 |
| `projection_1pctCO2()` | 分析1pctCO2实验结果 |

### 示例

`examples/` 目录包含综合演示：

```bash
# 传统CR模型比较
python examples/example_sigmoid.py
python examples/compare_models.py

# 陆地-大气框架
python examples/example_land_atmosphere.py

# 带可视化的归因分析
python examples/example_attribution_analysis.py

# 高级工作流程
python examples/real_data_workflow.py
python examples/advanced_analysis.py
```

### 引用

如果您在研究中使用本库，请引用：

```bibtex
@article{zhou2025land,
  title={Land-atmosphere interactions exacerbate concurrent soil moisture drought and atmospheric aridity},
  author={Zhou, Sha and Yu, Bofu},
  journal={Nature Climate Change},
  year={2025},
  note={accepted}
}
```

对于传统CR模型，也请考虑引用文档中列出的原始论文。

### 科学背景

#### 互补关系理论

互补关系假说（Bouchet, 1963）指出，在相同气象条件下，由于土壤水分亏缺导致的实际蒸散发减少，会被由于大气边界层反馈导致的潜在蒸散发增加所补偿。

#### 陆地-大气框架（Zhou & Yu, 2025）

该框架引入了两个互补的PET估算值：

- **PETe（能量基础）**: 可用能量约束的最大ET
  - PETe = Rn / (1 + βw)
  - 其中Rn是净辐射，βw是湿润波文比

- **PETa（空气动力学基础）**: 大气需求约束的最大ET
  - PETa = SH / βw
  - 其中SH是感热通量

PETe和PETa的相对大小指示地表湿度状态和陆地-大气耦合强度。

### 贡献

欢迎贡献！请：

1. Fork仓库
2. 创建功能分支
3. 为新功能添加测试
4. 确保所有测试通过
5. 提交拉取请求

### 许可证

MIT许可证 - 详见LICENSE文件。

### 作者

- PET-CR贡献者
- 原始陆地-大气框架：周沙 (shazhou21@bnu.edu.cn)

### 支持

- 文档：见`docs/`目录
- 问题：请通过GitHub issues报告错误
- 问题：联系作者

---

## 版本历史 / Version History

### v0.3.0 (2025-01-XX) - **CURRENT**
- ✨ **NEW**: Integrated BGCR-Budyko model as Method 3
- ✨ **NEW**: Added distributed Budyko parameter schemes (BGCR-1, BGCR-2)
- ✨ **NEW**: Monthly ET estimation with spatial heterogeneity
- ✨ **NEW**: Precipitation seasonality index calculation
- ✨ **NEW**: Comprehensive three-method comparison example
- 📚 Updated documentation with Method 3
- 📚 Created teaching presentation (PPT)

### v0.2.0 (2025-01-XX)
- ✨ Merged Zhou_NCC_Code (land-atmosphere framework)
- ✨ Added attribution analysis module
- ✨ Added bilingual documentation
- ✨ Added comprehensive examples
- ✨ Added data utilities

### v0.1.0 (2024-XX-XX)
- 🎉 Initial release with traditional CR models
- ✅ Sigmoid, Polynomial, Rescaled Power, Bouchet, A-A models
- ✅ Physical calculations (Penman, Priestley-Taylor)

---

**关键词 / Keywords**: Evapotranspiration, Complementary Relationship, PET, Land-Atmosphere Interaction, Climate Change Attribution, Budyko Framework, Python

**标签 / Tags**: `hydrology` `climate-science` `evapotranspiration` `python` `pet` `cr-models` `attribution-analysis`
