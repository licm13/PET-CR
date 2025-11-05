# PET-CR 教学演示文稿
# PET-CR Teaching Presentation

## 概述 / Overview

本目录包含 PET-CR 库的教学演示材料，适用于课堂教学、学术讲座和培训工作坊。

This directory contains teaching presentation materials for the PET-CR library, suitable for classroom teaching, academic lectures, and training workshops.

## 文件列表 / Files

### 1. `PET-CR_Teaching_Presentation.md`

**格式 / Format**: Markdown (Marp-compatible)
**幻灯片数量 / Slides**: 40+
**时长 / Duration**: 90-120 minutes

**内容大纲 / Content Outline**:
1. 简介：ET与互补关系 (Introduction: ET & CR)
2. PET-CR库概览 (Library Overview)
3. 方法一：传统CR模型 (Method 1: Traditional CR)
4. 方法二：陆-气框架 (Method 2: Land-Atmosphere)
5. 方法三：BGCR-Budyko (Method 3: BGCR-Budyko)
6. 应用：ET归因分析 (Applications: Attribution)
7. 三种方法综合对比 (Comprehensive Comparison)
8. 代码实战 (Hands-on Coding)
9. 总结与展望 (Summary & Outlook)

## 使用方法 / Usage

### 方案1: 使用Marp转换为PowerPoint

```bash
# 安装Marp CLI
npm install -g @marp-team/marp-cli

# 转换为PowerPoint
marp PET-CR_Teaching_Presentation.md --pptx -o PET-CR_Presentation.pptx

# 转换为PDF
marp PET-CR_Teaching_Presentation.md --pdf -o PET-CR_Presentation.pdf

# 转换为HTML（带演讲者视图）
marp PET-CR_Teaching_Presentation.md --html -o PET-CR_Presentation.html
```

### 方案2: 使用Pandoc转换

```bash
# 安装Pandoc
sudo apt-get install pandoc

# 转换为PowerPoint
pandoc PET-CR_Teaching_Presentation.md -o PET-CR_Presentation.pptx

# 转换为PDF (需要LaTeX)
pandoc PET-CR_Teaching_Presentation.md -o PET-CR_Presentation.pdf
```

### 方案3: 直接在VS Code中演示

```bash
# 安装Marp for VS Code扩展
code --install-extension marp-team.marp-vscode

# 在VS Code中打开.md文件
# 按 Ctrl+Shift+P，选择 "Marp: Open Preview"
```

## 演讲者备注 / Speaker Notes

### 时间分配建议 / Suggested Time Allocation

- **简介 (Introduction)**: 10 min
- **方法一 (Method 1)**: 15 min
- **方法二 (Method 2)**: 15 min
- **方法三 (Method 3)**: 20 min
- **应用案例 (Applications)**: 15 min
- **综合对比 (Comparison)**: 10 min
- **代码实战 (Coding)**: 10 min
- **Q&A**: 10 min

**总计**: ~105 minutes

### 关键幻灯片标记 / Key Slides

**必讲 (Must Cover)**:
- Slide 2: Bouchet互补假说
- Slide 6: 三种方法架构图
- Slide 12-13: 方法一代码示例
- Slide 19: PETe vs PETa概念
- Slide 27: BGCR w参数物理意义
- Slide 38: 归因分析结果
- Slide 46: 决策树

**可选 (Optional)**:
- Slide 8: 详细对比表
- Slide 42: 空间分布代码
- 附录幻灯片 (根据听众水平决定)

## 受众定位 / Target Audience

### 适合对象 / Suitable For

✅ **研究生课程** (Graduate Course)
- 水文学、气象学、地理学专业
- 需要基础编程知识

✅ **学术讲座** (Academic Seminar)
- 研究人员和博士后
- 对蒸散发研究感兴趣

✅ **培训工作坊** (Training Workshop)
- 实践导向的代码演示
- 需要笔记本电脑和Python环境

### 前置知识要求 / Prerequisites

**最小要求 (Minimum)**:
- 基础水文学概念 (ET, 水平衡)
- Python基础语法 (变量、函数、数组)

**推荐掌握 (Recommended)**:
- Penman-Monteith方程
- NumPy数组操作
- Matplotlib绘图

## 配套材料 / Supporting Materials

### 需要准备 / Required

1. **软件环境** (Software)
   ```bash
   pip install petcr numpy matplotlib pandas
   ```

2. **示例数据** (Sample Data)
   - 位于 `/examples/data/` (如有)
   - 或使用 `petcr.generate_sample_data()`

3. **示例代码** (Example Code)
   - `/examples/compare_all_three_methods.py`
   - `/examples/example_attribution_analysis.py`

### 可选补充 / Optional

1. **图片素材** (Images)
   - 水循环示意图
   - 流程图 (可用draw.io创建)
   - 案例结果图

2. **参考文献** (References)
   - Bouchet (1963) 原文
   - Zhou & Yu (2025) Nature CC论文
   - Yang et al. (2006) GRL论文

3. **练习题** (Exercises)
   - 见 `/examples/exercises/` (待创建)

## 定制建议 / Customization Tips

### 调整难度 / Adjust Difficulty

**简化版 (简化到60分钟)**:
- 删除附录幻灯片
- 缩短代码示例
- 跳过数学推导

**深化版 (扩展到180分钟)**:
- 添加更多案例研究
- 深入讲解数学原理
- 增加实操练习时间

### 针对不同听众 / For Different Audiences

**学生 (Students)**:
- 强调基本概念
- 多展示可视化结果
- 简化数学公式

**研究人员 (Researchers)**:
- 重点讲方法对比
- 讨论不确定性
- 分享最新研究进展

**工程师 (Engineers)**:
- 聚焦应用案例
- 强调代码实现
- 讨论实际问题解决

## 反馈与改进 / Feedback & Improvement

如果您使用了这个演示文稿，欢迎反馈：
If you use this presentation, please provide feedback:

- 📧 Email: shazhou21@bnu.edu.cn
- 🐛 GitHub Issues: 报告错误或建议改进
- ⭐ GitHub: 如果觉得有用请给个星！

## 许可证 / License

本演示文稿遵循 MIT 许可证，可自由使用和修改。
This presentation is licensed under MIT License, free to use and modify.

**引用 / Citation**:
如在学术场合使用，请引用 PET-CR 库的相关论文。
When used in academic settings, please cite the relevant PET-CR papers.

---

**最后更新 / Last Updated**: 2025-01
**版本 / Version**: 1.0.0
**作者 / Authors**: PET-CR Contributors
