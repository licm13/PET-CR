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
├── petcr/                  # 主包目录 / Main package directory
│   ├── __init__.py        # 包初始化 / Package initialization
│   ├── models.py          # CR 模型实现 / CR model implementations
│   └── physics.py         # 物理计算模块 / Physics calculations
├── tests/                  # 测试目录 (待添加) / Tests directory (to be added)
├── examples/              # 示例脚本 (待添加) / Example scripts (to be added)
├── requirements.txt       # 依赖包 / Dependencies
├── setup.py              # 安装配置 / Setup configuration
└── README.md             # 本文件 / This file
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

## 联系方式 / Contact

如有问题或建议，请在 GitHub 仓库提交 Issue。

For questions or suggestions, please submit an Issue on the GitHub repository.

---

**开发状态 / Development Status**: Alpha

**Python 版本要求 / Python Version**: 3.9+
