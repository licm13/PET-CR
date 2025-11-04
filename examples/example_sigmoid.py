"""
示例: 使用 Sigmoid CR 模型估算实际蒸散发
Example: Estimating actual evapotranspiration using Sigmoid CR model

这个示例展示了如何使用 PET-CR 库中的 Sigmoid 模型 (Han & Tian, 2018) 
来估算实际蒸散发。

This example demonstrates how to use the Sigmoid model (Han & Tian, 2018) 
from the PET-CR library to estimate actual evapotranspiration.

Note: Install the package first with: pip install -e . (from project root)
Or run from project root: python -m examples.example_sigmoid
"""

import numpy as np

try:
    from petcr import sigmoid_cr, penman_potential_et, priestley_taylor_et
except ImportError:
    # Fallback for running directly without installation
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from petcr import sigmoid_cr, penman_potential_et, priestley_taylor_et

def main():
    print("=" * 70)
    print("PET-CR Sigmoid 模型示例 / Sigmoid CR Model Example")
    print("=" * 70)
    print()
    
    # 输入气象数据 (SI 单位) / Input meteorological data (SI units)
    print("输入气象数据 / Input Meteorological Data:")
    print("-" * 70)
    
    net_radiation = 500.0       # W m⁻²
    ground_heat_flux = 50.0     # W m⁻²
    temperature = 20.0          # °C
    relative_humidity = 50.0    # %
    wind_speed = 2.0           # m s⁻¹
    pressure = 101325.0        # Pa
    
    print(f"净辐射 Net Radiation:           {net_radiation:.1f} W m⁻²")
    print(f"土壤热通量 Ground Heat Flux:    {ground_heat_flux:.1f} W m⁻²")
    print(f"气温 Air Temperature:           {temperature:.1f} °C")
    print(f"相对湿度 Relative Humidity:     {relative_humidity:.1f} %")
    print(f"风速 Wind Speed:                {wind_speed:.1f} m s⁻¹")
    print(f"气压 Atmospheric Pressure:      {pressure:.1f} Pa")
    print()
    
    # 计算潜在蒸散发 (Penman) / Calculate potential ET (Penman)
    print("计算潜在蒸散发 / Calculating Potential ET (Penman)...")
    ep = penman_potential_et(
        net_radiation=net_radiation,
        ground_heat_flux=ground_heat_flux,
        temperature=temperature,
        relative_humidity=relative_humidity,
        wind_speed=wind_speed,
        pressure=pressure
    )
    print(f"Ep (Penman): {ep:.2f} W m⁻²")
    print()
    
    # 计算湿环境蒸散发 (Priestley-Taylor) / Calculate wet-environment ET
    print("计算湿环境蒸散发 / Calculating Wet-environment ET (Priestley-Taylor)...")
    ew = priestley_taylor_et(
        net_radiation=net_radiation,
        ground_heat_flux=ground_heat_flux,
        temperature=temperature,
        pressure=pressure,
        alpha=1.26
    )
    print(f"Ew (Priestley-Taylor): {ew:.2f} W m⁻²")
    print()
    
    # 使用 Sigmoid CR 模型估算实际蒸散发 / Estimate actual ET using Sigmoid CR
    print("使用 Sigmoid CR 模型估算实际蒸散发 / Estimating Actual ET...")
    print("-" * 70)
    
    # 测试不同的 beta 参数 / Test different beta parameters
    beta_values = [0.3, 0.5, 0.7, 1.0]
    
    print(f"{'Beta':<10} {'Ea (W m⁻²)':<15} {'Ea/Ew':<10}")
    print("-" * 70)
    
    for beta in beta_values:
        ea = sigmoid_cr(ep=ep, ew=ew, beta=beta)
        ratio = ea / ew
        print(f"{beta:<10.1f} {ea:<15.2f} {ratio:<10.3f}")
    
    print()
    print("=" * 70)
    print("时间序列分析示例 / Time Series Analysis Example")
    print("=" * 70)
    print()
    
    # 模拟 7 天的时间序列 / Simulate 7-day time series
    days = 7
    ep_series = np.array([250, 300, 400, 500, 600, 550, 350])  # W m⁻²
    ew_series = np.array([350, 350, 350, 350, 350, 350, 350])  # W m⁻²
    
    # 使用 beta = 0.5 计算实际蒸散发 / Calculate actual ET with beta=0.5
    ea_series = sigmoid_cr(ep=ep_series, ew=ew_series, beta=0.5)
    
    print(f"{'Day':<6} {'Ep (W m⁻²)':<12} {'Ew (W m⁻²)':<12} {'Ea (W m⁻²)':<12} {'Ea/Ew':<10}")
    print("-" * 70)
    
    for i in range(days):
        ratio = ea_series[i] / ew_series[i]
        print(f"{i+1:<6} {ep_series[i]:<12.1f} {ew_series[i]:<12.1f} "
              f"{ea_series[i]:<12.2f} {ratio:<10.3f}")
    
    print()
    
    # 统计分析 / Statistical analysis
    print("统计摘要 / Statistical Summary:")
    print("-" * 70)
    print(f"平均 Ep / Mean Ep:        {np.mean(ep_series):.2f} W m⁻²")
    print(f"平均 Ea / Mean Ea:        {np.mean(ea_series):.2f} W m⁻²")
    print(f"平均 Ea/Ew / Mean Ea/Ew:  {np.mean(ea_series/ew_series):.3f}")
    print(f"Ea 范围 / Ea range:       {np.min(ea_series):.2f} - {np.max(ea_series):.2f} W m⁻²")
    print()
    
    print("=" * 70)
    print("说明 / Notes:")
    print("=" * 70)
    print("1. Ep > Ew 表示干燥条件 / Ep > Ew indicates dry conditions")
    print("2. Ep < Ew 表示湿润条件 / Ep < Ew indicates wet conditions")
    print("3. Ea/Ew 比值反映土壤湿度状况 / Ea/Ew ratio reflects soil moisture status")
    print("4. beta 参数控制 sigmoid 曲线的陡峭程度 / beta controls sigmoid steepness")
    print()
    
    print("参考文献 / Reference:")
    print("Han, S., & Tian, F. (2018). A review of the complementary principle")
    print("of evaporation. Hydrology and Earth System Sciences, 22(3), 1813-1834.")
    print("=" * 70)

if __name__ == "__main__":
    main()
