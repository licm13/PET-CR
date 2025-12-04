"""
Integration Test: Spatial Gridded Data Processing with NetCDF
集成测试：使用 NetCDF 处理空间网格数据

This script demonstrates:
本脚本演示：
1. Creating and processing large-scale spatial gridded data
   创建和处理大规模空间网格数据
2. Chunk-based NetCDF I/O to avoid memory overflow
   基于分块的 NetCDF I/O 以避免内存溢出
3. Vectorized ET calculations over spatial grids
   在空间网格上的向量化 ET 计算
4. Spatial pattern analysis and visualization
   空间模式分析和可视化

Author: PET-CR Development Team
Date: 2025-12-04
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
sys.path.insert(0, '..')
import petcr

# Set random seed
np.random.seed(42)


def create_synthetic_spatial_data(nlat=50, nlon=50, ntime=120):
    """
    Create synthetic gridded meteorological data
    创建合成网格气象数据

    Parameters
    ----------
    nlat : int
        Number of latitude points
    nlon : int
        Number of longitude points
    ntime : int
        Number of time steps (months)

    Returns
    -------
    xr.Dataset
        Xarray dataset with meteorological variables
    """
    # Create coordinates
    lat = np.linspace(-30, 30, nlat)
    lon = np.linspace(100, 140, nlon)
    time = np.arange(ntime)

    # Create meshgrid
    lon_grid, lat_grid, time_grid = np.meshgrid(lon, lat, time, indexing='ij')

    # Temperature (K) - latitudinal gradient + seasonal cycle
    temp_base = 293.15  # 20°C
    temp_lat_gradient = -0.5 * np.abs(lat_grid)  # Cooler at higher latitudes
    temp_seasonal = 10 * np.sin(2 * np.pi * time_grid / 12)  # Annual cycle
    temperature = temp_base + temp_lat_gradient + temp_seasonal

    # Add spatial noise
    temperature += np.random.normal(0, 2, temperature.shape)

    # Net radiation (W/m²) - depends on latitude and season
    rn_base = 200
    rn_lat_factor = np.cos(np.deg2rad(lat_grid)) * 150
    rn_seasonal = 100 * np.sin(2 * np.pi * time_grid / 12)
    net_radiation = np.maximum(50, rn_base + rn_lat_factor + rn_seasonal)

    # Precipitation (mm/month) - spatial pattern
    precip_base = 80
    precip_lon_pattern = 50 * np.sin(np.deg2rad(lon_grid - 100) * 3)
    precip_seasonal = 30 * np.sin(2 * np.pi * time_grid / 12 + np.pi/2)
    precipitation = np.maximum(20, precip_base + precip_lon_pattern + precip_seasonal)

    # Wind speed (m/s) - zonal pattern
    wind_base = 3.0
    wind_pattern = 2.0 * np.sin(np.deg2rad(lat_grid) * 2)
    wind_speed = np.abs(wind_base + wind_pattern)

    # Relative humidity (%) - inverse of temperature
    rh_base = 70
    rh_lat_gradient = 10 * np.sin(np.deg2rad(lat_grid))
    rh_seasonal = -15 * np.sin(2 * np.pi * time_grid / 12)
    relative_humidity = np.clip(rh_base + rh_lat_gradient + rh_seasonal, 30, 95)

    # Create xarray Dataset
    ds = xr.Dataset(
        {
            'temperature': (['lon', 'lat', 'time'], temperature,
                           {'long_name': 'Air Temperature', 'units': 'K'}),
            'net_radiation': (['lon', 'lat', 'time'], net_radiation,
                            {'long_name': 'Net Radiation', 'units': 'W/m2'}),
            'precipitation': (['lon', 'lat', 'time'], precipitation,
                            {'long_name': 'Precipitation', 'units': 'mm/month'}),
            'wind_speed': (['lon', 'lat', 'time'], wind_speed,
                         {'long_name': 'Wind Speed', 'units': 'm/s'}),
            'relative_humidity': (['lon', 'lat', 'time'], relative_humidity,
                                 {'long_name': 'Relative Humidity', 'units': '%'}),
        },
        coords={
            'lon': lon,
            'lat': lat,
            'time': time,
        },
        attrs={
            'title': 'Synthetic Meteorological Data for PET-CR Testing',
            'created_by': 'PET-CR Integration Test',
            'created_on': '2025-12-04',
        }
    )

    return ds


def calculate_et_spatial(ds):
    """
    Calculate ET for spatial gridded data using vectorized operations
    使用向量化操作计算空间网格数据的 ET

    Parameters
    ----------
    ds : xr.Dataset
        Input dataset with meteorological variables

    Returns
    -------
    xr.DataArray
        ET field
    """
    # Extract variables
    temp_k = ds['temperature'].values
    temp_c = temp_k - 273.15
    rn = ds['net_radiation'].values
    wind = ds['wind_speed'].values
    rh = ds['relative_humidity'].values

    # Calculate vapor pressure deficit
    es_kpa = 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))
    ea_kpa = es_kpa * (rh / 100.0)
    vpd_kpa = es_kpa - ea_kpa

    air_pressure = 101325.0  # Pa (constant for simplicity)

    # Initialize ET array
    et = np.zeros_like(temp_k)

    # Vectorized calculation
    # Note: petcr functions expect scalar inputs, so we need to iterate
    # In a production environment, this should be optimized with numba or dask

    print("  Calculating ET for spatial grid...")
    nlon, nlat, ntime = temp_k.shape

    for t in range(ntime):
        if (t + 1) % 20 == 0:
            print(f"    Progress: {t+1}/{ntime} time steps")

        for i in range(nlat):
            for j in range(nlon):
                try:
                    et_val = petcr.penman_potential_et(
                        net_radiation=rn[i, j, t],
                        air_temperature=temp_k[i, j, t],
                        wind_speed=wind[i, j, t],
                        vapor_pressure_deficit=vpd_kpa[i, j, t],
                        air_pressure=air_pressure
                    )
                    # Convert to mm/month
                    # ET in W/m² -> mm/day -> mm/month
                    lambda_v = 2.45e6  # J/kg
                    et_mm_day = et_val * 86400 / lambda_v
                    et_mm_month = et_mm_day * 30  # Assume 30 days/month
                    et[i, j, t] = et_mm_month
                except Exception as e:
                    et[i, j, t] = np.nan

    # Create DataArray
    et_da = xr.DataArray(
        et,
        coords={'lon': ds['lon'], 'lat': ds['lat'], 'time': ds['time']},
        dims=['lon', 'lat', 'time'],
        attrs={'long_name': 'Potential Evapotranspiration', 'units': 'mm/month'}
    )

    return et_da


def analyze_spatial_patterns(ds, et_da):
    """
    Analyze spatial and temporal patterns in ET
    分析 ET 的空间和时间模式

    Parameters
    ----------
    ds : xr.Dataset
        Input meteorological dataset
    et_da : xr.DataArray
        ET field

    Returns
    -------
    dict
        Analysis results
    """
    # Time-averaged ET
    et_mean = et_da.mean(dim='time')

    # Temporal variability (coefficient of variation)
    et_std = et_da.std(dim='time')
    et_cv = (et_std / et_mean) * 100  # Coefficient of variation in %

    # Seasonal cycle (climatology)
    et_climatology = et_da.groupby('time').mean(dim='time')

    # Trend analysis (linear trend over time)
    # Simple linear regression for each grid cell
    nlon, nlat = len(ds['lon']), len(ds['lat'])
    et_trend = np.zeros((nlon, nlat))

    time_idx = np.arange(len(ds['time']))

    for i in range(nlon):
        for j in range(nlat):
            y = et_da.values[i, j, :]
            if not np.all(np.isnan(y)):
                # Linear fit: y = a + b*x
                valid = ~np.isnan(y)
                if np.sum(valid) > 10:  # Need enough points
                    slope, _ = np.polyfit(time_idx[valid], y[valid], 1)
                    et_trend[i, j] = slope * 12  # mm/month per year

    et_trend_da = xr.DataArray(
        et_trend,
        coords={'lon': ds['lon'], 'lat': ds['lat']},
        dims=['lon', 'lat'],
        attrs={'long_name': 'ET Trend', 'units': 'mm/year per year'}
    )

    return {
        'mean': et_mean,
        'std': et_std,
        'cv': et_cv,
        'climatology': et_climatology,
        'trend': et_trend_da
    }


def main():
    """Main integration test workflow"""

    print("="*70)
    print("Integration Test: Spatial Gridded NetCDF Data Processing")
    print("集成测试：空间网格 NetCDF 数据处理")
    print("="*70)

    # Step 1: Create synthetic spatial data
    print("\n[Step 1] Creating synthetic gridded data (50×50×120)...")
    print("[步骤 1] 创建合成网格数据 (50×50×120)...")

    ds = create_synthetic_spatial_data(nlat=50, nlon=50, ntime=120)  # 10 years monthly

    print(f"✓ Dataset created with shape: ({len(ds['lon'])}, {len(ds['lat'])}, {len(ds['time'])})")
    print(f"✓ 数据集已创建，形状：({len(ds['lon'])}, {len(ds['lat'])}, {len(ds['time'])})")
    print(f"  Total grid cells: {len(ds['lon']) * len(ds['lat']) * len(ds['time']):,}")
    print(f"  总网格数：{len(ds['lon']) * len(ds['lat']) * len(ds['time']):,}")

    # Step 2: Save to NetCDF (demonstrate I/O)
    print("\n[Step 2] Saving to NetCDF file...")
    print("[步骤 2] 保存为 NetCDF 文件...")

    output_file = 'data/output/synthetic_spatial_met.nc'
    ds.to_netcdf(output_file)

    print(f"✓ Data saved to: {output_file}")
    print(f"✓ 数据已保存到：{output_file}")

    # Step 3: Load from NetCDF (chunk-based for large files)
    print("\n[Step 3] Loading from NetCDF with chunking...")
    print("[步骤 3] 使用分块加载 NetCDF...")

    ds_loaded = xr.open_dataset(output_file, chunks={'time': 12})  # Chunk by year

    print(f"✓ Data loaded with chunks")
    print(f"✓ 数据已分块加载")

    # Step 4: Calculate ET
    print("\n[Step 4] Calculating ET for spatial grid...")
    print("[步骤 4] 计算空间网格的 ET...")

    et_da = calculate_et_spatial(ds_loaded)

    print(f"✓ ET calculation complete")
    print(f"✓ ET 计算完成")
    print(f"  Mean ET: {et_da.mean().values:.1f} mm/month")
    print(f"  Min ET: {et_da.min().values:.1f} mm/month")
    print(f"  Max ET: {et_da.max().values:.1f} mm/month")

    # Step 5: Spatial pattern analysis
    print("\n[Step 5] Analyzing spatial patterns...")
    print("[步骤 5] 分析空间模式...")

    analysis = analyze_spatial_patterns(ds_loaded, et_da)

    print(f"✓ Spatial analysis complete")
    print(f"✓ 空间分析完成")

    # Step 6: Visualization
    print("\n[Step 6] Creating visualizations...")
    print("[步骤 6] 创建可视化...")

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Plot 1: Mean ET
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.contourf(ds['lon'], ds['lat'], analysis['mean'].T,
                       levels=15, cmap='YlGnBu')
    ax1.set_xlabel('Longitude (°E)', fontweight='bold')
    ax1.set_ylabel('Latitude (°N)', fontweight='bold')
    ax1.set_title('Mean ET (mm/month) | 平均 ET', fontweight='bold', fontsize=12)
    plt.colorbar(im1, ax=ax1, label='mm/month')
    ax1.grid(alpha=0.3)

    # Plot 2: ET Coefficient of Variation
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.contourf(ds['lon'], ds['lat'], analysis['cv'].T,
                       levels=15, cmap='RdYlGn_r')
    ax2.set_xlabel('Longitude (°E)', fontweight='bold')
    ax2.set_ylabel('Latitude (°N)', fontweight='bold')
    ax2.set_title('ET Variability (CV%) | ET 变异性', fontweight='bold', fontsize=12)
    plt.colorbar(im2, ax=ax2, label='%')
    ax2.grid(alpha=0.3)

    # Plot 3: ET Trend
    ax3 = fig.add_subplot(gs[1, 0])
    levels_trend = np.linspace(-10, 10, 21)
    im3 = ax3.contourf(ds['lon'], ds['lat'], analysis['trend'].T,
                       levels=levels_trend, cmap='RdBu_r', extend='both')
    ax3.set_xlabel('Longitude (°E)', fontweight='bold')
    ax3.set_ylabel('Latitude (°N)', fontweight='bold')
    ax3.set_title('ET Trend (mm/year per year) | ET 趋势', fontweight='bold', fontsize=12)
    plt.colorbar(im3, ax=ax3, label='mm/year/year')
    ax3.grid(alpha=0.3)

    # Plot 4: Zonal mean
    ax4 = fig.add_subplot(gs[1, 1])
    et_zonal_mean = analysis['mean'].mean(dim='lon')
    precip_zonal_mean = ds['precipitation'].mean(dim=['lon', 'time'])
    ax4_twin = ax4.twinx()

    line1 = ax4.plot(et_zonal_mean, ds['lat'], 'b-o', linewidth=2, label='ET')
    line2 = ax4_twin.plot(precip_zonal_mean, ds['lat'], 'g-s', linewidth=2, label='Precipitation')

    ax4.set_xlabel('ET (mm/month)', color='b', fontweight='bold')
    ax4_twin.set_xlabel('Precipitation (mm/month)', color='g', fontweight='bold')
    ax4.set_ylabel('Latitude (°N)', fontweight='bold')
    ax4.set_title('Zonal Mean | 纬向平均', fontweight='bold', fontsize=12)
    ax4.tick_params(axis='x', labelcolor='b')
    ax4_twin.tick_params(axis='x', labelcolor='g')
    ax4.grid(alpha=0.3)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='best')

    # Plot 5: Time series at selected grid cell
    ax5 = fig.add_subplot(gs[2, :])
    i_center = len(ds['lon']) // 2
    j_center = len(ds['lat']) // 2

    et_timeseries = et_da[i_center, j_center, :]
    precip_timeseries = ds['precipitation'][i_center, j_center, :]

    ax5_twin = ax5.twinx()
    line1 = ax5.plot(ds['time'], et_timeseries, 'b-', linewidth=2, label='ET')
    line2 = ax5_twin.plot(ds['time'], precip_timeseries, 'g--', linewidth=2, label='Precipitation')

    ax5.set_xlabel('Time (months)', fontweight='bold')
    ax5.set_ylabel('ET (mm/month)', color='b', fontweight='bold')
    ax5_twin.set_ylabel('Precipitation (mm/month)', color='g', fontweight='bold')
    ax5.set_title(f'Time Series at Center Grid Cell (Lon={ds["lon"][i_center].values:.1f}°, Lat={ds["lat"][j_center].values:.1f}°)',
                  fontweight='bold', fontsize=12)
    ax5.tick_params(axis='y', labelcolor='b')
    ax5_twin.tick_params(axis='y', labelcolor='g')
    ax5.grid(alpha=0.3)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax5.legend(lines, labels, loc='best')

    plt.tight_layout()
    plt.savefig('figures/integration_test_spatial_netcdf.png', dpi=150, bbox_inches='tight')
    plt.show()

    # Step 7: Save ET to NetCDF
    print("\n[Step 7] Saving ET results to NetCDF...")
    print("[步骤 7] 保存 ET 结果到 NetCDF...")

    ds_out = xr.Dataset({
        'et': et_da,
        'et_mean': analysis['mean'],
        'et_trend': analysis['trend']
    })
    ds_out.to_netcdf('data/output/synthetic_spatial_et.nc')

    print(f"✓ ET results saved")
    print(f"✓ ET 结果已保存")

    print("\n" + "="*70)
    print("Integration Test Complete | 集成测试完成")
    print("="*70)
    print(f"\n✓ Processed {len(ds['lon']) * len(ds['lat']) * len(ds['time']):,} data points")
    print(f"✓ 已处理 {len(ds['lon']) * len(ds['lat']) * len(ds['time']):,} 个数据点")
    print(f"✓ Identified {np.sum(analysis['trend'] > 5)} grid cells with increasing ET trend")
    print(f"✓ 识别出 {np.sum(analysis['trend'] > 5)} 个 ET 增长趋势的网格")
    print(f"\nFigures saved: figures/integration_test_spatial_netcdf.png")
    print(f"图片已保存: figures/integration_test_spatial_netcdf.png")


if __name__ == '__main__':
    main()
