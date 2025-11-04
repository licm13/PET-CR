"""
示例: 比较所有 CR 模型
Example: Comparing all CR models

这个示例比较了 PET-CR 库中所有的互补关系模型。
This example compares all Complementary Relationship models in the PET-CR library.

Note: Install the package first with: pip install -e . (from project root)
Or run from project root: python -m examples.compare_models
"""

import numpy as np

try:
    from petcr import (
        sigmoid_cr, 
        polynomial_cr, 
        rescaled_power_cr,
        bouchet_cr,
        aa_cr,
        penman_potential_et,
        priestley_taylor_et
    )
except ImportError:
    # Fallback for running directly without installation
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from petcr import (
        sigmoid_cr, 
        polynomial_cr, 
        rescaled_power_cr,
        bouchet_cr,
        aa_cr,
        penman_potential_et,
        priestley_taylor_et
    )

def main():
    print("=" * 80)
    print("所有 CR 模型比较 / Comparison of All CR Models")
    print("=" * 80)
    print()
    
    # 设置气象条件 / Set meteorological conditions
    net_radiation = 500.0       # W m⁻²
    ground_heat_flux = 50.0     # W m⁻²
    temperature = 20.0          # °C
    relative_humidity = 50.0    # %
    wind_speed = 2.0           # m s⁻¹
    pressure = 101325.0        # Pa
    
    # 计算 Ep 和 Ew / Calculate Ep and Ew
    ep = penman_potential_et(
        net_radiation, ground_heat_flux, temperature, 
        relative_humidity, wind_speed, pressure
    )
    
    ew = priestley_taylor_et(
        net_radiation, ground_heat_flux, temperature, 
        pressure, alpha=1.26
    )
    
    print(f"参考蒸散发 / Reference ET:")
    print(f"  Ep (Penman):           {ep:.2f} W m⁻²")
    print(f"  Ew (Priestley-Taylor): {ew:.2f} W m⁻²")
    print(f"  Ep/Ew ratio:           {ep/ew:.3f}")
    print()
    
    # 计算不同模型的 Ea / Calculate Ea using different models
    print("=" * 80)
    print("单点比较 / Single Point Comparison")
    print("=" * 80)
    print()
    
    models = {
        'Sigmoid (β=0.5)': sigmoid_cr(ep, ew, beta=0.5),
        'Sigmoid (β=0.7)': sigmoid_cr(ep, ew, beta=0.7),
        'Polynomial (b=2.0)': polynomial_cr(ep, ew, b=2.0),
        'Polynomial (b=1.5)': polynomial_cr(ep, ew, b=1.5),
        'Rescaled Power (n=0.5)': rescaled_power_cr(ep, ew, n=0.5),
        'Bouchet': bouchet_cr(ep, ew),
        'A-A': aa_cr(ep, ew),
    }
    
    print(f"{'模型 / Model':<30} {'Ea (W m⁻²)':<15} {'Ea/Ew':<10}")
    print("-" * 80)
    for model_name, ea in models.items():
        ratio = ea / ew
        print(f"{model_name:<30} {ea:<15.2f} {ratio:<10.3f}")
    
    print()
    print("=" * 80)
    print("时间序列比较 / Time Series Comparison")
    print("=" * 80)
    print()
    
    # 创建时间序列 (10天) / Create time series (10 days)
    days = 10
    ep_series = np.array([250, 300, 350, 400, 450, 500, 550, 450, 350, 300])
    ew_series = np.full(days, 350.0)
    
    # 使用各个模型计算 / Calculate using each model
    ea_sigmoid = sigmoid_cr(ep_series, ew_series, beta=0.5)
    ea_polynomial = polynomial_cr(ep_series, ew_series, b=2.0)
    ea_rescaled = rescaled_power_cr(ep_series, ew_series, n=0.5)
    ea_bouchet = bouchet_cr(ep_series, ew_series)
    ea_aa = aa_cr(ep_series, ew_series)
    
    print(f"{'Day':<5} {'Ep':<8} {'Ew':<8} {'Sigmoid':<10} {'Polynomial':<12} "
          f"{'Rescaled':<10} {'Bouchet':<10} {'A-A':<10}")
    print("-" * 80)
    
    for i in range(days):
        print(f"{i+1:<5} {ep_series[i]:<8.0f} {ew_series[i]:<8.0f} "
              f"{ea_sigmoid[i]:<10.2f} {ea_polynomial[i]:<12.2f} "
              f"{ea_rescaled[i]:<10.2f} {ea_bouchet[i]:<10.2f} "
              f"{ea_aa[i]:<10.2f}")
    
    print()
    
    # 统计摘要 / Statistical summary
    print("=" * 80)
    print("统计摘要 / Statistical Summary")
    print("=" * 80)
    print()
    
    print(f"{'模型 / Model':<20} {'平均Ea / Mean':<15} {'标准差 / Std':<15} "
          f"{'范围 / Range':<20}")
    print("-" * 80)
    
    all_models = {
        'Sigmoid (β=0.5)': ea_sigmoid,
        'Polynomial (b=2.0)': ea_polynomial,
        'Rescaled Power': ea_rescaled,
        'Bouchet': ea_bouchet,
        'A-A': ea_aa,
    }
    
    for model_name, ea in all_models.items():
        mean_ea = np.mean(ea)
        std_ea = np.std(ea)
        min_ea = np.min(ea)
        max_ea = np.max(ea)
        print(f"{model_name:<20} {mean_ea:<15.2f} {std_ea:<15.2f} "
              f"{min_ea:.2f} - {max_ea:.2f}")
    
    print()
    
    # 模型特性说明 / Model characteristics
    print("=" * 80)
    print("模型特性 / Model Characteristics")
    print("=" * 80)
    print()
    print("1. Sigmoid (Han & Tian, 2018)")
    print("   - 广义非线性模型 / Generalized nonlinear model")
    print("   - β 参数控制曲线陡峭程度 / β controls curve steepness")
    print("   - 适用于多种气候条件 / Suitable for various climates")
    print()
    print("2. Polynomial (Brutsaert, 2015)")
    print("   - 带物理约束的多项式 / Polynomial with physical constraints")
    print("   - b=1 时退化为 Bouchet / Reduces to Bouchet when b=1")
    print("   - 凹形关系 / Concave relationship")
    print()
    print("3. Rescaled Power (Szilagyi et al., 2017)")
    print("   - 无需校准 / Calibration-free")
    print("   - 适合大陆尺度 / Suitable for continental scales")
    print("   - n=0.5 为最优值 / n=0.5 is optimal")
    print()
    print("4. Bouchet (1963)")
    print("   - 经典对称线性模型 / Classic symmetric linear model")
    print("   - 简单但可能不够精确 / Simple but may lack precision")
    print("   - Ea = 2*Ew - Ep")
    print()
    print("5. A-A (Advection-Aridity)")
    print("   - 非对称模型 / Asymmetric model")
    print("   - 区分湿润和干燥状态 / Distinguishes wet and dry regimes")
    print("   - 考虑平流效应 / Accounts for advection effects")
    print()
    print("=" * 80)
    
    # 使用建议 / Usage recommendations
    print("使用建议 / Usage Recommendations")
    print("=" * 80)
    print()
    print("• 湿润气候 / Humid climates:")
    print("  推荐 Sigmoid 或 Polynomial / Recommend Sigmoid or Polynomial")
    print()
    print("• 干旱/半干旱气候 / Arid/semi-arid climates:")
    print("  推荐 A-A 或 Rescaled Power / Recommend A-A or Rescaled Power")
    print()
    print("• 大陆尺度研究 / Continental-scale studies:")
    print("  推荐 Rescaled Power (无需校准) / Recommend Rescaled Power (calibration-free)")
    print()
    print("• 快速估算 / Quick estimation:")
    print("  使用 Bouchet (最简单) / Use Bouchet (simplest)")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
