# 小组汇报 PPT 页序调整

## 底稿与范围

以用户提供的 `CDS535_Group_raw.pptx` 为唯一底稿。保留全部 40 张内容页、26 个实际媒体文件及原始排版，仅删除 6 张独立 SPEAKER 页。最终 `deliverables/CDS535_Group.pptx` 为 40 页，不新增 Weka 页面。

## 页序

- Mushroom：数据特征与预处理 → ZeroR 图示与基线 → J48 内部筛选 → Logistic Regression → KNN → 横向比较 → Apriori。
- Ionosphere：章节流程 → 数据与预处理 → J48 → RandomForest 与 Logistic → SVM 特征方案与 PCA → 四模型总评 → 评估协议 → KMeans。
- 保留跨数据集比较、总结和致谢。

## 角标与文字

右上角统一显示 `编号 · 英文姓名`，底框使用原稿主色 `#2563EB`。跨数据集总结页标为 GROUP。删除 A1 的 `CDS535 · DATAWARTS`、A2 的 `A2 · MUSHROOM` 和 B2 的 `Model Card · B2 HE Mingen` 旧角标，避免重复。数据集章节页删除主讲人名单，改为流程提示；目录不再列主讲人；删除依赖原页序的交接语。

## 跨数据集对比

依据报告 §6.6，将原第 44 页的独立文本框逐项改为 J48 与 Logistic Regression 的共同模型 F1、ROC-AUC 对比，保留原页面设计，并补充性能变化原因、最终模型及“归纳偏置与数据结构匹配”的结论。

## 验证

- 使用 PowerPoint 16.0 打开并导出 PDF，逐页渲染检查全部 40 页。
- 单独检查跨数据集页，确认共同模型数值和解释均正确显示。
- 对原稿和最终文件的实际媒体内容计算 SHA-256，26 个媒体文件全部逐字节一致。
- 原稿中的图片、原生图表、曲线和截图均保留；不存在 SPEAKER 页。

生成脚本：`src/reorder_group_presentation.py`。
