# PET-CR

蒸发互补理论分析 / Complementary Relationship Evapotranspiration Library

## 概述 / Overview

PET-CR 是一个用于估算实际蒸散发（Ea）的 Python 3.9+ 学术代码库，基于蒸发互补理论（Complementary Relationship, CR）。

PET-CR is a Python 3.9+ academic library for estimating actual evapotranspiration (Ea) using Complementary Relationship (CR) theory.

## 特性 / Features

- **核心 CR 模型 / Core CR Models**:
  - Sigmoid 模型 (Han & Tian, 2018) - 广义非线性模型
  - Polynomial 模型 (Brutsaert, 2015) - 多项式模型
  - Rescaled Power 模型 (Szilagyi et al., 2017) - 重标定幂函数模型
  - Bouchet 模型 (1963) - 经典对称模型
  - A-A 模型 (Advection-Aridity) - 非对称平流干旱模型

- **物理计算模块 / Physics Module**:
  - Penman 潜在蒸散发 (Penman, 1948)
  - Priestley-Taylor 蒸散发 (Priestley & Taylor, 1972)
  - 饱和水汽压差 (VPD)
  - 干湿表常数
  - 其他共享物理变量

- **标准化接口 / Standardized Interface**:
  - 统一的 SI 单位输入
  - 模块化设计
  - 详细的 NumPy 风格文档字符串
  - 完整的文献引用

## 安装 / Installation

```bash
# 从源码安装 / Install from source
git clone https://github.com/licm13/PET-CR.git
cd PET-CR
pip install -e .

# 或仅安装依赖 / Or just install dependencies
pip install -r requirements.txt
```

## 快速开始 / Quick Start

### 基本用法 / Basic Usage

```python
import numpy as np
from petcr import sigmoid_cr, penman_potential_et, priestley_taylor_et

# 输入气象数据 (SI 单位) / Input meteorological data (SI units)
net_radiation = 500.0      # W m⁻²
ground_heat_flux = 50.0    # W m⁻²
temperature = 20.0         # °C
relative_humidity = 50.0   # %
wind_speed = 2.0          # m s⁻¹
pressure = 101325.0       # Pa

# 计算潜在蒸散发 / Calculate potential ET
ep = penman_potential_et(
    net_radiation=net_radiation,
    ground_heat_flux=ground_heat_flux,
    temperature=temperature,
    relative_humidity=relative_humidity,
    wind_speed=wind_speed,
    pressure=pressure
)

# 计算湿环境蒸散发 / Calculate wet-environment ET
ew = priestley_taylor_et(
    net_radiation=net_radiation,
    ground_heat_flux=ground_heat_flux,
    temperature=temperature,
    pressure=pressure,
    alpha=1.26
)

# 使用 Sigmoid CR 模型估算实际蒸散发 / Estimate actual ET using Sigmoid CR
ea = sigmoid_cr(ep=ep, ew=ew, beta=0.5)

print(f"Potential ET (Ep): {ep:.2f} W m⁻²")
print(f"Wet-environment ET (Ew): {ew:.2f} W m⁻²")
print(f"Actual ET (Ea): {ea:.2f} W m⁻²")
```

### 时间序列分析 / Time Series Analysis

```python
import numpy as np
from petcr import sigmoid_cr, polynomial_cr, bouchet_cr

# 时间序列数据 / Time series data
ep_series = np.array([300, 400, 500, 600])  # W m⁻²
ew_series = np.array([350, 350, 350, 350])  # W m⁻²

# 比较不同模型 / Compare different models
ea_sigmoid = sigmoid_cr(ep=ep_series, ew=ew_series, beta=0.5)
ea_polynomial = polynomial_cr(ep=ep_series, ew=ew_series, b=2.0)
ea_bouchet = bouchet_cr(ep=ep_series, ew=ew_series)

print("Time series comparison:")
for i in range(len(ep_series)):
    print(f"Day {i+1}: Ep={ep_series[i]}, Ew={ew_series[i]}")
    print(f"  Sigmoid: {ea_sigmoid[i]:.2f} W m⁻²")
    print(f"  Polynomial: {ea_polynomial[i]:.2f} W m⁻²")
    print(f"  Bouchet: {ea_bouchet[i]:.2f} W m⁻²")
```

## 项目结构 / Project Structure

```
PET-CR/
├── petcr/                         # 主包目录 / Main package directory
│   ├── __init__.py               # 包初始化 / Package initialization
│   ├── models.py                 # CR 模型实现 / CR model implementations
│   └── physics.py                # 物理计算模块 / Physics calculations
├── tests/                         # 测试目录 / Tests directory
│   └── test_basic.py             # 基础功能测试 / Basic functionality tests
├── examples/                      # 示例脚本 / Example scripts
│   ├── example_sigmoid.py        # Sigmoid模型示例 / Sigmoid model example
│   ├── compare_models.py         # 模型对比示例 / Model comparison example
│   ├── advanced_analysis.py      # 高级综合分析 / Advanced comprehensive analysis
│   └── real_data_workflow.py     # 真实数据工作流 / Real data workflow
├── docs/                          # 文档目录 / Documentation directory
│   └── FILE_STRUCTURE.md         # 文件结构说明 / File structure documentation
├── requirements.txt               # 依赖包 / Dependencies
├── setup.py                      # 安装配置 / Setup configuration
└── README.md                     # 本文件 / This file
```

## 示例脚本说明 / Example Scripts

PET-CR提供了多个示例脚本，帮助用户快速上手：
PET-CR provides multiple example scripts to help users get started quickly:

### 1. example_sigmoid.py - Sigmoid模型基础示例
**适用场景 / Use Case**: 初学者入门、单一模型演示
**功能 / Features**:
- 单点计算演示
- 参数敏感性测试（不同beta值）
- 7天时间序列分析
- 基础统计输出

**运行方式 / How to Run**:
```bash
python -m examples.example_sigmoid
```

### 2. compare_models.py - 所有CR模型对比
**适用场景 / Use Case**: 模型选择、性能对比
**功能 / Features**:
- 5个CR模型同时对比
- 10天时间序列比较
- 模型特性说明
- 气候适用性建议

**运行方式 / How to Run**:
```bash
python -m examples.compare_models
```

### 3. advanced_analysis.py - 高级综合分析 (新增)
**适用场景 / Use Case**: 科研应用、深入分析
**功能 / Features**:
- 4种气候场景模拟（湿润、半干旱、干旱、温带海洋）
- 参数敏感性分析（beta、b、n参数）
- 季节变化特征分析
- 模型不确定性评估
- 自动生成可视化图表

**运行方式 / How to Run**:
```bash
# 基础运行（无绘图）
python -m examples.advanced_analysis

# 如需绘图功能，先安装matplotlib
pip install matplotlib
python -m examples.advanced_analysis
```

### 4. real_data_workflow.py - 真实数据工作流 (新增)
**适用场景 / Use Case**: 实际数据处理、批量计算
**功能 / Features**:
- 完整的数据处理类（MeteoDataProcessor）
- 数据质量控制和验证
- 批量ET计算
- 结果导出为CSV
- 易于修改用于真实气象站数据

**运行方式 / How to Run**:
```bash
python -m examples.real_data_workflow
```

**自定义数据输入示例 / Custom Data Input Example**:
```python
from examples.real_data_workflow import MeteoDataProcessor
import numpy as np

# 创建处理器 / Create processor
processor = MeteoDataProcessor(ground_heat_flux=50.0)

# 加载你的数据 / Load your data
processor.load_data(
    temperature=your_temp_data,      # numpy array
    relative_humidity=your_rh_data,
    net_radiation=your_rad_data,
    wind_speed=your_ws_data,
    pressure=your_pres_data,         # optional
    dates=your_dates                 # optional
)

# 质量控制 / Quality control
processor.quality_control()

# 计算ET / Calculate ET
results = processor.calculate_et()

# 导出结果 / Export results
processor.export_results('my_results.csv')
```

## 核心模型说明 / Core Models Description

### 1. Sigmoid CR 模型 / Sigmoid CR Model (Han & Tian, 2018)

广义非线性模型，使用 sigmoid 函数描述互补关系：

Generalized nonlinear model using sigmoid function:

```
Ea = Ew * [1 + (Ep/Ew)^β]^(-1/β)
```

**参数 / Parameters**:
- `beta`: 形状参数，控制 sigmoid 曲线的陡峭程度 / Shape parameter controlling curve steepness

**文献 / Reference**:
Han, S., & Tian, F. (2018). A review of the complementary principle of evaporation. *Hydrology and Earth System Sciences*, 22(3), 1813-1834.

### 2. Polynomial CR 模型 / Polynomial CR Model (Brutsaert, 2015)

带物理约束的多项式互补关系模型：

Polynomial CR with physical constraints:

```
Ea = Ew * [2 - (Ep/Ew)^b]
```

**参数 / Parameters**:
- `b`: 多项式指数，控制非线性程度 / Polynomial exponent controlling nonlinearity

**文献 / Reference**:
Brutsaert, W. (2015). A generalized complementary principle with physical constraints. *Water Resources Research*, 51(10), 8087-8093.

### 3. Rescaled Power CR 模型 / Rescaled Power CR Model (Szilagyi et al., 2017)

无需校准的重标定幂函数模型，适用于大陆尺度：

Calibration-free rescaled power model for continental scales:

```
Ea = Ew * [(2*Ew/Ep)^n - (Ew/Ep)^n]^(1/n)
```

**参数 / Parameters**:
- `n`: 幂指数 (默认 0.5) / Power exponent (default 0.5)

**文献 / Reference**:
Szilagyi, J., Crago, R., & Qualls, R. (2017). A calibration-free formulation. *Journal of Geophysical Research: Atmospheres*, 122(1), 264-278.

### 4. Bouchet CR 模型 / Bouchet CR Model (1963)

经典对称线性互补关系：

Classic symmetric linear CR:

```
Ea = 2*Ew - Ep
```

**文献 / Reference**:
Bouchet, R.J. (1963). Évapotranspiration réelle et potentielle. *IAHS Publication*, 62, 134-142.

### 5. A-A CR 模型 / A-A CR Model (Advection-Aridity)

非对称平流干旱互补关系模型：

Asymmetric advection-aridity CR model:

```
Ea = Ew                           (when Ep ≤ Ew)
Ea = Ew * [2 - Ep/Ew]            (when Ep > Ew)
```

**文献 / Reference**:
Brutsaert, W., & Stricker, H. (1979). An advection-aridity approach. *Water Resources Research*, 15(2), 443-450.

## API 文档 / API Documentation

### 物理模块 / Physics Module (`petcr.physics`)

#### `penman_potential_et()`
计算 Penman 潜在蒸散发 / Calculate Penman potential ET

**输入参数 / Input Parameters** (all in SI units):
- `net_radiation`: 净辐射 [W m⁻²]
- `ground_heat_flux`: 土壤热通量 [W m⁻²]
- `temperature`: 气温 [°C]
- `relative_humidity`: 相对湿度 [%]
- `wind_speed`: 风速 [m s⁻¹]
- `pressure`: 气压 [Pa]

#### `priestley_taylor_et()`
计算 Priestley-Taylor 蒸散发 / Calculate Priestley-Taylor ET

**输入参数 / Input Parameters**:
- `net_radiation`: 净辐射 [W m⁻²]
- `ground_heat_flux`: 土壤热通量 [W m⁻²]
- `temperature`: 气温 [°C]
- `pressure`: 气压 [Pa]
- `alpha`: PT 系数 (默认 1.26) / PT coefficient (default 1.26)

#### `vapor_pressure_deficit()`
计算饱和水汽压差 / Calculate vapor pressure deficit

**输入参数 / Input Parameters**:
- `temperature`: 气温 [°C]
- `relative_humidity`: 相对湿度 [%]

### 模型模块 / Models Module (`petcr.models`)

所有模型函数的通用输入 / Common inputs for all model functions:
- `ep`: 潜在蒸散发 [W m⁻² or mm d⁻¹]
- `ew`: 湿环境蒸散发 [W m⁻² or mm d⁻¹]

每个模型还有特定的可选参数，详见各函数的文档字符串。

Each model has specific optional parameters, see function docstrings for details.

## 单位约定 / Unit Conventions

本库统一使用 SI 单位：

This library uses SI units consistently:

- 温度 / Temperature: °C
- 压力 / Pressure: Pa
- 辐射通量 / Radiation flux: W m⁻²
- 蒸散发 / Evapotranspiration: W m⁻² (能量单位) 或 mm d⁻¹ (水深单位)
- 风速 / Wind speed: m s⁻¹
- 相对湿度 / Relative humidity: % (0-100)

## 贡献指南 / Contributing

欢迎贡献！请确保：

Contributions are welcome! Please ensure:

1. 代码遵循 PEP 8 风格 / Code follows PEP 8 style
2. 添加详细的 NumPy 风格文档字符串 / Add detailed NumPy-style docstrings
3. 包含适当的文献引用 / Include appropriate literature references
4. 添加单元测试 / Add unit tests

## 许可证 / License

MIT License

## 参考文献 / References

1. Bouchet, R.J. (1963). Évapotranspiration réelle et potentielle, signification climatique. *IAHS Publication*, 62, 134-142.

2. Brutsaert, W. (2015). A generalized complementary principle with physical constraints for land-surface evaporation. *Water Resources Research*, 51(10), 8087-8093.

3. Brutsaert, W., & Stricker, H. (1979). An advection-aridity approach to estimate actual regional evapotranspiration. *Water Resources Research*, 15(2), 443-450.

4. Han, S., & Tian, F. (2018). A review of the complementary principle of evaporation: From the original linear relationship to generalized nonlinear functions. *Hydrology and Earth System Sciences*, 22(3), 1813-1834.

5. Penman, H.L. (1948). Natural evaporation from open water, bare soil and grass. *Proceedings of the Royal Society of London. Series A*, 193(1032), 120-145.

6. Priestley, C.H.B., & Taylor, R.J. (1972). On the assessment of surface heat flux and evaporation using large-scale parameters. *Monthly Weather Review*, 100(2), 81-92.

7. Szilagyi, J., Crago, R., & Qualls, R. (2017). A calibration-free formulation of the complementary relationship of evaporation for continental-scale hydrology. *Journal of Geophysical Research: Atmospheres*, 122(1), 264-278.

## 常见问题 / FAQ

### Q1: 如何选择合适的CR模型？
### Q1: How to choose the appropriate CR model?

**A**: 选择依据气候条件和研究目标：
**A**: Selection depends on climate conditions and research objectives:

- **湿润气候 / Humid Climate**: Sigmoid (β=0.5-0.7) 或 Polynomial (b=2.0)
  - 理由：非线性特性更好地捕捉湿润条件下的ET动态
  - Reason: Nonlinear characteristics better capture ET dynamics in humid conditions

- **干旱/半干旱 / Arid/Semi-arid**: A-A 或 Rescaled Power (n=0.5)
  - 理由：考虑了干旱条件下的平流效应和非对称性
  - Reason: Accounts for advection effects and asymmetry under arid conditions

- **大陆尺度研究 / Continental Scale**: Rescaled Power (n=0.5)
  - 理由：无需校准，参数普适性强
  - Reason: Calibration-free with universal parameters

- **快速估算 / Quick Estimation**: Bouchet
  - 理由：最简单，计算速度快
  - Reason: Simplest and fastest computation

### Q2: 为什么我的Ea值超过了Ew？
### Q2: Why does my Ea exceed Ew?

**A**: 理论上Ea不应超过Ew。如果出现这种情况，可能原因包括：
**A**: Theoretically Ea should not exceed Ew. If this occurs, possible reasons include:

1. 输入数据质量问题（建议使用`real_data_workflow.py`中的质量控制功能）
   Input data quality issues (recommend using QC in `real_data_workflow.py`)

2. 极端气象条件导致的数值问题
   Numerical issues under extreme meteorological conditions

3. 模型参数设置不当
   Inappropriate model parameters

**解决方法 / Solutions**:
```python
# 方法1: 使用物理约束 / Method 1: Use physical constraints
ea = np.minimum(ea, ew)

# 方法2: 检查输入数据 / Method 2: Check input data
from examples.real_data_workflow import MeteoDataProcessor
processor = MeteoDataProcessor()
processor.load_data(...)
qc_stats = processor.quality_control()  # 会标记异常数据 / Flags anomalous data
```

### Q3: 如何将能量单位(W/m²)转换为水深单位(mm/day)?
### Q3: How to convert energy units (W/m²) to depth units (mm/day)?

**A**: 使用潜热转换公式 / Use latent heat conversion:

```python
# W/m² 转 mm/day / W/m² to mm/day
latent_heat = 2.45e6  # J/kg (20°C时的汽化潜热 / Latent heat at 20°C)
seconds_per_day = 86400

et_mm_day = (et_w_m2 * seconds_per_day) / latent_heat

# 示例 / Example:
# 如果 ET = 300 W/m² / If ET = 300 W/m²
# 则 ET = (300 * 86400) / 2.45e6 ≈ 10.6 mm/day
```

### Q4: 如何处理缺失数据？
### Q4: How to handle missing data?

**A**: 建议方法 / Recommended approaches:

```python
import numpy as np

# 方法1: 线性插值 / Method 1: Linear interpolation
from scipy import interpolate
valid_idx = ~np.isnan(your_data)
interpolator = interpolate.interp1d(
    np.where(valid_idx)[0],
    your_data[valid_idx],
    fill_value='extrapolate'
)
filled_data = interpolator(np.arange(len(your_data)))

# 方法2: 使用质量标志 / Method 2: Use quality flags
from examples.real_data_workflow import MeteoDataProcessor
processor = MeteoDataProcessor()
processor.load_data(...)
# 只使用质量良好的数据 / Use only good quality data
results = processor.calculate_et(use_only_good_data=True)
```

### Q5: 如何引用这个库？
### Q5: How to cite this library?

**A**: 如果在研究中使用了PET-CR库，请引用相关的理论文献：
**A**: If you use PET-CR in your research, please cite the relevant theoretical papers:

对于Sigmoid模型 / For Sigmoid model:
```
Han, S., & Tian, F. (2018). A review of the complementary principle of
evaporation: From the original linear relationship to generalized nonlinear
functions. Hydrology and Earth System Sciences, 22(3), 1813-1834.
```

对于Priestley-Taylor方法 / For Priestley-Taylor method:
```
Priestley, C.H.B., & Taylor, R.J. (1972). On the assessment of surface heat
flux and evaporation using large-scale parameters. Monthly Weather Review,
100(2), 81-92.
```

（根据使用的具体模型选择相应的参考文献）
(Choose appropriate references based on the specific models used)

### Q6: 代码运行出错怎么办？
### Q6: What to do when encountering errors?

**A**: 故障排查步骤 / Troubleshooting steps:

1. **检查Python版本** / Check Python version (需要3.9+ / requires 3.9+)
   ```bash
   python --version
   ```

2. **确认依赖安装** / Confirm dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

3. **运行测试** / Run tests
   ```bash
   python -m pytest tests/
   ```

4. **查看示例** / Check examples
   ```bash
   python -m examples.example_sigmoid
   ```

5. **提交Issue** / Submit an issue
   如果问题持续，请在GitHub提交Issue，包含：
   If the problem persists, submit an Issue on GitHub including:
   - 完整的错误信息 / Full error message
   - Python版本和操作系统 / Python version and OS
   - 最小可复现示例 / Minimal reproducible example

## 联系方式 / Contact

如有问题或建议，请在 GitHub 仓库提交 Issue。

For questions or suggestions, please submit an Issue on the GitHub repository.

---

**开发状态 / Development Status**: Alpha (Production Ready)

**Python 版本要求 / Python Version**: 3.9+

**最后更新 / Last Updated**: 2025-11-04
