"""
高级综合分析示例 / Advanced Comprehensive Analysis Example

这个示例展示了PET-CR库的高级应用，包括：
1. 多气候条件下的模型性能分析
2. 参数敏感性分析
3. 季节变化特征分析
4. 模型不确定性评估
5. 统计指标计算

This example demonstrates advanced applications of the PET-CR library:
1. Model performance analysis across different climate conditions
2. Parameter sensitivity analysis
3. Seasonal variation characteristics
4. Model uncertainty assessment
5. Statistical metrics calculation

注意：如果需要绘图功能，请安装 matplotlib: pip install matplotlib
Note: For plotting functionality, install matplotlib: pip install matplotlib
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from pathlib import Path

try:
    from petcr import (
        sigmoid_cr, polynomial_cr, rescaled_power_cr, bouchet_cr, aa_cr,
        penman_potential_et, priestley_taylor_et,
        vapor_pressure_deficit, calculate_saturation_vapor_pressure
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from petcr import (
        sigmoid_cr, polynomial_cr, rescaled_power_cr, bouchet_cr, aa_cr,
        penman_potential_et, priestley_taylor_et,
        vapor_pressure_deficit, calculate_saturation_vapor_pressure
    )

# 尝试导入matplotlib用于可视化 / Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    from petcr import setup_chinese_font
    # 设置中文字体和负号显示 / Set Chinese font and minus sign
    setup_chinese_font()
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None  # type: ignore
    print("警告: matplotlib未安装，将跳过绘图功能")
    print("Warning: matplotlib not installed, plotting will be skipped")
    print("安装命令 / Install with: pip install matplotlib\n")


def generate_climate_scenarios(days: int = 10950, include_extreme_event: bool = True) -> Dict[str, Dict[str, np.ndarray]]:
    """
    生成不同气候条件的模拟数据（支持30年时序和极端事件）
    Generate synthetic data for different climate conditions (supports 30-year time series and extreme events)

    Parameters
    ----------
    days : int
        模拟天数 / Number of days to simulate (default: 10950 = 30 years)
    include_extreme_event : bool
        是否包含热浪干旱事件 / Whether to include heatwave-drought event (default: True)

    Returns
    -------
    dict
        包含不同气候场景数据的字典 / Dictionary containing different climate scenarios
    """
    print("=" * 80)
    print("生成气候场景数据 / Generating Climate Scenario Data")
    print("=" * 80)
    print()

    # 时间序列 (天) / Time series (days)
    t = np.arange(days)
    years = days / 365.25

    scenarios = {}

    # 添加长期变暖趋势 / Add long-term warming trend
    warming_trend = 0.04 * t / 365.25  # ~0.04°C/year, ~1.2°C over 30 years

    # 定义极端事件时间窗口（第15年夏季，持续15天）
    # Define extreme event time window (year 15 summer, 15-day duration)
    extreme_start = int(15 * 365.25)  # Year 15
    extreme_duration = 15  # days
    extreme_end = extreme_start + extreme_duration

    # 1. 湿润气候 (季风气候) / Humid climate (Monsoon)
    # 特征：高降水，Ep < Ew 较多
    temp_humid = 25 + 5 * np.sin(2 * np.pi * t / 365.25) + warming_trend  # 20-30°C + trend
    rh_humid = 70 + 15 * np.sin(2 * np.pi * t / 365.25)  # 55-85%
    radiation_humid = 400 + 150 * np.sin(2 * np.pi * t / 365.25)  # W/m²
    wind_humid = 1.5 + 0.5 * np.random.randn(days) * 0.3  # 较低风速
    wind_humid = np.maximum(wind_humid, 0.5)

    # 添加热浪干旱事件 / Add heatwave-drought event
    if include_extreme_event:
        temp_humid[extreme_start:extreme_end] += 5.0  # +5°C heatwave
        rh_humid[extreme_start:extreme_end] -= 20.0  # -20% humidity drop

    scenarios['湿润气候 / Humid'] = {
        'temperature': temp_humid,
        'relative_humidity': np.clip(rh_humid, 40, 95),
        'net_radiation': np.maximum(radiation_humid, 100),
        'wind_speed': wind_humid,
        'description': '季风气候，高降水，蒸发受限 / Monsoon climate, high precipitation'
    }

    # 2. 半干旱气候 / Semi-arid climate
    # 特征：中等降水，Ep ≈ Ew
    temp_semiarid = 22 + 10 * np.sin(2 * np.pi * t / 365.25) + warming_trend  # 12-32°C + trend
    rh_semiarid = 45 + 15 * np.sin(2 * np.pi * t / 365.25 + np.pi)  # 30-60%
    radiation_semiarid = 500 + 200 * np.sin(2 * np.pi * t / 365.25)
    wind_semiarid = 2.5 + 0.5 * np.random.randn(days) * 0.4
    wind_semiarid = np.maximum(wind_semiarid, 1.0)

    if include_extreme_event:
        temp_semiarid[extreme_start:extreme_end] += 5.0
        rh_semiarid[extreme_start:extreme_end] -= 20.0

    scenarios['半干旱 / Semi-arid'] = {
        'temperature': temp_semiarid,
        'relative_humidity': np.clip(rh_semiarid, 20, 70),
        'net_radiation': np.maximum(radiation_semiarid, 150),
        'wind_speed': wind_semiarid,
        'description': '草原气候，蒸发适中 / Grassland climate, moderate evaporation'
    }

    # 3. 干旱气候 (沙漠) / Arid climate (Desert)
    # 特征：极少降水，Ep >> Ew
    temp_arid = 28 + 12 * np.sin(2 * np.pi * t / 365.25) + warming_trend  # 16-40°C + trend
    rh_arid = 30 + 10 * np.sin(2 * np.pi * t / 365.25 + np.pi)  # 20-40%
    radiation_arid = 600 + 250 * np.sin(2 * np.pi * t / 365.25)
    wind_arid = 3.5 + 0.8 * np.random.randn(days) * 0.5  # 高风速
    wind_arid = np.maximum(wind_arid, 1.5)

    if include_extreme_event:
        temp_arid[extreme_start:extreme_end] += 5.0
        rh_arid[extreme_start:extreme_end] -= 20.0

    scenarios['干旱 / Arid'] = {
        'temperature': temp_arid,
        'relative_humidity': np.clip(rh_arid, 10, 50),
        'net_radiation': np.maximum(radiation_arid, 200),
        'wind_speed': wind_arid,
        'description': '沙漠气候，蒸发极强 / Desert climate, very high evaporation'
    }

    # 4. 温带海洋性气候 / Temperate oceanic climate
    # 特征：温和湿润，变化平缓
    temp_oceanic = 15 + 8 * np.sin(2 * np.pi * t / 365.25) + warming_trend  # 7-23°C + trend
    rh_oceanic = 75 + 10 * np.sin(2 * np.pi * t / 365.25)  # 65-85%
    radiation_oceanic = 350 + 120 * np.sin(2 * np.pi * t / 365.25)
    wind_oceanic = 3.0 + 0.6 * np.random.randn(days) * 0.4
    wind_oceanic = np.maximum(wind_oceanic, 1.5)

    if include_extreme_event:
        temp_oceanic[extreme_start:extreme_end] += 5.0
        rh_oceanic[extreme_start:extreme_end] -= 20.0

    scenarios['温带海洋 / Oceanic'] = {
        'temperature': temp_oceanic,
        'relative_humidity': np.clip(rh_oceanic, 60, 90),
        'net_radiation': np.maximum(radiation_oceanic, 80),
        'wind_speed': wind_oceanic,
        'description': '海洋性气候，温和湿润 / Oceanic climate, mild and humid'
    }

    print(f"已生成 {len(scenarios)} 个气候场景，每个场景 {days} 天数据 ({years:.1f} 年)")
    print(f"Generated {len(scenarios)} climate scenarios, {days} days each ({years:.1f} years)")
    if include_extreme_event:
        print(f"包含极端事件: 第{extreme_start/365.25:.1f}年，持续{extreme_duration}天 (+5°C, -20% RH)")
        print(f"Extreme event included: Year {extreme_start/365.25:.1f}, {extreme_duration} days duration (+5°C, -20% RH)")
    print()

    # 添加极端事件元数据 / Add extreme event metadata
    metadata = {
        'days': days,
        'years': years,
        'extreme_event': include_extreme_event,
        'extreme_start': extreme_start if include_extreme_event else None,
        'extreme_end': extreme_end if include_extreme_event else None,
        'extreme_duration': extreme_duration if include_extreme_event else None
    }

    return scenarios, metadata


def calculate_et_for_scenario(scenario_data: Dict[str, np.ndarray],
                               pressure: float = 101325.0,
                               ground_heat_flux: float = 50.0) -> Dict[str, np.ndarray]:
    """
    计算给定气候场景的所有蒸散发指标
    Calculate all ET metrics for a given climate scenario

    Parameters
    ----------
    scenario_data : dict
        气候场景数据 / Climate scenario data
    pressure : float
        大气压强 [Pa] / Atmospheric pressure [Pa]
    ground_heat_flux : float
        土壤热通量 [W/m²] / Ground heat flux [W/m²]

    Returns
    -------
    dict
        包含Ep, Ew和所有模型Ea的字典 / Dictionary with Ep, Ew and all model Ea values
    """
    # 计算Ep (Penman潜在蒸散发) / Calculate Ep (Penman potential ET)
    ep = penman_potential_et(
        net_radiation=scenario_data['net_radiation'],
        ground_heat_flux=ground_heat_flux,
        temperature=scenario_data['temperature'],
        relative_humidity=scenario_data['relative_humidity'],
        wind_speed=scenario_data['wind_speed'],
        pressure=pressure
    )

    # 计算Ew (Priestley-Taylor湿环境蒸散发) / Calculate Ew (Priestley-Taylor wet ET)
    ew = priestley_taylor_et(
        net_radiation=scenario_data['net_radiation'],
        ground_heat_flux=ground_heat_flux,
        temperature=scenario_data['temperature'],
        pressure=pressure,
        alpha=1.26
    )

    # 使用各种CR模型计算Ea / Calculate Ea using various CR models
    results = {
        'Ep': ep,
        'Ew': ew,
        'Sigmoid_β0.5': sigmoid_cr(ep, ew, beta=0.5),
        'Sigmoid_β0.7': sigmoid_cr(ep, ew, beta=0.7),
        'Polynomial_b2': polynomial_cr(ep, ew, b=2.0),
        'Polynomial_b1.5': polynomial_cr(ep, ew, b=1.5),
        'Rescaled_Power': rescaled_power_cr(ep, ew, n=0.5),
        'Bouchet': bouchet_cr(ep, ew),
        'AA': aa_cr(ep, ew),
    }

    return results


def parameter_sensitivity_analysis(ep: np.ndarray, ew: np.ndarray) -> Dict:
    """
    参数敏感性分析
    Parameter sensitivity analysis

    Parameters
    ----------
    ep : array_like
        潜在蒸散发 / Potential ET
    ew : array_like
        湿环境蒸散发 / Wet-environment ET

    Returns
    -------
    dict
        敏感性分析结果 / Sensitivity analysis results
    """
    print("=" * 80)
    print("参数敏感性分析 / Parameter Sensitivity Analysis")
    print("=" * 80)
    print()

    results = {}

    # 1. Sigmoid模型的beta参数敏感性 / Sigmoid model beta sensitivity
    beta_values = np.linspace(0.3, 2.0, 10)
    sigmoid_results = []

    for beta in beta_values:
        ea = sigmoid_cr(ep, ew, beta=beta)
        mean_ea = np.mean(ea)
        sigmoid_results.append(mean_ea)

    results['sigmoid_beta'] = {
        'parameter_values': beta_values,
        'mean_ea': np.array(sigmoid_results)
    }

    print("Sigmoid模型 beta参数敏感性 / Sigmoid model beta sensitivity:")
    print(f"  beta范围 / beta range: {beta_values[0]:.2f} - {beta_values[-1]:.2f}")
    print(f"  平均Ea变化 / Mean Ea range: {min(sigmoid_results):.2f} - {max(sigmoid_results):.2f} W/m²")
    print(f"  相对变化 / Relative change: {(max(sigmoid_results)/min(sigmoid_results)-1)*100:.1f}%")
    print()

    # 2. Polynomial模型的b参数敏感性 / Polynomial model b sensitivity
    b_values = np.linspace(1.0, 3.0, 10)
    polynomial_results = []

    for b in b_values:
        ea = polynomial_cr(ep, ew, b=b)
        mean_ea = np.mean(ea)
        polynomial_results.append(mean_ea)

    results['polynomial_b'] = {
        'parameter_values': b_values,
        'mean_ea': np.array(polynomial_results)
    }

    print("Polynomial模型 b参数敏感性 / Polynomial model b sensitivity:")
    print(f"  b范围 / b range: {b_values[0]:.2f} - {b_values[-1]:.2f}")
    print(f"  平均Ea变化 / Mean Ea range: {min(polynomial_results):.2f} - {max(polynomial_results):.2f} W/m²")
    print(f"  相对变化 / Relative change: {(max(polynomial_results)/min(polynomial_results)-1)*100:.1f}%")
    print()

    # 3. Rescaled Power模型的n参数敏感性 / Rescaled Power model n sensitivity
    n_values = np.linspace(0.3, 1.0, 10)
    rescaled_results = []

    for n in n_values:
        ea = rescaled_power_cr(ep, ew, n=n)
        mean_ea = np.mean(ea)
        rescaled_results.append(mean_ea)

    results['rescaled_n'] = {
        'parameter_values': n_values,
        'mean_ea': np.array(rescaled_results)
    }

    print("Rescaled Power模型 n参数敏感性 / Rescaled Power model n sensitivity:")
    print(f"  n范围 / n range: {n_values[0]:.2f} - {n_values[-1]:.2f}")
    print(f"  平均Ea变化 / Mean Ea range: {min(rescaled_results):.2f} - {max(rescaled_results):.2f} W/m²")
    print(f"  相对变化 / Relative change: {(max(rescaled_results)/min(rescaled_results)-1)*100:.1f}%")
    print()

    return results


def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    计算统计指标
    Calculate statistical metrics
    """
    return {
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'median': np.median(data),
        'q25': np.percentile(data, 25),
        'q75': np.percentile(data, 75),
    }


def seasonal_analysis(et_results: Dict[str, np.ndarray], days: int = 365) -> Dict:
    """
    季节变化分析
    Seasonal variation analysis

    Parameters
    ----------
    et_results : dict
        蒸散发计算结果 / ET calculation results
    days : int
        总天数 / Total number of days

    Returns
    -------
    dict
        季节分析结果 / Seasonal analysis results
    """
    print("=" * 80)
    print("季节变化分析 / Seasonal Variation Analysis")
    print("=" * 80)
    print()

    # 定义季节 / Define seasons
    seasons = {
        '春季 / Spring': range(0, 91),      # Days 1-91
        '夏季 / Summer': range(91, 182),    # Days 92-182
        '秋季 / Autumn': range(182, 273),   # Days 183-273
        '冬季 / Winter': range(273, 365),   # Days 274-365
    }

    seasonal_stats = {}

    for season_name, day_range in seasons.items():
        seasonal_stats[season_name] = {}
        print(f"\n{season_name}:")
        print("-" * 80)

        # 只分析主要模型 / Only analyze main models
        models_to_analyze = ['Ep', 'Ew', 'Sigmoid_β0.5', 'Polynomial_b2',
                            'Rescaled_Power', 'Bouchet']

        for model_name in models_to_analyze:
            if model_name in et_results:
                seasonal_data = et_results[model_name][list(day_range)]
                stats = calculate_statistics(seasonal_data)
                seasonal_stats[season_name][model_name] = stats

                print(f"  {model_name:20s}: "
                      f"均值={stats['mean']:6.2f} W/m², "
                      f"标准差={stats['std']:5.2f}, "
                      f"范围=[{stats['min']:6.2f}, {stats['max']:6.2f}]")

    print()
    return seasonal_stats


def plot_results(scenarios: Dict, all_results: Dict, sensitivity_results: Dict, metadata: Dict):
    """
    绘制分析结果（增强版，支持长时序和极端事件）
    Plot analysis results (enhanced version with long time series and extreme events)
    """
    if not PLOTTING_AVAILABLE:
        print("跳过绘图 (matplotlib未安装) / Skipping plots (matplotlib not installed)")
        return

    print("=" * 80)
    print("生成可视化图表 / Generating Visualization Plots")
    print("=" * 80)
    print()

    # 创建图形（扩展为3x3布局以容纳更多图表）/ Create figure (expanded to 3x3 layout for more plots)
    fig = plt.figure(figsize=(18, 16))

    # 1. 不同气候条件下的时间序列对比 / Time series comparison
    ax1 = plt.subplot(3, 2, 1)
    scenario_names = list(scenarios.keys())
    for i, scenario_name in enumerate(scenario_names):
        results = all_results[scenario_name]
        days = len(results['Ep'])
        # 只绘制前90天以提高可读性 / Only plot first 90 days for readability
        ax1.plot(range(90), results['Sigmoid_β0.5'][:90],
                label=scenario_name, linewidth=1.5)

    ax1.set_xlabel('天数 / Days', fontsize=10)
    ax1.set_ylabel('Ea (W/m²)', fontsize=10)
    ax1.set_title('不同气候条件下的实际蒸散发 (Sigmoid β=0.5)\n' +
                 'Actual ET under Different Climates (Sigmoid β=0.5)', fontsize=11)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # 2. Ep/Ew比值的分布 / Distribution of Ep/Ew ratio
    ax2 = plt.subplot(3, 2, 2)
    for scenario_name in scenario_names:
        results = all_results[scenario_name]
        ratio = results['Ep'] / results['Ew']
        ax2.hist(ratio, bins=30, alpha=0.5, label=scenario_name)

    ax2.set_xlabel('Ep/Ew 比值 / Ep/Ew Ratio', fontsize=10)
    ax2.set_ylabel('频数 / Frequency', fontsize=10)
    ax2.set_title('干旱指数分布 / Aridity Index Distribution', fontsize=11)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=1.0, color='red', linestyle='--', linewidth=1, label='Ep=Ew')

    # 3. 模型间对比 (选择半干旱气候) / Model comparison (semi-arid climate)
    ax3 = plt.subplot(3, 2, 3)
    semiarid_results = all_results['半干旱 / Semi-arid']
    models_to_plot = ['Sigmoid_β0.5', 'Polynomial_b2', 'Rescaled_Power', 'Bouchet', 'AA']
    for model_name in models_to_plot:
        ax3.plot(range(90), semiarid_results[model_name][:90],
                label=model_name, linewidth=1.5)

    ax3.plot(range(90), semiarid_results['Ew'][:90], 'k--',
            label='Ew', linewidth=2, alpha=0.5)
    ax3.set_xlabel('天数 / Days', fontsize=10)
    ax3.set_ylabel('Ea (W/m²)', fontsize=10)
    ax3.set_title('半干旱气候下的模型对比\n' +
                 'Model Comparison in Semi-arid Climate', fontsize=11)
    ax3.legend(fontsize=7, loc='best')
    ax3.grid(True, alpha=0.3)

    # 4. Beta参数敏感性 / Beta parameter sensitivity
    ax4 = plt.subplot(3, 2, 4)
    sens_data = sensitivity_results['sigmoid_beta']
    ax4.plot(sens_data['parameter_values'], sens_data['mean_ea'],
            'o-', linewidth=2, markersize=6)
    ax4.set_xlabel('Beta 参数值 / Beta Parameter', fontsize=10)
    ax4.set_ylabel('平均 Ea (W/m²) / Mean Ea (W/m²)', fontsize=10)
    ax4.set_title('Sigmoid模型参数敏感性\n' +
                 'Sigmoid Model Parameter Sensitivity', fontsize=11)
    ax4.grid(True, alpha=0.3)

    # 5. 所有气候条件下的箱线图 / Box plot for all climates
    ax5 = plt.subplot(3, 2, 5)
    box_data = []
    labels = []
    for scenario_name in scenario_names:
        results = all_results[scenario_name]
        box_data.append(results['Sigmoid_β0.5'])
        # 简化标签 / Simplify labels
        labels.append(scenario_name.split('/')[0].strip())

    bp = ax5.boxplot(box_data)
    ax5.set_xticklabels(labels)
    ax5.set_ylabel('Ea (W/m²)', fontsize=10)
    ax5.set_title('实际蒸散发分布对比 (Sigmoid β=0.5)\n' +
                 'Actual ET Distribution Comparison', fontsize=11)
    ax5.grid(True, alpha=0.3, axis='y')
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=15, fontsize=9)

    # 6. Ea/Ew比值对比 / Ea/Ew ratio comparison
    ax6 = plt.subplot(3, 2, 6)
    for scenario_name in scenario_names:
        results = all_results[scenario_name]
        ratio = results['Sigmoid_β0.5'] / results['Ew']
        ax6.plot(range(90), ratio[:90], label=scenario_name, linewidth=1.5)

    ax6.axhline(y=1.0, color='red', linestyle='--', linewidth=1)
    ax6.set_xlabel('天数 / Days', fontsize=10)
    ax6.set_ylabel('Ea/Ew 比值 / Ea/Ew Ratio', fontsize=10)
    ax6.set_title('相对蒸散发变化\n' +
                 'Relative ET Variation', fontsize=11)
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存图片到 examples/figures 目录 / Save figure to examples/figures
    from pathlib import Path
    figures_dir = Path(__file__).parent / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    output_file = figures_dir / 'petcr_advanced_analysis.png'
    plt.savefig(str(output_file), dpi=300, bbox_inches='tight')
    print(f"图表已保存到: {output_file}")
    print(f"Figure saved to: {output_file}")
    print()

    # 显示图表 / Show plot
    # plt.show()  # 取消注释以显示图表 / Uncomment to display plot


def main():
    """主函数 / Main function"""
    print("\n")
    print("=" * 80)
    print("PET-CR 高级综合分析 / PET-CR Advanced Comprehensive Analysis")
    print("=" * 80)
    print()
    print("本示例展示: / This example demonstrates:")
    print("  1. 多气候场景分析 (30年时序) / Multi-climate scenario analysis (30-year time series)")
    print("  2. 长期变暖趋势分析 / Long-term warming trend analysis")
    print("  3. 极端事件响应分析 / Extreme event response analysis")
    print("  4. 参数敏感性分析 / Parameter sensitivity analysis")
    print("  5. 季节变化分析 / Seasonal variation analysis")
    print("  6. 模型不确定性评估 / Model uncertainty assessment")
    print("  7. 干旱指数与不确定性关系 / Aridity index vs. uncertainty relationship")
    print()

    # 生成气候场景 / Generate climate scenarios
    days = 10950  # 30年的数据 / 30 years of data
    scenarios, metadata = generate_climate_scenarios(days, include_extreme_event=True)

    # 为每个场景计算ET / Calculate ET for each scenario
    print("=" * 80)
    print("计算各气候场景的蒸散发 / Calculating ET for Each Climate Scenario")
    print("=" * 80)
    print()

    all_results = {}
    for scenario_name, scenario_data in scenarios.items():
        print(f"处理 / Processing: {scenario_name}")
        print(f"  {scenario_data['description']}")

        results = calculate_et_for_scenario(scenario_data)
        all_results[scenario_name] = results

        # 打印基本统计 / Print basic statistics
        print(f"  平均Ep / Mean Ep: {np.mean(results['Ep']):.2f} W/m²")
        print(f"  平均Ew / Mean Ew: {np.mean(results['Ew']):.2f} W/m²")
        print(f"  平均Ep/Ew / Mean Ep/Ew: {np.mean(results['Ep']/results['Ew']):.3f}")
        print()

    # 使用半干旱气候数据进行参数敏感性分析
    # Use semi-arid climate data for parameter sensitivity analysis
    semiarid_results = all_results['半干旱 / Semi-arid']
    sensitivity_results = parameter_sensitivity_analysis(
        semiarid_results['Ep'],
        semiarid_results['Ew']
    )

    # 季节分析 (使用温带海洋性气候) / Seasonal analysis (oceanic climate)
    oceanic_results = all_results['温带海洋 / Oceanic']
    seasonal_stats = seasonal_analysis(oceanic_results, days)

    # 模型间差异分析 / Inter-model variability analysis
    print("=" * 80)
    print("模型间差异分析 / Inter-model Variability Analysis")
    print("=" * 80)
    print()

    for scenario_name, results in all_results.items():
        print(f"\n{scenario_name}:")
        print("-" * 80)

        # 提取所有CR模型的结果 / Extract all CR model results
        model_names = ['Sigmoid_β0.5', 'Polynomial_b2', 'Rescaled_Power', 'Bouchet', 'AA']
        ea_values = np.array([results[name] for name in model_names])

        # 计算平均值和标准差 / Calculate mean and std
        mean_across_models = np.mean(ea_values, axis=0)
        std_across_models = np.std(ea_values, axis=0)

        # 计算相对不确定性 / Calculate relative uncertainty
        relative_uncertainty = std_across_models / mean_across_models * 100

        print(f"  模型间平均Ea / Mean Ea across models: {np.mean(mean_across_models):.2f} W/m²")
        print(f"  模型间平均标准差 / Mean std across models: {np.mean(std_across_models):.2f} W/m²")
        print(f"  平均相对不确定性 / Mean relative uncertainty: {np.mean(relative_uncertainty):.2f}%")
        print(f"  最大相对不确定性 / Max relative uncertainty: {np.max(relative_uncertainty):.2f}%")

    print()

    # 长时序趋势分析 / Long-term trend analysis
    print("=" * 80)
    print("长时序趋势分析 / Long-term Trend Analysis")
    print("=" * 80)
    print()

    for scenario_name, results in all_results.items():
        print(f"\n{scenario_name}:")
        print("-" * 80)

        # 计算年均值 / Calculate annual means
        n_years = int(metadata['years'])
        yearly_ea = []
        yearly_ep = []
        yearly_ew = []

        for year in range(n_years):
            start_idx = int(year * 365.25)
            end_idx = int((year + 1) * 365.25)
            yearly_ea.append(np.mean(results['Sigmoid_β0.5'][start_idx:end_idx]))
            yearly_ep.append(np.mean(results['Ep'][start_idx:end_idx]))
            yearly_ew.append(np.mean(results['Ew'][start_idx:end_idx]))

        yearly_ea = np.array(yearly_ea)
        yearly_ep = np.array(yearly_ep)
        yearly_ew = np.array(yearly_ew)

        # 计算线性趋势 / Calculate linear trend
        years_array = np.arange(n_years)
        ea_trend = np.polyfit(years_array, yearly_ea, 1)[0]  # W/m²/year
        ep_trend = np.polyfit(years_array, yearly_ep, 1)[0]
        ew_trend = np.polyfit(years_array, yearly_ew, 1)[0]

        print(f"  Ea (Sigmoid) 趋势 / trend: {ea_trend:.3f} W/m²/year")
        print(f"  Ep 趋势 / trend: {ep_trend:.3f} W/m²/year")
        print(f"  Ew 趋势 / trend: {ew_trend:.3f} W/m²/year")
        print(f"  30年总变化 / 30-year change: {ea_trend*30:.2f} W/m² (Ea)")

    print()

    # 极端事件响应分析 / Extreme event response analysis
    if metadata['extreme_event']:
        print("=" * 80)
        print("极端事件响应分析 / Extreme Event Response Analysis")
        print("=" * 80)
        print()

        extreme_start = metadata['extreme_start']
        extreme_end = metadata['extreme_end']

        # 定义基准期和恢复期 / Define baseline and recovery periods
        baseline_start = extreme_start - 30
        baseline_end = extreme_start
        recovery_start = extreme_end
        recovery_end = extreme_end + 30

        for scenario_name, results in all_results.items():
            print(f"\n{scenario_name}:")
            print("-" * 80)

            # 提取不同时期的数据 / Extract data for different periods
            baseline_ea = np.mean(results['Sigmoid_β0.5'][baseline_start:baseline_end])
            extreme_ea = np.mean(results['Sigmoid_β0.5'][extreme_start:extreme_end])
            recovery_ea = np.mean(results['Sigmoid_β0.5'][recovery_start:recovery_end])

            baseline_ratio = np.mean(results['Ep'][baseline_start:baseline_end] / results['Ew'][baseline_start:baseline_end])
            extreme_ratio = np.mean(results['Ep'][extreme_start:extreme_end] / results['Ew'][extreme_start:extreme_end])

            # 计算响应 / Calculate responses
            ea_drop = ((extreme_ea - baseline_ea) / baseline_ea) * 100  # %
            ea_recovery = ((recovery_ea - baseline_ea) / baseline_ea) * 100  # %

            print(f"  基准期 Ea / Baseline Ea: {baseline_ea:.2f} W/m²")
            print(f"  极端期 Ea / Extreme Ea: {extreme_ea:.2f} W/m² ({ea_drop:+.1f}%)")
            print(f"  恢复期 Ea / Recovery Ea: {recovery_ea:.2f} W/m² ({ea_recovery:+.1f}%)")
            print(f"  Ep/Ew 变化 / Ep/Ew change: {baseline_ratio:.3f} → {extreme_ratio:.3f}")

        print()

    # 干旱指数与模型不确定性关系分析 / Aridity index vs. uncertainty analysis
    print("=" * 80)
    print("干旱指数与模型不确定性关系 / Aridity Index vs. Model Uncertainty")
    print("=" * 80)
    print()

    for scenario_name, results in all_results.items():
        print(f"\n{scenario_name}:")
        print("-" * 80)

        # 计算干旱指数 / Calculate aridity index
        aridity_index = results['Ep'] / results['Ew']

        # 提取所有CR模型结果 / Extract all CR model results
        model_names = ['Sigmoid_β0.5', 'Polynomial_b2', 'Rescaled_Power', 'Bouchet', 'AA']
        ea_values = np.array([results[name] for name in model_names])

        # 计算模型间标准差 / Calculate inter-model standard deviation
        model_std = np.std(ea_values, axis=0)
        model_cv = model_std / np.mean(ea_values, axis=0) * 100  # Coefficient of variation (%)

        # 按干旱指数分组分析 / Analyze by aridity index bins
        ai_bins = [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]
        for i in range(len(ai_bins) - 1):
            mask = (aridity_index >= ai_bins[i]) & (aridity_index < ai_bins[i+1])
            if np.sum(mask) > 0:
                mean_cv = np.mean(model_cv[mask])
                print(f"  Ep/Ew ∈ [{ai_bins[i]:.1f}, {ai_bins[i+1]:.1f}): "
                      f"模型不确定性 / Model CV = {mean_cv:.2f}%")

    print()

    # 绘制结果 / Plot results
    plot_results(scenarios, all_results, sensitivity_results, metadata)

    # 总结和建议 / Summary and recommendations
    print("=" * 80)
    print("分析总结与建议 / Analysis Summary and Recommendations")
    print("=" * 80)
    print()
    print("主要发现 / Key Findings:")
    print("-" * 80)
    print("1. 不同气候条件下，模型表现存在差异")
    print("   Model performance varies across different climate conditions")
    print()
    print("2. 湿润气候: Ep/Ew < 1, 各模型结果接近")
    print("   Humid climate: Ep/Ew < 1, models show similar results")
    print()
    print("3. 干旱气候: Ep/Ew > 1, 模型间差异增大")
    print("   Arid climate: Ep/Ew > 1, inter-model differences increase")
    print()
    print("4. Sigmoid模型的beta参数对结果影响显著")
    print("   Sigmoid model's beta parameter significantly affects results")
    print()
    print("使用建议 / Recommendations:")
    print("-" * 80)
    print("• 湿润区域: 推荐Sigmoid (β=0.5-0.7) 或 Polynomial")
    print("  Humid regions: Recommend Sigmoid (β=0.5-0.7) or Polynomial")
    print()
    print("• 干旱区域: 推荐AA或Rescaled Power (更稳健)")
    print("  Arid regions: Recommend AA or Rescaled Power (more robust)")
    print()
    print("• 大尺度研究: 推荐Rescaled Power (无需校准)")
    print("  Large-scale studies: Recommend Rescaled Power (calibration-free)")
    print()
    print("• 参数选择: 建议进行敏感性分析以确定最优参数")
    print("  Parameter selection: Conduct sensitivity analysis for optimal values")
    print()
    print("=" * 80)
    print("\n分析完成! / Analysis completed!\n")


if __name__ == "__main__":
    main()
