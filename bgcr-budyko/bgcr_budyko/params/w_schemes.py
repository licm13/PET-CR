# -*- coding: utf-8 -*-
"""
Distributed Budyko-`w` parameterization schemes (EN/中文)
--------------------------------------------------------
Two regression-based regionalization schemes (as in paper):

BGCR-1 (single variable):  w = 0.214 - 0.651*SI + 7.350*SI^2
BGCR-2 (dual variable):    w = 0.5931 + 7.0871*SI^3 + 0.0175/ALB^2

Notes:
- SI: precipitation seasonality index (dimensionless, ~0-1+)
- ALB: blue-sky albedo (0-1), clamp to avoid division issues

中文说明：
- 以下函数用于将降水季节性与反照率映射为 Budyko 参数 w；
  可接受标量或网格输入；返回与输入同形状数组。
"""
import numpy as np

def w_from_SI(SI):
    SI = np.asarray(SI, dtype=float)
    return 0.214 - 0.651*SI + 7.350*np.square(SI)

def w_from_SI_albedo(SI, ALB):
    SI = np.asarray(SI, dtype=float)
    ALB = np.asarray(ALB, dtype=float)
    ALB = np.clip(ALB, 1e-3, 1.0)  # avoid division by zero
    return 0.5931 + 7.0871*np.power(SI, 3) + 0.0175/np.square(ALB)
