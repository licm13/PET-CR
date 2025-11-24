# -*- coding: utf-8 -*-
"""
model_definition.py

广义互补原理 (GCP) + Monin-Obukhov 稳定度修正的核心模型定义。

Core model definition of:
- Generalized Complementary Principle (GCP)
- Monin-Obukhov Similarity Theory (MOST) based stability corrections
"""

from dataclasses import dataclass
from typing import Tuple, Dict

import numpy as np
from scipy.optimize import minimize_scalar

from utils import compute_metrics, objective_m_r2, log


# 物理常数 / Physical constants
KARMAN = 0.4          # von Karman constant
G = 9.81              # gravity (m/s^2)
P_ATM_KPA = 101.3     # standard pressure (kPa)
CP = 1004.0           # specific heat of air at constant pressure (J/kg/K)
RD = 287.0            # gas constant for dry air (J/kg/K)
RHO_AIR = 1.225       # air density (kg/m3)
LV = 2.45e6           # latent heat of vaporization (J/kg)


def saturation_vapor_pressure_kpa(ta_c: np.ndarray) -> np.ndarray:
    """Same as in preprocessing; duplicated here for independence."""
    return 0.6108 * np.exp(17.27 * ta_c / (ta_c + 237.3))


def slope_svp_kpa_per_c(ta_c: np.ndarray) -> np.ndarray:
    """
    计算饱和水汽压曲线斜率 Δ (kPa/℃)
    Compute slope of saturation vapor pressure curve Δ (kPa/degC).
    """
    es = saturation_vapor_pressure_kpa(ta_c)
    return 4098.0 * es / (ta_c + 237.3) ** 2


def psychrometric_constant_kpa_per_c(p_kpa: float = P_ATM_KPA) -> float:
    """
    计算湿球常数 γ (kPa/℃)。
    Compute psychrometric constant γ (kPa/degC).
    """
    return (CP * p_kpa) / (0.622 * LV) / 1000.0  # J->kPa·degC approx


def compute_equilibrium_evaporation(Qne: np.ndarray, Ta_C: np.ndarray) -> np.ndarray:
    """
    计算平衡蒸发 Ee（以能量通量单位, 如 W/m2）。
    Compute equilibrium evaporation Ee (in energy flux units, e.g., W/m2).
    """
    Delta = slope_svp_kpa_per_c(Ta_C)
    gamma = psychrometric_constant_kpa_per_c()
    coeff = Delta / (Delta + gamma)
    return coeff * Qne


def psi_stable(zeta: np.ndarray, a: float = 6.1, b: float = 2.5) -> np.ndarray:
    """
    稳定层稳定度修正函数 (Cheng & Brutsaert 2005).
    Stability correction for stable conditions.
    """
    zeta = np.maximum(zeta, 1e-6)
    return -a * np.log(zeta + (1.0 + zeta ** b) ** (1.0 / b))


def psi_unstable_m(zeta: np.ndarray) -> np.ndarray:
    """
    不稳定层的动量稳定度修正函数 (Businger-Dyer 形式近似)。
    Stability correction for momentum under unstable conditions.
    """
    x = (1.0 - 16.0 * zeta) ** 0.25
    return (
        2.0 * np.log((1.0 + x) / 2.0)
        + np.log((1.0 + x ** 2) / 2.0)
        - 2.0 * np.arctan(x)
        + np.pi / 2.0
    )


def psi_unstable_v(zeta: np.ndarray) -> np.ndarray:
    """
    不稳定层的标量（如水汽）稳定度修正函数 (Businger-Dyer 形式)。
    Stability correction for scalars (e.g., humidity) under unstable conditions.
    """
    x = (1.0 - 16.0 * zeta) ** 0.25
    return 2.0 * np.log((1.0 + x ** 2) / 2.0)


def compute_friction_velocity(
    u2: np.ndarray,
    z: float,
    d0: float,
    z0m: float,
    psi_m: np.ndarray,
) -> np.ndarray:
    """
    计算摩擦速度 u*。
    Compute friction velocity u*.
    """
    denom = np.log((z - d0) / z0m) - psi_m
    denom = np.where(np.abs(denom) < 1e-6, 1e-6, denom)
    return KARMAN * u2 / denom


def compute_obukhov_length(
    u_star: np.ndarray,
    Qne: np.ndarray,
    E: np.ndarray,
    Ta_C: np.ndarray,
    rho_air: float = RHO_AIR,
) -> np.ndarray:
    """
    计算 Obukhov 长度 L。
    Compute Obukhov length L.
    """
    Ta_K = Ta_C + 273.15
    H = Qne - E  # sensible heat flux
    denom = (H / (Ta_K * CP) + 0.61 * E / (rho_air * CP))
    denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)

    return -(rho_air * CP * Ta_K * u_star ** 3) / (KARMAN * G * denom)


def wind_function_with_stability(
    u2: np.ndarray,
    Ta_C: np.ndarray,
    z: float,
    d0: float,
    z0m: float,
    z0v: float,
    psi_m: np.ndarray,
    psi_v: np.ndarray,
) -> np.ndarray:
    """
    计算含稳定度修正的风函数 f_e(u2)。
    Compute wind function with stability corrections f_e(u2).
    """
    Ta_K = Ta_C + 273.15
    num = 0.622 * KARMAN ** 2 * u2
    denom = (
        RD * Ta_K
        * (np.log((z - d0) / z0v) - psi_v)
        * (np.log((z - d0) / z0m) - psi_m)
    )
    denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
    return num / denom


def gcp_evaporation(beta_c: float, Ee: np.ndarray, Epa: np.ndarray) -> np.ndarray:
    """
    根据 GCP 公式计算实际蒸发 E。
    Compute actual evaporation E from GCP formula.
    """
    Epa_safe = np.where(Epa <= 1e-6, 1e-6, Epa)
    x = beta_c * Ee / Epa_safe
    x = np.clip(x, 0.0, 1.0)
    E = x ** 2 * (2.0 * Epa_safe - beta_c * Ee)
    E = np.maximum(E, 0.0)
    return E


@dataclass
class GCPWithStability:
    """
    GCP + MOST 模型配置。

    Configuration for GCP + MOST model.

    Attributes:
        z (float): 测量高度 (m) / reference height.
        d0 (float): 零平面位移高度 (m) / zero-plane displacement height.
        z0m (float): 动量粗糙度长度 (m) / roughness length for momentum.
        z0v (float): 水汽粗糙度长度 (m) / roughness length for vapor.
        p_kpa (float): 大气压 (kPa) / air pressure.
    """
    z: float
    d0: float
    z0m: float
    z0v: float
    p_kpa: float = P_ATM_KPA

    def _compute_penman_epa(
        self,
        Qne: np.ndarray,
        Ta_C: np.ndarray,
        D1_kpa: np.ndarray,
        u2: np.ndarray,
        E: np.ndarray,
        with_stability: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        由给定的 E 和稳定度假设计算 Epa。

        Compute Epa given provisional E and stability assumption.

        Returns:
            Epa, psi_m, psi_v
        """
        Delta = slope_svp_kpa_per_c(Ta_C)
        gamma = psychrometric_constant_kpa_per_c(self.p_kpa)

        if with_stability:
            psi_m = np.zeros_like(Qne)
            psi_v = np.zeros_like(Qne)

            for _ in range(3):
                u_star = compute_friction_velocity(
                    u2=u2,
                    z=self.z,
                    d0=self.d0,
                    z0m=self.z0m,
                    psi_m=psi_m,
                )
                L = compute_obukhov_length(
                    u_star=u_star,
                    Qne=Qne,
                    E=E,
                    Ta_C=Ta_C,
                    rho_air=RHO_AIR,
                )
                zeta = (self.z - self.d0) / L
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
        else:
            psi_m = np.zeros_like(Qne)
            psi_v = np.zeros_like(Qne)

        fe = wind_function_with_stability(
            u2=u2,
            Ta_C=Ta_C,
            z=self.z,
            d0=self.d0,
            z0m=self.z0m,
            z0v=self.z0v,
            psi_m=psi_m,
            psi_v=psi_v,
        )

        rad_term = Delta / (Delta + gamma) * Qne
        aero_term = gamma / (Delta + gamma) * fe * D1_kpa
        Epa = rad_term + aero_term

        return Epa, psi_m, psi_v

    def estimate_time_series(
        self,
        Qne: np.ndarray,
        Ta_C: np.ndarray,
        D1_kpa: np.ndarray,
        u2: np.ndarray,
        beta_c: float,
        max_iter: int = 20,
        tol: float = 1e-3,
        with_stability: bool = True,
    ) -> Dict[str, np.ndarray]:
        """
        对整段时间序列估算 GCP 蒸发（带/不带稳定度修正）。
        Estimate GCP evaporation for a full time series with/without stability.
        """
        n = len(Qne)
        Ee = compute_equilibrium_evaporation(Qne, Ta_C)

        E = Ee.copy()
        psi_m = np.zeros(n)
        psi_v = np.zeros(n)

        for it in range(max_iter):
            E_old = E.copy()
            Epa, psi_m, psi_v = self._compute_penman_epa(
                Qne=Qne,
                Ta_C=Ta_C,
                D1_kpa=D1_kpa,
                u2=u2,
                E=E,
                with_stability=with_stability,
            )
            Ee = compute_equilibrium_evaporation(Qne, Ta_C)
            E = gcp_evaporation(beta_c=beta_c, Ee=Ee, Epa=Epa)

            diff = np.nanmax(np.abs(E - E_old))
            if diff < tol:
                log(
                    f"GCP iteration converged in {it+1} steps "
                    f"(with_stability={with_stability}).",
                )
                break

        return dict(E=E, Epa=Epa, Ee=Ee, psi_m=psi_m, psi_v=psi_v)

    def calibrate_beta_c(
        self,
        Qne: np.ndarray,
        Ta_C: np.ndarray,
        D1_kpa: np.ndarray,
        u2: np.ndarray,
        E_obs: np.ndarray,
        beta_bounds: Tuple[float, float] = (0.7, 1.5),
        with_stability: bool = True,
    ) -> Dict[str, float]:
        """
        使用 Brent 一维搜索标定 βc，使 Obj = m * R^2 最大。

        Calibrate beta_c using Brent search to maximize Obj = m * R^2.
        """

        def neg_obj(beta: float) -> float:
            res = self.estimate_time_series(
                Qne=Qne,
                Ta_C=Ta_C,
                D1_kpa=D1_kpa,
                u2=u2,
                beta_c=beta,
                with_stability=with_stability,
                max_iter=20,
            )
            E_est = res["E"]
            obj = objective_m_r2(E_est, E_obs)
            return -obj

        log(
            f"Start calibrating beta_c in {beta_bounds} "
            f"(with_stability={with_stability}) ...",
        )
        res_opt = minimize_scalar(
            neg_obj,
            bounds=beta_bounds,
            method="bounded",
            options=dict(xatol=1e-3),
        )
        best_beta = float(res_opt.x)

        res_best = self.estimate_time_series(
            Qne=Qne,
            Ta_C=Ta_C,
            D1_kpa=D1_kpa,
            u2=u2,
            beta_c=best_beta,
            with_stability=with_stability,
            max_iter=20,
        )
        metrics = compute_metrics(res_best["E"], E_obs)
        obj_best = -float(res_opt.fun)

        log(
            f"Calibrated beta_c={best_beta:.3f}, "
            f"Obj={obj_best:.3f}, slope={metrics['slope']:.2f}, "
            f"R2={metrics['r2']:.2f}, RMSE={metrics['rmse']:.2f}, "
            f"Bias={metrics['bias_pct']:.2f}%.",
        )

        return dict(
            beta_c=best_beta,
            obj=obj_best,
            **metrics,
        )
