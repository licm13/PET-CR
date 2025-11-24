# -*- coding: utf-8 -*-
"""
utils.py

通用工具函数：
- 性能评估指标 (slope, R2, RMSE, Bias)
- 简单的日志打印

General utility functions:
- Performance metrics (slope, R2, RMSE, Bias)
- Simple logging helper
"""

import numpy as np
from typing import Dict


def compute_metrics(est: np.ndarray, obs: np.ndarray) -> Dict[str, float]:
    """
    计算一组估算值与观测值之间的常用误差指标。
    Compute common performance metrics between estimated and observed values.

    Args:
        est (np.ndarray): 估算值数组 / estimated values.
        obs (np.ndarray): 观测值数组 / observed values.

    Returns:
        dict: 包含 slope, r2, rmse, bias_pct 的字典。
              A dict with slope, r2, rmse, bias_pct.
    """
    mask = np.isfinite(est) & np.isfinite(obs)
    est = est[mask]
    obs = obs[mask]

    if est.size == 0:
        return dict(slope=np.nan, r2=np.nan, rmse=np.nan, bias_pct=np.nan)

    # 斜率（通过原点） / slope (through origin)
    s_num = np.sum(obs * est)
    s_den = np.sum(obs ** 2)
    slope = s_num / s_den if s_den != 0 else np.nan

    # R^2
    obs_mean = np.mean(obs)
    ss_res = np.sum((obs - est) ** 2)
    ss_tot = np.sum((obs - obs_mean) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else np.nan

    # RMSE
    rmse = np.sqrt(np.mean((obs - est) ** 2))

    # Bias (%)
    bias_pct = 100.0 * (np.mean(est) - np.mean(obs)) / np.mean(obs)

    return dict(slope=slope, r2=r2, rmse=rmse, bias_pct=bias_pct)


def objective_m_r2(est: np.ndarray, obs: np.ndarray) -> float:
    """
    目标函数：Obj = m * R^2，其中 m = min(1/s, s)
    Objective function: Obj = m * R^2, where m = min(1/s, s).

    Args:
        est (np.ndarray): 估算值 / estimated values.
        obs (np.ndarray): 观测值 / observed values.

    Returns:
        float: 目标函数值 / objective value.
    """
    metrics = compute_metrics(est, obs)
    s = metrics["slope"]
    r2 = metrics["r2"]
    if np.isnan(s) or np.isnan(r2):
        return -np.inf
    m = min(1.0 / s, s) if s > 0 else 0.0
    return m * r2


def log(msg: str):
    """
    简单的日志打印函数。
    Simple logging helper.
    """
    print(f"[GCP_LOG] {msg}")
