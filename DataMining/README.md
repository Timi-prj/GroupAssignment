# CDS 535 Data Mining 小组项目

本目录包含 Mushroom 与 Ionosphere 两个数据集的分类实验、最终交付物和可复现材料。

## 目录导航

- `deliverables/`：最终报告、汇报 PPT、模型卡及成员提交包。`Mushroom_J48_submit/` 保留原有内部结构，复现方法见其中的 `README.md`。
- `src/`：Python 实验、可视化和 PPT 生成源码。
- `data/`：跨模型共用的预处理数据；各提交包专用的数据仍保留在对应提交包内。
- `artifacts/`：实验划分、逐折指标、预测结果、模型对比、学习曲线及其他中间结果。
- `models/`：独立提交的 Weka 模型；J48 五方案模型保留在 `deliverables/Mushroom_J48_submit/02_results/models/`。
- `docs/`：需求、实验分析、报告草稿和开发说明；原始作业要求位于 `docs/requirements/`。

## 实验口径

- 随机种子：42。
- 评估：分层 10 折交叉验证，并辅以固定 80/20 留出评估。
- 模型选择：优先 F1，其次 ROC-AUC，再次考虑模型简单程度和运行成本。
- 监督式预处理应置于训练折内部，避免数据泄露。

## 复现

在 `DataMining/` 目录运行。Mushroom 的 Python 实验步骤见 `docs/a2_development.md`，J48 五方案的 Weka 命令见 `deliverables/Mushroom_J48_submit/README.md`。Ionosphere 图表脚本使用 `deliverables/Ionoshpere_dataprocess&J48/ionosphere_preprocessed.arff`，结果输出到 `artifacts/ionosphere/`。

Python 依赖和版本记录见 `docs/a2_development.md`。PPT 生成脚本位于 `src/a2_presentation/`，其第三方依赖未收入仓库，运行前需按原开发环境安装。
