# 🌍 PET-CR: 互补关系蒸散发库 / Complementary Relationship Evapotranspiration Library

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-bilingual-brightgreen.svg)](./docs/)

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## 📖 English Documentation

### 🎯 Project Overview in One Sentence

**PET-CR** is a **Python 3.9+ scientific computing library** that estimates actual evapotranspiration (ET) using three complementary methods based on **Complementary Relationship (CR) theory**, integrating traditional models, land-atmosphere energy balance analysis, and monthly catchment-scale estimation with spatial heterogeneity handling.

**Core Technology Stack:**
- **Language**: Python 3.9+
- **Core Dependencies**: NumPy, SciPy, Pandas
- **Visualization**: Matplotlib, Seaborn
- **Data Handling**: xarray, netCDF4 (for climate model data)
- **Testing**: pytest
- **Scientific Domain**: Hydrology, Climate Science, Land-Atmosphere Interactions

---

### 🏗️ Architecture Overview

PET-CR provides **three distinct but complementary approaches** for evapotranspiration estimation:

**Method 1: Traditional CR Models** 🔄
- **When to use**: You have pre-calculated Penman (Ep) and Priestley-Taylor (Ew) potential ET
- **What it does**: Applies classical CR theory to estimate actual ET from potential ET components
- **Models**: Sigmoid, Polynomial, Rescaled Power, Bouchet, Advection-Aridity
- **Key module**: `petcr.models`

**Method 2: Land-Atmosphere Framework** 🌤️
- **When to use**: You have energy flux measurements (latent/sensible heat) and want to understand land-atmosphere coupling
- **What it does**: Calculates energy-based PET (PETe) and aerodynamics-based PET (PETa), performs climate attribution analysis
- **Research basis**: Zhou & Yu (2025, Nature Climate Change)
- **Key modules**: `petcr.land_atmosphere`, `petcr.attribution`

**Method 3: BGCR-Budyko Model** 🏔️
- **When to use**: You need monthly ET estimates for heterogeneous catchments with precipitation seasonality
- **What it does**: Combines long-term Budyko framework with short-term generalized CR
- **Special feature**: Handles spatial variability through distributed Budyko parameter
- **Key module**: `petcr.bgcr_model`

---

### 📁 Directory Structure Analysis

```
PET-CR/
├── 📦 petcr/                          # ⭐ MAIN PACKAGE - All active development here
│   ├── __init__.py                   # 🚪 Package entry point, exports public API
│   ├── constants.py                  # 🔧 Physical constants (SINGLE SOURCE OF TRUTH)
│   ├── models.py                     # 📊 Traditional CR models (Method 1)
│   ├── physics.py                    # ⚛️  Core physics (Penman, Priestley-Taylor)
│   ├── land_atmosphere.py            # 🌍 Land-atmosphere framework (Method 2)
│   ├── bgcr_model.py                 # 🏔️ BGCR-Budyko model (Method 3)
│   ├── attribution.py                # 📈 Climate attribution analysis
│   ├── subdaily.py                   # ⏰ Sub-daily GCP model
│   ├── stability.py                  # 🎯 Stability functions
│   └── utils.py                      # 🛠️ Data generation & loading utilities
│
├── 📚 examples/                       # ⭐ START HERE - Learn by example
│   ├── example_sigmoid.py            # 101: Basic CR model usage
│   ├── example_land_atmosphere.py    # 201: Energy flux analysis
│   ├── example_attribution_analysis.py # 301: Climate attribution
│   ├── compare_models.py             # 🔬 Compare traditional CR models
│   ├── compare_all_three_methods.py  # 🔬 Compare all three methods
│   ├── advanced_analysis.py          # 🎓 30-year trends & extreme events
│   ├── spatial_bgcr_example.py       # 🗺️ Spatial heterogeneity
│   ├── real_data_workflow.py         # 📊 Real-world data processing
│   └── figures/                      # 📊 Generated visualization outputs
│
├── 🧪 tests/                          # Unit tests for validation
│   └── test_basic.py                 # Basic functionality tests
│
├── 📖 docs/                           # Documentation materials
│   ├── FILE_STRUCTURE.md             # Project structure guide
│   ├── THEORY.md                     # Scientific theory background
│   └── presentations/                # Teaching materials (PPT)
│
├── 🏛️ Zhou_NCC_Code/                  # 📦 LEGACY: Original land-atmosphere code (READ-ONLY)
├── 🏛️ bgcr-budyko/                    # 📦 LEGACY: Original BGCR implementation (READ-ONLY)
├── 📄 paper_replication_GCP_Subdaily_Evap/ # Research paper replication code
├── 📚 tutorials/                      # Step-by-step learning tutorials
│
├── 📝 README.md                       # This file
├── 📝 CLAUDE.md                       # AI assistant guide (internal)
├── ⚙️  setup.py                        # Package installation script
├── 📋 requirements.txt                # Python dependencies
└── 🔍 .gitignore                     # Git ignore patterns
```

#### 🎯 Dependency Relationships

```
petcr/
  ├── constants.py          [Base Layer - No dependencies]
  │
  ├── physics.py            [Physics Layer]
  │   └── uses: constants
  │
  ├── models.py             [Traditional CR Layer]
  │   └── uses: constants
  │
  ├── land_atmosphere.py    [Energy Balance Layer]
  │   └── uses: constants, physics
  │
  ├── bgcr_model.py         [Catchment Scale Layer]
  │   └── uses: constants, physics
  │
  ├── attribution.py        [Attribution Analysis Layer]
  │   └── uses: land_atmosphere
  │
  ├── subdaily.py           [Sub-daily Model Layer]
  │   └── uses: constants, physics, stability
  │
  └── utils.py              [Utilities Layer]
      └── uses: land_atmosphere, bgcr_model
```

**Key Design Principles:**
- ✅ **Layered Architecture**: Lower layers have no dependencies on upper layers
- ✅ **Single Source of Truth**: All physical constants in `constants.py`
- ✅ **Strict SI Units**: Consistent units throughout (Temperature in K, Pressure in Pa, Energy flux in W/m²)
- ✅ **Minimal Coupling**: Each module can be used independently

---

### 🧭 Core Code Navigation

#### 🚀 Entry Points (Start Here)

**For Users:**
1. **`petcr/__init__.py`** - Public API, see all available functions
2. **`examples/example_sigmoid.py`** - Simplest example to understand the library
3. **`examples/compare_all_three_methods.py`** - Comprehensive overview of all methods

**For Developers:**
1. **`petcr/constants.py`** - Understand physical constants used throughout
2. **`petcr/models.py`** - See how CR models are implemented
3. **`tests/test_basic.py`** - Understand expected behavior and validation

#### 🔑 Core Logic Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| **`petcr/models.py`** | Traditional CR models | `sigmoid_cr()`, `bouchet_cr()`, `polynomial_cr()` |
| **`petcr/physics.py`** | Physical calculations | `penman_potential_et()`, `priestley_taylor_et()` |
| **`petcr/land_atmosphere.py`** | Energy balance PET | `calculate_pet_land()`, `calculate_wet_bowen_ratio()` |
| **`petcr/bgcr_model.py`** | Monthly catchment ET | `calculate_bgcr_et()`, `bgcr_monthly()` |
| **`petcr/attribution.py`** | Climate attribution | `attribution_analysis()`, `calibrate_budyko_parameter()` |
| **`petcr/utils.py`** | Data utilities | `generate_sample_data()`, `load_fluxnet_data()` |

#### 🗺️ Routing Map (Main Workflows)

```
Workflow 1: Traditional CR Estimation
────────────────────────────────────
User Input → physics.py (calculate Ep, Ew) 
         → models.py (apply CR model) 
         → Actual ET output

Workflow 2: Land-Atmosphere Analysis
────────────────────────────────────
Energy Fluxes → land_atmosphere.py (calculate PETe, PETa)
            → attribution.py (separate climate/land effects)
            → Attribution results

Workflow 3: Monthly Catchment ET
────────────────────────────────────
Meteorology + Precip → bgcr_model.py (calculate w parameter)
                    → bgcr_model.py (estimate monthly ET)
                    → ET time series
```

---

### 🎓 Code Reading Path (Step-by-Step Guide)

**For absolute beginners (30 minutes):**

1. **Step 1** (5 min): Read `README.md` (this file) to understand what the library does
   
2. **Step 2** (10 min): Open and run `examples/example_sigmoid.py`
   - Understand input/output format
   - See how to call a simple CR model
   - Observe the meteorological variables used

3. **Step 3** (10 min): Read `petcr/__init__.py`
   - See all available functions in the public API
   - Understand the three main methods
   - Note the bilingual documentation

4. **Step 4** (5 min): Skim `petcr/models.py` (lines 1-100)
   - See how a CR model is implemented
   - Understand the math behind sigmoid_cr()
   - Note input validation and physical constraints

**For developers who want to modify code (2-3 hours):**

1. **Phase 1 - Understand the Foundation** (30 min)
   ```
   petcr/constants.py        → Physical constants (γ, λ, Cp, etc.)
   petcr/physics.py          → Penman equation, Priestley-Taylor
   tests/test_basic.py       → See expected behavior and edge cases
   ```

2. **Phase 2 - Choose Your Method** (30 min)
   ```
   Traditional CR Path:
     petcr/models.py         → 5 CR model implementations
     examples/compare_models.py → How models compare
   
   Land-Atmosphere Path:
     petcr/land_atmosphere.py → PETe/PETa calculation
     examples/example_land_atmosphere.py
   
   BGCR-Budyko Path:
     petcr/bgcr_model.py     → Monthly ET with spatial heterogeneity
     examples/spatial_bgcr_example.py
   ```

3. **Phase 3 - Advanced Topics** (1 hour)
   ```
   Attribution Analysis:
     petcr/attribution.py    → Separate climate vs land effects
     examples/example_attribution_analysis.py
   
   Real Data Workflows:
     petcr/utils.py          → Data loading (FLUXNET, CMIP6)
     examples/real_data_workflow.py
   
   Sub-daily Models:
     petcr/subdaily.py       → High-frequency ET estimation
     examples/example_subdaily_gcp.py
   ```

4. **Phase 4 - Understanding Data Flow** (30 min)
   - Trace a calculation from input to output
   - Follow variable transformations (units, constraints)
   - Understand error handling and validation

**Data Flow Example (Traditional CR):**

```python
# USER INPUT (meteorological variables)
net_radiation = 500.0      # W/m²
temperature = 20.0         # °C
wind_speed = 2.0          # m/s
# ... other variables

# STEP 1: Calculate potential ET components
ep = penman_potential_et(...)           # → petcr/physics.py
ew = priestley_taylor_et(...)           # → petcr/physics.py

# STEP 2: Apply CR model
ea = sigmoid_cr(ep, ew, beta=0.5)      # → petcr/models.py

# STEP 3: Output actual ET
# ea is now actual evapotranspiration in W/m²
```

**Data Transformation Flow:**

```
Raw Meteorology
    ↓ (unit conversion, validation)
Standardized SI Units
    ↓ (physics calculations)
Potential ET Components (Ep, Ew)
    ↓ (CR model application)
Actual ET (Ea)
    ↓ (physical constraints: 0 ≤ Ea ≤ min(Ep, Ew))
Valid Output
```

---

### 🏢 Business Scenario Mapping

#### Real-World Concepts → Code Implementation

| Business/Research Scenario | Code Components | Key Functions |
|---------------------------|-----------------|---------------|
| **"Calculate crop water requirements"** | Traditional CR models | `petcr.sigmoid_cr()`, `petcr.penman_potential_et()` |
| **"Analyze drought conditions"** | Land-atmosphere framework | `petcr.calculate_pet_land()`, check PETe vs PETa ratio |
| **"Attribute ET changes to climate warming"** | Attribution analysis | `petcr.attribution_analysis()`, `petcr.calibrate_budyko_parameter()` |
| **"Estimate monthly catchment water balance"** | BGCR-Budyko model | `petcr.calculate_bgcr_et()`, `petcr.calculate_seasonality_index()` |
| **"Process FLUXNET tower data"** | Data utilities | `petcr.load_fluxnet_data()`, `petcr.batch_calculate_pet()` |
| **"Understand surface-atmosphere coupling"** | Energy balance analysis | `petcr.calculate_wet_bowen_ratio()`, βw interpretation |
| **"Handle spatial heterogeneity in basins"** | Distributed parameters | `petcr.calculate_budyko_w_from_SI_albedo()` |
| **"Detect land use change impacts"** | Attribution + time series | `petcr.attribution_analysis()` with land surface term |

#### Specific Use Cases with Code Paths

**Use Case 1: Agricultural Water Management**
```python
# Scenario: A farmer needs daily crop water requirements
# → Use Method 1: Traditional CR

import petcr

# Calculate potential ET from weather station data
ep = petcr.penman_potential_et(net_radiation=500, temperature=25, 
                                wind_speed=2.0, ...)
ew = petcr.priestley_taylor_et(net_radiation=500, temperature=25, ...)

# Estimate actual ET under current soil moisture
ea = petcr.sigmoid_cr(ep, ew, beta=0.5)

# Result: ea is crop water use in W/m² (convert to mm/day for irrigation)
```

**Use Case 2: Climate Change Impact Assessment**
```python
# Scenario: Researcher wants to separate climate vs land surface effects
# → Use Method 2: Land-Atmosphere Framework + Attribution

import petcr

# Load 30-year climate model data
data = petcr.load_cmip6_data('1pctCO2_experiment.nc')

# Perform attribution analysis
results = petcr.attribution_analysis(
    et_timeseries=data['et'],
    pete_timeseries=data['pete'],
    pr_timeseries=data['pr'],
    window_size=30
)

# Result: Separate climate contribution vs land surface contribution
# results['et_climate'] = ET change due to climate
# results['et_landsurf'] = ET change due to land surface changes
```

**Use Case 3: Basin-Scale Hydrological Modeling**
```python
# Scenario: Water resources engineer needs monthly water balance for a basin
# → Use Method 3: BGCR-Budyko

import petcr

# Basin characteristics
seasonality_index = 0.6  # Precipitation seasonality
albedo = 0.25            # Basin average albedo

# Calculate monthly ET for the basin
results = petcr.calculate_bgcr_et(
    net_radiation=150, temperature=20, wind_speed=2.5,
    actual_vapor_pressure=1.5, saturation_vapor_pressure=2.3,
    precipitation=80, seasonality_index=seasonality_index,
    albedo=albedo
)

# Result: results['et'] is monthly ET accounting for spatial heterogeneity
```

#### Class/Function → Business Concept Mapping

| Code Element | Business Concept | Explanation |
|--------------|------------------|-------------|
| `sigmoid_cr()` | **Dryness-wetness transition** | Models smooth transition from wet to dry conditions |
| `calculate_pet_land()` | **Surface energy budget** | Represents how energy partitions between heating and evaporation |
| `PETe` | **Energy-limited evaporation** | Maximum ET when water is available (energy is limiting factor) |
| `PETa` | **Atmosphere-limited evaporation** | Maximum ET when energy is available (atmospheric demand limits) |
| `wet_bowen_ratio` | **Partitioning efficiency** | How efficiently surface converts available energy to evaporation |
| `attribution_analysis()` | **Change detection & causality** | Separates "why did ET change?" into climate vs land factors |
| `budyko_parameter (n)` | **Catchment water retention** | Represents catchment's ability to retain water (vegetation, soil) |
| `seasonality_index (SI)` | **Precipitation variability** | Quantifies how concentrated precipitation is in time |
| `bgcr_monthly()` | **Long-term water balance** | Integrates short-term dynamics into monthly/annual water budget |

---

### 🚀 Quick Start Guide

#### Installation

```bash
# Clone the repository
git clone https://github.com/licm13/PET-CR.git
cd PET-CR

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

#### Your First Calculation (2 minutes)

```python
import petcr

# Example 1: Calculate actual ET using traditional CR model
ep = 400.0  # Penman potential ET [W/m²]
ew = 350.0  # Priestley-Taylor ET [W/m²]

ea = petcr.sigmoid_cr(ep=ep, ew=ew, beta=0.5)
print(f"Actual ET: {ea:.2f} W/m²")
# Output: Actual ET: 331.78 W/m²
```

#### Run Examples

```bash
# Basic CR model
python examples/example_sigmoid.py

# Land-atmosphere framework
python examples/example_land_atmosphere.py

# Compare all three methods
python examples/compare_all_three_methods.py

# Climate attribution analysis
python examples/example_attribution_analysis.py
```

---

### 🔧 Development Workflow

#### For Adding New Features

1. **Choose the right module**:
   - New CR model? → Add to `petcr/models.py`
   - New physical calculation? → Add to `petcr/physics.py`
   - New analysis method? → Consider new module or extend existing

2. **Follow conventions**:
   - Use SI units throughout (see `petcr/constants.py`)
   - Add bilingual docstrings (English/Chinese)
   - Include input validation and physical constraints
   - Write unit tests in `tests/`

3. **Test your changes**:
   ```bash
   pytest tests/                    # Run all tests
   pytest tests/test_basic.py -v    # Run specific test file
   ```

4. **Create an example**:
   - Add to `examples/` directory
   - Show typical use case
   - Include visualization if applicable
   - Add bilingual comments

5. **Update documentation**:
   - Add function to `petcr/__init__.py` exports
   - Update README.md if needed
   - Add to API reference table

#### Common Development Patterns

**Pattern 1: Vectorized Operations**
```python
import numpy as np

def my_function(value):
    """Works with both scalars and arrays."""
    value = np.asarray(value, dtype=float)  # Convert to numpy array
    result = np.sqrt(value) * 2.5           # Vectorized operation
    return result
```

**Pattern 2: Physical Constraints**
```python
def calculate_et(ep, ew):
    """ET cannot exceed potential ET."""
    ea = some_calculation(ep, ew)
    
    # Apply physical constraints
    ea = np.maximum(ea, 0)              # Cannot be negative
    ea = np.minimum(ea, np.minimum(ep, ew))  # Cannot exceed potential
    
    return ea
```

**Pattern 3: Safe Division**
```python
def safe_divide(numerator, denominator, fill_value=0.0):
    """Avoid division by zero."""
    result = np.divide(
        numerator, 
        denominator,
        out=np.full_like(numerator, fill_value, dtype=float),
        where=(denominator != 0)
    )
    return result
```

---

### 📚 Available Models Reference

#### Method 1: Traditional CR Models

| Model | Function | Parameters | Reference |
|-------|----------|------------|-----------|
| Sigmoid | `sigmoid_cr(ep, ew, beta=0.5)` | β: shape parameter | Han & Tian (2018) |
| Polynomial | `polynomial_cr(ep, ew, b=1.0)` | b: polynomial degree | Brutsaert (2015) |
| Rescaled Power | `rescaled_power_cr(ep, ew, n=2.0)` | n: power exponent | Szilagyi et al. (2017) |
| Bouchet | `bouchet_cr(ep, ew)` | None (symmetric) | Bouchet (1963) |
| Advection-Aridity | `aa_cr(ep, ew, ea_min)` | ea_min: minimum ET | Brutsaert & Stricker (1979) |

#### Method 2: Land-Atmosphere Functions

| Function | Purpose | Key Output |
|----------|---------|------------|
| `calculate_pet_land()` | PET for land surfaces | PETe, PETa, βw, ET |
| `calculate_pet_ocean()` | PET for water surfaces | PET_wet, PET_dry |
| `calculate_wet_bowen_ratio()` | Bowen ratio calculation | βw (constrained) |
| `batch_calculate_pet()` | Time series processing | Arrays of results |

#### Method 3: BGCR-Budyko Functions

| Function | Purpose | Key Output |
|----------|---------|------------|
| `calculate_bgcr_et()` | High-level interface | Monthly ET, w, β_c |
| `bgcr_monthly()` | Core model | ET from GCR-Budyko |
| `calculate_penman_components()` | Decompose Penman | E_rad, E_aero |
| `calculate_seasonality_index()` | Precip seasonality | SI index |
| `calculate_budyko_w_from_SI()` | Parameter (BGCR-1) | w from SI only |
| `calculate_budyko_w_from_SI_albedo()` | Parameter (BGCR-2) | w from SI and albedo |

---

### 🧪 Testing and Validation

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=petcr --cov-report=html

# Run specific test
pytest tests/test_basic.py::test_sigmoid_cr -v
```

**Test Structure:**
- `tests/test_basic.py` - Core functionality tests
- Examples serve as integration tests
- Physical constraint validation in each test

---

### 📊 Example Gallery

All examples generate figures in `examples/figures/`:

1. **example_sigmoid.py** - CR model response curves
2. **compare_models.py** - Multi-model comparison
3. **example_land_atmosphere.py** - Energy balance analysis
4. **example_attribution_analysis.py** - Climate attribution plots
5. **advanced_analysis.py** - 30-year trends, extreme events
6. **spatial_bgcr_example.py** - Spatial heterogeneity visualization

---

### 📖 Citation

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

---

### 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Update documentation (including bilingual docstrings)
6. Submit a pull request

**Coding Standards:**
- Use SI units exclusively
- Add bilingual documentation (English/Chinese)
- Follow existing code patterns
- Validate inputs and apply physical constraints
- Write unit tests

---

### 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: Report via [GitHub Issues](https://github.com/licm13/PET-CR/issues)
- **Questions**: Contact Sha Zhou (shazhou21@bnu.edu.cn)

---

### 📜 License

MIT License - see LICENSE file for details.

---

### 👥 Authors

- **PET-CR Contributors**
- **Original Land-Atmosphere Framework**: Sha Zhou (周沙), Beijing Normal University
- **BGCR-Budyko Integration**: PET-CR Team

---

### 🔖 Keywords

`evapotranspiration` `complementary-relationship` `hydrology` `climate-science` `land-atmosphere-interaction` `budyko-framework` `python` `scientific-computing`

---

<a name="中文"></a>
## 📖 中文文档

### 🎯 一句话概括项目

**PET-CR** 是一个基于**互补关系（CR）理论**的 **Python 3.9+科学计算库**，通过三种互补方法估算实际蒸散发（ET）：传统模型、陆地-大气能量平衡分析、以及考虑空间异质性的月尺度流域估算。

**核心技术栈：**
- **语言**: Python 3.9+
- **核心依赖**: NumPy, SciPy, Pandas
- **可视化**: Matplotlib, Seaborn
- **数据处理**: xarray, netCDF4 (用于气候模型数据)
- **测试**: pytest
- **科学领域**: 水文学、气候科学、陆地-大气相互作用

---

### 🏗️ 架构概述

PET-CR 提供**三种不同但互补的方法**用于蒸散发估算：

**方法1：传统CR模型** 🔄
- **使用场景**: 您已有预计算的Penman (Ep)和Priestley-Taylor (Ew)潜在蒸散发
- **功能**: 应用经典CR理论从潜在蒸散发分量估算实际ET
- **模型**: Sigmoid, Polynomial, Rescaled Power, Bouchet, Advection-Aridity
- **核心模块**: `petcr.models`

**方法2：陆地-大气框架** 🌤️
- **使用场景**: 您有能量通量测量（潜热/感热）并想了解陆地-大气耦合
- **功能**: 计算能量基础PET (PETe)和空气动力学基础PET (PETa)，执行气候归因分析
- **研究基础**: Zhou & Yu (2025, Nature Climate Change)
- **核心模块**: `petcr.land_atmosphere`, `petcr.attribution`

**方法3：BGCR-Budyko模型** 🏔️
- **使用场景**: 需要考虑降水季节性的异质流域月尺度ET估算
- **功能**: 结合长期Budyko框架与短期广义CR
- **特色功能**: 通过分布式Budyko参数处理空间变异性
- **核心模块**: `petcr.bgcr_model`

---

### 📁 目录结构详解

```
PET-CR/
├── 📦 petcr/                          # ⭐ 主包 - 所有活跃开发在此进行
│   ├── __init__.py                   # 🚪 包入口点，导出公共API
│   ├── constants.py                  # 🔧 物理常数（唯一真实来源）
│   ├── models.py                     # 📊 传统CR模型（方法1）
│   ├── physics.py                    # ⚛️  核心物理计算（Penman, Priestley-Taylor）
│   ├── land_atmosphere.py            # 🌍 陆地-大气框架（方法2）
│   ├── bgcr_model.py                 # 🏔️ BGCR-Budyko模型（方法3）
│   ├── attribution.py                # 📈 气候归因分析
│   ├── subdaily.py                   # ⏰ 亚日尺度GCP模型
│   ├── stability.py                  # 🎯 稳定性函数
│   └── utils.py                      # ��️ 数据生成与加载工具
│
├── 📚 examples/                       # ⭐ 从这里开始 - 通过示例学习
│   ├── example_sigmoid.py            # 101: 基础CR模型使用
│   ├── example_land_atmosphere.py    # 201: 能量通量分析
│   ├── example_attribution_analysis.py # 301: 气候归因
│   ├── compare_models.py             # 🔬 比较传统CR模型
│   ├── compare_all_three_methods.py  # 🔬 比较所有三种方法
│   ├── advanced_analysis.py          # 🎓 30年趋势与极端事件
│   ├── spatial_bgcr_example.py       # 🗺️ 空间异质性
│   ├── real_data_workflow.py         # 📊 真实数据处理
│   └── figures/                      # 📊 生成的可视化输出
│
├── 🧪 tests/                          # 单元测试验证
│   └── test_basic.py                 # 基础功能测试
│
├── 📖 docs/                           # 文档材料
│   ├── FILE_STRUCTURE.md             # 项目结构指南
│   ├── THEORY.md                     # 科学理论背景
│   └── presentations/                # 教学材料（PPT）
│
├── 🏛️ Zhou_NCC_Code/                  # 📦 遗留代码：原始陆地-大气代码（只读）
├── 🏛️ bgcr-budyko/                    # 📦 遗留代码：原始BGCR实现（只读）
├── 📄 paper_replication_GCP_Subdaily_Evap/ # 研究论文复现代码
├── 📚 tutorials/                      # 分步学习教程
│
├── 📝 README.md                       # 本文件
├── 📝 CLAUDE.md                       # AI助手指南（内部）
├── ⚙️  setup.py                        # 包安装脚本
├── 📋 requirements.txt                # Python依赖
└── 🔍 .gitignore                     # Git忽略规则
```

#### 🎯 依赖关系

```
petcr/
  ├── constants.py          [基础层 - 无依赖]
  │
  ├── physics.py            [物理层]
  │   └── 使用: constants
  │
  ├── models.py             [传统CR层]
  │   └── 使用: constants
  │
  ├── land_atmosphere.py    [能量平衡层]
  │   └── 使用: constants, physics
  │
  ├── bgcr_model.py         [流域尺度层]
  │   └── 使用: constants, physics
  │
  ├── attribution.py        [归因分析层]
  │   └── 使用: land_atmosphere
  │
  ├── subdaily.py           [亚日尺度模型层]
  │   └── 使用: constants, physics, stability
  │
  └── utils.py              [工具层]
      └── 使用: land_atmosphere, bgcr_model
```

**关键设计原则：**
- ✅ **分层架构**: 底层不依赖上层
- ✅ **单一真实来源**: 所有物理常数在`constants.py`中
- ✅ **严格SI单位**: 全程一致的单位（温度K、压强Pa、能量通量W/m²）
- ✅ **最小耦合**: 每个模块可独立使用

---

### 🧭 核心代码导航

#### 🚀 入口点（从这里开始）

**用户视角：**
1. **`petcr/__init__.py`** - 公共API，查看所有可用函数
2. **`examples/example_sigmoid.py`** - 最简单的示例，理解库的使用
3. **`examples/compare_all_three_methods.py`** - 全面概览三种方法

**开发者视角：**
1. **`petcr/constants.py`** - 理解全局使用的物理常数
2. **`petcr/models.py`** - 了解CR模型如何实现
3. **`tests/test_basic.py`** - 理解预期行为和验证方法

#### 🔑 核心逻辑文件

| 文件 | 用途 | 关键函数 |
|------|------|----------|
| **`petcr/models.py`** | 传统CR模型 | `sigmoid_cr()`, `bouchet_cr()`, `polynomial_cr()` |
| **`petcr/physics.py`** | 物理计算 | `penman_potential_et()`, `priestley_taylor_et()` |
| **`petcr/land_atmosphere.py`** | 能量平衡PET | `calculate_pet_land()`, `calculate_wet_bowen_ratio()` |
| **`petcr/bgcr_model.py`** | 月尺度流域ET | `calculate_bgcr_et()`, `bgcr_monthly()` |
| **`petcr/attribution.py`** | 气候归因 | `attribution_analysis()`, `calibrate_budyko_parameter()` |
| **`petcr/utils.py`** | 数据工具 | `generate_sample_data()`, `load_fluxnet_data()` |

#### 🗺️ 路由图（主要工作流程）

```
工作流1：传统CR估算
────────────────────
用户输入 → physics.py (计算 Ep, Ew) 
       → models.py (应用CR模型) 
       → 实际ET输出

工作流2：陆地-大气分析
────────────────────
能量通量 → land_atmosphere.py (计算PETe, PETa)
        → attribution.py (分离气候/陆地效应)
        → 归因结果

工作流3：月尺度流域ET
────────────────────
气象+降水 → bgcr_model.py (计算w参数)
         → bgcr_model.py (估算月ET)
         → ET时间序列
```

---

### 🎓 代码阅读路径（分步指南）

**初学者路径（30分钟）：**

1. **步骤1** (5分钟): 阅读`README.md`（本文件）理解库的功能
   
2. **步骤2** (10分钟): 打开并运行`examples/example_sigmoid.py`
   - 理解输入/输出格式
   - 了解如何调用简单CR模型
   - 观察使用的气象变量

3. **步骤3** (10分钟): 阅读`petcr/__init__.py`
   - 查看公共API中所有可用函数
   - 理解三种主要方法
   - 注意双语文档

4. **步骤4** (5分钟): 浏览`petcr/models.py`（前100行）
   - 了解CR模型如何实现
   - 理解sigmoid_cr()背后的数学
   - 注意输入验证和物理约束

**开发者修改代码路径（2-3小时）：**

1. **阶段1 - 理解基础** (30分钟)
   ```
   petcr/constants.py        → 物理常数（γ, λ, Cp等）
   petcr/physics.py          → Penman方程、Priestley-Taylor
   tests/test_basic.py       → 查看预期行为和边界情况
   ```

2. **阶段2 - 选择您的方法** (30分钟)
   ```
   传统CR路径:
     petcr/models.py         → 5个CR模型实现
     examples/compare_models.py → 模型如何比较
   
   陆地-大气路径:
     petcr/land_atmosphere.py → PETe/PETa计算
     examples/example_land_atmosphere.py
   
   BGCR-Budyko路径:
     petcr/bgcr_model.py     → 考虑空间异质性的月ET
     examples/spatial_bgcr_example.py
   ```

3. **阶段3 - 高级主题** (1小时)
   ```
   归因分析:
     petcr/attribution.py    → 分离气候vs陆地效应
     examples/example_attribution_analysis.py
   
   真实数据工作流:
     petcr/utils.py          → 数据加载（FLUXNET, CMIP6）
     examples/real_data_workflow.py
   
   亚日尺度模型:
     petcr/subdaily.py       → 高频ET估算
     examples/example_subdaily_gcp.py
   ```

4. **阶段4 - 理解数据流** (30分钟)
   - 追踪从输入到输出的计算过程
   - 跟踪变量转换（单位、约束）
   - 理解错误处理和验证

**数据流示例（传统CR）：**

```python
# 用户输入（气象变量）
net_radiation = 500.0      # W/m²
temperature = 20.0         # °C
wind_speed = 2.0          # m/s
# ... 其他变量

# 步骤1: 计算潜在ET分量
ep = penman_potential_et(...)           # → petcr/physics.py
ew = priestley_taylor_et(...)           # → petcr/physics.py

# 步骤2: 应用CR模型
ea = sigmoid_cr(ep, ew, beta=0.5)      # → petcr/models.py

# 步骤3: 输出实际ET
# ea 现在是实际蒸散发，单位W/m²
```

**数据转换流程：**

```
原始气象数据
    ↓ (单位转换、验证)
标准化SI单位
    ↓ (物理计算)
潜在ET分量（Ep, Ew）
    ↓ (应用CR模型)
实际ET（Ea）
    ↓ (物理约束: 0 ≤ Ea ≤ min(Ep, Ew))
有效输出
```

---

### 🏢 业务场景映射

#### 现实世界概念 → 代码实现

| 业务/研究场景 | 代码组件 | 关键函数 |
|--------------|---------|----------|
| **"计算作物需水量"** | 传统CR模型 | `petcr.sigmoid_cr()`, `petcr.penman_potential_et()` |
| **"分析干旱状况"** | 陆地-大气框架 | `petcr.calculate_pet_land()`, 检查PETe vs PETa比值 |
| **"将ET变化归因于气候变暖"** | 归因分析 | `petcr.attribution_analysis()`, `petcr.calibrate_budyko_parameter()` |
| **"估算月尺度流域水平衡"** | BGCR-Budyko模型 | `petcr.calculate_bgcr_et()`, `petcr.calculate_seasonality_index()` |
| **"处理FLUXNET涡度相关数据"** | 数据工具 | `petcr.load_fluxnet_data()`, `petcr.batch_calculate_pet()` |
| **"理解地表-大气耦合"** | 能量平衡分析 | `petcr.calculate_wet_bowen_ratio()`, βw解释 |
| **"处理流域空间异质性"** | 分布式参数 | `petcr.calculate_budyko_w_from_SI_albedo()` |
| **"检测土地利用变化影响"** | 归因+时间序列 | `petcr.attribution_analysis()`的陆地表面项 |

#### 具体用例及代码路径

**用例1：农业水管理**
```python
# 场景: 农民需要每日作物需水量
# → 使用方法1: 传统CR

import petcr

# 从气象站数据计算潜在ET
ep = petcr.penman_potential_et(net_radiation=500, temperature=25, 
                                wind_speed=2.0, ...)
ew = petcr.priestley_taylor_et(net_radiation=500, temperature=25, ...)

# 在当前土壤湿度下估算实际ET
ea = petcr.sigmoid_cr(ep, ew, beta=0.5)

# 结果: ea是作物用水量，单位W/m²（转换为mm/day用于灌溉）
```

**用例2：气候变化影响评估**
```python
# 场景: 研究人员想分离气候vs陆地表面效应
# → 使用方法2: 陆地-大气框架+归因

import petcr

# 加载30年气候模型数据
data = petcr.load_cmip6_data('1pctCO2_experiment.nc')

# 执行归因分析
results = petcr.attribution_analysis(
    et_timeseries=data['et'],
    pete_timeseries=data['pete'],
    pr_timeseries=data['pr'],
    window_size=30
)

# 结果: 分离气候贡献vs陆地表面贡献
# results['et_climate'] = 气候引起的ET变化
# results['et_landsurf'] = 陆地表面变化引起的ET变化
```

**用例3：流域尺度水文建模**
```python
# 场景: 水资源工程师需要流域月水平衡
# → 使用方法3: BGCR-Budyko

import petcr

# 流域特征
seasonality_index = 0.6  # 降水季节性
albedo = 0.25            # 流域平均反照率

# 计算流域月ET
results = petcr.calculate_bgcr_et(
    net_radiation=150, temperature=20, wind_speed=2.5,
    actual_vapor_pressure=1.5, saturation_vapor_pressure=2.3,
    precipitation=80, seasonality_index=seasonality_index,
    albedo=albedo
)

# 结果: results['et']是考虑空间异质性的月ET
```

#### 类/函数 → 业务概念映射

| 代码元素 | 业务概念 | 解释 |
|---------|---------|------|
| `sigmoid_cr()` | **干湿转换** | 模拟从湿润到干旱条件的平滑过渡 |
| `calculate_pet_land()` | **地表能量收支** | 代表能量如何在加热和蒸发间分配 |
| `PETe` | **能量限制蒸发** | 水可用时的最大ET（能量是限制因素） |
| `PETa` | **大气限制蒸发** | 能量可用时的最大ET（大气需求限制） |
| `wet_bowen_ratio` | **分配效率** | 地表将可用能量转化为蒸发的效率 |
| `attribution_analysis()` | **变化检测与因果关系** | 将"ET为何变化？"分解为气候vs陆地因素 |
| `budyko_parameter (n)` | **流域保水能力** | 代表流域保持水分的能力（植被、土壤） |
| `seasonality_index (SI)` | **降水变异性** | 量化降水在时间上的集中程度 |
| `bgcr_monthly()` | **长期水平衡** | 将短期动态整合到月/年水收支中 |

---

### 🚀 快速开始指南

#### 安装

```bash
# 克隆仓库
git clone https://github.com/licm13/PET-CR.git
cd PET-CR

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装包
pip install -e .
```

#### 您的第一次计算（2分钟）

```python
import petcr

# 示例1: 使用传统CR模型计算实际ET
ep = 400.0  # Penman潜在蒸散发 [W/m²]
ew = 350.0  # Priestley-Taylor蒸散发 [W/m²]

ea = petcr.sigmoid_cr(ep=ep, ew=ew, beta=0.5)
print(f"实际ET: {ea:.2f} W/m²")
# 输出: 实际ET: 331.78 W/m²
```

#### 运行示例

```bash
# 基础CR模型
python examples/example_sigmoid.py

# 陆地-大气框架
python examples/example_land_atmosphere.py

# 比较所有三种方法
python examples/compare_all_three_methods.py

# 气候归因分析
python examples/example_attribution_analysis.py
```

---

### 🔧 开发工作流程

#### 添加新功能

1. **选择正确的模块**:
   - 新CR模型？ → 添加到`petcr/models.py`
   - 新物理计算？ → 添加到`petcr/physics.py`
   - 新分析方法？ → 考虑新模块或扩展现有模块

2. **遵循约定**:
   - 全程使用SI单位（参见`petcr/constants.py`）
   - 添加双语文档字符串（英文/中文）
   - 包含输入验证和物理约束
   - 在`tests/`中编写单元测试

3. **测试您的更改**:
   ```bash
   pytest tests/                    # 运行所有测试
   pytest tests/test_basic.py -v    # 运行特定测试文件
   ```

4. **创建示例**:
   - 添加到`examples/`目录
   - 展示典型用例
   - 如适用，包含可视化
   - 添加双语注释

5. **更新文档**:
   - 将函数添加到`petcr/__init__.py`导出
   - 如需要更新README.md
   - 添加到API参考表

#### 常用开发模式

**模式1: 向量化操作**
```python
import numpy as np

def my_function(value):
    \"\"\"适用于标量和数组。\"\"\"
    value = np.asarray(value, dtype=float)  # 转换为numpy数组
    result = np.sqrt(value) * 2.5           # 向量化操作
    return result
```

**模式2: 物理约束**
```python
def calculate_et(ep, ew):
    \"\"\"ET不能超过潜在ET。\"\"\"
    ea = some_calculation(ep, ew)
    
    # 应用物理约束
    ea = np.maximum(ea, 0)              # 不能为负
    ea = np.minimum(ea, np.minimum(ep, ew))  # 不能超过潜在值
    
    return ea
```

**模式3: 安全除法**
```python
def safe_divide(numerator, denominator, fill_value=0.0):
    \"\"\"避免除零错误。\"\"\"
    result = np.divide(
        numerator, 
        denominator,
        out=np.full_like(numerator, fill_value, dtype=float),
        where=(denominator != 0)
    )
    return result
```

---

### 📚 可用模型参考

#### 方法1: 传统CR模型

| 模型 | 函数 | 参数 | 参考文献 |
|------|------|------|----------|
| Sigmoid | `sigmoid_cr(ep, ew, beta=0.5)` | β: 形状参数 | Han & Tian (2018) |
| Polynomial | `polynomial_cr(ep, ew, b=1.0)` | b: 多项式次数 | Brutsaert (2015) |
| Rescaled Power | `rescaled_power_cr(ep, ew, n=2.0)` | n: 幂指数 | Szilagyi et al. (2017) |
| Bouchet | `bouchet_cr(ep, ew)` | 无（对称） | Bouchet (1963) |
| Advection-Aridity | `aa_cr(ep, ew, ea_min)` | ea_min: 最小ET | Brutsaert & Stricker (1979) |

#### 方法2: 陆地-大气函数

| 函数 | 用途 | 关键输出 |
|------|------|----------|
| `calculate_pet_land()` | 陆地表面PET | PETe, PETa, βw, ET |
| `calculate_pet_ocean()` | 水表面PET | PET_wet, PET_dry |
| `calculate_wet_bowen_ratio()` | 波文比计算 | βw（有约束） |
| `batch_calculate_pet()` | 时间序列处理 | 结果数组 |

#### 方法3: BGCR-Budyko函数

| 函数 | 用途 | 关键输出 |
|------|------|----------|
| `calculate_bgcr_et()` | 高级接口 | 月ET, w, β_c |
| `bgcr_monthly()` | 核心模型 | 来自GCR-Budyko的ET |
| `calculate_penman_components()` | 分解Penman | E_rad, E_aero |
| `calculate_seasonality_index()` | 降水季节性 | SI指数 |
| `calculate_budyko_w_from_SI()` | 参数（BGCR-1） | 仅从SI得w |
| `calculate_budyko_w_from_SI_albedo()` | 参数（BGCR-2） | 从SI和albedo得w |

---

### 🧪 测试和验证

```bash
# 运行所有测试
pytest tests/

# 运行带覆盖率报告
pytest tests/ --cov=petcr --cov-report=html

# 运行特定测试
pytest tests/test_basic.py::test_sigmoid_cr -v
```

**测试结构:**
- `tests/test_basic.py` - 核心功能测试
- 示例作为集成测试
- 每个测试中的物理约束验证

---

### 📊 示例画廊

所有示例在`examples/figures/`中生成图形：

1. **example_sigmoid.py** - CR模型响应曲线
2. **compare_models.py** - 多模型比较
3. **example_land_atmosphere.py** - 能量平衡分析
4. **example_attribution_analysis.py** - 气候归因图
5. **advanced_analysis.py** - 30年趋势、极端事件
6. **spatial_bgcr_example.py** - 空间异质性可视化

---

### 📖 引用

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

对于BGCR-Budyko模型:
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

---

### 🤝 贡献

欢迎贡献！请：

1. Fork仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 为新功能添加测试
4. 确保所有测试通过（`pytest tests/`）
5. 更新文档（包括双语文档字符串）
6. 提交拉取请求

**编码标准：**
- 专用SI单位
- 添加双语文档（英文/中文）
- 遵循现有代码模式
- 验证输入并应用物理约束
- 编写单元测试

---

### 📞 支持

- **文档**: 见`docs/`目录
- **问题**: 通过[GitHub Issues](https://github.com/licm13/PET-CR/issues)报告
- **咨询**: 联系周沙 (shazhou21@bnu.edu.cn)

---

### 📜 许可证

MIT许可证 - 详见LICENSE文件。

---

### 👥 作者

- **PET-CR贡献者**
- **原始陆地-大气框架**: 周沙，北京师范大学
- **BGCR-Budyko集成**: PET-CR团队

---

### 🔖 关键词

`蒸散发` `互补关系` `水文学` `气候科学` `陆地-大气相互作用` `Budyko框架` `python` `科学计算`

---

## 📚 附录：关键概念速查

### 物理概念对照表

| 英文 | 中文 | 符号 | 单位 |
|-----|------|------|------|
| Actual Evapotranspiration | 实际蒸散发 | Ea | W/m² or mm/day |
| Potential Evapotranspiration | 潜在蒸散发 | Ep | W/m² or mm/day |
| Priestley-Taylor ET | Priestley-Taylor蒸散发 | Ew | W/m² or mm/day |
| Energy-based PET | 能量基础PET | PETe | mm/day |
| Aerodynamics-based PET | 空气动力学基础PET | PETa | mm/day |
| Wet Bowen Ratio | 湿润波文比 | βw | - |
| Net Radiation | 净辐射 | Rn | W/m² |
| Latent Heat Flux | 潜热通量 | LH | W/m² |
| Sensible Heat Flux | 感热通量 | SH | W/m² |
| Budyko Parameter | Budyko参数 | n or w | - |
| Seasonality Index | 季节性指数 | SI | - |
| Dryness Index | 干燥度指数 | Ep/Ew | - |

### 常用单位转换

```python
# 温度转换
temperature_K = temperature_C + 273.15

# 压强转换
pressure_Pa = pressure_kPa * 1000

# ET单位转换（W/m² ↔ mm/day）
λ = 2.45e6  # 汽化潜热 [J/kg]
et_mm_day = et_W_m2 * 86400 / λ
et_W_m2 = et_mm_day * λ / 86400
```

---

## 🎯 快速决策树：选择合适的方法

```
您有什么数据？
    │
    ├─ 已有Ep和Ew → 使用方法1: 传统CR模型
    │                选择模型: sigmoid_cr, bouchet_cr等
    │
    ├─ 有能量通量(LH, SH) → 使用方法2: 陆地-大气框架
    │                        适用于: calculate_pet_land, attribution_analysis
    │
    └─ 有气象数据+降水 → 使用方法3: BGCR-Budyko模型
                         适用于: calculate_bgcr_et, bgcr_monthly

您的研究目标？
    │
    ├─ 日尺度ET估算 → 方法1或方法2
    ├─ 月尺度ET估算 → 方法3
    ├─ 气候归因分析 → 方法2 + attribution_analysis
    ├─ 流域异质性 → 方法3 + BGCR参数化
    └─ 陆地-大气耦合 → 方法2 + PETe/PETa分析
```

---

## 📞 获取帮助

### 常见问题（FAQ）

**Q: 如何选择合适的CR模型？**
A: 运行`examples/compare_models.py`查看不同模型的行为。通常sigmoid模型是好的起点。

**Q: 单位不匹配怎么办？**
A: 所有输入必须使用SI单位。温度用K，压强用Pa，能量通量用W/m²。参见`petcr/constants.py`。

**Q: 如何处理缺失数据？**
A: 参见`examples/integration_test_missing_data.py`了解处理策略。

**Q: 可以用于格网数据吗？**
A: 可以。所有函数支持numpy数组输入。参见`examples/spatial_bgcr_example.py`。

**Q: 如何加载自己的数据？**
A: 参见`examples/real_data_workflow.py`和`petcr/utils.py`中的数据加载函数。

### 联系方式

- **Email**: shazhou21@bnu.edu.cn (周沙)
- **GitHub**: https://github.com/licm13/PET-CR
- **Issues**: https://github.com/licm13/PET-CR/issues

---

## 🙏 致谢

感谢所有贡献者对PET-CR库的贡献。特别感谢：

- 周沙博士开发原始陆地-大气框架
- BGCR-Budyko模型的原始作者
- 所有测试和反馈的用户

---

**文档版本**: v1.0 (2025-12-08)

**最后更新**: 2025年12月8日

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

Made with ❤️ by PET-CR Contributors

</div>
