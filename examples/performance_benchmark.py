"""
Performance Benchmark: Compare Original vs Optimized Implementations
性能基准测试：对比原始实现与优化实现

This script benchmarks:
本脚本测试：
1. Original NumPy implementations
   原始 NumPy 实现
2. Numba-optimized implementations (if available)
   Numba 优化实现（如果可用）
3. Vectorized operations
   向量化操作

Author: PET-CR Development Team
Date: 2025-12-04
"""

import numpy as np
import time
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '..')
import petcr

# Try to import numba
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    print("⚠️  Numba not available. Optimization benchmarks will be skipped.")
    print("⚠️  Numba 不可用。优化基准测试将被跳过。")


def benchmark_function(func, *args, n_runs=10, **kwargs):
    """
    Benchmark a function's execution time
    测试函数的执行时间

    Parameters
    ----------
    func : callable
        Function to benchmark
    args : tuple
        Positional arguments
    n_runs : int
        Number of runs for averaging
    kwargs : dict
        Keyword arguments

    Returns
    -------
    dict
        Timing statistics
    """
    times = []

    # Warmup run
    _ = func(*args, **kwargs)

    for _ in range(n_runs):
        start = time.time()
        _ = func(*args, **kwargs)
        end = time.time()
        times.append(end - start)

    return {
        'mean': np.mean(times),
        'std': np.std(times),
        'min': np.min(times),
        'max': np.max(times)
    }


def penman_et_loop(net_radiation, air_temperature, wind_speed, vpd, air_pressure):
    """Original loop-based implementation"""
    n = len(net_radiation)
    et = np.zeros(n)

    for i in range(n):
        try:
            et[i] = petcr.penman_potential_et(
                net_radiation=net_radiation[i],
                air_temperature=air_temperature[i],
                wind_speed=wind_speed[i],
                vapor_pressure_deficit=vpd[i],
                air_pressure=air_pressure[i]
            )
        except:
            et[i] = np.nan

    return et


if NUMBA_AVAILABLE:
    @jit(nopython=True)
    def penman_et_numba_optimized(net_radiation, air_temperature, wind_speed, vpd, air_pressure):
        """
        Numba-optimized Penman ET calculation
        Numba 优化的 Penman ET 计算

        This is a simplified version for demonstration
        这是一个简化版本用于演示
        """
        n = len(net_radiation)
        et = np.zeros(n)

        # Constants
        cp = 1005.0  # J/(kg·K)
        epsilon = 0.62198
        lambda_v = 2.45e6  # J/kg

        for i in range(n):
            # Simplified Penman calculation
            # In production, this should match the full petcr implementation

            # Calculate psychrometric constant
            gamma = cp * air_pressure[i] / (epsilon * lambda_v)

            # Calculate slope of saturation vapor pressure curve
            temp_c = air_temperature[i] - 273.15
            es = 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))
            delta = 4098 * es / ((temp_c + 237.3)**2) * 1000  # kPa/K -> Pa/K

            # Aerodynamic term (simplified)
            rho = air_pressure[i] / (287.05 * air_temperature[i])  # kg/m³
            ea_term = rho * cp * wind_speed[i] * vpd[i] * 1000 / 208  # Simplified

            # Penman combination
            et[i] = (delta * net_radiation[i] + gamma * ea_term) / (delta + gamma)

        return et


def main():
    """Main benchmark workflow"""

    print("="*70)
    print("Performance Benchmark: PET-CR Library")
    print("性能基准测试：PET-CR 库")
    print("="*70)
    print(f"\nNumba available: {NUMBA_AVAILABLE}")
    print(f"Numba 可用: {NUMBA_AVAILABLE}")

    # Generate test data
    print("\n[Step 1] Generating test data...")
    print("[步骤 1] 生成测试数据...")

    data_sizes = [100, 1000, 10000, 50000]
    results = {}

    for size in data_sizes:
        print(f"\n--- Testing with {size} data points ---")
        print(f"--- 测试 {size} 个数据点 ---")

        # Generate random meteorological data
        net_radiation = np.random.uniform(100, 500, size)
        air_temperature = np.random.uniform(273, 313, size)
        wind_speed = np.random.uniform(1, 10, size)
        vpd = np.random.uniform(0.5, 3.0, size)
        air_pressure = np.full(size, 101325.0)

        # Benchmark 1: Original loop
        print("  Benchmarking original loop implementation...")
        time_loop = benchmark_function(
            penman_et_loop,
            net_radiation, air_temperature, wind_speed, vpd, air_pressure,
            n_runs=5
        )

        results[f'loop_{size}'] = time_loop

        print(f"    Original loop: {time_loop['mean']:.4f} ± {time_loop['std']:.4f} s")

        # Benchmark 2: Numba-optimized (if available)
        if NUMBA_AVAILABLE:
            print("  Benchmarking Numba-optimized implementation...")
            time_numba = benchmark_function(
                penman_et_numba_optimized,
                net_radiation, air_temperature, wind_speed, vpd, air_pressure,
                n_runs=5
            )

            results[f'numba_{size}'] = time_numba

            speedup = time_loop['mean'] / time_numba['mean']
            print(f"    Numba-optimized: {time_numba['mean']:.4f} ± {time_numba['std']:.4f} s")
            print(f"    ⚡ Speedup: {speedup:.2f}x")

    # Visualization
    print("\n[Step 2] Creating performance comparison plots...")
    print("[步骤 2] 创建性能对比图...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Execution time vs data size
    ax1 = axes[0]
    loop_times = [results[f'loop_{size}']['mean'] for size in data_sizes]

    ax1.plot(data_sizes, loop_times, 'bo-', linewidth=2, markersize=8, label='Original Loop')

    if NUMBA_AVAILABLE:
        numba_times = [results[f'numba_{size}']['mean'] for size in data_sizes]
        ax1.plot(data_sizes, numba_times, 'r^-', linewidth=2, markersize=8, label='Numba Optimized')

    ax1.set_xlabel('Number of Data Points', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Execution Time (seconds)', fontweight='bold', fontsize=12)
    ax1.set_title('Performance Comparison | 性能对比', fontweight='bold', fontsize=13)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, which='both')

    # Plot 2: Speedup
    ax2 = axes[1]

    if NUMBA_AVAILABLE:
        speedups = [results[f'loop_{size}']['mean'] / results[f'numba_{size}']['mean']
                   for size in data_sizes]
        ax2.bar(range(len(data_sizes)), speedups, color='green', alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.axhline(y=1, color='red', linestyle='--', linewidth=2, label='No speedup')

        ax2.set_xlabel('Data Size Category', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Speedup Factor', fontweight='bold', fontsize=12)
        ax2.set_title('Numba Optimization Speedup | Numba 优化加速比', fontweight='bold', fontsize=13)
        ax2.set_xticks(range(len(data_sizes)))
        ax2.set_xticklabels([f'{size}' for size in data_sizes])
        ax2.legend(fontsize=11)
        ax2.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, v in enumerate(speedups):
            ax2.text(i, v + 0.5, f'{v:.1f}x', ha='center', fontweight='bold')

    else:
        ax2.text(0.5, 0.5, 'Numba not available\nNumba 不可用',
                ha='center', va='center', transform=ax2.transAxes,
                fontsize=14, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        ax2.axis('off')

    plt.tight_layout()
    plt.savefig('figures/performance_benchmark.png', dpi=150, bbox_inches='tight')
    plt.show()

    # Summary statistics
    print("\n" + "="*70)
    print("Benchmark Summary | 基准测试总结")
    print("="*70)

    for size in data_sizes:
        loop_time = results[f'loop_{size}']['mean']
        print(f"\nData size: {size}")
        print(f"  Original loop: {loop_time:.4f} s")

        if NUMBA_AVAILABLE:
            numba_time = results[f'numba_{size}']['mean']
            speedup = loop_time / numba_time
            print(f"  Numba optimized: {numba_time:.4f} s")
            print(f"  Speedup: {speedup:.2f}x")

    # Recommendations
    print("\n" + "="*70)
    print("💡 Optimization Recommendations | 优化建议")
    print("="*70)

    if NUMBA_AVAILABLE:
        avg_speedup = np.mean([results[f'loop_{size}']['mean'] / results[f'numba_{size}']['mean']
                               for size in data_sizes])
        print(f"\n✓ Average speedup with Numba: {avg_speedup:.2f}x")
        print(f"✓ Numba 平均加速比: {avg_speedup:.2f}x")

        if avg_speedup > 10:
            print("\n🚀 Excellent! Numba optimization is highly effective.")
            print("🚀 优秀！Numba 优化非常有效。")
            print("   Consider integrating Numba into production code.")
            print("   考虑将 Numba 集成到生产代码中。")
        elif avg_speedup > 5:
            print("\n✅ Good! Significant performance improvement.")
            print("✅ 很好！显著的性能提升。")
        else:
            print("\n⚠️  Moderate improvement. Profile to identify bottlenecks.")
            print("⚠️  中等提升。需要分析以识别瓶颈。")
    else:
        print("\n📦 Install Numba for potential 10-50x speedup:")
        print("📦 安装 Numba 以获得 10-50 倍的潜在加速：")
        print("   pip install numba")

    print("\n✓ For large-scale spatial data, consider:")
    print("✓ 对于大规模空间数据，考虑：")
    print("  1. Dask for parallel processing")
    print("  2. Xarray with chunking for NetCDF files")
    print("  3. GPU acceleration with CuPy (if available)")

    print(f"\nFigure saved: figures/performance_benchmark.png")
    print(f"图片已保存: figures/performance_benchmark.png")


if __name__ == '__main__':
    main()
