# Quick Start Guide 快速开始指南

## Installation 安装

### Step 1: Clone the repository 克隆仓库

```bash
git clone https://github.com/yourusername/et_landatmosphere_feedback.git
cd et_landatmosphere_feedback
```

### Step 2: Create a virtual environment (optional but recommended) 创建虚拟环境(可选但推荐)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies 安装依赖

```bash
pip install -r requirements.txt
```

## Quick Usage 快速使用

### Example 1: Basic PET Calculation 基础PET计算

```python
from src import calculate_pet_land

# Calculate PETe and PETa for land surface
results = calculate_pet_land(
    latent_heat=100.0,      # W/m²
    sensible_heat=50.0,     # W/m²
    specific_humidity=0.01, # kg/kg
    air_pressure=101325.0,  # Pa
    air_temperature=298.15, # K
    skin_temperature=300.15 # K
)

print(f"PETe: {results['pete']:.2f} mm/day")
print(f"PETa: {results['peta']:.2f} mm/day")
```

### Example 2: Run the provided examples 运行提供的示例

```bash
# Basic usage example
python examples/example_basic.py

# Attribution analysis (coming soon)
# python examples/example_attribution.py

# Visualization (coming soon)
# python examples/example_visualization.py
```

### Example 3: Generate sample data 生成示例数据

```python
from src import generate_sample_data, batch_calculate_pet

# Generate 100 random samples
data = generate_sample_data(n_samples=100, surface_type='land', seed=42)

# Calculate PET for all samples
results = batch_calculate_pet(data)

print(f"Mean PETe: {results['pete'].mean():.2f} mm/day")
print(f"Mean PETa: {results['peta'].mean():.2f} mm/day")
```

## Project Structure 项目结构

```
et_landatmosphere_feedback/
├── README.md                   # English documentation
├── README_CN.md               # Chinese documentation
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── .gitignore                # Git ignore file
│
├── src/                      # Source code
│   ├── __init__.py          # Package initialization
│   ├── pet_estimation.py    # PET calculation for land surfaces
│   ├── wet_dry_conditions.py # PET under wet/driest conditions
│   ├── et_attribution.py    # ET projection and attribution
│   └── data_generator.py    # Sample data generation
│
├── examples/                 # Usage examples
│   ├── example_basic.py     # Basic usage
│   ├── (more examples coming soon...)
│
├── data/                     # Data directory
│   ├── input/               # Input data (empty, for user data)
│   └── output/              # Output results
│
└── docs/                     # Additional documentation
    └── QUICKSTART.md        # This file
```

## Next Steps 下一步

1. **Explore the examples** 探索示例
   - Run `python examples/example_basic.py` to see basic usage
   - Check the generated plots in `data/output/`

2. **Load your own data** 加载自己的数据
   - Download Fluxnet2015 data: https://fluxnet.org/data/fluxnet2015-dataset/
   - Download CMIP6 data: https://esgf-node.llnl.gov/search/cmip6/
   - Place data files in `data/input/`
   - Use `load_fluxnet_data()` or `load_cmip6_data()` functions

3. **Perform attribution analysis** 执行归因分析
   - Use `attribution_analysis()` function
   - See documentation in `src/et_attribution.py`

4. **Customize for your research** 为您的研究定制
   - Modify the code to suit your needs
   - Refer to the paper for methodology details

## Troubleshooting 故障排除

### Import errors 导入错误

If you get import errors, make sure:
- You have activated the virtual environment
- All dependencies are installed: `pip install -r requirements.txt`
- You are running Python from the project root directory

### Data loading issues 数据加载问题

If data files are not found:
- The code will automatically generate sample data
- Download real data from the sources mentioned above
- Place files in the correct directory structure

### Questions? 有问题?

- Check the full README: `README.md` or `README_CN.md`
- Refer to the paper for methodology details
- Contact: shazhou21@bnu.edu.cn

## Citation 引用

If you use this code in your research, please cite:

```bibtex
@article{zhou2025neglecting,
  title={Neglecting land–atmosphere feedbacks overestimates climate-driven increases in evapotranspiration},
  author={Zhou, Sha and Yu, Bofu},
  journal={Nature Climate Change},
  year={2025},
  doi={10.1038/s41558-025-02428-5}
}
```

---

**Happy coding! 祝编码愉快!**
