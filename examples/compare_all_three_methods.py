"""
示例: 比较 PET-CR 库的所有三种方法
Example: Comparing All Three Methods in PET-CR Library

这个示例展示了 PET-CR 库中所有三种蒸散发估算方法的对比：
1. 传统CR模型 (Ep/Ew输入)
2. 陆地-大气框架 (通量数据输入)
3. BGCR-Budyko模型 (气象数据+降水+流域特征)

This example demonstrates a comparison of all three ET estimation methods:
1. Traditional CR Models (Ep/Ew input)
2. Land-Atmosphere Framework (flux data input)
3. BGCR-Budyko Model (meteorological + precipitation + catchment characteristics)

作者 / Authors: PET-CR Contributors
版本 / Version: 0.3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

try:
    import petcr
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import petcr

# 设置中文字体 / Setup Chinese font
try:
    petcr.setup_chinese_font()
except:
    pass

def main():
    print("=" * 80)
    print("PET-CR 三种方法综合对比 / Comprehensive Comparison of Three Methods")
    print("=" * 80)
    print()

    # ========================================================================
    # 方法1: 传统CR模型 / Method 1: Traditional CR Models
    # ========================================================================
    print("【方法1: 传统CR模型 / Method 1: Traditional CR Models】")
    print("-" * 80)

    # 设置气象条件 / Set meteorological conditions
    net_radiation = 500.0       # W/m²
    ground_heat_flux = 50.0     # W/m²
    temperature = 20.0          # °C
    relative_humidity = 50.0    # %
    wind_speed = 2.0           # m/s
    pressure = 101325.0        # Pa

    # 计算 Ep 和 Ew / Calculate Ep and Ew
    ep = petcr.penman_potential_et(
        net_radiation, ground_heat_flux, temperature,
        relative_humidity, wind_speed, pressure
    )

    ew = petcr.priestley_taylor_et(
        net_radiation, ground_heat_flux, temperature,
        pressure, alpha=1.26
    )

    print(f"输入 / Inputs:")
    print(f"  Ep (Penman):           {ep:.2f} W/m²")
    print(f"  Ew (Priestley-Taylor): {ew:.2f} W/m²")
    print()

    # 应用不同CR模型 / Apply different CR models
    method1_results = {
        'Sigmoid (β=0.5)': petcr.sigmoid_cr(ep, ew, beta=0.5),
        'Polynomial (b=2.0)': petcr.polynomial_cr(ep, ew, b=2.0),
        'Rescaled Power': petcr.rescaled_power_cr(ep, ew, n=0.5),
        'Bouchet': petcr.bouchet_cr(ep, ew),
        'A-A': petcr.aa_cr(ep, ew),
    }

    print("结果 / Results:")
    for model_name, ea in method1_results.items():
        print(f"  {model_name:<25} Ea = {ea:.2f} W/m² ({ea/ew:.3f} × Ew)")
    print()

    # ========================================================================
    # 方法2: 陆地-大气框架 / Method 2: Land-Atmosphere Framework
    # ========================================================================
    print("【方法2: 陆地-大气框架 / Method 2: Land-Atmosphere Framework】")
    print("-" * 80)

    # 通量数据输入 / Flux data input
    latent_heat_flux = 100.0        # W/m²
    sensible_heat_flux = 50.0       # W/m²
    specific_humidity = 0.01        # kg/kg
    air_pressure = 101325.0         # Pa
    air_temperature = 298.15        # K
    skin_temperature = 300.15       # K

    print(f"输入 / Inputs:")
    print(f"  潜热通量 / Latent heat:     {latent_heat_flux:.1f} W/m²")
    print(f"  感热通量 / Sensible heat:   {sensible_heat_flux:.1f} W/m²")
    print(f"  气温 / Air temperature:     {air_temperature-273.15:.2f} °C")
    print()

    # 计算PETe和PETa / Calculate PETe and PETa
    method2_results = petcr.calculate_pet_land(
        latent_heat=latent_heat_flux,
        sensible_heat=sensible_heat_flux,
        specific_humidity=specific_humidity,
        air_pressure=air_pressure,
        air_temperature=air_temperature,
        skin_temperature=skin_temperature
    )

    print("结果 / Results:")
    print(f"  PETe (能量基础):          {method2_results['pete']:.2f} mm/day")
    print(f"  PETa (空气动力学):        {method2_results['peta']:.2f} mm/day")
    print(f"  湿润波文比 / Wet Bowen:   {method2_results['beta_w']:.3f}")
    print(f"  实际ET / Actual ET:       {method2_results['et']:.2f} mm/day")
    print()

    # ========================================================================
    # 方法3: BGCR-Budyko模型 / Method 3: BGCR-Budyko Model
    # ========================================================================
    print("【方法3: BGCR-Budyko模型 / Method 3: BGCR-Budyko Model】")
    print("-" * 80)

    # 气象数据 + 降水 + 流域特征 / Meteorological + precipitation + catchment
    monthly_net_radiation = 150.0   # W/m²
    monthly_temperature = 20.0      # °C
    monthly_wind_speed = 2.0        # m/s
    actual_vapor_pressure = 1.5     # kPa
    saturation_vapor_pressure = 2.3 # kPa
    monthly_precipitation = 80.0    # mm
    seasonality_index = 0.5         # dimensionless
    albedo = 0.2                    # dimensionless

    print(f"输入 / Inputs:")
    print(f"  净辐射 / Net radiation:    {monthly_net_radiation:.1f} W/m²")
    print(f"  气温 / Temperature:         {monthly_temperature:.1f} °C")
    print(f"  降水 / Precipitation:       {monthly_precipitation:.1f} mm")
    print(f"  季节性指数 / SI:            {seasonality_index:.2f}")
    print(f"  反照率 / Albedo:            {albedo:.2f}")
    print()

    # 计算BGCR-ET / Calculate BGCR-ET
    method3_results = petcr.calculate_bgcr_et(
        net_radiation=monthly_net_radiation,
        temperature=monthly_temperature,
        wind_speed=monthly_wind_speed,
        actual_vapor_pressure=actual_vapor_pressure,
        saturation_vapor_pressure=saturation_vapor_pressure,
        precipitation=monthly_precipitation,
        seasonality_index=seasonality_index,
        albedo=albedo
    )

    print("结果 / Results:")
    print(f"  表观潜在蒸发 / Epa:       {method3_results['epa']:.2f} mm/month")
    print(f"  辐射项 / Erad:            {method3_results['erad']:.2f} mm/month")
    print(f"  空气动力项 / Eaero:       {method3_results['eaero']:.2f} mm/month")
    print(f"  Budyko参数 / w:           {method3_results['w']:.3f}")
    print(f"  互补系数 / β_c:           {method3_results['beta_c']:.3f}")
    print(f"  实际ET / Actual ET:       {method3_results['et']:.2f} mm/month")
    print()

    # ========================================================================
    # 时间序列对比 / Time Series Comparison
    # ========================================================================
    print("=" * 80)
    print("时间序列对比 (12个月) / Time Series Comparison (12 months)")
    print("=" * 80)
    print()

    # 生成12个月的模拟数据 / Generate 12 months of synthetic data
    months = np.arange(1, 13)

    # 方法1的时间序列 / Method 1 time series
    ep_series = 300 + 150 * np.sin(2 * np.pi * (months - 3) / 12)
    ew_series = np.full(12, 350.0)
    ea_sigmoid_series = petcr.sigmoid_cr(ep_series, ew_series, beta=0.5)
    ea_bouchet_series = petcr.bouchet_cr(ep_series, ew_series)

    # 方法2的时间序列 / Method 2 time series (假设通量变化)
    # 转换单位: W/m² to mm/day (简化假设 1 W/m² ≈ 0.035 mm/day)
    conversion_factor = 0.035
    pete_series = np.full(12, method2_results['pete'])
    et_method2_series = np.full(12, method2_results['et'])

    # 方法3的时间序列 / Method 3 time series
    # 模拟月降水季节变化
    precip_series = 50 + 80 * np.sin(2 * np.pi * (months - 2) / 12)
    precip_series = np.maximum(precip_series, 10)  # 最小10mm

    et_method3_series = np.zeros(12)
    for i in range(12):
        results_i = petcr.calculate_bgcr_et(
            net_radiation=monthly_net_radiation * (0.8 + 0.4 * np.sin(2 * np.pi * (i+1 - 3) / 12)),
            temperature=monthly_temperature,
            wind_speed=monthly_wind_speed,
            actual_vapor_pressure=actual_vapor_pressure,
            saturation_vapor_pressure=saturation_vapor_pressure,
            precipitation=precip_series[i],
            seasonality_index=seasonality_index,
            albedo=albedo
        )
        et_method3_series[i] = results_i['et']

    # ========================================================================
    # 可视化对比 / Visualization
    # ========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('PET-CR 三种方法综合对比\nComprehensive Comparison of Three Methods',
                 fontsize=16, fontweight='bold')

    # 子图1: 方法1的不同模型对比
    ax1 = axes[0, 0]
    ax1.plot(months, ea_sigmoid_series, 'o-', label='Sigmoid CR', linewidth=2)
    ax1.plot(months, ea_bouchet_series, 's-', label='Bouchet CR', linewidth=2)
    ax1.plot(months, ew_series, '--', label='Ew (Reference)', linewidth=2, alpha=0.7)
    ax1.set_xlabel('月份 / Month')
    ax1.set_ylabel('ET (W/m²)')
    ax1.set_title('方法1: 传统CR模型\nMethod 1: Traditional CR Models')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 子图2: 方法2的PETe vs ET
    ax2 = axes[0, 1]
    ax2.bar(months - 0.2, pete_series, width=0.4, label='PETe', alpha=0.7)
    ax2.bar(months + 0.2, et_method2_series, width=0.4, label='Actual ET', alpha=0.7)
    ax2.set_xlabel('月份 / Month')
    ax2.set_ylabel('ET (mm/day)')
    ax2.set_title('方法2: 陆地-大气框架\nMethod 2: Land-Atmosphere Framework')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # 子图3: 方法3的降水与ET关系
    ax3 = axes[1, 0]
    ax3.plot(months, precip_series, 'o-', label='降水 / Precipitation',
             linewidth=2, color='blue')
    ax3.plot(months, et_method3_series, 's-', label='BGCR-ET',
             linewidth=2, color='red')
    ax3.set_xlabel('月份 / Month')
    ax3.set_ylabel('水量 / Water (mm/month)')
    ax3.set_title('方法3: BGCR-Budyko模型\nMethod 3: BGCR-Budyko Model')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 子图4: 三种方法的年均ET对比 (归一化)
    ax4 = axes[1, 1]
    # 转换到相同单位进行对比 (归一化到[0,1])
    method1_normalized = np.mean(ea_sigmoid_series) / np.max([np.mean(ea_sigmoid_series),
                                                               np.mean(et_method2_series)*28.5,
                                                               np.mean(et_method3_series)])
    method2_normalized = (np.mean(et_method2_series)*28.5) / np.max([np.mean(ea_sigmoid_series),
                                                                      np.mean(et_method2_series)*28.5,
                                                                      np.mean(et_method3_series)])
    method3_normalized = np.mean(et_method3_series) / np.max([np.mean(ea_sigmoid_series),
                                                               np.mean(et_method2_series)*28.5,
                                                               np.mean(et_method3_series)])

    methods = ['方法1\nTraditional CR', '方法2\nLand-Atmos', '方法3\nBGCR-Budyko']
    values = [method1_normalized, method2_normalized, method3_normalized]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    bars = ax4.bar(methods, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax4.set_ylabel('相对ET / Relative ET (归一化)')
    ax4.set_title('三种方法年均ET对比 (归一化)\nAnnual Mean ET Comparison (Normalized)')
    ax4.set_ylim([0, 1.2])
    ax4.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    plt.tight_layout()
    from pathlib import Path
    figures_dir = Path(__file__).parent / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    output_file = figures_dir / 'compare_all_three_methods.png'
    plt.savefig(str(output_file), dpi=300, bbox_inches='tight')
    print(f"保存图片 / Figure saved: {output_file}")
    print()

    # ========================================================================
    # 方法特点总结 / Method Characteristics Summary
    # ========================================================================
    print("=" * 80)
    print("方法特点总结 / Method Characteristics Summary")
    print("=" * 80)
    print()

    print("┌─────────────────┬───────────────────────┬─────────────────────────┐")
    print("│ 特性 / Feature  │ 优点 / Advantages     │ 局限 / Limitations      │")
    print("├─────────────────┼───────────────────────┼─────────────────────────┤")
    print("│ 方法1:          │ • 经典理论成熟        │ • 需要预计算Ep/Ew       │")
    print("│ Traditional CR  │ • 多种模型可选        │ • 参数需要校准          │")
    print("│                 │ • 计算快速简单        │ • 空间异质性考虑有限    │")
    print("├─────────────────┼───────────────────────┼─────────────────────────┤")
    print("│ 方法2:          │ • 基于能量平衡        │ • 需要通量观测数据      │")
    print("│ Land-Atmosphere │ • 物理意义明确        │ • 适用于站点尺度        │")
    print("│                 │ • 诊断陆气反馈        │ • 区域应用受限          │")
    print("├─────────────────┼───────────────────────┼─────────────────────────┤")
    print("│ 方法3:          │ • 结合长短期框架      │ • 需要流域特征数据      │")
    print("│ BGCR-Budyko     │ • 处理空间异质性      │ • 月尺度计算            │")
    print("│                 │ • 考虑降水季节性      │ • 模型相对复杂          │")
    print("└─────────────────┴───────────────────────┴─────────────────────────┘")
    print()

    # ========================================================================
    # 应用建议 / Application Recommendations
    # ========================================================================
    print("=" * 80)
    print("应用建议 / Application Recommendations")
    print("=" * 80)
    print()

    print("【选择方法1】当你:")
    print("  ✓ 拥有标准气象数据（温度、湿度、风速、辐射）")
    print("  ✓ 需要快速估算区域尺度ET")
    print("  ✓ 研究湿润-干旱转换")
    print()

    print("【选择方法2】当你:")
    print("  ✓ 拥有涡度相关观测数据（LH/SH通量）")
    print("  ✓ 研究陆地-大气相互作用")
    print("  ✓ 进行气候变化归因分析")
    print()

    print("【选择方法3】当你:")
    print("  ✓ 研究异质流域的月尺度ET")
    print("  ✓ 需要考虑降水季节性影响")
    print("  ✓ 分析长期水文变化")
    print()

    print("=" * 80)
    print("分析完成 / Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
