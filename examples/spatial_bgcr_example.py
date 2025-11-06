#!/usr/bin/env python
"""
Xarray-Based Gridded Spatial Analysis Example for BGCR Model
=============================================================

This example demonstrates how to use the PET-CR library with xarray for
spatial (gridded) evapotranspiration estimation using the BGCR-Budyko model.

The script:
1. Simulates realistic monthly gridded meteorological data (50x50 grid, 12 months)
2. Computes BGCR ET with proper broadcasting across spatial and temporal dimensions
3. Visualizes annual mean ET as a spatial map using cartopy

Requirements:
- xarray
- numpy
- matplotlib

Author: PET-CR Contributors
Date: 2025
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path if running as script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from petcr import calculate_bgcr_et
from petcr.constants import DAYS_PER_MONTH_AVG

# ============================================================================
# Configuration / 配置
# ============================================================================

# Spatial grid configuration / 空间网格配置
NLAT = 50  # Number of latitude points / 纬度点数
NLON = 50  # Number of longitude points / 经度点数
NMONTH = 12  # Number of months / 月数

# Spatial domain / 空间范围
LAT_MIN, LAT_MAX = 30.0, 50.0  # Degrees N / 北纬度数
LON_MIN, LON_MAX = -120.0, -90.0  # Degrees E / 东经度数

# Random seed for reproducibility / 随机种子以保证可重复性
np.random.seed(42)

# Output figure path / 输出图像路径
OUTPUT_FIG = Path(__file__).parent / 'figures' / 'spatial_bgcr_example.png'
OUTPUT_FIG.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Generate Synthetic Spatial Data / 生成合成空间数据
# ============================================================================

def generate_spatial_meteorological_data():
    """
    Generate synthetic gridded meteorological data for demonstration.
    
    生成用于演示的合成网格气象数据。
    
    Returns
    -------
    xr.Dataset
        Dataset containing all required meteorological variables
        包含所有所需气象变量的数据集
    """
    print("Generating synthetic spatial meteorological data...")
    print("生成合成空间气象数据...")
    
    # Create coordinate arrays / 创建坐标数组
    lat = np.linspace(LAT_MIN, LAT_MAX, NLAT)
    lon = np.linspace(LON_MIN, LON_MAX, NLON)
    month = np.arange(1, NMONTH + 1)
    
    # Create 2D meshgrid for spatial patterns / 创建2D网格用于空间模式
    lon_2d, lat_2d = np.meshgrid(lon, lat)
    
    # ========================================================================
    # Simulate spatial patterns / 模拟空间模式
    # ========================================================================
    
    # Elevation effect (increases with latitude) / 海拔效应（随纬度增加）
    elevation_factor = (lat_2d - LAT_MIN) / (LAT_MAX - LAT_MIN)
    
    # Distance from coast effect (increases with longitude) / 离海岸距离效应（随经度增加）
    continentality_factor = (lon_2d - LON_MIN) / (LON_MAX - LON_MIN)
    
    # ========================================================================
    # Generate time-varying variables (12 months) / 生成时变变量（12个月）
    # ========================================================================
    
    # Net radiation [W/m²] - seasonal cycle / 净辐射 [W/m²] - 季节循环
    # Higher in summer (June-August, months 6-8), lower in winter
    seasonal_cycle = np.sin(2 * np.pi * (month - 3) / 12)  # Peak in June
    net_radiation_base = 200.0 + 150.0 * seasonal_cycle[None, None, :]
    spatial_variation = 50.0 * (1.0 - elevation_factor[:, :, None])
    net_radiation = net_radiation_base + spatial_variation + np.random.normal(0, 10, (NLAT, NLON, NMONTH))
    net_radiation = np.maximum(net_radiation, 50.0)  # Ensure positive
    
    # Temperature [°C] - seasonal and spatial variation / 温度 [°C] - 季节和空间变化
    temp_base = 15.0 + 10.0 * seasonal_cycle[None, None, :]
    temp_spatial = -10.0 * elevation_factor[:, :, None]  # Cooler at higher latitudes
    temp_spatial += 5.0 * continentality_factor[:, :, None]  # Warmer inland
    temperature = temp_base + temp_spatial + np.random.normal(0, 2, (NLAT, NLON, NMONTH))
    
    # Wind speed [m/s] - generally higher in winter and coastal areas / 风速 [m/s]
    wind_base = 3.0 - 1.0 * seasonal_cycle[None, None, :]  # Higher in winter
    wind_spatial = 2.0 * (1.0 - continentality_factor[:, :, None])  # Higher near coast
    wind_speed = wind_base + wind_spatial + np.random.normal(0, 0.5, (NLAT, NLON, NMONTH))
    wind_speed = np.maximum(wind_speed, 0.5)  # Ensure positive and reasonable minimum
    
    # Vapor pressure [kPa] - depends on temperature / 水汽压 [kPa] - 依赖于温度
    # Actual vapor pressure (approximately 60-80% of saturation)
    es_approx = 0.611 * np.exp(17.27 * temperature / (temperature + 237.3))
    actual_vapor_pressure = es_approx * (0.6 + 0.2 * np.random.random((NLAT, NLON, NMONTH)))
    saturation_vapor_pressure = es_approx
    
    # Precipitation [mm/month] - higher in summer and near coast / 降水 [mm/月]
    precip_base = 80.0 + 40.0 * seasonal_cycle[None, None, :]
    precip_spatial = 30.0 * (1.0 - continentality_factor[:, :, None])
    precipitation = precip_base + precip_spatial + np.random.gamma(2, 10, (NLAT, NLON, NMONTH))
    precipitation = np.maximum(precipitation, 1.0)
    
    # ========================================================================
    # Generate static spatial variables / 生成静态空间变量
    # ========================================================================
    
    # Surface albedo [0-1] - varies with land cover / 地表反照率 [0-1]
    # Lower near coast (vegetation), higher inland (drier)
    albedo = 0.15 + 0.15 * continentality_factor
    albedo += np.random.normal(0, 0.02, (NLAT, NLON))
    albedo = np.clip(albedo, 0.1, 0.4)
    
    # Compute seasonality index from precipitation / 从降水计算季节性指数
    # SI = (1/Pa) × Σ|Pi - Pa/12|
    P_annual = np.sum(precipitation, axis=2)
    P_mean_month = P_annual[:, :, None] / 12.0
    SI_sum = np.sum(np.abs(precipitation - P_mean_month), axis=2)
    seasonality_index = SI_sum / P_annual
    seasonality_index = np.clip(seasonality_index, 0.0, 2.0)
    
    # ========================================================================
    # Create xarray Dataset / 创建xarray数据集
    # ========================================================================
    
    ds = xr.Dataset(
        {
            # Time-varying 3D variables (lat, lon, month)
            'net_radiation': (['lat', 'lon', 'month'], net_radiation,
                            {'units': 'W/m²', 'long_name': 'Net radiation'}),
            'temperature': (['lat', 'lon', 'month'], temperature,
                          {'units': '°C', 'long_name': 'Air temperature'}),
            'wind_speed': (['lat', 'lon', 'month'], wind_speed,
                         {'units': 'm/s', 'long_name': 'Wind speed at 2m'}),
            'actual_vapor_pressure': (['lat', 'lon', 'month'], actual_vapor_pressure,
                                    {'units': 'kPa', 'long_name': 'Actual vapor pressure'}),
            'saturation_vapor_pressure': (['lat', 'lon', 'month'], saturation_vapor_pressure,
                                        {'units': 'kPa', 'long_name': 'Saturation vapor pressure'}),
            'precipitation': (['lat', 'lon', 'month'], precipitation,
                            {'units': 'mm/month', 'long_name': 'Monthly precipitation'}),
            
            # Static 2D variables (lat, lon)
            'albedo': (['lat', 'lon'], albedo,
                     {'units': 'dimensionless', 'long_name': 'Surface albedo'}),
            'seasonality_index': (['lat', 'lon'], seasonality_index,
                                {'units': 'dimensionless', 'long_name': 'Precipitation seasonality index'}),
        },
        coords={
            'lat': (['lat'], lat, {'units': 'degrees_north', 'long_name': 'Latitude'}),
            'lon': (['lon'], lon, {'units': 'degrees_east', 'long_name': 'Longitude'}),
            'month': (['month'], month, {'units': '1', 'long_name': 'Month of year'}),
        },
        attrs={
            'title': 'Synthetic gridded meteorological data for BGCR example',
            'description': 'Simulated data with realistic spatial and temporal patterns',
            'grid_size': f'{NLAT}x{NLON}',
            'time_steps': NMONTH,
        }
    )
    
    print(f"✓ Generated data: {NLAT}x{NLON} grid, {NMONTH} months")
    print(f"✓ 生成数据：{NLAT}x{NLON} 网格，{NMONTH} 个月")
    
    return ds


# ============================================================================
# Compute BGCR ET / 计算 BGCR 蒸散发
# ============================================================================

def compute_bgcr_et_spatial(ds):
    """
    Compute BGCR evapotranspiration for the entire spatial grid.
    
    为整个空间网格计算 BGCR 蒸散发。
    
    Parameters
    ----------
    ds : xr.Dataset
        Input meteorological dataset
        输入气象数据集
    
    Returns
    -------
    xr.Dataset
        Dataset with added BGCR ET variables
        添加了 BGCR ET 变量的数据集
    """
    print("\nComputing BGCR ET for spatial grid...")
    print("为空间网格计算 BGCR ET...")
    
    # Create array of days in each month for proper conversion
    # 为适当的转换创建每月天数数组
    days_in_months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    
    # Extract variables from dataset / 从数据集中提取变量
    net_radiation = ds['net_radiation'].values
    temperature = ds['temperature'].values
    wind_speed = ds['wind_speed'].values
    actual_vapor_pressure = ds['actual_vapor_pressure'].values
    saturation_vapor_pressure = ds['saturation_vapor_pressure'].values
    precipitation = ds['precipitation'].values
    seasonality_index = ds['seasonality_index'].values
    albedo = ds['albedo'].values
    
    # Prepare days_in_month for broadcasting (1, 1, 12)
    # 准备 days_in_month 以进行广播 (1, 1, 12)
    days_array = days_in_months[None, None, :]
    
    # Broadcast spatial variables to match temporal dimension
    # 广播空间变量以匹配时间维度
    # seasonality_index and albedo are (50, 50), need to become (50, 50, 12) or keep (50, 50)
    # The calculate_bgcr_et function should handle this internally by broadcasting
    # But we need to ensure they have compatible shapes
    
    # Call calculate_bgcr_et with spatial arrays
    # xarray broadcasting handles the spatial and temporal dimensions
    # 使用空间数组调用 calculate_bgcr_et
    # xarray 广播处理空间和时间维度
    print(f"  Processing {NLAT * NLON * NMONTH:,} grid points...")
    print(f"  处理 {NLAT * NLON * NMONTH:,} 个网格点...")
    
    results = calculate_bgcr_et(
        net_radiation=net_radiation,
        temperature=temperature,
        wind_speed=wind_speed,
        actual_vapor_pressure=actual_vapor_pressure,
        saturation_vapor_pressure=saturation_vapor_pressure,
        precipitation=precipitation,
        seasonality_index=seasonality_index,
        albedo=albedo,
        ground_heat_flux=0.0,  # Assume negligible for monthly averages
        use_dual_scheme=True,  # Use dual-variable (SI + albedo) scheme
        days_in_month=days_array  # Use actual month lengths
    )
    
    # Add results to dataset / 将结果添加到数据集
    ds['et'] = (['lat', 'lon', 'month'], results['et'],
                {'units': 'mm/month', 'long_name': 'Actual evapotranspiration (BGCR)'})
    ds['epa'] = (['lat', 'lon', 'month'], results['epa'],
                 {'units': 'mm/month', 'long_name': 'Apparent potential evaporation'})
    
    # w_parameter might be 2D or 3D depending on input, extract 2D version
    # w_parameter 可能是2D或3D，取决于输入，提取2D版本
    w_result = results['w']
    if w_result.ndim == 3:
        w_2d = w_result[:, :, 0]  # Take first month (same for all)
    else:
        w_2d = w_result
    ds['w_parameter'] = (['lat', 'lon'], w_2d,
                        {'units': 'dimensionless', 'long_name': 'Budyko parameter'})
    
    ds['beta_c'] = (['lat', 'lon', 'month'], results['beta_c'],
                    {'units': 'dimensionless', 'long_name': 'Complementary coefficient'})
    
    # Compute annual totals and means / 计算年总量和平均值
    ds['et_annual'] = ds['et'].sum(dim='month')
    ds['et_annual'].attrs = {'units': 'mm/year', 'long_name': 'Annual evapotranspiration'}
    
    ds['precip_annual'] = ds['precipitation'].sum(dim='month')
    ds['precip_annual'].attrs = {'units': 'mm/year', 'long_name': 'Annual precipitation'}
    
    # Compute evaporative index (ET/P) / 计算蒸发指数 (ET/P)
    ds['evaporative_index'] = ds['et_annual'] / ds['precip_annual']
    ds['evaporative_index'].attrs = {'units': 'dimensionless', 'long_name': 'Evaporative index (ET/P)'}
    
    print("✓ BGCR ET computation complete")
    print("✓ BGCR ET 计算完成")
    
    # Print summary statistics / 打印汇总统计
    print(f"\nSummary Statistics / 汇总统计:")
    print(f"  Annual ET:  mean = {ds['et_annual'].mean().values:.1f} mm, "
          f"std = {ds['et_annual'].std().values:.1f} mm")
    print(f"  Annual P:   mean = {ds['precip_annual'].mean().values:.1f} mm, "
          f"std = {ds['precip_annual'].std().values:.1f} mm")
    print(f"  ET/P ratio: mean = {ds['evaporative_index'].mean().values:.2f}, "
          f"std = {ds['evaporative_index'].std().values:.2f}")
    
    return ds


# ============================================================================
# Visualization / 可视化
# ============================================================================

def plot_spatial_results(ds, output_path):
    """
    Create spatial visualization of BGCR ET results.
    
    创建 BGCR ET 结果的空间可视化。
    
    Parameters
    ----------
    ds : xr.Dataset
        Dataset with BGCR ET results
        包含 BGCR ET 结果的数据集
    output_path : Path
        Path to save the output figure
        保存输出图像的路径
    """
    print(f"\nCreating spatial visualization...")
    print(f"创建空间可视化...")
    
    # Create figure with subplots / 创建带子图的图形
    fig = plt.figure(figsize=(16, 10))
    
    # Use simple axes without cartopy projection to avoid requiring downloads
    # 使用简单的坐标轴而不是cart opy投影以避免需要下载
    # (cartopy requires downloading geographic data which may not be available)
    
    # ========================================================================
    # Panel 1: Annual ET / 年 ET
    # ========================================================================
    ax1 = fig.add_subplot(2, 3, 1)
    im1 = ax1.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['et_annual'].values,
        levels=15,
        cmap='YlGnBu',
        vmin=0,
        vmax=800
    )
    ax1.set_xlabel('Longitude (°E)')
    ax1.set_ylabel('Latitude (°N)')
    ax1.set_title('(a) Annual ET (mm/year)', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    cbar1 = plt.colorbar(im1, ax=ax1, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar1.set_label('mm/year', fontsize=10)
    
    # ========================================================================
    # Panel 2: Annual Precipitation / 年降水
    # ========================================================================
    ax2 = fig.add_subplot(2, 3, 2)
    im2 = ax2.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['precip_annual'].values,
        levels=15,
        cmap='Blues',
        vmin=1000,
        vmax=1600
    )
    ax2.set_xlabel('Longitude (°E)')
    ax2.set_ylabel('Latitude (°N)')
    ax2.set_title('(b) Annual Precipitation (mm/year)', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    cbar2 = plt.colorbar(im2, ax=ax2, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar2.set_label('mm/year', fontsize=10)
    
    # ========================================================================
    # Panel 3: Evaporative Index (ET/P) / 蒸发指数 (ET/P)
    # ========================================================================
    ax3 = fig.add_subplot(2, 3, 3)
    im3 = ax3.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['evaporative_index'].values,
        levels=15,
        cmap='RdYlGn_r',
        vmin=0.0,
        vmax=0.6
    )
    ax3.set_xlabel('Longitude (°E)')
    ax3.set_ylabel('Latitude (°N)')
    ax3.set_title('(c) Evaporative Index (ET/P)', fontsize=12, fontweight='bold')
    ax3.grid(True, linestyle=':', alpha=0.5)
    cbar3 = plt.colorbar(im3, ax=ax3, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar3.set_label('dimensionless', fontsize=10)
    
    # ========================================================================
    # Panel 4: Budyko Parameter (w) / Budyko 参数 (w)
    # ========================================================================
    ax4 = fig.add_subplot(2, 3, 4)
    im4 = ax4.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['w_parameter'].values,
        levels=15,
        cmap='viridis',
        vmin=1.5,
        vmax=2.5
    )
    ax4.set_xlabel('Longitude (°E)')
    ax4.set_ylabel('Latitude (°N)')
    ax4.set_title('(d) Budyko Parameter (w)', fontsize=12, fontweight='bold')
    ax4.grid(True, linestyle=':', alpha=0.5)
    cbar4 = plt.colorbar(im4, ax=ax4, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar4.set_label('dimensionless', fontsize=10)
    
    # ========================================================================
    # Panel 5: Seasonality Index / 季节性指数
    # ========================================================================
    ax5 = fig.add_subplot(2, 3, 5)
    im5 = ax5.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['seasonality_index'].values,
        levels=15,
        cmap='plasma',
        vmin=0.2,
        vmax=0.8
    )
    ax5.set_xlabel('Longitude (°E)')
    ax5.set_ylabel('Latitude (°N)')
    ax5.set_title('(e) Seasonality Index', fontsize=12, fontweight='bold')
    ax5.grid(True, linestyle=':', alpha=0.5)
    cbar5 = plt.colorbar(im5, ax=ax5, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar5.set_label('dimensionless', fontsize=10)
    
    # ========================================================================
    # Panel 6: Surface Albedo / 地表反照率
    # ========================================================================
    ax6 = fig.add_subplot(2, 3, 6)
    im6 = ax6.contourf(
        ds['lon'].values,
        ds['lat'].values,
        ds['albedo'].values,
        levels=15,
        cmap='gray_r',
        vmin=0.1,
        vmax=0.4
    )
    ax6.set_xlabel('Longitude (°E)')
    ax6.set_ylabel('Latitude (°N)')
    ax6.set_title('(f) Surface Albedo', fontsize=12, fontweight='bold')
    ax6.grid(True, linestyle=':', alpha=0.5)
    cbar6 = plt.colorbar(im6, ax=ax6, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar6.set_label('dimensionless', fontsize=10)
    
    # ========================================================================
    # Add overall title / 添加总标题
    # ========================================================================
    fig.suptitle(
        'Spatial BGCR Evapotranspiration Analysis\nXarray-Based Gridded Computation',
        fontsize=16,
        fontweight='bold',
        y=0.98
    )
    
    # Add description / 添加描述
    fig.text(
        0.5, 0.02,
        f'Synthetic data: {NLAT}×{NLON} grid, 12 months | '
        f'Model: BGCR-Budyko (dual-variable scheme with SI and albedo)',
        ha='center',
        fontsize=10,
        style='italic'
    )
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
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
    Main function to run the spatial BGCR example.
    
    运行空间 BGCR 示例的主函数。
    """
    print("="*70)
    print("Spatial BGCR Evapotranspiration Analysis")
    print("空间 BGCR 蒸散发分析")
    print("="*70)
    
    # Step 1: Generate synthetic data / 步骤1：生成合成数据
    ds = generate_spatial_meteorological_data()
    
    # Step 2: Compute BGCR ET / 步骤2：计算 BGCR ET
    ds = compute_bgcr_et_spatial(ds)
    
    # Step 3: Visualize results / 步骤3：可视化结果
    plot_spatial_results(ds, OUTPUT_FIG)
    
    print("\n" + "="*70)
    print("✓ Analysis complete! / 分析完成！")
    print("="*70)
    
    return ds


if __name__ == '__main__':
    main()
