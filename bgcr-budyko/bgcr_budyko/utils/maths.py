# -*- coding: utf-8 -*-
"""
Math helpers (EN/中文)
----------------------------------
- cubic_root_trig: Solve depressed cubic using trigonometric form used by BGCR.
- clamp, safe_div: small numerical utils
"""
import numpy as np

def clamp(x, lo=None, hi=None):
    if lo is not None:
        x = np.maximum(x, lo)
    if hi is not None:
        x = np.minimum(x, hi)
    return x

def safe_div(a, b, eps=1e-12):
    return a / (b + eps)

def cubic_root_trig(z):
    """
    Solve x in x^3 - 2x^2 + z = 0 (BGCR form).

    中文：解三次方程 x^3 - 2x^2 + z = 0，采用论文中使用的三角形式。
    Returns x in [0,2] physically relevant branch.
    """
    z = np.asarray(z, dtype=float)
    p = -4.0/3.0
    q = (-16.0/27.0 + z)
    # trig solution ensuring principal branch
    tmp = 3*np.sqrt(3)/(2.0) * q / np.power(-p, 1.5)
    tmp = np.clip(tmp, -1.0, 1.0)
    theta = (1.0/3.0) * np.arcsin(tmp)
    x = 2.0/np.sqrt(3.0) * np.sin(theta) + 2.0/3.0
    return clamp(x, 0.0, 2.0)
