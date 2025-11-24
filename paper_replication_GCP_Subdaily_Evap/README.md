# A generalized Complementary Principle (GCP) Model With Atmospheric Stability Correction for Estimating Sub-Daily Evaporation

## 论文信息 (Paper Information)

* **期刊 (Journal):** Water Resources Research, 61, e2025WR040300 (2025)
* **DOI:** 10.1029/2025WR040300
* **一句话总结 (Summary):**
  * 中文：在两个澳大利亚通量站上验证了广义互补原理结合 Monin-Obukhov 稳定度修正，可在 30–60 分钟尺度准确估算陆面蒸发。
  * English: The study demonstrates that a generalized complementary principle with atmospheric stability correction can accurately estimate sub-daily land-surface evaporation at two Australian flux sites.

* **关键词 (Keywords):**
  * Complementary relationship, GCP, Penman equation, Monin-Obukhov similarity, sub-daily evaporation, OzFlux, eddy covariance.

---

## 复现说明 (Replication Note)

本代码库旨在（最大程度地）复现 Zhang et al. (2025, WRR) 一文中提出的：  
> “广义互补原理 (GCP) + Monin-Obukhov 稳定度修正” 子日尺度蒸发估算方法。

This repository aims to (to the best extent possible) replicate the sub-daily evaporation estimation method based on
a generalized complementary principle (GCP) with atmospheric stability corrections, as described in Zhang et al. (2025, WRR).

* **复现状态 (Replication Status):**
  * ✅ 已实现：数据预处理框架、GCP 模型、MOST 稳定度修正、βc 优化、性能评估与主要图形绘制。
  * ⏳ 待完善：根据实际 OZFlux 数据字段名调整 I/O、补充更多站点与敏感性试验。

* **主要差异 (Known Deviations):**
  * 原文使用 R 语言实现参数优化，本库采用 Python + SciPy 的 Brent 法实现一维搜索；
  * 稳定度修正函数采用文献中给出的形式与通用 Businger-Dyer 形式的组合，可能与作者 R 代码中的具体实现细节存在细微差异；
  * 由于原始、完全相同的 QC 和能量闭合处理过程不可获得，预处理部分提供了可扩展框架和占位函数，你需要按实际数据格式做少量修改。

---

## 核心方法与数学描述 (Core Methodology & Mathematical Description)

本文基于 **广义互补原理 (Generalized Complementary Principle, GCP)**，使用  
**平衡蒸发 (equilibrium evaporation, Ee)**、**大气蒸发需求 (apparent potential evaporation, Epa)** 与  
**实际蒸发 (actual evaporation, E)** 之间的非线性互补关系来估算陆面蒸发：

\[
E = \left(\frac{\beta_c E_e}{E_{pa}}\right)^2 \left(2 E_{pa} - \beta_c E_e\right)
\]

其中：

* \(E_e = \dfrac{\Delta}{\Delta + \gamma} Q_{ne}\) 为平衡蒸发，\(\Delta\) 为饱和水汽压曲线斜率，\(\gamma\) 为湿球常数，
  \(Q_{ne} = R_n - G\) 为可用能量；
* \(E_{pa}\) 使用带 Monin-Obukhov 稳定度修正的 Penman 方程估算；
* \(\beta_c\) 为待标定的互补关系参数。

The key idea is that actual evaporation from a drying surface and evaporation from a small wet patch in the same
environment (apparent potential evaporation) exhibit a generalized complementary relationship around a baseline
evaporation \(\beta_c E_e\).

> **详细数学推导、所有公式和符号解释请见：**  
> `docs/methodology_details.md`

---

## 分析工作流 (Analysis Workflow)

本仓库严格对应论文中的分析路径，分为如下步骤：

1. **数据预处理 (Data Preprocessing)**
   * 输入 (Input):
     * `data/raw/tumbarumba_raw.csv`
     * `data/raw/daly_river_pasture_raw.csv`
   * 主要操作 (Main operations):
     * 解析时间戳、筛选子日时间步（30 或 60 分钟）；
     * 读取通量与气象变量（Rn, G, Ta, RH, wind speed, LE 等）；
     * 计算可用能量 \(Q_{ne} = R_n - G\)；
     * 计算水汽压亏缺 D1 (根据 Ta 和 RH)，统一单位；
     * 生成包含 `Qne, Ta, u2, D1, E_obs` 等字段的 DataFrame，并写入 `data/processed/`。
   * 对应脚本 (Script):
     * `src/01_data_preprocessing.py`
   * 输出 (Output):
     * `data/processed/tumbarumba_subdaily.csv`
     * `data/processed/daly_river_pasture_subdaily.csv`

2. **模型定义 (Model Definition)**
   * 核心内容：
     * GCP 非线性互补关系；
     * Penman 方程估算 Epa；
     * Monin-Obukhov 稳定度修正（Obukhov 长度、稳定度函数）；
     * 单步时间的迭代求解 (E, stability)。
   * 对应脚本：
     * `src/model_definition.py`（核心实现）
     * `src/02_model_definition.py`（薄包装以符合 01/02/03/04 命名结构）

3. **参数优化与批量运行 (Model Calibration & Batch Runs)**
   * 对每个站点：
     * 读取预处理数据；
     * 使用 Brent 法搜索 \(\beta_c\)，最大化 Obj = m·R²；
     * 计算性能指标（斜率、R²、RMSE、Bias%）；
     * 保存估算的子日 E、无量纲变量以及统计结果。
   * 对应脚本：
     * `src/03_analysis_workflow.py`

4. **可视化 (Visualization)**
   * 再现（或近似）论文中的关键图形：
     * 平均日变化曲线 (E_obs vs E_est, 中性 vs 含稳定度修正)；
     * 子日 E_est vs E_obs 散点/hexbin；
     * 无量纲互补曲线 \(E/E_{pa}\) vs \(\beta_c E_e / E_{pa}\)；
     * 稳定度对风函数的影响示意图等。
   * 对应脚本：
     * `src/04_visualization.py`
   * 输出：
     * `results/figures/` 中的 PNG / PDF 图像

---

## 数据 (Data)

> ⚠️ 注意：本仓库不直接包含 OZFlux 原始数据，只提供数据接口与预处理框架。

| 数据名称 (Data Name) | 站点 (Site) | 来源 (Source) | 分辨率 (Resolution) | 时段 (Period) | 访问 (Access) |
|----------------------|------------|----------------|----------------------|----------------|----------------|
| OzFlux Tumbarumba flux data | Tumbarumba (Eucalyptus forest) | OZFlux / FLUXNET | 60 min | 2008-08 – 2009-07 | 通过 OZFlux 注册仓库 (DOI: 10.17616/R3M04W) 下载 |
| OzFlux Daly River Pasture flux data | Daly River Pasture (pasture) | OZFlux / FLUXNET | 30 min | 2011-07 – 2012-06 | 同上 |

在实际使用中，请下载相应的 NetCDF/CSV 文件并放到 `data/raw/`，然后根据字段名更新  
`src/01_data_preprocessing.py` 中的列名映射。

---

## 如何运行 (How to Run)

### 1. 克隆仓库 (Clone Repo)

```bash
git clone https://github.com/your_username/paper_replication_GCP_Subdaily_Evap.git
cd paper_replication_GCP_Subdaily_Evap
```

### 2. 创建环境并安装依赖 (Create Environment & Install Dependencies)

```bash
conda create -n gcp_evap python=3.10
conda activate gcp_evap
pip install -r requirements.txt
```

### 3. 下载数据并放置 (Download Data)

1. 前往 OZFlux / FLUXNET 数据仓库（OZFlux network, DOI: 10.17616/R3M04W）；
2. 下载 Tumbarumba 与 Daly River Pasture 的通量站点数据（例如 NetCDF 或 CSV）；
3. 将文件放入：

```text
data/raw/tumbarumba_raw.csv
data/raw/daly_river_pasture_raw.csv
```

4. 在 `src/01_data_preprocessing.py` 中调整列名映射以匹配实际文件格式。

### 4. 执行工作流 (Run Workflow)

```bash
# 步骤 1: 预处理数据
python src/01_data_preprocessing.py

# 步骤 2: 模型标定与估算 (包括 βc 优化)
python src/03_analysis_workflow.py

# 步骤 3: 生成图表与表格
python src/04_visualization.py
```

生成的中间结果与图表将保存在：

```text
data/processed/
results/figures/
results/tables/
```

---

## 引用 (Citation)

如果你在研究中使用了本代码库，请引用原始论文：

> Zhang, L., Qin, S., & Brutsaert, W. (2025). A generalized complementary principle (GCP) model with atmospheric stability correction for estimating sub-daily evaporation. *Water Resources Research*, 61, e2025WR040300. https://doi.org/10.1029/2025WR040300
