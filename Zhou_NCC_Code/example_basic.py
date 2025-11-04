"""
Basic Usage Example
====================

This example demonstrates the basic usage of the PET estimation module.

运行方式:
python examples/example_basic.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from src import (
    calculate_pet_land,
    generate_sample_data,
    batch_calculate_pet
)


def example_single_calculation():
    """
    Example 1: Single PET calculation
    示例1: 单次PET计算
    """
    print("=" * 70)
    print("Example 1: Single PET Calculation")
    print("示例1: 单次PET计算")
    print("=" * 70)
    
    # Define input data (typical values for a land surface)
    # 定义输入数据(陆地表面的典型值)
    results = calculate_pet_land(
        latent_heat=100.0,      # W/m²
        sensible_heat=50.0,     # W/m²
        specific_humidity=0.01, # kg/kg
        air_pressure=101325.0,  # Pa
        air_temperature=298.15, # K (25°C)
        skin_temperature=300.15 # K (27°C)
    )
    
    print("\nInput Parameters:")
    print(f"  Latent Heat Flux: 100.0 W/m²")
    print(f"  Sensible Heat Flux: 50.0 W/m²")
    print(f"  Specific Humidity: 0.01 kg/kg")
    print(f"  Air Pressure: 101325.0 Pa")
    print(f"  Air Temperature: 298.15 K (25.0°C)")
    print(f"  Skin Temperature: 300.15 K (27.0°C)")
    
    print("\nResults:")
    print(f"  PETe (Energy-based): {results['pete']:.3f} mm/day")
    print(f"  PETa (Aerodynamics-based): {results['peta']:.3f} mm/day")
    print(f"  Wet Bowen Ratio (βw): {results['beta_w']:.4f}")
    print(f"  Net Radiation: {results['rn']:.3f} mm/day (water equivalent)")
    print(f"  Actual ET: {results['et']:.3f} mm/day")
    
    print("\nInterpretation:")
    print("  - PETe represents the maximum ET constrained by available energy")
    print("    PETe表示可用能量约束的最大ET")
    print(f"  - PETa ({results['peta']:.3f}) > PETe ({results['pete']:.3f}),")
    print("    indicating aerodynamic capacity exceeds energy constraint")
    print("    表明空气动力学容量超过能量约束")
    print(f"  - Actual ET ({results['et']:.3f}) < PETe ({results['pete']:.3f}),")
    print("    suggesting some water limitation")
    print("    表明存在一定的水分限制")


def example_batch_calculation():
    """
    Example 2: Batch PET calculation with multiple samples
    示例2: 多个样本的批量PET计算
    """
    print("\n" + "=" * 70)
    print("Example 2: Batch PET Calculation")
    print("示例2: 批量PET计算")
    print("=" * 70)
    
    # Generate sample data
    # 生成示例数据
    n_samples = 100
    print(f"\nGenerating {n_samples} random samples...")
    
    data = generate_sample_data(n_samples=n_samples, surface_type='land', seed=42)
    
    # Calculate PET for all samples
    # 为所有样本计算PET
    results = batch_calculate_pet(data)
    
    print("\nBatch Statistics:")
    print(f"  Number of samples: {n_samples}")
    print(f"\n  PETe (mm/day):")
    print(f"    Mean: {np.mean(results['pete']):.3f}")
    print(f"    Std:  {np.std(results['pete']):.3f}")
    print(f"    Min:  {np.min(results['pete']):.3f}")
    print(f"    Max:  {np.max(results['pete']):.3f}")
    
    print(f"\n  PETa (mm/day):")
    print(f"    Mean: {np.mean(results['peta']):.3f}")
    print(f"    Std:  {np.std(results['peta']):.3f}")
    print(f"    Min:  {np.min(results['peta']):.3f}")
    print(f"    Max:  {np.max(results['peta']):.3f}")
    
    print(f"\n  Wet Bowen Ratio:")
    print(f"    Mean: {np.mean(results['beta_w']):.4f}")
    print(f"    Std:  {np.std(results['beta_w']):.4f}")
    
    # Create visualization
    # 创建可视化
    print("\nCreating visualization...")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: PETe vs PETa
    # 图1: PETe vs PETa
    ax1 = axes[0, 0]
    ax1.scatter(results['pete'], results['peta'], alpha=0.6, s=30)
    ax1.plot([0, max(results['pete'])], [0, max(results['pete'])], 
             'r--', label='1:1 line', linewidth=2)
    ax1.set_xlabel('PETe (mm/day)', fontsize=11)
    ax1.set_ylabel('PETa (mm/day)', fontsize=11)
    ax1.set_title('PETe vs PETa', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: ET vs PETe
    # 图2: ET vs PETe
    ax2 = axes[0, 1]
    ax2.scatter(results['pete'], results['et'], alpha=0.6, s=30, color='green')
    ax2.plot([0, max(results['pete'])], [0, max(results['pete'])], 
             'r--', label='1:1 line', linewidth=2)
    ax2.set_xlabel('PETe (mm/day)', fontsize=11)
    ax2.set_ylabel('Actual ET (mm/day)', fontsize=11)
    ax2.set_title('Actual ET vs PETe', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Distribution of PETe
    # 图3: PETe的分布
    ax3 = axes[1, 0]
    ax3.hist(results['pete'], bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax3.axvline(np.mean(results['pete']), color='red', linestyle='--', 
                linewidth=2, label=f'Mean = {np.mean(results["pete"]):.2f}')
    ax3.set_xlabel('PETe (mm/day)', fontsize=11)
    ax3.set_ylabel('Frequency', fontsize=11)
    ax3.set_title('Distribution of PETe', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Distribution of Wet Bowen Ratio
    # 图4: 湿润波文比的分布
    ax4 = axes[1, 1]
    ax4.hist(results['beta_w'], bins=20, alpha=0.7, color='orange', edgecolor='black')
    ax4.axvline(np.mean(results['beta_w']), color='red', linestyle='--', 
                linewidth=2, label=f'Mean = {np.mean(results["beta_w"]):.3f}')
    ax4.set_xlabel('Wet Bowen Ratio', fontsize=11)
    ax4.set_ylabel('Frequency', fontsize=11)
    ax4.set_title('Distribution of Wet Bowen Ratio', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    # 保存图形
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'example_basic_results.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    
    # Uncomment to display the plot
    # 取消注释以显示图形
    # plt.show()
    plt.close()


def example_complementary_relationship():
    """
    Example 3: Demonstrate complementary relationship between ET and PETa
    示例3: 演示ET和PETa之间的互补关系
    """
    print("\n" + "=" * 70)
    print("Example 3: Complementary Relationship")
    print("示例3: 互补关系")
    print("=" * 70)
    
    # Generate data with varying moisture conditions
    # 生成具有不同湿度条件的数据
    n_samples = 100
    
    # Simulate dry to wet gradient
    # 模拟从干到湿的梯度
    latent_heat = np.linspace(40, 150, n_samples)  # Increasing moisture
    sensible_heat = np.linspace(80, 30, n_samples)  # Decreasing sensible heat
    
    data = {
        'hfls': latent_heat,
        'hfss': sensible_heat,
        'huss': np.full(n_samples, 0.01),
        'ps': np.full(n_samples, 101325.0),
        'tas': np.full(n_samples, 298.15),
        'ts': np.full(n_samples, 300.15)
    }
    
    results = batch_calculate_pet(data)
    
    # Calculate moisture index (ET/PETa)
    # 计算湿度指数(ET/PETa)
    moisture_index = results['et'] / results['peta']
    
    # Scale by PETe
    # 按PETe缩放
    et_scaled = results['et'] / results['pete']
    peta_scaled = results['peta'] / results['pete']
    
    print("\nComplementary Relationship Analysis:")
    print(f"  Moisture Index range: {np.min(moisture_index):.3f} to {np.max(moisture_index):.3f}")
    print(f"  Correlation (ET/PETe, PETa/PETe): {np.corrcoef(et_scaled, peta_scaled)[0,1]:.4f}")
    print("\n  The negative correlation confirms the complementary relationship:")
    print("  负相关证实了互补关系:")
    print("  - As ET increases (wetter conditions), PETa decreases")
    print("    随着ET增加(更湿润的条件),PETa减少")
    print("  - As ET decreases (drier conditions), PETa increases")
    print("    随着ET减少(更干燥的条件),PETa增加")
    
    # Visualization
    # 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: ET and PETa scaled by PETe vs moisture index
    # 图1: 按PETe缩放的ET和PETa vs 湿度指数
    ax1.scatter(moisture_index, et_scaled, alpha=0.7, s=40, 
                label='ET/PETe', color='blue')
    ax1.scatter(moisture_index, peta_scaled, alpha=0.7, s=40, 
                label='PETa/PETe', color='red')
    ax1.set_xlabel('Moisture Index (ET/PETa)', fontsize=11)
    ax1.set_ylabel('Scaled Value', fontsize=11)
    ax1.set_title('Complementary Relationship', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: ET/PETe vs PETa/PETe
    # 图2: ET/PETe vs PETa/PETe
    ax2.scatter(peta_scaled, et_scaled, alpha=0.7, s=40, color='purple')
    ax2.set_xlabel('PETa/PETe', fontsize=11)
    ax2.set_ylabel('ET/PETe', fontsize=11)
    ax2.set_title(f'Negative Correlation (r = {np.corrcoef(et_scaled, peta_scaled)[0,1]:.3f})', 
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add trend line
    # 添加趋势线
    z = np.polyfit(peta_scaled, et_scaled, 1)
    p = np.poly1d(z)
    ax2.plot(peta_scaled, p(peta_scaled), "r--", linewidth=2, alpha=0.8, 
             label=f'y = {z[0]:.3f}x + {z[1]:.3f}')
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    
    # Save figure
    # 保存图形
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')
    output_path = os.path.join(output_dir, 'example_complementary_relationship.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    
    plt.close()


def main():
    """Main function to run all examples"""
    print("\n" + "=" * 70)
    print("BASIC USAGE EXAMPLES")
    print("基础使用示例")
    print("=" * 70)
    
    # Run examples
    # 运行示例
    example_single_calculation()
    example_batch_calculation()
    example_complementary_relationship()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("所有示例成功完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
