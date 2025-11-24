"""
示例：使用亚日尺度 GCP + 稳定度修正计算蒸发并标定 β_c。

Example: Estimate sub-daily evaporation with the GCP + stability method and
calibrate ``beta_c`` using synthetic data inspired by Zhang et al. (2025).
"""
from __future__ import annotations

import numpy as np

from petcr import (
    SurfaceRoughness,
    calculate_subdaily_gcp_et,
    calibrate_subdaily_beta_c,
    generate_sample_data,
)


def main():
    # 生成示例数据（气温 K，气压 Pa）/ Generate demo inputs (temperature K, pressure Pa)
    n_steps = 48  # 2 days of half-hourly data
    rng = np.random.default_rng(42)
    sample = generate_sample_data(n_samples=n_steps, surface_type="land", seed=24)

    Ta = sample["tas"]
    pressure = float(np.mean(sample["ps"]))
    Qne = rng.uniform(80.0, 200.0, size=n_steps)  # Available energy [W/m²]
    u2 = rng.uniform(0.5, 4.0, size=n_steps)  # Wind speed [m/s]
    rh = rng.uniform(0.45, 0.9, size=n_steps)  # Relative humidity [0-1]

    # 设定粗糙度参数 / Define surface roughness
    roughness = SurfaceRoughness(z=2.0, d0=0.0, z0m=0.12, z0v=0.012)

    # 生成“观测”数据：用已知 β_c=1.05 计算，再添加小噪声。
    # Create synthetic observations using beta_c=1.05 plus small noise.
    beta_true = 1.05
    synthetic = calculate_subdaily_gcp_et(
        Qne=Qne,
        Ta=Ta,
        u2=u2,
        pressure=pressure,
        rh=rh,
        beta_c=beta_true,
        roughness=roughness,
        with_stability=True,
    )
    noise = rng.normal(0.0, 5.0, size=n_steps)
    E_obs = synthetic["E"] + noise

    # 标定 β_c（带稳定度修正） / Calibrate beta_c with stability correction
    calib = calibrate_subdaily_beta_c(
        Qne=Qne,
        Ta=Ta,
        u2=u2,
        E_obs=E_obs,
        pressure=pressure,
        rh=rh,
        roughness=roughness,
        with_stability=True,
    )

    # 使用标定后的 β_c 重新计算蒸发 / Re-compute ET using calibrated beta_c
    results = calculate_subdaily_gcp_et(
        Qne=Qne,
        Ta=Ta,
        u2=u2,
        pressure=pressure,
        rh=rh,
        beta_c=calib["beta_c"],
        roughness=roughness,
        with_stability=True,
    )

    print("=== Sub-daily GCP Example ===")
    print(f"Calibrated beta_c : {calib['beta_c']:.3f}")
    print(f"Objective (m·R^2): {calib['objective']:.3f}")
    print(f"RMSE (W/m²)      : {calib['rmse']:.2f}")
    print(f"Bias (%)         : {calib['bias_pct']:.2f}")
    print("First 5 estimated E (W/m²):", np.round(results["E"][:5], 2))


if __name__ == "__main__":
    main()
