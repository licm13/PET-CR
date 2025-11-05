# BGCR–Budyko Evaporation Toolkit （蒸散发估算工具包）

> **Paper replicated / 论文复刻**：Diagnosing evaporation in heterogeneous alpine basins using the generalized complementary relationship model integrated with the Budyko framework （将广义互补关系与Budyko框架耦合，诊断高寒异质流域蒸散发）

**What this repo provides / 本仓库提供：**
- A clean, well-tested Python implementation of the BGCR model integrated with the Tixeront–Fu Budyko curve.
- Distributed parameterization of the Budyko `w` using precipitation seasonality (SI) and albedo (two schemes).
- Bilingual (EN/中文) docstrings & comments, and a reproducible synthetic demo of heterogeneous sub-basins.
- Publication‑ready figures (matplotlib) with Chinese label support hints.
- A minimal test suite and continuous integration boilerplate.

> 本仓库实现 BGCR 模型，并提供 w 的区域化参数方案（基于降水季节性 SI 与反照率 Albedo），包含中英文注释、复杂示例与图形输出。

---

## 1. Background / 背景简介
- **GCR (Generalized Complementary Relationship)** connects actual evaporation `E` with potential terms via non‑linear constraints.  
- **Budyko** constrains long‑term water–energy partition using aridity index.  
- **BGCR** eliminates `E/Epa` between GCR and Budyko to solve a cubic for `x = β_c E_rad / E_pa`, then derives `β_c` and `E`.

核心关系式（符号与论文一致）：
1) `E = (Epo/Epa)^2 * (2 Epa - Epo)`，其中 `Epo = β_c * E_rad`。  
2) Tixeront–Fu：`E/Epa = 1 + (P/Epa) - [1 + (P/Epa)^w]^{1/w}`。  
3) 联立得到三次方程解，进而解出 `β_c` 与 `E`。

> 注：本实现为复刻与教学演示用途，未绑定任何专有数据产品。用户可替换为自身数据。

---

## 2. Install / 安装
```bash
pip install -e .
```

## 3. Quickstart / 快速开始
```python
from bgcr_budyko.models.bgcr import bgcr_monthly
from bgcr_budyko.params.w_schemes import w_from_SI, w_from_SI_albedo

E, out = bgcr_monthly(P, Epa, Erad, w=1.6)        # 标准 BGCR（统一 w）
w_grid = w_from_SI_albedo(SI_grid, ALB_grid)      # 区域化 w
E2, out2 = bgcr_monthly(P, Epa, Erad, w=w_grid)   # 分布式 w
```

## 4. Examples / 示例
请运行 `examples/run_synthetic_demo.py` 生成：
- 8 个“子流域”合成情景（不同海拔/干湿度/季节性/反照率）
- 月尺度 1982–2022 的 `P, Epa, Erad` 合成序列
- 比较统一 w、单变量 SI、双变量 SI+Albedo 三种方案的性能与图件

> 中文字体：若系统无黑体等中文字体，请参考示例中的“字体配置”注释。

## 5. Tests / 测试
```bash
pytest -q
```

## 6. References / 参考
- Zhang et al., Journal of Hydrology, 2026. BGCR with Budyko integration (replicated here).

---

**Disclaimer / 免责声明**：
此实现依据公开文献推导式复刻，偏教学与科研试验。真实再现论文精确数值需使用原文相同数据源、插值与质量控制流程。

