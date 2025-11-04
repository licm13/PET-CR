# PET-CR 项目文件结构 / Project File Structure

本文档描述了 PET-CR 库的推荐文件结构及各文件的功能。

This document describes the recommended file structure for the PET-CR library and the purpose of each file.

## 文件结构 / File Structure

```
PET-CR/
│
├── petcr/                      # 主包目录 / Main package directory
│   ├── __init__.py            # 包初始化，导出公共API / Package init, exports public API
│   ├── models.py              # CR模型实现 / CR model implementations
│   └── physics.py             # 物理计算模块 / Physics calculation module
│
├── examples/                   # 示例脚本 / Example scripts
│   ├── example_sigmoid.py     # Sigmoid模型示例 / Sigmoid model example
│   └── compare_models.py      # 模型比较示例 / Model comparison example
│
├── tests/                      # 测试目录 / Test directory
│   └── test_basic.py          # 基础功能测试 / Basic functionality tests
│
├── docs/                       # 文档目录 / Documentation directory
│   └── FILE_STRUCTURE.md      # 本文件 / This file
│
├── .gitignore                 # Git忽略文件 / Git ignore file
├── README.md                  # 项目说明 / Project README
├── requirements.txt           # 依赖包列表 / Dependencies list
└── setup.py                   # 安装配置 / Setup configuration
```

## 文件说明 / File Descriptions

### 核心包文件 / Core Package Files

#### `petcr/__init__.py`
- **功能 / Purpose**: 包初始化文件，定义公共API
- **内容 / Content**: 
  - 导入所有公共函数和类
  - 定义 `__version__` 和 `__all__`
  - 提供包级文档字符串

#### `petcr/models.py`
- **功能 / Purpose**: 实现所有CR模型
- **包含函数 / Functions**:
  - `sigmoid_cr()` - Sigmoid模型 (Han & Tian, 2018)
  - `polynomial_cr()` - 多项式模型 (Brutsaert, 2015)
  - `rescaled_power_cr()` - 重标定幂函数模型 (Szilagyi et al., 2017)
  - `bouchet_cr()` - Bouchet对称模型 (1963)
  - `aa_cr()` - A-A非对称模型

#### `petcr/physics.py`
- **功能 / Purpose**: 提供物理计算函数
- **包含函数 / Functions**:
  - `penman_potential_et()` - Penman潜在蒸散发
  - `priestley_taylor_et()` - Priestley-Taylor蒸散发
  - `vapor_pressure_deficit()` - 饱和水汽压差
  - `calculate_saturation_vapor_pressure()` - 饱和水汽压
  - `calculate_slope_svp()` - 饱和水汽压曲线斜率
  - `calculate_psychrometric_constant()` - 干湿表常数

### 示例文件 / Example Files

#### `examples/example_sigmoid.py`
- **功能 / Purpose**: 演示Sigmoid CR模型的使用
- **内容 / Content**:
  - 单点计算示例
  - 时间序列分析
  - 参数敏感性测试
  - 双语注释和输出

#### `examples/compare_models.py`
- **功能 / Purpose**: 比较所有CR模型
- **内容 / Content**:
  - 多模型并行计算
  - 统计分析和比较
  - 使用建议
  - 模型特性说明

### 测试文件 / Test Files

#### `tests/test_basic.py`
- **功能 / Purpose**: 基础功能测试
- **测试内容 / Test Coverage**:
  - 物理函数计算正确性
  - CR模型函数正确性
  - 数组输入处理
  - 边界条件和特殊情况
  - 物理约束验证

### 配置文件 / Configuration Files

#### `.gitignore`
- **功能 / Purpose**: 指定Git应忽略的文件
- **内容 / Content**:
  - Python缓存文件 (`__pycache__/`, `*.pyc`)
  - 虚拟环境 (`venv/`, `env/`)
  - IDE配置文件
  - 构建产物 (`dist/`, `build/`)

#### `requirements.txt`
- **功能 / Purpose**: 列出项目依赖
- **内容 / Content**:
  - `numpy>=1.20.0` (核心依赖)

#### `setup.py`
- **功能 / Purpose**: Python包安装配置
- **内容 / Content**:
  - 包元数据
  - 依赖定义
  - 入口点配置
  - 分类器信息

#### `README.md`
- **功能 / Purpose**: 项目主文档
- **内容 / Content**:
  - 项目概述
  - 安装说明
  - 快速开始
  - API文档
  - 使用示例
  - 参考文献

## 代码规范 / Coding Standards

### 文档字符串 / Docstrings
- 使用NumPy风格文档字符串
- 包含详细的参数说明
- 提供使用示例
- 标注关键文献引用

### 单位约定 / Unit Conventions
- 统一使用SI单位
- 在文档中明确标注单位
- 温度: °C
- 压力: Pa
- 辐射: W m⁻²
- 风速: m s⁻¹

### 命名约定 / Naming Conventions
- 函数: `snake_case`
- 类: `PascalCase`
- 常量: `UPPER_CASE`
- 模块: `lowercase`

## 核心模型说明 / Core Model Details

### Sigmoid CR 模型 (Han & Tian, 2018)

**完整实现框架 / Complete Implementation Framework**:

```python
def sigmoid_cr(ep, ew, alpha=1.26, beta=0.5):
    """
    Sigmoid Complementary Relationship model.
    
    Parameters
    ----------
    ep : float or array_like
        Potential evapotranspiration (Penman) [W m⁻² or mm d⁻¹]
    ew : float or array_like
        Wet-environment evapotranspiration (Priestley-Taylor) [W m⁻² or mm d⁻¹]
    alpha : float, optional
        Shape parameter (default: 1.26)
    beta : float, optional
        Shape parameter controlling steepness (default: 0.5)
    
    Returns
    -------
    float or array_like
        Actual evapotranspiration (Ea) [same units as inputs]
    
    Notes
    -----
    Model equation: Ea = Ew / [1 + |Ep/Ew - 1|^β]^(1/β)
    
    Reference: Han, S., & Tian, F. (2018). Hydrol. Earth Syst. Sci., 22(3), 1813-1834.
    """
    # Implementation ensures:
    # - Ea = Ew when Ep = Ew (equilibrium)
    # - Ea < Ew when Ep > Ew (dry conditions)
    # - Smooth sigmoid transition
```

关键特性 / Key Features:
- 广义非线性模型，适用多种气候
- β参数可调节，控制曲线陡峭程度
- 确保在Ep=Ew时，Ea=Ew（物理约束）
- 提供湿润到干燥的平滑过渡

## 开发工作流 / Development Workflow

1. **开发模式安装 / Development Installation**
   ```bash
   pip install -e .
   ```

2. **运行测试 / Run Tests**
   ```bash
   python tests/test_basic.py
   ```

3. **运行示例 / Run Examples**
   ```bash
   python examples/example_sigmoid.py
   python examples/compare_models.py
   ```

## 维护建议 / Maintenance Recommendations

1. **定期更新依赖 / Update Dependencies Regularly**
   - 检查numpy版本兼容性
   - 测试新版本Python

2. **文档同步 / Keep Documentation in Sync**
   - 代码变更后及时更新文档
   - 确保示例代码可运行

3. **测试覆盖 / Test Coverage**
   - 为新功能添加测试
   - 保持测试通过率

---

**最后更新 / Last Updated**: 2025-11
**维护者 / Maintainer**: PET-CR Contributors
