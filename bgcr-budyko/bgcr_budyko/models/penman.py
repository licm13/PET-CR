# -*- coding: utf-8 -*-
"""
Penman-like components for Epa (EN/中文)
---------------------------------------
Epa = Erad + Eaero
Erad = Δ/(Δ+γ) * Qne
Eaero = γ/(Δ+γ) * f(U2) * (es - ea)

Notes / 说明：
- Qne = (Rn - G)/Le，演示中 G≈0；Le 取 2.45e6 J/kg；若单位统一为 mm/day，需要配套系数。
- 本模块提供相对一致的量纲流，示例中使用“合成量纲”，关注相对变化与模型结构。
- 真实复刻请用与论文一致的单位体系与数据源。
"""
import numpy as np

def slope_svpc(T):
    """Slope of saturation vapor pressure curve Δ (kPa/°C). Tetens-derivative approx."""
    # es(T) kPa
    es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
    return 4098 * es / (T + 237.3)**2

def penman_components(Rn, G, T, U2, ea, es, gamma=0.066, Le=2.45e6):
    """
    Return Erad, Eaero (in consistent pseudo-units).

    中文：返回 Penman 的辐射项与动力项（示例单位）。
    参数单位需一致；示例中以相对量为主，图示比较不依赖绝对单位。
    """
    T = np.asarray(T, dtype=float)
    U2 = np.asarray(U2, dtype=float)
    ea = np.asarray(ea, dtype=float)
    es = np.asarray(es, dtype=float)
    Rn = np.asarray(Rn, dtype=float)
    G = np.asarray(G, dtype=float)

    Delta = slope_svpc(T)  # kPa/°C
    fU = 2.6*(1.0 + 0.54*U2)  # Penman empirical
    Qne = (Rn - G) / 2.45e6   # -> mm/day equivalent (approx)

    Erad = Delta/(Delta + gamma) * Qne
    Eaero = gamma/(Delta + gamma) * fU * (es - ea)
    return Erad, Eaero

def epa_from_penman(Rn, G, T, U2, ea, es):
    Erad, Eaero = penman_components(Rn, G, T, U2, ea, es)
    return Erad + Eaero, Erad, Eaero
