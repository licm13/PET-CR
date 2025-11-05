# -*- coding: utf-8 -*-
"""
BGCR model (EN/中文)
====================
Implements monthly BGCR evaporation:
- Penman-like apparent potential evaporation Epa = Erad + Eaero
- Epo = β_c * Erad
- Combine with Budyko (Tixeront–Fu) to eliminate E/Epa, solve cubic for x = β_c Erad / Epa
- Then compute β_c and E

变量定义（与论文一致，单位按输入约定）：
- P    : precipitation (同时间尺度的总量) / 降水
- Epa  : apparent potential evaporation / 表观潜在蒸发
- Erad : radiation term from Penman / 辐射项
- w    : Budyko 参数（可为标量或网格/时空变化）

注意：输入可为 np.ndarray（可广播），输出同形状。
"""
import numpy as np
from .penman import penman_components
from ..utils.maths import cubic_root_trig, safe_div, clamp

def budyko_tixeront_fu_ratio(P, Epa, w):
    """
    Return y = E/Epa per Tixeront–Fu.
    y = 1 + (P/Epa) - [1 + (P/Epa)^w]^{1/w}
    中文：返回 Budyko 曲线给出的蒸发率比值。
    """
    Phi = safe_div(P, Epa)  # P/Epa
    term = np.power(1.0 + np.power(Phi, w), 1.0/w)
    y = 1.0 + Phi - term
    return clamp(y, 0.0, 1.0)  # physically 0..1

def _beta_c_from_cubic(P, Epa, Erad, w):
    """Compute β_c using the cubic solution (Eq. (14) equivalence)."""
    Phi = safe_div(P, Epa)  # AI-1 + 1 actually P/Epa
    # z = 1 + Phi - [1 + Phi^w]^(1/w)
    z = 1.0 + Phi - np.power(1.0 + np.power(Phi, w), 1.0/w)
    x = cubic_root_trig(z)
    beta_c = safe_div(Epa, Erad) * x
    return beta_c, x

def bgcr_monthly(P, Epa, Erad, w):
    """
    Compute monthly evaporation E by BGCR.

    Parameters
    ----------
    P, Epa, Erad : array-like
        Monthly precipitation, apparent potential evaporation, radiation term.
    w : float or array-like
        Budyko parameter (can be distributed).

    Returns
    -------
    E : array-like
        Estimated evaporation.
    out : dict
        Diagnostics, including beta_c and ratio.
    """
    P = np.asarray(P, dtype=float)
    Epa = np.asarray(Epa, dtype=float)
    Erad = np.asarray(Erad, dtype=float)
    w = np.asarray(w, dtype=float)

    beta_c, x = _beta_c_from_cubic(P, Epa, Erad, w)
    # E/Epa from Budyko:
    y = budyko_tixeront_fu_ratio(P, Epa, w)
    E = y * Epa
    return E, {"beta_c": beta_c, "x": x, "ratio": y}

