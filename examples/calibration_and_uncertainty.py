#!/usr/bin/env python
"""
Model Calibration and Uncertainty Analysis Example
===================================================

This example demonstrates:
1. Model calibration using synthetic data and scipy.optimize
2. Uncertainty quantification through ensemble modeling
3. Visualization of model performance and uncertainty

The script generates synthetic ET data, calibrates the sigmoid_cr model,
and evaluates structural uncertainty by comparing 5 different CR models.

Requirements:
- numpy
- scipy
- matplotlib

Author: PET-CR Contributors
Date: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from pathlib import Path

# Add parent directory to path if running as script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from petcr import (
    sigmoid_cr,
    polynomial_cr,
    rescaled_power_cr,
    bouchet_cr,
    aa_cr
)

# ============================================================================
# Configuration / 配置
# ============================================================================

# Number of synthetic data points / 合成数据点数
N_POINTS = 100

# True parameter for synthetic data generation / 用于生成合成数据的真实参数
TRUE_BETA = 0.75

# Noise level for synthetic observations / 合成观测的噪声水平
NOISE_STD = 5.0  # mm/day

# Random seed for reproducibility / 随机种子以保证可重复性
np.random.seed(42)

# Output figure path / 输出图像路径
OUTPUT_FIG = Path(__file__).parent / 'figures' / 'calibration_and_uncertainty.png'
OUTPUT_FIG.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Step 1: Generate Synthetic Data / 步骤1：生成合成数据
# ============================================================================

def generate_synthetic_data(n_points=N_POINTS, beta_true=TRUE_BETA, noise_std=NOISE_STD):
    """
    Generate synthetic ET data using sigmoid_cr model.
    
    使用 sigmoid_cr 模型生成合成 ET 数据。
    
    Parameters
    ----------
    n_points : int
        Number of data points to generate
        生成的数据点数
    beta_true : float
        True beta parameter for data generation
        用于数据生成的真实 beta 参数
    noise_std : float
        Standard deviation of observation noise [mm/day]
        观测噪声的标准差 [mm/day]
    
    Returns
    -------
    dict
        Dictionary containing Ep, Ew, Ea_true, and Ea_observed
        包含 Ep, Ew, Ea_true 和 Ea_observed 的字典
    """
    print("="*70)
    print("Step 1: Generating Synthetic Data")
    print("步骤1：生成合成数据")
    print("="*70)
    
    # Generate Ew (wet-environment ET) with realistic range
    # 生成 Ew（湿环境蒸散发），范围合理
    Ew = np.random.uniform(50, 150, n_points)  # mm/day
    
    # Generate dryness index (Ep/Ew) spanning from wet to dry conditions
    # 生成干燥度指数 (Ep/Ew)，跨越从湿润到干旱条件
    dryness_index = np.random.uniform(0.5, 2.5, n_points)
    Ep = Ew * dryness_index
    
    # Generate true Ea using sigmoid_cr model with true parameter
    # 使用真实参数的 sigmoid_cr 模型生成真实 Ea
    Ea_true = sigmoid_cr(Ep, Ew, alpha=1.26, beta=beta_true)
    
    # Add observation noise / 添加观测噪声
    noise = np.random.normal(0, noise_std, n_points)
    Ea_observed = Ea_true + noise
    
    # Ensure physical constraints / 确保物理约束
    Ea_observed = np.clip(Ea_observed, 0, Ew)
    
    print(f"✓ Generated {n_points} synthetic data points")
    print(f"  Ep range: [{Ep.min():.1f}, {Ep.max():.1f}] mm/day")
    print(f"  Ew range: [{Ew.min():.1f}, {Ew.max():.1f}] mm/day")
    print(f"  Ea range: [{Ea_observed.min():.1f}, {Ea_observed.max():.1f}] mm/day")
    print(f"  True beta: {beta_true:.3f}")
    print(f"  Noise std: {noise_std:.1f} mm/day")
    
    return {
        'Ep': Ep,
        'Ew': Ew,
        'Ea_true': Ea_true,
        'Ea_observed': Ea_observed
    }


# ============================================================================
# Step 2: Model Calibration / 步骤2：模型校准
# ============================================================================

def calibrate_sigmoid_model(data):
    """
    Calibrate sigmoid_cr model by finding optimal beta parameter.
    
    通过找到最优 beta 参数来校准 sigmoid_cr 模型。
    
    Parameters
    ----------
    data : dict
        Dictionary with Ep, Ew, and Ea_observed
        包含 Ep, Ew 和 Ea_observed 的字典
    
    Returns
    -------
    dict
        Calibration results including optimal beta and RMSE
        校准结果，包括最优 beta 和 RMSE
    """
    print("\n" + "="*70)
    print("Step 2: Model Calibration")
    print("步骤2：模型校准")
    print("="*70)
    
    Ep = data['Ep']
    Ew = data['Ew']
    Ea_obs = data['Ea_observed']
    
    # Define objective function (RMSE) / 定义目标函数 (RMSE)
    def objective(params):
        """Objective function: Root Mean Square Error"""
        beta = params[0]
        
        # Ensure beta is positive / 确保 beta 为正
        if beta <= 0:
            return 1e10
        
        # Compute model predictions / 计算模型预测
        Ea_pred = sigmoid_cr(Ep, Ew, alpha=1.26, beta=beta)
        
        # Compute RMSE / 计算 RMSE
        rmse = np.sqrt(np.mean((Ea_pred - Ea_obs)**2))
        
        return rmse
    
    # Initial guess / 初始猜测
    beta_init = 0.5
    
    # Bounds for beta / beta 的界限
    bounds = [(0.1, 2.0)]
    
    print(f"Starting calibration...")
    print(f"  Initial beta: {beta_init:.3f}")
    print(f"  Bounds: {bounds[0]}")
    
    # Perform optimization / 执行优化
    result = minimize(
        objective,
        [beta_init],
        method='L-BFGS-B',
        bounds=bounds,
        options={'disp': False}
    )
    
    beta_opt = result.x[0]
    rmse_opt = result.fun
    
    # Compute calibrated predictions / 计算校准预测
    Ea_calibrated = sigmoid_cr(Ep, Ew, alpha=1.26, beta=beta_opt)
    
    # Compute R² / 计算 R²
    ss_res = np.sum((Ea_obs - Ea_calibrated)**2)
    ss_tot = np.sum((Ea_obs - np.mean(Ea_obs))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    print(f"✓ Calibration complete")
    print(f"  Optimal beta: {beta_opt:.3f} (true: {TRUE_BETA:.3f})")
    print(f"  RMSE: {rmse_opt:.2f} mm/day")
    print(f"  R²: {r_squared:.3f}")
    
    return {
        'beta_opt': beta_opt,
        'rmse': rmse_opt,
        'r_squared': r_squared,
        'Ea_calibrated': Ea_calibrated
    }


# ============================================================================
# Step 3: Uncertainty Analysis / 步骤3：不确定性分析
# ============================================================================

def uncertainty_analysis(data):
    """
    Evaluate structural uncertainty using ensemble of CR models.
    
    使用 CR 模型集合评估结构不确定性。
    
    Parameters
    ----------
    data : dict
        Dictionary with Ep and Ew
        包含 Ep 和 Ew 的字典
    
    Returns
    -------
    dict
        Uncertainty analysis results
        不确定性分析结果
    """
    print("\n" + "="*70)
    print("Step 3: Uncertainty Analysis")
    print("步骤3：不确定性分析")
    print("="*70)
    
    Ep = data['Ep']
    Ew = data['Ew']
    
    # Run all 5 CR models / 运行所有5个CR模型
    print("Running ensemble of 5 CR models...")
    
    models = {
        'Sigmoid': sigmoid_cr(Ep, Ew, alpha=1.26, beta=0.75),
        'Polynomial': polynomial_cr(Ep, Ew, b=2.0),
        'Rescaled Power': rescaled_power_cr(Ep, Ew, n=0.5),
        'Bouchet': bouchet_cr(Ep, Ew),
        'AA': aa_cr(Ep, Ew, ea_min=None)
    }
    
    # Stack model results / 堆叠模型结果
    model_array = np.array([models[name] for name in models.keys()])
    
    # Compute ensemble statistics / 计算集合统计
    ensemble_mean = np.mean(model_array, axis=0)
    ensemble_std = np.std(model_array, axis=0)
    ensemble_min = np.min(model_array, axis=0)
    ensemble_max = np.max(model_array, axis=0)
    
    print(f"✓ Ensemble analysis complete")
    print(f"  Number of models: {len(models)}")
    print(f"  Mean ensemble ET: {ensemble_mean.mean():.1f} ± {ensemble_std.mean():.1f} mm/day")
    print(f"  Structural uncertainty range: [{ensemble_min.mean():.1f}, {ensemble_max.mean():.1f}] mm/day")
    
    # Print model statistics / 打印模型统计
    print("\n  Individual model means:")
    for name, values in models.items():
        print(f"    {name:16s}: {values.mean():.2f} mm/day")
    
    return {
        'models': models,
        'ensemble_mean': ensemble_mean,
        'ensemble_std': ensemble_std,
        'ensemble_min': ensemble_min,
        'ensemble_max': ensemble_max
    }


# ============================================================================
# Step 4: Visualization / 步骤4：可视化
# ============================================================================

def plot_calibration_and_uncertainty(data, calib_results, uncert_results, output_path):
    """
    Create comprehensive visualization of calibration and uncertainty.
    
    创建校准和不确定性的综合可视化。
    
    Parameters
    ----------
    data : dict
        Synthetic data
        合成数据
    calib_results : dict
        Calibration results
        校准结果
    uncert_results : dict
        Uncertainty analysis results
        不确定性分析结果
    output_path : Path
        Output figure path
        输出图像路径
    """
    print("\n" + "="*70)
    print("Step 4: Creating Visualization")
    print("步骤4：创建可视化")
    print("="*70)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    Ep = data['Ep']
    Ew = data['Ew']
    Ea_true = data['Ea_true']
    Ea_obs = data['Ea_observed']
    Ea_calib = calib_results['Ea_calibrated']
    
    # Sort by dryness index for plotting / 按干燥度指数排序以便绘图
    dryness = Ep / Ew
    sort_idx = np.argsort(dryness)
    
    # ========================================================================
    # Panel 1: Scatter plot with calibration / 散点图与校准
    # ========================================================================
    ax1 = axes[0, 0]
    
    ax1.scatter(dryness[sort_idx], Ea_obs[sort_idx], 
                c='gray', alpha=0.5, s=30, label='Observed (with noise)')
    ax1.plot(dryness[sort_idx], Ea_true[sort_idx],
             'k-', linewidth=2, label=f'True model (β={TRUE_BETA:.2f})')
    ax1.plot(dryness[sort_idx], Ea_calib[sort_idx],
             'r--', linewidth=2, label=f'Calibrated (β={calib_results["beta_opt"]:.2f})')
    
    ax1.set_xlabel('Dryness Index (Ep/Ew)', fontsize=11)
    ax1.set_ylabel('Actual ET (mm/day)', fontsize=11)
    ax1.set_title('(a) Model Calibration', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, linestyle=':', alpha=0.3)
    
    # Add statistics text / 添加统计文本
    stats_text = f'RMSE = {calib_results["rmse"]:.2f} mm/day\nR² = {calib_results["r_squared"]:.3f}'
    ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes,
             verticalalignment='top', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # ========================================================================
    # Panel 2: Ensemble uncertainty / 集合不确定性
    # ========================================================================
    ax2 = axes[0, 1]
    
    ensemble_mean = uncert_results['ensemble_mean']
    ensemble_std = uncert_results['ensemble_std']
    
    # Plot observed data / 绘制观测数据
    ax2.scatter(dryness[sort_idx], Ea_obs[sort_idx],
                c='gray', alpha=0.4, s=20, label='Observed', zorder=1)
    
    # Plot true model / 绘制真实模型
    ax2.plot(dryness[sort_idx], Ea_true[sort_idx],
             'k-', linewidth=2, label='True model', zorder=4)
    
    # Plot ensemble mean / 绘制集合平均
    ax2.plot(dryness[sort_idx], ensemble_mean[sort_idx],
             'b-', linewidth=2.5, label='Ensemble mean', zorder=3)
    
    # Plot ±2σ uncertainty band / 绘制 ±2σ 不确定性带
    ax2.fill_between(dryness[sort_idx],
                      (ensemble_mean - 2*ensemble_std)[sort_idx],
                      (ensemble_mean + 2*ensemble_std)[sort_idx],
                      color='blue', alpha=0.2, label='±2σ uncertainty', zorder=2)
    
    ax2.set_xlabel('Dryness Index (Ep/Ew)', fontsize=11)
    ax2.set_ylabel('Actual ET (mm/day)', fontsize=11)
    ax2.set_title('(b) Ensemble Uncertainty', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, linestyle=':', alpha=0.3)
    
    # ========================================================================
    # Panel 3: Individual model comparison / 单个模型比较
    # ========================================================================
    ax3 = axes[1, 0]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i, (name, values) in enumerate(uncert_results['models'].items()):
        ax3.plot(dryness[sort_idx], values[sort_idx],
                 '-', linewidth=1.5, color=colors[i], label=name, alpha=0.8)
    
    # Add true model / 添加真实模型
    ax3.plot(dryness[sort_idx], Ea_true[sort_idx],
             'k--', linewidth=2, label='True model')
    
    ax3.set_xlabel('Dryness Index (Ep/Ew)', fontsize=11)
    ax3.set_ylabel('Actual ET (mm/day)', fontsize=11)
    ax3.set_title('(c) Individual CR Models', fontsize=12, fontweight='bold')
    ax3.legend(loc='best', fontsize=9, ncol=2)
    ax3.grid(True, linestyle=':', alpha=0.3)
    
    # ========================================================================
    # Panel 4: Residuals analysis / 残差分析
    # ========================================================================
    ax4 = axes[1, 1]
    
    # Compute residuals / 计算残差
    residuals_calib = Ea_obs - Ea_calib
    residuals_ensemble = Ea_obs - ensemble_mean
    
    # Histogram of residuals / 残差直方图
    ax4.hist(residuals_calib, bins=20, alpha=0.6, color='red',
             label=f'Calibrated (std={np.std(residuals_calib):.2f})', density=True)
    ax4.hist(residuals_ensemble, bins=20, alpha=0.6, color='blue',
             label=f'Ensemble (std={np.std(residuals_ensemble):.2f})', density=True)
    
    # Add zero line / 添加零线
    ax4.axvline(0, color='k', linestyle='--', linewidth=1)
    
    # Add normal distribution reference / 添加正态分布参考
    x_range = np.linspace(residuals_calib.min(), residuals_calib.max(), 100)
    ax4.plot(x_range, 
             1/(NOISE_STD * np.sqrt(2*np.pi)) * np.exp(-0.5*(x_range/NOISE_STD)**2),
             'k-', linewidth=2, alpha=0.5, label=f'Expected (std={NOISE_STD:.1f})')
    
    ax4.set_xlabel('Residuals (mm/day)', fontsize=11)
    ax4.set_ylabel('Probability Density', fontsize=11)
    ax4.set_title('(d) Residuals Distribution', fontsize=12, fontweight='bold')
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, linestyle=':', alpha=0.3)
    
    # ========================================================================
    # Overall title / 总标题
    # ========================================================================
    fig.suptitle(
        'Model Calibration and Uncertainty Analysis for CR Models',
        fontsize=16,
        fontweight='bold',
        y=0.995
    )
    
    # Add description / 添加描述
    fig.text(
        0.5, 0.01,
        f'Synthetic data: N={N_POINTS}, true β={TRUE_BETA:.2f}, noise σ={NOISE_STD:.1f} mm/day | '
        f'5 CR models: Sigmoid, Polynomial, Rescaled Power, Bouchet, AA',
        ha='center',
        fontsize=9,
        style='italic'
    )
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.99])
    
    # Save figure / 保存图像
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Figure saved to: {output_path}")
    print(f"✓ 图像已保存至: {output_path}")
    
    plt.close()


# ============================================================================
# Main Execution / 主执行
# ============================================================================

def main():
    """
    Main function to run calibration and uncertainty analysis.
    
    运行校准和不确定性分析的主函数。
    """
    print("\n" + "="*70)
    print("Model Calibration and Uncertainty Analysis")
    print("模型校准和不确定性分析")
    print("="*70)
    print()
    
    # Step 1: Generate synthetic data / 步骤1：生成合成数据
    data = generate_synthetic_data()
    
    # Step 2: Calibrate model / 步骤2：校准模型
    calib_results = calibrate_sigmoid_model(data)
    
    # Step 3: Uncertainty analysis / 步骤3：不确定性分析
    uncert_results = uncertainty_analysis(data)
    
    # Step 4: Visualize results / 步骤4：可视化结果
    plot_calibration_and_uncertainty(data, calib_results, uncert_results, OUTPUT_FIG)
    
    print("\n" + "="*70)
    print("✓ Analysis complete! / 分析完成！")
    print("="*70)
    
    return data, calib_results, uncert_results


if __name__ == '__main__':
    main()
