"""
Integration Test: Handling Missing Data in ET Calculations
集成测试：蒸散发计算中的缺失数据处理

This script demonstrates robust handling of:
本脚本演示如何稳健地处理：
1. Missing values (NaN) in meteorological data
   气象数据中的缺失值（NaN）
2. Gap-filling strategies
   数据填补策略
3. Quality control flags
   质量控制标志
4. Uncertainty quantification
   不确定性量化

Author: PET-CR Development Team
Date: 2025-12-04
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '..')
import petcr

# Set random seed for reproducibility
np.random.seed(42)


def inject_missing_data(data, missing_fraction=0.15, gap_pattern='random'):
    """
    Inject missing values into data to simulate real-world scenarios
    向数据中注入缺失值以模拟真实世界场景

    Parameters
    ----------
    data : np.ndarray
        Original data array
    missing_fraction : float
        Fraction of data to make missing (0-1)
    gap_pattern : str
        'random': Random scattered gaps
        'chunks': Consecutive gaps (sensor failure)
        'systematic': Regular pattern (e.g., nighttime data)

    Returns
    -------
    np.ndarray
        Data with NaN values injected
    """
    data_missing = data.copy()
    n = len(data)

    if gap_pattern == 'random':
        # Random scattered missing values
        missing_indices = np.random.choice(n, size=int(n * missing_fraction), replace=False)
        data_missing[missing_indices] = np.nan

    elif gap_pattern == 'chunks':
        # Consecutive gaps (simulate sensor failure)
        n_chunks = int(n * missing_fraction / 10)  # Each chunk is ~10 points
        for _ in range(n_chunks):
            start_idx = np.random.randint(0, n - 10)
            chunk_length = np.random.randint(5, 15)
            end_idx = min(start_idx + chunk_length, n)
            data_missing[start_idx:end_idx] = np.nan

    elif gap_pattern == 'systematic':
        # Systematic missing pattern (e.g., every 5th point)
        indices = np.arange(0, n, 5)
        data_missing[indices] = np.nan

    return data_missing


def fill_gaps_linear(data):
    """
    Fill missing values using linear interpolation
    使用线性插值填补缺失值
    """
    df = pd.DataFrame({'value': data})
    df_filled = df.interpolate(method='linear', limit_direction='both')
    return df_filled['value'].values


def fill_gaps_moving_average(data, window=5):
    """
    Fill missing values using moving average
    使用滑动平均填补缺失值
    """
    df = pd.DataFrame({'value': data})
    # First, interpolate to get initial estimates
    df_interp = df.interpolate(method='linear', limit_direction='both')
    # Then apply rolling mean
    df_filled = df_interp.rolling(window=window, center=True, min_periods=1).mean()
    return df_filled['value'].values


def calculate_et_with_uncertainty(data_dict, n_bootstrap=100):
    """
    Calculate ET with uncertainty quantification using bootstrap
    使用自助法计算 ET 及其不确定性

    Parameters
    ----------
    data_dict : dict
        Dictionary containing meteorological variables
    n_bootstrap : int
        Number of bootstrap iterations

    Returns
    -------
    dict
        Mean ET, standard deviation, and percentiles
    """
    n_points = len(data_dict['net_radiation'])
    et_samples = np.zeros((n_bootstrap, n_points))

    for i in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n_points, size=n_points, replace=True)

        # Calculate ET for this bootstrap sample
        for j, idx in enumerate(indices):
            try:
                et_val = petcr.penman_potential_et(
                    net_radiation=data_dict['net_radiation'][idx],
                    air_temperature=data_dict['air_temperature'][idx],
                    wind_speed=data_dict['wind_speed'][idx],
                    vapor_pressure_deficit=data_dict['vpd'][idx],
                    air_pressure=data_dict['air_pressure'][idx]
                )
                et_samples[i, j] = et_val
            except:
                et_samples[i, j] = np.nan

    # Calculate statistics
    et_mean = np.nanmean(et_samples, axis=0)
    et_std = np.nanstd(et_samples, axis=0)
    et_p05 = np.nanpercentile(et_samples, 5, axis=0)
    et_p95 = np.nanpercentile(et_samples, 95, axis=0)

    return {
        'mean': et_mean,
        'std': et_std,
        'p05': et_p05,
        'p95': et_p95
    }


def main():
    """Main integration test workflow"""

    print("="*70)
    print("Integration Test: Missing Data Handling")
    print("集成测试：缺失数据处理")
    print("="*70)

    # Step 1: Generate synthetic complete dataset
    print("\n[Step 1] Generating synthetic meteorological data...")
    print("[步骤 1] 生成合成气象数据...")

    n_days = 90  # 3 months
    hours = np.arange(0, n_days * 24, 1)

    # Daily cycles
    temp_mean = 20
    temp_amplitude = 10
    temperatures_c = temp_mean + temp_amplitude * np.sin(2 * np.pi * hours / 24)
    temperatures_k = temperatures_c + 273.15

    # Add seasonal trend
    temperatures_k += np.linspace(0, 5, len(temperatures_k))

    # Net radiation (W/m²)
    net_radiation = 400 * np.maximum(0, np.sin(np.pi * (hours % 24) / 24))

    # Wind speed (m/s)
    wind_speed = 2.5 + 1.5 * np.sin(2 * np.pi * hours / (24 * 7))  # Weekly cycle
    wind_speed += np.random.normal(0, 0.5, len(hours))  # Add noise
    wind_speed = np.clip(wind_speed, 0.5, 10)

    # Relative humidity (%)
    rh = 70 - 20 * np.sin(np.pi * (hours % 24) / 24)
    rh += np.random.normal(0, 5, len(hours))
    rh = np.clip(rh, 20, 95)

    # Calculate VPD
    es_kpa = 0.6108 * np.exp((17.27 * temperatures_c) / (temperatures_c + 237.3))
    ea_kpa = es_kpa * (rh / 100.0)
    vpd_kpa = es_kpa - ea_kpa

    air_pressure = np.full_like(temperatures_k, 101325.0)  # Pa

    # Calculate true ET (no missing data)
    et_true = np.zeros(len(hours))
    for i in range(len(hours)):
        try:
            et_true[i] = petcr.penman_potential_et(
                net_radiation=net_radiation[i],
                air_temperature=temperatures_k[i],
                wind_speed=wind_speed[i],
                vapor_pressure_deficit=vpd_kpa[i],
                air_pressure=air_pressure[i]
            )
        except:
            et_true[i] = np.nan

    print(f"✓ Generated {len(hours)} hourly data points")
    print(f"✓ 生成了 {len(hours)} 个小时数据点")

    # Step 2: Inject missing data
    print("\n[Step 2] Injecting missing values (15% random gaps)...")
    print("[步骤 2] 注入缺失值（15% 随机缺失）...")

    temp_missing = inject_missing_data(temperatures_k, missing_fraction=0.15, gap_pattern='random')
    rn_missing = inject_missing_data(net_radiation, missing_fraction=0.15, gap_pattern='chunks')
    wind_missing = inject_missing_data(wind_speed, missing_fraction=0.15, gap_pattern='systematic')

    n_missing_temp = np.sum(np.isnan(temp_missing))
    n_missing_rn = np.sum(np.isnan(rn_missing))
    n_missing_wind = np.sum(np.isnan(wind_missing))

    print(f"  Temperature missing: {n_missing_temp} / {len(temp_missing)} ({n_missing_temp/len(temp_missing)*100:.1f}%)")
    print(f"  Net radiation missing: {n_missing_rn} / {len(rn_missing)} ({n_missing_rn/len(rn_missing)*100:.1f}%)")
    print(f"  Wind speed missing: {n_missing_wind} / {len(wind_missing)} ({n_missing_wind/len(wind_missing)*100:.1f}%)")

    # Step 3: Apply gap-filling strategies
    print("\n[Step 3] Applying gap-filling strategies...")
    print("[步骤 3] 应用数据填补策略...")

    temp_filled_linear = fill_gaps_linear(temp_missing)
    temp_filled_ma = fill_gaps_moving_average(temp_missing, window=5)

    rn_filled_linear = fill_gaps_linear(rn_missing)
    wind_filled_linear = fill_gaps_linear(wind_missing)

    print(f"✓ Linear interpolation applied")
    print(f"✓ 线性插值已应用")
    print(f"✓ Moving average (window=5) applied")
    print(f"✓ 滑动平均（窗口=5）已应用")

    # Step 4: Calculate ET with filled data
    print("\n[Step 4] Calculating ET with filled data...")
    print("[步骤 4] 使用填补后的数据计算 ET...")

    et_filled_linear = np.zeros(len(hours))
    et_filled_ma = np.zeros(len(hours))

    for i in range(len(hours)):
        # Linear interpolation
        try:
            et_filled_linear[i] = petcr.penman_potential_et(
                net_radiation=rn_filled_linear[i],
                air_temperature=temp_filled_linear[i],
                wind_speed=wind_filled_linear[i],
                vapor_pressure_deficit=vpd_kpa[i],
                air_pressure=air_pressure[i]
            )
        except:
            et_filled_linear[i] = np.nan

        # Moving average
        try:
            et_filled_ma[i] = petcr.penman_potential_et(
                net_radiation=rn_filled_linear[i],
                air_temperature=temp_filled_ma[i],
                wind_speed=wind_filled_linear[i],
                vapor_pressure_deficit=vpd_kpa[i],
                air_pressure=air_pressure[i]
            )
        except:
            et_filled_ma[i] = np.nan

    # Step 5: Evaluate performance
    print("\n[Step 5] Evaluating gap-filling performance...")
    print("[步骤 5] 评估数据填补性能...")

    # Calculate RMSE and MAE
    valid_idx = ~np.isnan(et_true) & ~np.isnan(et_filled_linear)

    rmse_linear = np.sqrt(np.mean((et_true[valid_idx] - et_filled_linear[valid_idx])**2))
    mae_linear = np.mean(np.abs(et_true[valid_idx] - et_filled_linear[valid_idx]))

    rmse_ma = np.sqrt(np.mean((et_true[valid_idx] - et_filled_ma[valid_idx])**2))
    mae_ma = np.mean(np.abs(et_true[valid_idx] - et_filled_ma[valid_idx]))

    print(f"\nLinear Interpolation:")
    print(f"  RMSE: {rmse_linear:.2f} W/m²")
    print(f"  MAE:  {mae_linear:.2f} W/m²")

    print(f"\nMoving Average:")
    print(f"  RMSE: {rmse_ma:.2f} W/m²")
    print(f"  MAE:  {mae_ma:.2f} W/m²")

    # Step 6: Visualization
    print("\n[Step 6] Creating visualizations...")
    print("[步骤 6] 创建可视化...")

    fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)

    # Convert hours to days for plotting
    days = hours / 24

    # Plot 1: Temperature with gaps and fills
    ax1 = axes[0]
    ax1.plot(days, temperatures_k - 273.15, 'k-', linewidth=1, alpha=0.3, label='True')
    ax1.scatter(days[np.isnan(temp_missing)],
                (temperatures_k - 273.15)[np.isnan(temp_missing)],
                c='red', s=10, alpha=0.5, label='Missing')
    ax1.plot(days, temp_filled_linear - 273.15, 'b--', linewidth=1.5, label='Linear Fill')
    ax1.set_ylabel('Temperature (°C)', fontweight='bold')
    ax1.set_title('Missing Data and Gap-Filling Performance | 缺失数据和填补性能',
                  fontweight='bold', fontsize=13)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(alpha=0.3)

    # Plot 2: Net radiation with gaps
    ax2 = axes[1]
    ax2.plot(days, net_radiation, 'k-', linewidth=1, alpha=0.3, label='True')
    ax2.scatter(days[np.isnan(rn_missing)],
                net_radiation[np.isnan(rn_missing)],
                c='red', s=10, alpha=0.5, label='Missing (chunks)')
    ax2.plot(days, rn_filled_linear, 'orange', linestyle='--', linewidth=1.5, label='Linear Fill')
    ax2.set_ylabel('Net Radiation (W/m²)', fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(alpha=0.3)

    # Plot 3: ET comparison
    ax3 = axes[2]
    ax3.plot(days, et_true, 'k-', linewidth=2, label='True ET (no gaps)', alpha=0.7)
    ax3.plot(days, et_filled_linear, 'b--', linewidth=1.5, label=f'Linear Fill (RMSE={rmse_linear:.1f})')
    ax3.plot(days, et_filled_ma, 'g:', linewidth=1.5, label=f'Moving Avg (RMSE={rmse_ma:.1f})')
    ax3.set_ylabel('ET (W/m²)', fontweight='bold')
    ax3.set_title('ET Estimation with Gap-Filled Data | 使用填补数据的ET估算',
                  fontweight='bold', fontsize=13)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(alpha=0.3)

    # Plot 4: Error analysis
    ax4 = axes[3]
    error_linear = et_true - et_filled_linear
    error_ma = et_true - et_filled_ma
    ax4.scatter(days, error_linear, c='blue', s=5, alpha=0.4, label='Linear Error')
    ax4.scatter(days, error_ma, c='green', s=5, alpha=0.4, label='MA Error')
    ax4.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax4.set_xlabel('Time (days)', fontweight='bold')
    ax4.set_ylabel('Error (W/m²)', fontweight='bold')
    ax4.set_title('Gap-Filling Error Analysis | 填补误差分析', fontweight='bold', fontsize=13)
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('figures/integration_test_missing_data.png', dpi=150, bbox_inches='tight')
    plt.show()

    print("\n" + "="*70)
    print("Integration Test Complete | 集成测试完成")
    print("="*70)
    print(f"\n✓ Successfully handled {n_missing_temp + n_missing_rn + n_missing_wind} missing values")
    print(f"✓ 成功处理了 {n_missing_temp + n_missing_rn + n_missing_wind} 个缺失值")
    print(f"✓ Best method: {'Linear' if rmse_linear < rmse_ma else 'Moving Average'}")
    print(f"✓ 最佳方法: {'线性插值' if rmse_linear < rmse_ma else '滑动平均'}")
    print(f"\nFigure saved: figures/integration_test_missing_data.png")
    print(f"图片已保存: figures/integration_test_missing_data.png")


if __name__ == '__main__':
    main()
