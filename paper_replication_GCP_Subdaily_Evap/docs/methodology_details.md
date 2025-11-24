# 附录：核心方法数学详解 (Appendix: Detailed Mathematical Methodology)

本附录总结了 Zhang et al. (2025) 中用于估算子日蒸发的核心数学公式与符号定义，
并与本代码库中的实现一一对应。

---

## 1. 广义互补原理 (Generalized Complementary Principle, GCP)

### 1.1 基本思想与变量

- 实际蒸发 (actual evaporation): \(E\)
- 平衡蒸发 (equilibrium evaporation): \(E_e\)
- 大气蒸发需求 / 表观潜在蒸发 (apparent potential evaporation): \(E_{pa}\)
- 基准蒸发 (baseline evaporation): \(\beta_c E_e\)
- 参数：\(\beta_c\) 为互补关系的标定系数。

### 1.2 平衡蒸发 (Equilibrium Evaporation)

根据 Slatyer and McIlroy (1961)，平衡蒸发定义为：

\[
E_e = \frac{\Delta}{\Delta + \gamma} Q_{ne},
\]

其中：

- \(\Delta = \dfrac{de^*}{dT}\)：饱和水汽压曲线相对于温度的斜率；
- \(\gamma\)：湿球常数 (psychrometric constant)；
- \(Q_{ne} = R_n - G\)：可用能量（净辐射减去土壤热通量）。

在本代码库中，`compute_equilibrium_evaporation` 函数实现了这一公式。

### 1.3 无量纲互补关系

引入无量纲变量：

\[
x = \frac{\beta_c E_e}{E_{pa}}, \qquad y = \frac{E}{E_{pa}},
\]

通过施加四个边界条件：

1. 当 \(x = 1\)（湿润、接近潜在条件）时：\(y = 1\) 且 \(\dfrac{dy}{dx} = 1\)；
2. 当 \(x = 0\)（极端干燥）时：\(y = 0\) 且 \(\dfrac{dy}{dx} = 0\)，

Brutsaert (2015) 推导出互补关系为三次多项式：

\[
y = 2 x^2 - x^3.
\]

换回原始变量得到广义互补关系的能量通量形式：

\[
E = \left(\frac{\beta_c E_e}{E_{pa}}\right)^2 \left(2 E_{pa} - \beta_c E_e\right).
\]

在代码中，这一公式由 `gcp_evaporation` 函数实现。

---

## 2. Penman 方程与大气蒸发需求 (Epa)

### 2.1 Penman 形式

在 GCP 框架中，大气蒸发需求 \(E_{pa}\) 通过 Penman (1948) 方程估算：

\[
E_{pa} = \frac{\Delta}{\Delta + \gamma} Q_{ne}
+ \frac{\gamma}{\Delta + \gamma} f_e(u_2) D_1,
\]

其中：

- \(D_1\)：在高度 \(z_1\) 处的水汽压亏缺 (vapor pressure deficit)；
- \(u_2\)：在高度 \(z_2\) 处的平均风速；
- \(f_e(u_2)\)：风函数，包含大气稳定度的影响。

### 2.2 风函数与稳定度修正

在子日尺度上，风函数 \(f_e(u_2)\) 写为：

\[
f_e(u_2) = \frac{0.622 k^2 u_2}{R_d T_a
\left[\ln\left(\frac{z_1 - d_0}{z_{0v}}\right) - \Psi_{sv}(\zeta)\right]
\left[\ln\left(\frac{z_2 - d_0}{z_{0m}}\right) - \Psi_{sm}(\zeta)\right]},
\]

其中：

- \(k\)：von Kármán 常数；
- \(R_d\)：干空气气体常数；
- \(T_a\)：平均气温；
- \(z_{0m}, z_{0v}\)：动量和水汽的粗糙度长度；
- \(d_0\)：零平面位移高度；
- \(\Psi_{sm}, \Psi_{sv}\)：分别为动量和水汽的稳定度修正函数；
- \(\zeta = \dfrac{z - d_0}{L}\)：稳定度参数。

本代码库使用函数 `wind_function_with_stability` 来实现这一计算。

---

## 3. Monin-Obukhov 相似理论与稳定度

### 3.1 Obukhov 长度

Obukhov 长度 \(L\) 表示浮力与机械湍流之间的平衡：

\[
L = -\frac{u_*^3 \rho}{k g \left[\dfrac{H}{T_a c_p} + 0.61 E\right]},
\]

其中：

- \(u_*\)：摩擦速度 (friction velocity)，通过  
  \[
  u_* = \frac{k u_2}{\ln\left(\frac{z - d_0}{z_{0m}}\right) - \Psi_{sm}(\zeta)}
  \]
  计算；
- \(\rho\)：空气密度；
- \(g\)：重力加速度；
- \(H\)：感热通量，按能量平衡：  
  \[
  H = Q_{ne} - E;
  \]
- \(c_p\)：定压比热；
- \(E\)：潜热通量（或按一致单位处理的蒸发通量）。

代码中，`compute_obukhov_length` 与 `compute_friction_velocity` 对应这一部分。

### 3.2 稳定 / 中性 / 不稳定情形

定义稳定度参数 \(\zeta = (z - d_0) / L\)：

1. **中性层 (Neutral, |L| ≥ 100)**  
   \[
   \Psi_{sm} = \Psi_{sv} = 0
   \]

2. **稳定层 (Stable, 0 < L < 100)**  
   使用 Cheng & Brutsaert (2005) 的形式：  
   \[
   \Psi_{sm}(\zeta) = \Psi_{sv}(\zeta)
   = -a \ln\left[\zeta + (1 + \zeta^b)^{1/b}\right],
   \]
   典型取值：\(a = 6.1, b = 2.5\)。

3. **不稳定层 (Unstable, −100 < L < 0)**  
   文中给出的形式较复杂（参见 Brutsaert, 2023），本代码提供了简化的
   Businger-Dyer 类型近似形式，实现函数 `psi_m_unstable` 和 `psi_v_unstable`，
   并在注释中注明可以替换为更精确的 Cheng & Brutsaert (2005)/Brutsaert (2023) 表达式。

---

## 4. GCP + MOST 的迭代实现

在单一时间步上，GCP 与 MOST 的耦合可写为：

\[
E = f(X, \Psi, \beta_c), \qquad \Psi = g(X, E),
\]

其中：

- \(X\)：气象与辅助变量集合，包括 \(Q_{ne}, T_a, u_2, D_1, z, d_0, z_{0m}, z_{0v}\) 等；
- \(\Psi = (\Psi_{sm}, \Psi_{sv})\)：稳定度修正函数；
- \(\beta_c\)：互补关系参数。

**数值实现步骤：**

1. 初始化 \(E^{(0)}\)（例如令 \(E^{(0)} = E_e\)）与 \(\Psi^{(0)} = 0\)（中性假设）；
2. 在第 \(k\) 次迭代：
   1. 由 \(E^{(k)}\) 计算 \(H^{(k)} = Q_{ne} - E^{(k)}\)，摩擦速度 \(u_*^{(k)}\)，Obukhov 长度 \(L^{(k)}\)，得到新的 \(\Psi^{(k+1)}\)；
   2. 由 \(\Psi^{(k+1)}\) 计算风函数 \(f_e^{(k+1)}\) 与 \(E_{pa}^{(k+1)}\)，更新平衡蒸发 \(E_e^{(k+1)}\)；
   3. 根据 GCP 公式得到新的 \(E^{(k+1)}\)：  
      \[
      E^{(k+1)} = \left(\frac{\beta_c E_e^{(k+1)}}{E_{pa}^{(k+1)}}\right)^2
      \left(2 E_{pa}^{(k+1)} - \beta_c E_e^{(k+1)}\right)
      \]
3. 若 \(|E^{(k+1)} - E^{(k)}| < \varepsilon\) 且 \(|\Psi^{(k+1)} - \Psi^{(k)}| < \varepsilon\)，则认为收敛。

代码中，`GCPWithStability.estimate_time_series` 实现了对整个时间序列的这一迭代过程。

---

## 5. 参数优化与评估指标

### 5.1 目标函数

为增强拟合斜率与相关性的双重约束，采用目标函数：

\[
\text{Obj} = m \cdot R^2, \qquad
m = \min\left(\frac{1}{s}, s\right),
\]

其中：

- \(s\)：估算 \(E_{\text{est}}\) 与观测 \(E_{\text{obs}}\) 之间的线性回归斜率（通过原点）；
- \(R^2\)：决定系数。

`GCPWithStability.calibrate_beta_c` 使用 SciPy 的 Brent 法搜索 \(\beta_c\) 以最大化 Obj。

### 5.2 评估指标

给定估算值 \(\{E_{\text{est}, i}\}\) 与观测值 \(\{E_{\text{obs}, i}\}\)：

- 斜率 (slope, 过原点)：  
  \[
  s = \frac{\sum_i E_{\text{obs}, i} E_{\text{est}, i}}{\sum_i E_{\text{obs}, i}^2}
  \]
- 决定系数：  
  \[
  R^2 = 1 - \frac{\sum_i (E_{\text{obs}, i} - E_{\text{est}, i})^2}
  {\sum_i (E_{\text{obs}, i} - \bar{E}_{\text{obs}})^2}
  \]
- 均方根误差：  
  \[
  \text{RMSE} = \sqrt{ \frac{1}{N} \sum_i (E_{\text{obs}, i} - E_{\text{est}, i})^2 }
  \]
- 平均偏差 (Bias, %)：  
  \[
  \text{Bias} (\%) =
  100 \times \frac{\bar{E}_{\text{est}} - \bar{E}_{\text{obs}}}{\bar{E}_{\text{obs}}}
  \]

这些在 `src/utils.py` 中由 `compute_metrics` 函数给出。

---

## 6. 单位与实现注意事项

- 本实现默认所有能量通量（Rn, G, H, E, Epa, Ee）使用统一单位，例如 W m⁻²；
- 水汽压与水汽压亏缺 D1 使用 kPa；
- 若希望将结果转换为水深（mm / 时间步），可通过潜热常数 \(L_v\) 与水密度 \(\rho_w\) 将能量通量转换为质量/厚度通量；
- 稳定度函数的具体形式在不同文献中略有差异，本仓库提供了可替换的模块化实现，你可以根据需要替换为原文精确形式。

---
