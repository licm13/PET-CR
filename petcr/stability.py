"""
大气稳定度与摩阻速度工具 / Atmospheric stability and friction velocity utilities.

本模块实现 Monin-Obukhov 相似理论中的常用稳定度修正和相关辅助计算，
包括稳定与不稳定条件下的 ψ 函数、Obukhov 长度和摩阻速度计算。

This module implements common stability corrections from Monin-Obukhov Similarity
Theory (MOST), including stability correction functions for stable/unstable
conditions, Obukhov length, and friction velocity calculations.

所有函数均使用 SI 单位 (温度: K, 气压: Pa) 并依赖 petcr.constants 中的
物理常数，以保证全库的一致性。
All functions use SI units (temperature: K, pressure: Pa) and rely on
physical constants from ``petcr.constants`` to ensure consistency across the
library.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from . import constants

Array = np.ndarray


def psi_stable(zeta: Array, a: float = 6.1, b: float = 2.5) -> Array:
    """
    稳定层的稳定度修正函数。/ Stability correction for stable conditions.

    参数 / Parameters
    ----------
    zeta : np.ndarray
        无量纲稳定度参数 (z/L)。/ Dimensionless stability parameter (z/L).
    a : float, optional
        Cheng & Brutsaert (2005) 系数。/ Parameter ``a`` from Cheng & Brutsaert (2005).
    b : float, optional
        Cheng & Brutsaert (2005) 系数。/ Parameter ``b`` from Cheng & Brutsaert (2005).

    返回 / Returns
    -------
    np.ndarray
        ψ_m 或 ψ_h 的稳定度修正值。/ Stability correction value.
    """
    zeta = np.maximum(zeta, constants.EPSILON_SAFE_DIV)
    return -a * np.log(zeta + (1.0 + zeta ** b) ** (1.0 / b))


def psi_unstable_m(zeta: Array) -> Array:
    """
    不稳定层动量的稳定度修正。/ Stability correction for momentum under unstable conditions.

    参数 / Parameters
    ----------
    zeta : np.ndarray
        无量纲稳定度参数 (z/L)。/ Dimensionless stability parameter (z/L).

    返回 / Returns
    -------
    np.ndarray
        动量修正 ψ_m。/ Momentum stability correction ψ_m.
    """
    x = (1.0 - 16.0 * zeta) ** 0.25
    return (
        2.0 * np.log((1.0 + x) / 2.0)
        + np.log((1.0 + x ** 2) / 2.0)
        - 2.0 * np.arctan(x)
        + np.pi / 2.0
    )


def psi_unstable_v(zeta: Array) -> Array:
    """
    不稳定层标量（如水汽）的稳定度修正。/ Stability correction for scalars under unstable conditions.

    参数 / Parameters
    ----------
    zeta : np.ndarray
        无量纲稳定度参数 (z/L)。/ Dimensionless stability parameter (z/L).

    返回 / Returns
    -------
    np.ndarray
        标量修正 ψ_h/ψ_v。/ Scalar stability correction ψ_h/ψ_v.
    """
    x = (1.0 - 16.0 * zeta) ** 0.25
    return 2.0 * np.log((1.0 + x ** 2) / 2.0)


def compute_friction_velocity(
    u2: Array,
    z: float,
    d0: float,
    z0m: float,
    psi_m: Array,
    karman: float = constants.KARMAN,
) -> Array:
    """
    计算摩阻速度 u*。/ Compute friction velocity ``u*``.

    参数 / Parameters
    ----------
    u2 : np.ndarray
        2 m 高度风速 [m/s]。/ Wind speed at measurement height [m/s].
    z : float
        测量高度 [m]。/ Measurement/reference height [m].
    d0 : float
        零平面位移 [m]。/ Zero-plane displacement height [m].
    z0m : float
        动量粗糙度长度 [m]。/ Roughness length for momentum [m].
    psi_m : np.ndarray
        动量稳定度修正。/ Momentum stability correction.
    karman : float, optional
        von Karman 常数。/ von Karman constant.

    返回 / Returns
    -------
    np.ndarray
        摩阻速度 [m/s]。/ Friction velocity [m/s].
    """
    denom = np.log((z - d0) / z0m) - psi_m
    denom = np.where(np.abs(denom) < constants.EPSILON_SAFE_DIV, constants.EPSILON_SAFE_DIV, denom)
    return karman * u2 / denom


def compute_obukhov_length(
    u_star: Array,
    Qne: Array,
    E: Array,
    ta_kelvin: Array,
    pressure: float,
    cp_air: float = constants.CP_AIR,
    gravity: float = constants.G,
    karman: float = constants.KARMAN,
    air_density: Optional[Array] = None,
) -> Array:
    """
    计算 Obukhov 长度 L。/ Compute Obukhov length ``L``.

    参数 / Parameters
    ----------
    u_star : np.ndarray
        摩阻速度 [m/s]。/ Friction velocity [m/s].
    Qne : np.ndarray
        可用能量 [W/m²]。/ Available energy [W/m²].
    E : np.ndarray
        潜热通量 (GCP 估计) [W/m²]。/ Latent heat flux estimate [W/m²].
    ta_kelvin : np.ndarray
        气温 [K]。/ Air temperature [K].
    pressure : float
        大气压 [Pa]。/ Atmospheric pressure [Pa].
    cp_air : float, optional
        空气定压比热 [J/(kg·K)]。/ Specific heat of air [J/(kg·K)].
    gravity : float, optional
        重力加速度 [m/s²]。/ Gravitational acceleration [m/s²].
    karman : float, optional
        von Karman 常数。/ von Karman constant.
    air_density : np.ndarray, optional
        预先计算的空气密度 [kg/m³]。如果为 None，将使用理想气体定律计算。
        Pre-computed air density [kg/m³]; computed via ideal gas law if None.

    返回 / Returns
    -------
    np.ndarray
        Obukhov 长度 [m]，符号遵循 MOST 约定。/ Obukhov length [m].
    """
    if air_density is None:
        air_density = pressure / (constants.R_SPECIFIC_DRY_AIR * ta_kelvin)

    sensible_heat = Qne - E
    denom = (sensible_heat / (ta_kelvin * cp_air)) + (0.61 * E / (air_density * cp_air))
    denom = np.where(np.abs(denom) < constants.EPSILON_SAFE_DIV, constants.EPSILON_SAFE_DIV, denom)

    return -(air_density * cp_air * ta_kelvin * u_star ** 3) / (karman * gravity * denom)
