"""
互补关系蒸散发模型模块 / Complementary Relationship Evapotranspiration Models Module
==============================================================================

该模块提供互补关系(CR)理论下常用的蒸散发估算模型，包括Sigmoid、Polynomial、
Rescaled Power、Bouchet以及Advection-Aridity (A-A) 等形式。
This module implements widely used Complementary Relationship (CR) models for
actual evapotranspiration estimation, including Sigmoid, Polynomial, Rescaled
Power, Bouchet, and Advection-Aridity (A-A) formulations.

所有函数均采用SI单位，除非特别说明。/ All functions use SI units unless noted.
"""

import numpy as np
from typing import Optional, Union

from . import constants

ArrayLike = Union[float, np.ndarray]

def _to_numpy(value: ArrayLike) -> np.ndarray:
    """Helper to convert inputs to NumPy arrays.

    将输入转换为NumPy数组的辅助函数。

    Parameters 参数
    -------------
    value : float or np.ndarray
        Input data to be converted.
        需要转换的输入数据。

    Returns 返回
    ----------
    np.ndarray
        Converted NumPy array with float dtype.
        转换后的浮点型NumPy数组。

    Notes 说明
    ---------
    This utility standardizes handling of scalars and arrays to simplify later
    vectorised operations.
    该工具统一标量与数组的处理方式，以便执行向量化运算。
    """
    return np.asarray(value, dtype=float)


def sigmoid_cr(ep: ArrayLike,
               ew: ArrayLike,
               alpha: float = 1.26,
               beta: float = 0.5) -> ArrayLike:
    """Sigmoid Complementary Relationship model.

    Sigmoid互补关系模型，用于估算实际蒸散发量。

    Parameters 参数
    -------------
    ep : float or np.ndarray
        Potential evapotranspiration (Penman) in W m⁻² or mm d⁻¹.
        Penman潜在蒸散发，单位W m⁻²或mm d⁻¹。
    ew : float or np.ndarray
        Wet-environment evapotranspiration (Priestley-Taylor) in W m⁻² or mm d⁻¹.
        Priestley-Taylor湿环境蒸散发，单位W m⁻²或mm d⁻¹。
    alpha : float, optional
        Scaling factor kept for compatibility with literature (default 1.26).
        为与文献保持一致而保留的缩放因子（默认1.26）。
    beta : float, optional
        Shape parameter controlling curve steepness (default 0.5).
        控制曲线陡峭度的形状参数（默认0.5）。

    Returns 返回
    ----------
    float or np.ndarray
        Actual evapotranspiration in the same units as the inputs.
        与输入单位一致的实际蒸散发量。

    Notes 说明
    ---------
    The dryness index :math:`y = E_p/E_w` is converted to a smooth sigmoid
    response :math:`E_a = E_w/[1 + |y-1|^{β}]^{1/β}` that reduces Ea
    under dry conditions while keeping Ea close to Ew when y≈1.
    无量纲干燥度指数 :math:`y = E_p/E_w` 被映射为平滑的Sigmoid关系
    :math:`E_a = E_w/[1 + |y-1|^{β}]^{1/β}`，在干旱条件下降低Ea，
    而当 y≈1 时保持 Ea 接近 Ew。

    References 参考文献
    -----------------
    Han, S., & Tian, F. (2018). A review of the complementary principle of
    evaporation: From the original linear relationship to generalized nonlinear
    functions. Hydrology and Earth System Sciences, 22(3), 1813-1834.
    韩帅, 田丰. (2018). 蒸散发互补原理综述：从线性关系到非线性函数. 水文与地球系统科学.
    """
    if beta <= 0:
        raise ValueError("beta must be positive for sigmoid_cr")

    ep_arr = np.maximum(_to_numpy(ep), 0.0)  # Input validation / 输入验证
    ew_arr = np.maximum(_to_numpy(ew), 1e-6)  # Avoid zero division / 避免除零

    dryness = ep_arr / ew_arr  # Dryness index / 干燥度指数
    deviation = dryness - 1.0
    scale = np.power(1.0 + np.power(np.abs(deviation), beta), -1.0 / beta)
    scale = np.where(np.abs(deviation) < 1e-10, 1.0, scale)  # Handle y≈1 / 处理y≈1

    ea = ew_arr * scale
    return np.minimum(ea, ew_arr)  # Ensure Ea ≤ Ew / 限制Ea不超过Ew


def polynomial_cr(ep: ArrayLike,
                  ew: ArrayLike,
                  b: float = 2.0) -> ArrayLike:
    """Polynomial Complementary Relationship model.

    多项式互补关系模型，用于描述非线性互补行为。

    Parameters 参数
    -------------
    ep : float or np.ndarray
        Potential evapotranspiration (Penman) in W m⁻² or mm d⁻¹.
        Penman潜在蒸散发，单位W m⁻²或mm d⁻¹。
    ew : float or np.ndarray
        Wet-environment evapotranspiration (Priestley-Taylor) in W m⁻² or mm d⁻¹.
        Priestley-Taylor湿环境蒸散发，单位W m⁻²或mm d⁻¹。
    b : float, optional
        Polynomial exponent controlling curvature (default 2.0).
        控制曲率的多项式指数，默认值2.0。

    Returns 返回
    ----------
    float or np.ndarray
        Actual evapotranspiration matching input units.
        与输入单位一致的实际蒸散发量。

    Notes 说明
    ---------
    The formulation :math:`E_a = E_w [2 - (E_p/E_w)^b]` generalizes the Bouchet
    symmetry and reduces to Brutsaert (2015) when :math:`b=2`.
    公式 :math:`E_a = E_w [2 - (E_p/E_w)^b]` 推广了Bouchet对称关系，:math:`b=2`
    时即为Brutsaert (2015) 的表达式。

    References 参考文献
    -----------------
    Brutsaert, W. (2015). A generalized complementary principle with physical
    constraints for land-surface evaporation. Water Resources Research, 51(10),
    8087-8093. 布鲁萨特(2015). 具物理约束的互补原理推广. 水资源研究, 51(10), 8087-8093.
    """
    if b <= 0:
        raise ValueError("Polynomial exponent b must be positive")

    ep_arr = np.maximum(_to_numpy(ep), 0.0)
    ew_arr = np.maximum(_to_numpy(ew), 1e-6)
    ratio = ep_arr / ew_arr
    # Apply polynomial CR relationship / 应用多项式互补公式
    ea = ew_arr * (2.0 - np.power(ratio, b))
    # Ensure 0 <= Ea <= Ew / 确保 0 <= Ea <= Ew
    return np.clip(ea, 0.0, ew_arr)


def rescaled_power_cr(ep: ArrayLike,
                      ew: ArrayLike,
                      n: float = 0.5) -> ArrayLike:
    """Rescaled power Complementary Relationship model.

    重标度幂函数互补关系模型，适用于大尺度无校准估算。

    Parameters 参数
    -------------
    ep : float or np.ndarray
        Potential evapotranspiration (Penman) in W m⁻² or mm d⁻¹.
        Penman潜在蒸散发，单位W m⁻²或mm d⁻¹。
    ew : float or np.ndarray
        Wet-environment evapotranspiration (Priestley-Taylor) in W m⁻² or mm d⁻¹.
        Priestley-Taylor湿环境蒸散发，单位W m⁻²或mm d⁻¹。
    n : float, optional
        Power exponent controlling nonlinearity (default 0.5).
        控制非线性的幂指数，默认值0.5。

    Returns 返回
    ----------
    float or np.ndarray
        Actual evapotranspiration matching input units.
        与输入单位一致的实际蒸散发量。

    Notes 说明
    ---------
    The rescaled power relation :math:`(E_a/E_w)^n = 2 - (E_p/E_w)^n` avoids
    calibration and keeps :math:`0 ≤ E_a ≤ E_w`.
    重标度幂关系 :math:`(E_a/E_w)^n = 2 - (E_p/E_w)^n` 无需校准，并保证
    :math:`0 ≤ E_a ≤ E_w`。

    References 参考文献
    -----------------
    Szilagyi, J., Crago, R., & Qualls, R. (2017). A calibration-free formulation
    of the complementary relationship of evaporation for continental-scale
    hydrology. Journal of Geophysical Research: Atmospheres, 122(1), 264-278.
    塞拉吉等(2017). 大陆尺度蒸散发互补关系的无校准公式. 大气层JGR, 122(1), 264-278.
    """
    if n <= 0:
        raise ValueError("Exponent n must be positive")

    ep_arr = np.maximum(_to_numpy(ep), 1e-6)
    ew_arr = np.maximum(_to_numpy(ew), 1e-6)
    ratio = ep_arr / ew_arr
    x_crit = np.power(2.0, 1.0 / n)
    ratio_limited = np.minimum(ratio, x_crit)
    term = 2.0 - np.power(ratio_limited, n)
    term = np.maximum(term, 0.0)
    # Raise term to 1/n power to recover Ea/Ew / 对项取1/n次方得到Ea/Ew
    ea = ew_arr * np.power(term, 1.0 / n)
    return np.clip(ea, 0.0, ew_arr)


def bouchet_cr(ep: ArrayLike, ew: ArrayLike) -> ArrayLike:
    """Bouchet symmetric Complementary Relationship model.

    Bouchet对称互补关系模型，是最经典的线性形式。

    Parameters 参数
    -------------
    ep : float or np.ndarray
        Potential evapotranspiration (Penman) in W m⁻² or mm d⁻¹.
        Penman潜在蒸散发，单位W m⁻²或mm d⁻¹。
    ew : float or np.ndarray
        Wet-environment evapotranspiration (Priestley-Taylor) in W m⁻² or mm d⁻¹.
        Priestley-Taylor湿环境蒸散发，单位W m⁻²或mm d⁻¹。

    Returns 返回
    ----------
    float or np.ndarray
        Actual evapotranspiration with the same units as inputs.
        与输入单位一致的实际蒸散发量。

    Notes 说明
    ---------
    The linear rule :math:`E_a = 2E_w - E_p` assumes symmetric response between
    drying and wetting.
    线性公式 :math:`E_a = 2E_w - E_p` 假设干湿响应完全对称。

    References 参考文献
    -----------------
    Bouchet, R. J. (1963). Évapotranspiration réelle et potentielle,
    signification climatique. IAHS Publication 62, 134-142.
    布歇(1963). 实际与潜在蒸散发的气候意义. 国际水文科学协会文集62, 134-142.
    """
    ep_arr = _to_numpy(ep)
    ew_arr = _to_numpy(ew)
    ea = 2.0 * ew_arr - ep_arr
    # Ensure 0 <= Ea <= Ew / 确保 0 <= Ea <= Ew
    return np.clip(ea, 0.0, ew_arr)


def aa_cr(ep: ArrayLike,
          ew: ArrayLike,
          ea_min: Optional[ArrayLike] = None) -> ArrayLike:
    """Advection-Aridity (A-A) Complementary Relationship model.

    平流-干旱互补关系模型，显式区分湿润与干旱过程。

    Parameters 参数
    -------------
    ep : float or np.ndarray
        Potential evapotranspiration (Penman) in W m⁻² or mm d⁻¹.
        Penman潜在蒸散发，单位W m⁻²或mm d⁻¹。
    ew : float or np.ndarray
        Wet-environment evapotranspiration (Priestley-Taylor) in W m⁻² or mm d⁻¹.
        Priestley-Taylor湿环境蒸散发，单位W m⁻²或mm d⁻¹。
    ea_min : float or np.ndarray, optional
        Minimum ET under extremely dry conditions (default 0).
        极端干旱条件下的最小蒸散发（默认0）。

    Returns 返回
    ----------
    float or np.ndarray
        Actual evapotranspiration matching input units.
        与输入单位一致的实际蒸散发量。

    Notes 说明
    ---------
    Wet regimes (E_p ≤ E_w) keep :math:`E_a = E_w`, while dry regimes follow
    :math:`E_a = E_w [1 + (1 - E_{a,min}/E_w)(1 - E_p/E_w)]`.
    在湿润阶段 (E_p ≤ E_w) 保持 :math:`E_a = E_w`，干旱阶段遵循
    :math:`E_a = E_w [1 + (1 - E_{a,min}/E_w)(1 - E_p/E_w)]`。

    References 参考文献
    -----------------
    Brutsaert, W., & Stricker, H. (1979). An advection-aridity approach to
    estimate actual regional evapotranspiration. Water Resources Research, 15(2),
    443-450. 布鲁萨特与斯特里克(1979). 平流-干旱法估算区域实际蒸散发. 水资源研究, 15(2), 443-450.
    """
    ep_arr = np.maximum(_to_numpy(ep), 0.0)
    ew_arr = np.maximum(_to_numpy(ew), 1e-6)
    if ea_min is None:
        ea_min_arr = np.zeros_like(ep_arr)
    else:
        ea_min_arr = np.maximum(_to_numpy(ea_min), 0.0)

    ea = np.zeros_like(ep_arr)
    wet_mask = ep_arr <= ew_arr
    # Wet regime retains Ew / 湿润阶段维持Ew
    ea = np.where(wet_mask, ew_arr, ea)
    dryness_ratio = ep_arr / ew_arr
    dry_component = ew_arr * (1.0 + (1.0 - ea_min_arr / ew_arr) * (1.0 - dryness_ratio))
    # Dry regime blends toward Ea_min / 干旱阶段逐渐逼近最小蒸散发
    ea = np.where(~wet_mask, dry_component, ea)
    ea = np.clip(ea, ea_min_arr, ew_arr)
    return ea
