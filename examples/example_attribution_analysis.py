"""
ET归因分析示例 / ET Attribution Analysis Example
=================================================

本示例演示如何使用PET-CR库进行高级ET归因分析，
分离气候变化和陆地表面变化对蒸散发的影响。

This example demonstrates how to use the PET-CR library for advanced ET
attribution analysis, separating climate change and land surface change
effects on evapotranspiration.

示例内容 / Example Contents
---------------------------
1. 生成140年合成气候数据（模拟1pctCO2实验）
   Generate 140-year synthetic climate data (simulating 1pctCO2 experiment)

2. 执行Budyko框架归因分析
   Perform Budyko framework attribution analysis

3. 创建高质量可视化图表（类似Nature Climate Change Figure 3e）
   Create high-quality visualization (similar to Nature Climate Change Figure 3e)

4. 分析气候变化和陆地表面贡献
   Analyze climate change and land surface contributions

运行方式 / How to Run
---------------------
python examples/example_attribution_analysis.py

作者 / Author: PET-CR Contributors
日期 / Date: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

# 导入PET-CR库 / Import PET-CR library
try:
    from petcr import (
        generate_timeseries_data,
        attribution_analysis,
        projection_1pctCO2,
        setup_chinese_font,
    )
except ImportError:
    # 如果未安装，添加路径 / If not installed, add path
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from petcr import (
        generate_timeseries_data,
        attribution_analysis,
        projection_1pctCO2,
        setup_chinese_font,
    )


def generate_1pctCO2_data(n_years=140, seed=42):
    """
    生成模拟1pctCO2实验的数据
    Generate data simulating 1pctCO2 experiment.

    参数 / Parameters
    ----------
    n_years : int
        年数（默认140年，对应CO2加倍）
        Number of years (default 140 years, corresponding to CO2 doubling)
    seed : int
        随机种子 / Random seed

    返回 / Returns
    -------
    dict
        包含ET、PETe、降水时间序列的字典
        Dictionary containing ET, PETe, precipitation time series
    """
    print("=" * 70)
    print("步骤 1: 生成合成气候数据 / Step 1: Generate Synthetic Climate Data")
    print("=" * 70)
    print(f"\n模拟1pctCO2实验（{n_years}年，CO2浓度每年增加1%）")
    print(f"Simulating 1pctCO2 experiment ({n_years} years, CO2 increases 1% per year)")

    np.random.seed(seed)
    time = np.arange(n_years)

    # 气候变化趋势 / Climate change trends
    # 温度升高约3-4°C / Temperature increases ~3-4°C
    temp_trend = 3.0 * (1.0 - np.exp(-time / 40.0))  # 非线性变暖 / Nonlinear warming

    # PETe随温度增加 / PETe increases with temperature
    # 每°C增加约2-3% / ~2-3% increase per °C
    pete_trend = 3.0 * (1.0 + 0.025 * temp_trend) + np.random.normal(0, 0.15, n_years)

    # 降水略有增加（约5-10%）/ Precipitation slight increase (~5-10%)
    pr_trend = 2.5 * (1.0 + 0.001 * time) + np.random.normal(0, 0.2, n_years)

    # ET变化：气候变化增加 + CO2生理效应减少
    # ET changes: climate change increase + CO2 physiological effect decrease
    # 气候效应: +0.4 mm/day / Climate effect: +0.4 mm/day
    # 生理效应: -0.15 mm/day / Physiological effect: -0.15 mm/day
    et_climate_component = 1.8 * (1.0 + 0.02 * temp_trend)
    et_landsurf_component = -0.0012 * time  # CO2导致的气孔关闭 / Stomatal closure from CO2
    et_trend = et_climate_component + et_landsurf_component + np.random.normal(0, 0.1, n_years)

    # 确保物理约束 / Ensure physical constraints
    pete_trend = np.maximum(pete_trend, 0.5)
    pr_trend = np.maximum(pr_trend, 0.1)
    et_trend = np.maximum(et_trend, 0.1)
    et_trend = np.minimum(et_trend, pr_trend)

    print(f"\n生成的数据统计 / Generated Data Statistics:")
    print(f"  初始PETe / Initial PETe: {pete_trend[0]:.2f} mm/day")
    print(f"  最终PETe / Final PETe: {pete_trend[-1]:.2f} mm/day")
    print(f"  PETe变化 / PETe change: +{pete_trend[-1]-pete_trend[0]:.2f} mm/day")
    print(f"\n  初始降水 / Initial Precipitation: {pr_trend[0]:.2f} mm/day")
    print(f"  最终降水 / Final Precipitation: {pr_trend[-1]:.2f} mm/day")
    print(f"  降水变化 / Precipitation change: +{pr_trend[-1]-pr_trend[0]:.2f} mm/day")
    print(f"\n  初始ET / Initial ET: {et_trend[0]:.2f} mm/day")
    print(f"  最终ET / Final ET: {et_trend[-1]:.2f} mm/day")
    print(f"  ET变化 / ET change: +{et_trend[-1]-et_trend[0]:.2f} mm/day")

    return {
        'time': time,
        'et': et_trend,
        'pete': pete_trend,
        'pr': pr_trend
    }


def perform_attribution(data, window_size=30):
    """
    执行归因分析
    Perform attribution analysis.

    参数 / Parameters
    ----------
    data : dict
        包含ET、PETe、降水时间序列的字典
        Dictionary containing ET, PETe, precipitation time series
    window_size : int
        滑动窗口大小（年）/ Moving window size (years)

    返回 / Returns
    -------
    dict
        归因分析结果 / Attribution analysis results
    """
    print("\n" + "=" * 70)
    print("步骤 2: 执行归因分析 / Step 2: Perform Attribution Analysis")
    print("=" * 70)
    print(f"\n使用{window_size}年滑动窗口进行归因分析")
    print(f"Using {window_size}-year moving window for attribution analysis")

    # 执行归因分析 / Perform attribution analysis
    results = attribution_analysis(
        et_timeseries=data['et'],
        pete_timeseries=data['pete'],
        pr_timeseries=data['pr'],
        window_size=window_size
    )

    print(f"\n归因分析结果 / Attribution Analysis Results:")
    print(f"  校准的Budyko参数 n / Calibrated Budyko parameter n: {results['n_parameter']:.3f}")
    print(f"  分析窗口数 / Number of analysis windows: {len(results['time_index'])}")

    # 显示不同时期的结果 / Show results at different periods
    periods = [0, len(results['time_index'])//2, len(results['time_index'])-1]
    period_names = ['初始 / Initial', '中期 / Middle', '最终 / Final']

    print(f"\nET变化分解 (mm/day) / ET Change Decomposition (mm/day):")
    print(f"{'时期 / Period':<20} {'总变化 / Total':<15} {'气候 / Climate':<15} {'陆面 / Land Surf':<15}")
    print("-" * 70)

    for period, name in zip(periods, period_names):
        print(f"{name:<20} "
              f"{results['et_total'][period]:>14.3f} "
              f"{results['et_climate'][period]:>14.3f} "
              f"{results['et_landsurf'][period]:>14.3f}")

    # 计算贡献百分比 / Calculate contribution percentages
    total_change = results['et_total'][-1]
    if abs(total_change) > 1e-6:
        climate_pct = (results['et_climate'][-1] / total_change) * 100
        landsurf_pct = (results['et_landsurf'][-1] / total_change) * 100

        print(f"\n最终时期贡献百分比 / Final Period Contribution Percentages:")
        print(f"  气候变化贡献 / Climate contribution: {climate_pct:.1f}%")
        print(f"  陆地表面贡献 / Land surface contribution: {landsurf_pct:.1f}%")

    return results


def create_visualization(data, results, output_path='examples/figures'):
    """
    创建高质量可视化图表
    Create high-quality visualization.

    类似于Zhou & Yu (2025) Nature Climate Change Figure 3e
    Similar to Zhou & Yu (2025) Nature Climate Change Figure 3e

    参数 / Parameters
    ----------
    data : dict
        原始数据 / Original data
    results : dict
        归因分析结果 / Attribution analysis results
    output_path : str
        输出路径 / Output path
    """
    print("\n" + "=" * 70)
    print("步骤 3: 创建可视化图表 / Step 3: Create Visualization")
    print("=" * 70)

    # 优先设置中文字体 / Prefer Chinese-capable font
    chosen_font = setup_chinese_font()

    # 设置matplotlib样式 / Set matplotlib style
    mpl.rcParams['font.family'] = 'sans-serif'
    if chosen_font:
        mpl.rcParams['font.sans-serif'] = [chosen_font]
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['axes.linewidth'] = 1.0
    mpl.rcParams['axes.labelsize'] = 11
    mpl.rcParams['xtick.labelsize'] = 10
    mpl.rcParams['ytick.labelsize'] = 10

    # 创建图形 / Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('ET归因分析：分离气候变化和陆地表面效应 / ET Attribution Analysis: Separating Climate and Land Surface Effects',
                 fontsize=14, fontweight='bold', y=0.995)

    # 时间轴（窗口中心年份）/ Time axis (center year of windows)
    window_size = len(data['et']) - len(results['time_index']) + 1
    time_center = results['time_index'] + window_size // 2

    # ========================================
    # 图1: ET变化的归因分解
    # Figure 1: Attribution decomposition of ET changes
    # ========================================
    ax1 = axes[0, 0]

    # 绘制各组分 / Plot components
    ax1.plot(time_center, results['et_total'], 'k-', linewidth=2.5,
             label='总变化 / Total Change', zorder=3)
    ax1.plot(time_center, results['et_climate'], 'r-', linewidth=2.0,
             label='气候贡献 / Climate Contribution', alpha=0.8, zorder=2)
    ax1.plot(time_center, results['et_landsurf'], 'b-', linewidth=2.0,
             label='陆面贡献 / Land Surface Contribution', alpha=0.8, zorder=2)

    # 填充区域 / Fill areas
    ax1.fill_between(time_center, 0, results['et_climate'],
                     color='red', alpha=0.2, label='_nolegend_')
    ax1.fill_between(time_center, 0, results['et_landsurf'],
                     color='blue', alpha=0.2, label='_nolegend_')

    # 零线 / Zero line
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    ax1.set_xlabel('年份 / Year', fontsize=11, fontweight='bold')
    ax1.set_ylabel('ET变化 / ET Change (mm/day)', fontsize=11, fontweight='bold')
    ax1.set_title('(a) ET变化归因 / ET Change Attribution', fontsize=12, fontweight='bold', loc='left')
    ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=9)
    ax1.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

    # ========================================
    # 图2: 累积贡献堆叠图
    # Figure 2: Cumulative contribution stacked plot
    # ========================================
    ax2 = axes[0, 1]

    # 创建堆叠面积图 / Create stacked area plot
    climate_positive = np.maximum(results['et_climate'], 0)
    landsurf_contribution = results['et_landsurf']

    ax2.fill_between(time_center, 0, climate_positive,
                     color='#d62728', alpha=0.7, label='气候贡献 / Climate (+)')
    ax2.fill_between(time_center, climate_positive,
                     climate_positive + landsurf_contribution,
                     color='#1f77b4', alpha=0.7, label='陆面贡献 / Land Surface')

    # 总变化线 / Total change line
    ax2.plot(time_center, results['et_total'], 'k-', linewidth=2.5,
             label='总变化 / Total', zorder=3)

    ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('年份 / Year', fontsize=11, fontweight='bold')
    ax2.set_ylabel('累积ET变化 / Cumulative ET Change (mm/day)', fontsize=11, fontweight='bold')
    ax2.set_title('(b) 累积贡献 / Cumulative Contributions', fontsize=12, fontweight='bold', loc='left')
    ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=9)
    ax2.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

    # ========================================
    # 图3: 驱动因子变化（PETe和降水）
    # Figure 3: Driver changes (PETe and precipitation)
    # ========================================
    ax3 = axes[1, 0]

    # 计算滑动平均 / Calculate moving averages
    window_size_data = 30
    n_windows = len(data['et']) - window_size_data + 1
    pete_smooth = np.array([np.mean(data['pete'][i:i+window_size_data]) for i in range(n_windows)])
    pr_smooth = np.array([np.mean(data['pr'][i:i+window_size_data]) for i in range(n_windows)])

    # 双Y轴 / Dual Y-axis
    color_pete = '#ff7f0e'
    color_pr = '#2ca02c'

    ax3.plot(time_center, pete_smooth - pete_smooth[0], color=color_pete,
             linewidth=2.0, label='ΔPETe', marker='o', markersize=3, markevery=10)
    ax3.set_xlabel('年份 / Year', fontsize=11, fontweight='bold')
    ax3.set_ylabel('ΔPETe (mm/day)', fontsize=11, fontweight='bold', color=color_pete)
    ax3.tick_params(axis='y', labelcolor=color_pete)

    ax3_twin = ax3.twinx()
    ax3_twin.plot(time_center, pr_smooth - pr_smooth[0], color=color_pr,
                  linewidth=2.0, label='Δ降水 / ΔPrecipitation',
                  marker='s', markersize=3, markevery=10)
    ax3_twin.set_ylabel('Δ降水 / ΔPrecipitation (mm/day)', fontsize=11,
                        fontweight='bold', color=color_pr)
    ax3_twin.tick_params(axis='y', labelcolor=color_pr)

    ax3.set_title('(c) 气候驱动因子变化 / Climate Driver Changes',
                  fontsize=12, fontweight='bold', loc='left')
    ax3.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

    # 合并图例 / Combined legend
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               frameon=True, fancybox=True, shadow=True, fontsize=9)

    # ========================================
    # 图4: 贡献百分比随时间变化
    # Figure 4: Contribution percentages over time
    # ========================================
    ax4 = axes[1, 1]

    # 计算百分比（避免除以零）/ Calculate percentages (avoid division by zero)
    total_nonzero = np.where(np.abs(results['et_total']) > 1e-6, results['et_total'], np.nan)
    climate_pct = (results['et_climate'] / total_nonzero) * 100
    landsurf_pct = (results['et_landsurf'] / total_nonzero) * 100

    ax4.plot(time_center, climate_pct, 'r-', linewidth=2.0,
             label='气候贡献 / Climate', marker='o', markersize=3, markevery=10)
    ax4.plot(time_center, landsurf_pct, 'b-', linewidth=2.0,
             label='陆面贡献 / Land Surface', marker='s', markersize=3, markevery=10)

    # 100%参考线 / 100% reference line
    ax4.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax4.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    ax4.set_xlabel('年份 / Year', fontsize=11, fontweight='bold')
    ax4.set_ylabel('贡献百分比 / Contribution (%)', fontsize=11, fontweight='bold')
    ax4.set_title('(d) 相对贡献 / Relative Contributions', fontsize=12, fontweight='bold', loc='left')
    ax4.legend(loc='best', frameon=True, fancybox=True, shadow=True, fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

    # 调整布局 / Adjust layout
    plt.tight_layout()

    # 保存图形 / Save figure
    Path(output_path).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_path) / 'attribution_analysis_results.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n图形已保存至 / Figure saved to: {output_file}")

    # 也保存为PDF（高质量出版）/ Also save as PDF (high-quality publication)
    output_file_pdf = Path(output_path) / 'attribution_analysis_results.pdf'
    plt.savefig(output_file_pdf, bbox_inches='tight', facecolor='white')
    print(f"PDF版本已保存至 / PDF version saved to: {output_file_pdf}")

    # 显示图形（可选）/ Display figure (optional)
    # plt.show()
    plt.close()


def print_summary(data, results):
    """
    打印分析总结
    Print analysis summary.

    参数 / Parameters
    ----------
    data : dict
        原始数据 / Original data
    results : dict
        归因分析结果 / Attribution analysis results
    """
    print("\n" + "=" * 70)
    print("分析总结 / Analysis Summary")
    print("=" * 70)

    total_change = results['et_total'][-1]
    climate_change = results['et_climate'][-1]
    landsurf_change = results['et_landsurf'][-1]

    print(f"\n140年间ET变化 / ET Changes Over 140 Years:")
    print(f"  总变化 / Total change: {total_change:+.3f} mm/day")
    print(f"  气候变化贡献 / Climate contribution: {climate_change:+.3f} mm/day")
    print(f"  陆地表面贡献 / Land surface contribution: {landsurf_change:+.3f} mm/day")

    if abs(total_change) > 1e-6:
        print(f"\n相对贡献 / Relative Contributions:")
        print(f"  气候变化 / Climate change: {(climate_change/total_change)*100:.1f}%")
        print(f"  陆地表面 / Land surface: {(landsurf_change/total_change)*100:.1f}%")

    print(f"\n物理解释 / Physical Interpretation:")
    if climate_change > 0:
        print(f"  ✓ 气候变暖增加了大气蒸发需求，促进ET增加")
        print(f"    Climate warming increases atmospheric evaporative demand, enhancing ET")

    if landsurf_change < 0:
        print(f"  ✓ CO2浓度升高导致植物气孔部分关闭，抑制ET")
        print(f"    Elevated CO2 causes partial stomatal closure, suppressing ET")
        print(f"  ✓ 陆地表面效应部分抵消了气候变化的影响")
        print(f"    Land surface effects partially offset climate change impacts")

    print("\n" + "=" * 70)


def main():
    """主函数 / Main function"""

    print("\n" + "=" * 70)
    print("ET归因分析高级示例 / Advanced ET Attribution Analysis Example")
    print("=" * 70)
    print("\n本示例演示如何使用PET-CR库进行ET变化的归因分析")
    print("This example demonstrates ET change attribution analysis using PET-CR\n")

    # 步骤1: 生成数据 / Step 1: Generate data
    data = generate_1pctCO2_data(n_years=140, seed=42)

    # 步骤2: 归因分析 / Step 2: Attribution analysis
    results = perform_attribution(data, window_size=30)

    # 步骤3: 可视化 / Step 3: Visualization
    create_visualization(data, results)

    # 步骤4: 打印总结 / Step 4: Print summary
    print_summary(data, results)

    print("\n" + "=" * 70)
    print("分析完成！/ Analysis Complete!")
    print("=" * 70)
    print("\n查看生成的图形：examples/figures/attribution_analysis_results.png")
    print("View generated figure: examples/figures/attribution_analysis_results.png\n")


if __name__ == "__main__":
    main()
