# PET-CR Interactive Tutorials
# PET-CR 交互式教程

Welcome to the PET-CR tutorial series! These Jupyter Notebooks are designed to help beginners understand evapotranspiration estimation and the complementary relationship theory.

欢迎来到 PET-CR 教程系列！这些 Jupyter Notebook 旨在帮助初学者理解蒸散发估算和互补关系理论。

---

## 🎯 Who Should Use These Tutorials? | 谁应该使用这些教程？

These tutorials are perfect for:

这些教程非常适合：

- **大一/大二本科生** | Freshman/Sophomore undergraduates
  - 刚接触水文学和气象学 | New to hydrology and meteorology
  - 想要通过动手实践学习 | Want to learn through hands-on practice

- **研究生新手** | Graduate students (beginners)
  - 需要快速入门 ET 估算 | Need a quick introduction to ET estimation
  - 想要理解物理原理而非公式推导 | Want to understand physics rather than mathematical derivations

- **Python 初学者** | Python beginners
  - 有基础编程经验 | Have basic programming experience
  - 想要学习科学计算工具 | Want to learn scientific computing tools

---

## 📚 Tutorial Series | 教程系列

### Notebook 1: Understanding ET Basics | 理解蒸散发基础
**File**: `01_Understanding_ET_Basics.ipynb`

**What you'll learn | 你将学到**:
- 什么是蒸散发？为什么重要？ | What is evapotranspiration? Why is it important?
- Penman 公式的两个组成部分（能量项和动力项）| Two components of Penman equation (radiation and aerodynamic terms)
- 如何用 Python 计算 ET | How to calculate ET with Python
- 一天中的 ET 变化规律 | Daily variation of ET

**Prerequisites | 先决条件**:
- 基础物理（温度、压强概念）| Basic physics (temperature, pressure concepts)
- 基础 Python（变量、函数、循环）| Basic Python (variables, functions, loops)

**Time required | 所需时间**: 1-2 hours | 1-2 小时

---

### Notebook 2: Complementary Relationship | 互补关系

**File**: `02_Complementary_Relationship.ipynb`

**What you'll learn | 你将学到**:
- 什么是互补关系？为什么"反直觉"？ | What is the complementary relationship? Why is it "counter-intuitive"?
- Bouchet 假设和能量守恒 | Bouchet hypothesis and energy conservation
- 不同 CR 模型的对比（Bouchet, Sigmoid, Polynomial）| Comparison of different CR models
- 干旱的反直觉现象 | Counter-intuitive drought phenomena

**Prerequisites | 先决条件**:
- 完成 Notebook 1 | Complete Notebook 1
- 理解能量平衡概念 | Understand energy balance concept

**Time required | 所需时间**: 1.5-2 hours | 1.5-2 小时

---

### Notebook 3: Attribution Analysis | 归因分析

**File**: `03_Attribution_Analysis.ipynb`

**What you'll learn | 你将学到**:
- 如何分离气候变化和人类活动的影响？ | How to separate climate change and human activity impacts?
- Budyko 框架和干燥度指数 | Budyko framework and aridity index
- 归因分析的三步法 | Three-step attribution method
- 真实案例：黄河流域径流减少 | Real case: Yellow River runoff reduction

**Prerequisites | 先决条件**:
- 完成 Notebook 1 和 2 | Complete Notebooks 1 and 2
- 理解长期水量平衡 | Understand long-term water balance

**Time required | 所需时间**: 2-3 hours | 2-3 小时

---

## 🚀 Getting Started | 快速开始

### Step 1: Install Dependencies | 安装依赖

```bash
# Clone the repository (if not done)
git clone https://github.com/shazhou/PET-CR.git
cd PET-CR

# Install required packages
pip install -r requirements.txt

# Install PET-CR in development mode
pip install -e .
```

### Step 2: Launch Jupyter Notebook | 启动 Jupyter Notebook

```bash
# Navigate to tutorials directory
cd tutorials

# Launch Jupyter Notebook
jupyter notebook
```

Your browser will open automatically with the Jupyter interface.

浏览器将自动打开 Jupyter 界面。

### Step 3: Open a Tutorial | 打开教程

Click on one of the `.ipynb` files to open:
- `01_Understanding_ET_Basics.ipynb` (Start here!)
- `02_Complementary_Relationship.ipynb`
- `03_Attribution_Analysis.ipynb`

点击任意 `.ipynb` 文件打开（建议从 01 开始）。

---

## 💡 How to Use These Notebooks | 如何使用这些 Notebook

### Interactive Learning | 交互式学习

1. **Read the explanations** | 阅读解释
   - Each cell contains bilingual (English/Chinese) explanations
   - 每个单元格包含双语（英文/中文）解释

2. **Run the code cells** | 运行代码单元格
   - Click on a code cell
   - Press `Shift + Enter` to run it
   - 点击代码单元格，按 `Shift + Enter` 运行

3. **Adjust the parameters** | 调整参数
   - Use interactive sliders to change values
   - 使用交互式滑块改变数值
   - See how results change in real-time
   - 实时查看结果变化

4. **Experiment!** | 实验！
   - Modify the code to test your understanding
   - 修改代码以测试你的理解
   - Try different scenarios
   - 尝试不同的场景

---

## 🎨 Interactive Features | 交互式功能

### Sliders | 滑块

Each tutorial includes interactive sliders powered by `ipywidgets`:

每个教程都包含基于 `ipywidgets` 的交互式滑块：

```python
interact(explore_et_basics,
         temperature_c=FloatSlider(min=0, max=40, step=1, value=20),
         wind_speed=FloatSlider(min=0.5, max=10, step=0.5, value=2.0),
         ...)
```

**Try it!** | 试试看！
- Drag the slider to change temperature
- 拖动滑块改变温度
- Watch the ET value update automatically
- 观察 ET 值自动更新

---

## 📊 Visualizations | 可视化

Each tutorial generates publication-quality figures:

每个教程都会生成出版级质量的图表：

- Time series plots | 时间序列图
- Energy budget diagrams | 能量收支图
- Budyko curves | Budyko 曲线
- Spatial maps (in Notebook 3) | 空间地图（在 Notebook 3）

**Tip**: All figures are saved automatically to `figures/` directory.

**提示**：所有图表自动保存到 `figures/` 目录。

---

## ❓ Discussion Questions | 讨论题

At the end of each notebook, you'll find discussion questions:

每个 notebook 结尾都有讨论题：

1. Test your understanding | 测试你的理解
2. Connect concepts to real-world problems | 将概念与实际问题联系起来
3. Encourage critical thinking | 鼓励批判性思维

**Suggestion**: Discuss these with classmates or instructors!

**建议**：与同学或老师讨论这些问题！

---

## 🛠️ Troubleshooting | 故障排除

### Common Issues | 常见问题

#### 1. "ModuleNotFoundError: No module named 'petcr'"

**Solution** | 解决方案:
```bash
cd /path/to/PET-CR
pip install -e .
```

#### 2. "ImportError: No module named 'ipywidgets'"

**Solution** | 解决方案:
```bash
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
```

#### 3. Sliders not showing

**Solution** | 解决方案:
```bash
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

#### 4. Figures not displaying

**Solution** | 解决方案:
- Check if `matplotlib` is installed
- Try adding `%matplotlib inline` at the top of the notebook
- 检查是否安装了 `matplotlib`
- 尝试在 notebook 顶部添加 `%matplotlib inline`

---

## 📖 Additional Resources | 额外资源

### Documentation | 文档

- **Main README**: `../README.md` (Project overview)
- **Theory Guide**: `../docs/THEORY.md` (Detailed theory)
- **API Reference**: `../petcr/` (Source code with docstrings)

### Examples | 示例

After completing the tutorials, explore advanced examples:

完成教程后，探索高级示例：

- `../examples/example_sigmoid.py` - Basic CR models
- `../examples/example_land_atmosphere.py` - Land-atmosphere framework
- `../examples/advanced_analysis.py` - 30-year trend analysis
- `../examples/spatial_bgcr_example.py` - Spatial heterogeneity

---

## 🤝 Contributing | 贡献

Found a typo or want to improve the tutorials?

发现错误或想改进教程？

1. Open an issue on GitHub
2. Submit a pull request
3. Contact the maintainer: shazhou21@bnu.edu.cn

---

## 📝 Learning Path | 学习路径

```
┌─────────────────────────────────────────────────────┐
│  Week 1: Fundamentals                               │
│  ├── Notebook 1: ET Basics                          │
│  └── Read: docs/THEORY.md (Sections 1-2)            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Week 2: Complementary Relationship                 │
│  ├── Notebook 2: CR Theory                          │
│  ├── Run: examples/compare_models.py                │
│  └── Read: docs/THEORY.md (Section 3)               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Week 3: Attribution Analysis                       │
│  ├── Notebook 3: Attribution                        │
│  ├── Run: examples/example_attribution_analysis.py  │
│  └── Read: Zhou & Yu (2025) paper                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Week 4: Real Data Application                      │
│  ├── Run: examples/real_data_workflow.py            │
│  ├── Try: Your own data!                            │
│  └── Explore: Spatial analysis                      │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Learning Objectives | 学习目标

By completing these tutorials, you will be able to:

完成这些教程后，你将能够：

✅ **Understand** the physical basis of evapotranspiration
   - 理解蒸散发的物理基础

✅ **Explain** the complementary relationship between actual and potential ET
   - 解释实际蒸散发和潜在蒸散发的互补关系

✅ **Calculate** ET using standard meteorological data
   - 使用标准气象数据计算 ET

✅ **Apply** attribution analysis to separate climate and land surface effects
   - 应用归因分析分离气候和下垫面影响

✅ **Interpret** Budyko curves and understand water-energy balance
   - 解读 Budyko 曲线并理解水-能量平衡

✅ **Use** Python and Jupyter Notebooks for scientific computing
   - 使用 Python 和 Jupyter Notebook 进行科学计算

---

## 📬 Feedback | 反馈

We'd love to hear your feedback!

我们希望听到您的反馈！

- **Email**: shazhou21@bnu.edu.cn
- **GitHub Issues**: Report bugs or suggest improvements
- **Discussions**: Ask questions in GitHub Discussions

---

**Happy Learning! | 学习愉快！**

---

**Authors**: PET-CR Development Team
**Version**: 1.0
**Last Updated**: 2025-12-04
**License**: MIT
