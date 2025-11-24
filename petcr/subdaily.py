"""
亚日尺度 GCP 蒸发（含稳定度修正）/ Sub-daily GCP evaporation with stability correction.

本模块根据 Zhang et al. (2025) 的“GCP with Atmospheric Stability Correction”
思路，将广义互补关系 (GCP) 与 Monin-Obukhov 稳定度修正相结合，提供
亚日尺度蒸发估算及 β_c 标定的便捷接口。

This module integrates the Generalized Complementary Principle (GCP) with
Monin-Obukhov stability corrections following Zhang et al. (2025) to provide a
sub-daily evaporation estimator and a helper for calibrating ``beta_c``.

所有公共接口均使用 SI 单位：温度 [K]、压强 [Pa]、能量通量 [W/m²]、风速 [m/s]。
All public interfaces use SI units: temperature [K], pressure [Pa], energy flux
[W/m²], and wind speed [m/s]. Vapor pressure deficit is expected in pascals; if
values < 10 are provided, they are assumed to be in kPa and converted to Pa.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

from . import constants
from .physics import (
    calculate_psychrometric_constant,
    calculate_saturation_vapor_pressure,
    calculate_slope_svp,
)
from .stability import (
    compute_friction_velocity,
    compute_obukhov_length,
    psi_stable,
    psi_unstable_m,
    psi_unstable_v,
)

Array = np.ndarray


@dataclass
class SurfaceRoughness:
    """
    下垫面粗糙度参数。/ Surface roughness parameters.

    Attributes
    ----------
    z : float
        观测高度 [m] / Measurement height [m].
    d0 : float
        零平面位移 [m] / Zero-plane displacement [m].
    z0m : float
        动量粗糙度长度 [m] / Roughness length for momentum [m].
    z0v : float
        水汽粗糙度长度 [m] / Roughness length for vapor [m].
    """

    z: float
    d0: float
    z0m: float
    z0v: float


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _compute_vpd_pa(
    ta_kelvin: Array,
    rh: Optional[Array] = None,
    vpd: Optional[Array] = None,
) -> Array:
    ta_c = ta_kelvin - constants.KELVIN_TO_CELSIUS_OFFSET
    es = calculate_saturation_vapor_pressure(ta_c)

    if vpd is not None:
        vpd_arr = np.asarray(vpd, dtype=float)
        # 如果提供的值看起来像 kPa，则转换到 Pa / Convert kPa-like values to Pa
        vpd_arr = np.where(vpd_arr < 10.0, vpd_arr * constants.KPA_TO_PA, vpd_arr)
        return vpd_arr

    if rh is None:
        raise ValueError("Either RH or VPD must be provided for VPD calculation.")

    rh_arr = np.asarray(rh, dtype=float)
    rh_arr = np.where(rh_arr > 1.0, rh_arr / 100.0, rh_arr)
    rh_arr = np.clip(rh_arr, 0.0, 1.0)
    ea = es * rh_arr
    return es - ea


def _wind_function_with_stability(
    u2: Array,
    ta_kelvin: Array,
    roughness: SurfaceRoughness,
    psi_m: Array,
    psi_v: Array,
) -> Array:
    num = constants.EPSILON_MOLWEIGHT * constants.KARMAN ** 2 * u2
    denom = (
        constants.R_SPECIFIC_DRY_AIR
        * ta_kelvin
        * (np.log((roughness.z - roughness.d0) / roughness.z0v) - psi_v)
        * (np.log((roughness.z - roughness.d0) / roughness.z0m) - psi_m)
    )
    denom = np.where(np.abs(denom) < constants.EPSILON_SAFE_DIV, constants.EPSILON_SAFE_DIV, denom)
    return num / denom


def compute_equilibrium_evaporation(Qne: Array, ta_kelvin: Array, pressure: float) -> Array:
    """
    计算平衡蒸发 Ee（能量通量单位）。/ Compute equilibrium evaporation ``Ee`` (energy flux).

    参数 / Parameters
    ----------
    Qne : np.ndarray
        可用能量 [W/m²]。/ Available energy [W/m²].
    ta_kelvin : np.ndarray
        气温 [K]。/ Air temperature [K].
    pressure : float
        大气压 [Pa]。/ Atmospheric pressure [Pa].

    返回 / Returns
    -------
    np.ndarray
        Ee [W/m²]。
    """
    ta_c = ta_kelvin - constants.KELVIN_TO_CELSIUS_OFFSET
    delta = calculate_slope_svp(ta_c)
    gamma = calculate_psychrometric_constant(pressure)
    coeff = delta / (delta + gamma)
    return coeff * Qne


def gcp_evaporation(beta_c: float, Ee: Array, Epa: Array) -> Array:
    """
    根据 GCP 公式计算实际蒸发。/ Compute actual evaporation from the GCP formula.

    参数 / Parameters
    ----------
    beta_c : float
        广义互补系数 β_c。/ Complementary coefficient β_c.
    Ee : np.ndarray
        平衡蒸发 [W/m²]。/ Equilibrium evaporation [W/m²].
    Epa : np.ndarray
        Penman 潜在蒸发 [W/m²]。/ Penman potential evaporation [W/m²].

    返回 / Returns
    -------
    np.ndarray
        实际蒸发通量 [W/m²]。/ Actual evaporation flux [W/m²].
    """
    Epa_safe = np.where(Epa <= constants.EPSILON_SAFE_DIV, constants.EPSILON_SAFE_DIV, Epa)
    x = np.clip(beta_c * Ee / Epa_safe, 0.0, 1.0)
    E = x ** 2 * (2.0 * Epa_safe - beta_c * Ee)
    return np.maximum(E, 0.0)


def _compute_penman_epa(
    Qne: Array,
    ta_kelvin: Array,
    vpd_pa: Array,
    u2: Array,
    roughness: SurfaceRoughness,
    pressure: float,
    E: Array,
    with_stability: bool = True,
    stability_iterations: int = 3,
) -> Tuple[Array, Array, Array]:
    ta_c = ta_kelvin - constants.KELVIN_TO_CELSIUS_OFFSET
    delta = calculate_slope_svp(ta_c)
    gamma = calculate_psychrometric_constant(pressure)

    psi_m = np.zeros_like(Qne)
    psi_v = np.zeros_like(Qne)

    if with_stability:
        air_density = pressure / (constants.R_SPECIFIC_DRY_AIR * ta_kelvin)
        for _ in range(stability_iterations):
            u_star = compute_friction_velocity(
                u2=u2,
                z=roughness.z,
                d0=roughness.d0,
                z0m=roughness.z0m,
                psi_m=psi_m,
            )
            L = compute_obukhov_length(
                u_star=u_star,
                Qne=Qne,
                E=E,
                ta_kelvin=ta_kelvin,
                pressure=pressure,
                air_density=air_density,
            )
            zeta = (roughness.z - roughness.d0) / L

            psi_m = np.zeros_like(zeta)
            psi_v = np.zeros_like(zeta)

            neutral = np.abs(L) >= 100.0
            stable = (L > 0.0) & (np.abs(L) < 100.0)
            unstable = (L < 0.0) & (np.abs(L) < 100.0)

            psi_m[neutral] = 0.0
            psi_v[neutral] = 0.0
            psi_m[stable] = psi_stable(zeta[stable])
            psi_v[stable] = psi_stable(zeta[stable])
            psi_m[unstable] = psi_unstable_m(zeta[unstable])
            psi_v[unstable] = psi_unstable_v(zeta[unstable])

    fe = _wind_function_with_stability(
        u2=u2,
        ta_kelvin=ta_kelvin,
        roughness=roughness,
        psi_m=psi_m,
        psi_v=psi_v,
    )

    rad_term = delta / (delta + gamma) * Qne
    aero_term = gamma / (delta + gamma) * fe * vpd_pa
    Epa = rad_term + aero_term
    return Epa, psi_m, psi_v


# ---------------------------------------------------------------------------
# Public APIs
# ---------------------------------------------------------------------------

def calculate_subdaily_gcp_et(
    Qne: Array,
    Ta: Array,
    u2: Array,
    *,
    pressure: float = 101325.0,
    rh: Optional[Array] = None,
    vpd: Optional[Array] = None,
    beta_c: float = 1.0,
    roughness: Optional[SurfaceRoughness] = None,
    with_stability: bool = True,
    max_iter: int = 20,
    tol: float = 1e-3,
    stability_iterations: int = 3,
) -> Dict[str, Array]:
    """
    计算亚日尺度 GCP 蒸发（可选稳定度修正）。
    Compute sub-daily GCP evaporation with optional stability correction.

    Parameters 参数
    ------------
    Qne : array_like
        可用能量 [W/m²]。/ Available energy [W/m²].
    Ta : array_like
        气温 [K]。/ Air temperature [K].
    u2 : array_like
        参考高度风速 [m/s]。/ Wind speed at reference height [m/s].
    pressure : float, optional
        大气压 [Pa]（默认 101325）。/ Atmospheric pressure [Pa] (default 101325).
    rh : array_like, optional
        相对湿度 (0-1 或 0-100)。/ Relative humidity (0-1 or 0-100).
    vpd : array_like, optional
        饱和水汽压差 [Pa]；若 <10 视为 kPa 自动转换。/ Vapor pressure deficit [Pa];
        values <10 are treated as kPa and converted.
    beta_c : float, optional
        GCP 系数 β_c（默认 1.0）。/ GCP coefficient β_c (default 1.0).
    roughness : SurfaceRoughness, optional
        粗糙度参数；若为 None 则使用草地典型值 (z=2 m, z0m=0.123 m, z0v=0.0123 m)。
        Surface roughness parameters; defaults emulate reference grass (z=2 m,
        z0m=0.123 m, z0v=0.0123 m).
    with_stability : bool, optional
        是否考虑大气稳定度修正。/ Whether to include stability correction.
    max_iter : int, optional
        GCP-稳定度迭代的最大步数。/ Maximum iterations for the coupled loop.
    tol : float, optional
        收敛阈值（E 绝对变化量）。/ Convergence threshold on absolute E change.
    stability_iterations : int, optional
        每次外循环中更新 ψ 的次数。/ Number of ψ-updates per outer iteration.

    Returns 返回
    ------------
    dict
        包含 ``E``、``Epa``、``Ee``、``psi_m``、``psi_v`` 的字典（单位 W/m²）。
        Dictionary with ``E``, ``Epa``, ``Ee``, ``psi_m`` and ``psi_v`` (W/m²).

    Notes 说明
    ----------
    - 基于 Zhang et al. (2025) 的 GCP + MOST 耦合思路。
    - 温度、压强均采用 SI 单位；如输入 VPD 为 kPa 会自动转换为 Pa。
    """
    Qne_arr = np.asarray(Qne, dtype=float)
    Ta_arr = np.asarray(Ta, dtype=float)
    u2_arr = np.asarray(u2, dtype=float)

    if roughness is None:
        roughness = SurfaceRoughness(z=2.0, d0=0.0, z0m=0.123, z0v=0.0123)

    vpd_pa = _compute_vpd_pa(Ta_arr, rh=rh, vpd=vpd)
    Ee = compute_equilibrium_evaporation(Qne_arr, Ta_arr, pressure)
    E = Ee.copy()
    psi_m = np.zeros_like(Qne_arr)
    psi_v = np.zeros_like(Qne_arr)

    for _ in range(max_iter):
        E_old = E.copy()
        Epa, psi_m, psi_v = _compute_penman_epa(
            Qne=Qne_arr,
            ta_kelvin=Ta_arr,
            vpd_pa=vpd_pa,
            u2=u2_arr,
            roughness=roughness,
            pressure=pressure,
            E=E,
            with_stability=with_stability,
            stability_iterations=stability_iterations,
        )
        Ee = compute_equilibrium_evaporation(Qne_arr, Ta_arr, pressure)
        E = gcp_evaporation(beta_c=beta_c, Ee=Ee, Epa=Epa)

        diff = np.nanmax(np.abs(E - E_old))
        if diff < tol:
            break

    return {"E": E, "Epa": Epa, "Ee": Ee, "psi_m": psi_m, "psi_v": psi_v}


def _compute_metrics(est: Array, obs: Array) -> Dict[str, float]:
    mask = np.isfinite(est) & np.isfinite(obs)
    est = est[mask]
    obs = obs[mask]

    if est.size == 0:
        return dict(slope=np.nan, r2=np.nan, rmse=np.nan, bias_pct=np.nan)

    s_num = np.sum(obs * est)
    s_den = np.sum(obs ** 2)
    slope = s_num / s_den if s_den != 0 else np.nan

    obs_mean = np.mean(obs)
    ss_res = np.sum((obs - est) ** 2)
    ss_tot = np.sum((obs - obs_mean) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else np.nan
    rmse = np.sqrt(np.mean((obs - est) ** 2))
    bias_pct = 100.0 * (np.mean(est) - np.mean(obs)) / obs_mean if obs_mean != 0 else np.nan

    return dict(slope=slope, r2=r2, rmse=rmse, bias_pct=bias_pct)


def _objective_m_r2(est: Array, obs: Array) -> float:
    metrics = _compute_metrics(est, obs)
    s = metrics["slope"]
    r2 = metrics["r2"]
    if np.isnan(s) or np.isnan(r2):
        return -np.inf
    m = min(1.0 / s, s) if s > 0 else 0.0
    return m * r2


def calibrate_subdaily_beta_c(
    Qne: Array,
    Ta: Array,
    u2: Array,
    E_obs: Array,
    *,
    pressure: float = 101325.0,
    rh: Optional[Array] = None,
    vpd: Optional[Array] = None,
    beta_bounds: Tuple[float, float] = (0.7, 1.5),
    roughness: Optional[SurfaceRoughness] = None,
    with_stability: bool = True,
    max_iter: int = 20,
    tol: float = 1e-3,
) -> Dict[str, float]:
    """
    使用 m·R² 目标函数标定 β_c。
    Calibrate ``beta_c`` using the ``m·R²`` objective.

    参数 / Parameters
    ----------
    Qne, Ta, u2 : array_like
        可用能量 [W/m²]、气温 [K]、风速 [m/s]。/ Available energy, temperature, wind speed.
    E_obs : array_like
        观测潜热通量 [W/m²]。/ Observed latent heat flux [W/m²].
    pressure : float, optional
        大气压 [Pa]。/ Atmospheric pressure [Pa].
    rh, vpd : array_like, optional
        相对湿度或 VPD（见 ``calculate_subdaily_gcp_et`` 说明）。/ Relative humidity or VPD.
    beta_bounds : tuple, optional
        β_c 搜索范围。/ Search bounds for β_c.
    roughness : SurfaceRoughness, optional
        粗糙度参数。/ Surface roughness parameters.
    with_stability : bool, optional
        是否考虑稳定度修正。/ Whether to include stability correction.
    max_iter : int, optional
        迭代上限。/ Maximum iterations for the coupled solver.
    tol : float, optional
        收敛阈值。/ Convergence tolerance.

    返回 / Returns
    -------
    dict
        包含最优 β_c 及性能指标。/ Dictionary with best ``beta_c`` and metrics.
    """
    E_obs_arr = np.asarray(E_obs, dtype=float)

    def neg_obj(beta: float) -> float:
        res = calculate_subdaily_gcp_et(
            Qne=Qne,
            Ta=Ta,
            u2=u2,
            pressure=pressure,
            rh=rh,
            vpd=vpd,
            beta_c=beta,
            roughness=roughness,
            with_stability=with_stability,
            max_iter=max_iter,
            tol=tol,
        )
        obj = _objective_m_r2(res["E"], E_obs_arr)
        return -obj

    res_opt = minimize_scalar(
        neg_obj,
        bounds=beta_bounds,
        method="bounded",
        options=dict(xatol=1e-3),
    )
    best_beta = float(res_opt.x)

    best = calculate_subdaily_gcp_et(
        Qne=Qne,
        Ta=Ta,
        u2=u2,
        pressure=pressure,
        rh=rh,
        vpd=vpd,
        beta_c=best_beta,
        roughness=roughness,
        with_stability=with_stability,
        max_iter=max_iter,
        tol=tol,
    )
    metrics = _compute_metrics(best["E"], E_obs_arr)
    obj_best = _objective_m_r2(best["E"], E_obs_arr)

    return dict(beta_c=best_beta, objective=obj_best, **metrics)
