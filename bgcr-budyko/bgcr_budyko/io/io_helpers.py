# -*- coding: utf-8 -*-
"""
I/O helpers & indices (EN/中文)
------------------------------
- seasonal_index(P_monthly_years): compute SI by year then average (Fu & Wang 2019 style)
- save_json, load_json: tiny utilities
"""
import numpy as np, json, os

def seasonal_index(P_monthly):
    """
    Compute seasonality index (SI) from monthly precip (shape: years, 12, ...).

    中文：从（月×年）降水计算季节性指数 SI。输入为 (years, 12, ...) 形状。
    """
    P_monthly = np.asarray(P_monthly, dtype=float)
    if P_monthly.shape[1] != 12:
        raise ValueError("month axis must be length 12 (years, 12, ...)")
    years = P_monthly.shape[0]
    # annual total for each year
    P_annual = np.sum(P_monthly, axis=1, keepdims=True)
    # expected monthly mean if uniform
    P_mean_month = P_annual/12.0
    # SI per year
    diff = np.abs(P_monthly - P_mean_month)
    with np.errstate(divide='ignore', invalid='ignore'):
        SI_year = np.where(P_annual>0, np.sum(diff, axis=1)/P_annual.squeeze(1), 0.0)
    # final SI is mean over years
    return np.mean(SI_year, axis=0)

def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
