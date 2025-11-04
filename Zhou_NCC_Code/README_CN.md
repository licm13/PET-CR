# 蒸散发预估中的陆-气反馈研究

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

本代码库为论文《忽略陆-气反馈会高估气候驱动的蒸散发增加》（发表于*Nature Climate Change*）的配套代码。

[English Documentation](README.md)

## 概述

本代码库提供了Python实现的理论框架,用于解耦蒸散发(ET)预估中的陆-气相互作用。代码区分了两种关键的潜在蒸散发(PET)估算器:

- **PETe**(能量基础PET): 由净辐射约束的最大ET
- **PETa**(空气动力学基础PET): 由空气动力学条件决定的最大ET

## 主要发现

- 以往对气候驱动的ET增加的估计被**高估了25-39%**
- 陆地表面变化的负贡献被**夸大了77-121%**
- PETe对陆-气反馈基本不敏感,使其适合用于隔离气候变化影响

## 安装说明

### 环境要求

```bash
pip install -r requirements.txt
```

必需的Python包:
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- netCDF4 >= 1.5.7 (可选,用于读取CMIP6数据)

### 快速开始

```python
from src.pet_estimation import calculate_pet_land
from src.data_generator import generate_sample_data

# 生成示例数据
data = generate_sample_data(n_samples=100)

# 计算PETe和PETa
results = calculate_pet_land(
    latent_heat=data['hfls'],
    sensible_heat=data['hfss'],
    specific_humidity=data['huss'],
    air_pressure=data['ps'],
    air_temperature=data['tas'],
    skin_temperature=data['ts']
)

print(f"PETe: {results['pete']} mm/day")
print(f"PETa: {results['peta']} mm/day")
```

## 项目结构

```
et_landatmosphere_feedback/
├── README.md                   # 英文文档
├── README_CN.md               # 中文文档
├── requirements.txt           # Python依赖
├── LICENSE                    # MIT许可证
├── src/
│   ├── __init__.py
│   ├── pet_estimation.py     # PET计算函数
│   ├── wet_dry_conditions.py # 湿润/最干条件下的PET
│   ├── et_attribution.py     # ET预估和归因
│   ├── budyko_framework.py   # Budyko框架实现
│   └── data_generator.py     # 示例数据生成
├── data/
│   ├── input/                # 输入数据目录(空)
│   └── output/               # 输出结果目录
├── examples/
│   ├── example_basic.py      # 基础使用示例
│   ├── example_attribution.py # 归因分析示例
│   └── example_visualization.py # 可视化示例
├── tests/
│   ├── test_pet_estimation.py
│   ├── test_attribution.py
│   └── test_budyko.py
└── docs/
    ├── methodology.md        # 详细方法论
    └── data_format.md        # 输入数据格式说明
```

## 使用方法

### 1. 基础PET计算(陆地表面)

```python
from src.pet_estimation import calculate_pet_land

# 输入数据(可以来自Fluxnet2015或CMIP6模型)
results = calculate_pet_land(
    latent_heat=100.0,      # W/m²
    sensible_heat=50.0,     # W/m²
    specific_humidity=0.01, # kg/kg
    air_pressure=101325.0,  # Pa
    air_temperature=298.15, # K
    skin_temperature=300.15 # K
)
```

### 2. 湿润和最干条件下的PET(海洋表面)

```python
from src.wet_dry_conditions import calculate_pet_ocean

results = calculate_pet_ocean(
    latent_heat=150.0,
    sensible_heat=30.0,
    specific_humidity=0.015,
    air_pressure=101325.0,
    air_temperature=298.15,
    skin_temperature=299.15
)

print(f"PETe(湿润): {results['pete_wet']} mm/day")
print(f"PETa(湿润): {results['peta_wet']} mm/day")
print(f"PETe(最干): {results['pete_driest']} mm/day")
print(f"PETa(最干): {results['peta_driest']} mm/day")
```

### 3. ET归因分析

```python
from src.et_attribution import attribution_analysis

# 历史和未来气候数据
results = attribution_analysis(
    et_timeseries=et_data,
    pete_timeseries=pete_data,
    pr_timeseries=pr_data,
    window_size=30  # 30年滑动平均
)

print(f"气候变化贡献: {results['et_climate']} mm/day")
print(f"陆地表面变化贡献: {results['et_landsurf']} mm/day")
```

## 数据格式

### 输入数据要求

代码需要以下单位的气象变量:

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 潜热通量 | `hfls` | W/m² | 地表向上潜热通量 |
| 感热通量 | `hfss` | W/m² | 地表向上感热通量 |
| 比湿 | `huss` | kg/kg | 近地表比湿 |
| 气压 | `ps` | Pa | 地表气压 |
| 气温 | `tas` | K | 近地表气温 |
| 表皮温度 | `ts` | K | 地表表皮温度 |
| 降水 | `pr` | mm/day | 降水量(用于归因) |

### 数据来源

#### 1. Fluxnet2015数据集
- **来源**: https://fluxnet.org/data/fluxnet2015-dataset/
- **覆盖范围**: 146个站点, 990站年(1997-2014)
- **变量**: 能量通量, 气象条件

#### 2. CMIP6模型模拟
- **来源**: https://esgf-node.llnl.gov/search/cmip6/
- **试验**: 
  - Historical历史(1980-2014)
  - SSP5-8.5(2015-2100)
  - 1pctCO2和1pctCO2-rad(理想化试验)
- **模型**: 32个CMIP6模型(见论文补充表2)

### 加载真实数据

```python
# 示例: 加载Fluxnet数据
from src.data_loader import load_fluxnet_data

data = load_fluxnet_data('data/input/fluxnet_site.csv')

# 示例: 加载CMIP6数据
from src.data_loader import load_cmip6_data

cmip6_data = load_cmip6_data(
    model='ACCESS-CM2',
    experiment='historical',
    variable='hfls',
    path='data/input/cmip6/'
)
```

## 方法论

### 理论框架

ET与两种PET估算器的关系为:

```
ET = (1 + βw) × PETe - βw × PETa
```

其中:
- `βw`是湿润波文比(饱和条件下感热与潜热的比值)
- `PETe`代表大气能量对ET的控制
- `PETa`代表空气动力学条件

### 关键方程

**1. 能量基础PET (PETe):**
```
PETe = Rn / (1 + βw)
```

**2. 空气动力学基础PET (PETa):**
```
PETa = H / βw
```

**3. 湿润波文比(βw):**
```
βw = γ × (Ts - Ta) / (e*s - ea)
```

其中:
- `Rn` = 净辐射 (W/m²)
- `H` = 感热通量 (W/m²)
- `γ` = 干湿表常数 (kPa/°C)
- `Ts` = 地表温度 (K)
- `Ta` = 气温 (K)
- `e*s` = 地表温度下的饱和水汽压 (kPa)
- `ea` = 实际水汽压 (kPa)

### Budyko框架

Budyko框架将ET比率与干燥度指数联系起来:

```
ET/P = [(PETe/P)^(-n) + 1]^(-1/n)
```

其中:
- `P` = 降水量 (mm/day)
- `n` = 考虑陆地表面特征的参数

## 示例

查看`examples/`目录获取详细的使用示例:

1. **example_basic.py**: 基础PET计算
2. **example_attribution.py**: ET归因分析
3. **example_visualization.py**: 结果可视化

运行示例:
```bash
python examples/example_basic.py
python examples/example_attribution.py
python examples/example_visualization.py
```

## 测试

运行测试套件:

```bash
pytest tests/
```

运行测试并生成覆盖率报告:

```bash
pytest --cov=src tests/
```

## 引用

如果您在研究中使用了本代码,请引用:

```bibtex
@article{zhou2025neglecting,
  title={Neglecting land–atmosphere feedbacks overestimates climate-driven increases in evapotranspiration},
  author={Zhou, Sha and Yu, Bofu},
  journal={Nature Climate Change},
  year={2025},
  doi={10.1038/s41558-025-02428-5}
}
```

## 贡献

欢迎贡献! 请随时提交Pull Request。

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 联系方式

- **通讯作者**: 周沙 (shazhou21@bnu.edu.cn)
- **单位**: 北京师范大学

## 致谢

- Fluxnet2015数据集贡献者
- CMIP6模式组
- 国家自然科学基金(资助号42471108和42521001)
- 国家重点研发计划(资助号2022YFF0801303)

## 参考文献

1. Zhou, S., & Yu, B. (2024). Physical basis of the potential evapotranspiration and its estimation over land. *Journal of Hydrology*, 641, 131825.

2. Zhou, S., Yu, B., Huang, Y., & Wang, G. (2015). The complementary relationship and generation of the Budyko functions. *Geophysical Research Letters*, 42(6), 1781-1790.

3. Budyko, M. I. (1974). *Climate and Life*. Academic Press.

---

**注意**: 本代码库提供计算框架。真实观测数据(Fluxnet2015)和模式模拟(CMIP6)需要从各自来源单独下载,因为文件大小和许可证限制。
