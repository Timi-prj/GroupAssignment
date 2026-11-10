# CDS535 小组报告大纲

> 按 `Example_Format.pdf` 的章节结构组织，并覆盖原始作业要求。正文目标 10–12 页、字号 12。`[Ionosphere 占位]` 由 B 组补充，不与 Mushroom 混写。

## 封面

- 报告标题：Comparative Data Mining on UCI Mushroom and Ionosphere Datasets
- 课程：CDS535 - Data Mining
- Team Name、成员姓名与 Student ID、Instructor、日期
- Git 链接（如有）

## Abstract

- 研究目标：比较传统分类算法在类别型与数值型 UCI 数据集上的表现。
- 方法：预处理、分类建模、分层 10 折交叉验证与 80/20 独立切分。
- 主要结果：[Mushroom 核心结论]；[Ionosphere 占位]。
- 最终发现：[跨数据集核心结论，待两组结果汇总]。

**Keywords:** Data Mining; Classification; Mushroom; Ionosphere; Cross-validation

## Contents

自动生成目录及页码。

## 1 Group Project Requirement

### 1.1 Project Objectives and Scope

- 说明两个 UCI 数据集均完成“预处理—建模—评估”的完整流程。
- 列明分类模型、无监督组件、可视化与模型比较的总体安排。
- 说明两组在规模、属性类型、缺失情况和类别不平衡上的差异。

### 1.2 Division of Labour

| 成员 | 数据集/角色 | 具体贡献 | 工作量 |
|---|---|---|---:|
| A1 | Mushroom | 预处理、J48 | [%] |
| A2 | Mushroom | 逻辑回归、RBF-SVM、跨模型比较 | [%] |
| A3 | Mushroom | ZeroR、结果汇总、报告/PPT | [%] |
| B1 | Ionosphere | [占位] | [%] |
| B2 | Ionosphere | [占位] | [%] |
| B3 | Ionosphere | [占位] | [%] |

## 2 Introduction

### 2.1 Background and Motivation for Research

- 分类任务背景及正确识别有毒蘑菇、判断雷达回波类别的意义。
- 为什么需要同时关注 F1、ROC-AUC，而不能只看 Accuracy。

### 2.2 Research Implication

- 研究问题 1：不同算法在两个数据集上的 F1 和泛化稳定性如何？
- 研究问题 2：预处理与特征选择如何影响模型表现？
- 研究问题 3：模型性能提升是否值得额外的训练和解释成本？

### 2.3 Key Points of Innovation

- 使用统一的 `seed=42`、分层 10 折和 80/20 协议进行可复现比较。
- 将监督预处理放入折内，防止数据泄露。
- 结合 F1、错误类型、算法复杂度和可解释性进行择优。

## 3 Data Distribution and Preprocessing

### 3.1 Data Visualisation and Analysis

#### 3.1.1 Mushroom

- 数据来源：UCI 页面、DOI `10.24432/C5959T`、原始提供者与许可。
- 8124 条样本、原始 22 个类别输入特征、二分类标签。
- 类别分布：edible 4208、poisonous 3916。
- 数据质量：`stalk-root` 原始缺失 2480 条；`veil-type` 为单值属性。
- 图 1：Mushroom 类别分布；图 2：关键属性分布。
- 每图配 2–3 句结果解读。

#### 3.1.2 Ionosphere

- **[Ionosphere 占位：UCI 页面、DOI/ID、原始提供者、许可]**
- **[Ionosphere 占位：样本数、属性数与类型、类别含义和分布]**
- **[Ionosphere 占位：缺失值、噪声、冗余属性与类别不平衡]**
- **[Ionosphere 占位：类别分布图、相关性/散点图及解读]**

### 3.2 Data Preprocessing

#### 3.2.1 Mushroom

- `ReplaceMissingValues`：以众数填补缺失值，说明理由。
- `RemoveUseless`：删除单值属性 `veil-type`。
- J48 原生处理类别属性；逻辑回归与 RBF-SVM 使用 21 属性 → 115 维 One-Hot。
- J48 的 InfoGain/Wrapper 特征选择通过 `FilteredClassifier` 在折内执行。
- One-Hot 编码器仅在训练折拟合；holdout 不参与调参。
- 消融/对照：raw 与 clean 对 J48 的结果一致，预处理价值在于统一输入和支持后续模型，而非提高 J48 分数。

#### 3.2.2 Ionosphere

- **[Ionosphere 占位：至少三项过滤器/处理及参数、目的和选择理由]**
- **[Ionosphere 占位：标准化、特征选择等必须在折内完成的步骤]**
- **[Ionosphere 占位：一项预处理对比或消融实验]**

#### 3.2.3 Workflow Differences

| 步骤 | Mushroom | Ionosphere |
|---|---|---|
| 缺失值处理 | 众数填补 | [占位] |
| 属性转换 | 类别属性；部分模型 One-Hot | [占位] |
| 缩放 | 二元 One-Hot 不额外标准化 | [占位] |
| 特征选择 | J48 折内 InfoGain/Wrapper | [占位] |
| 防泄露方式 | Pipeline / FilteredClassifier | [占位] |

## 4 Basic Concepts of Algorithms

每种算法用 2–3 句说明原理，并绑定数据特征说明适用性。

- **ZeroR**：多数类基线，用于检验复杂模型是否真正学习到了类别规律。
- **J48**：通过信息增益递归分裂并剪枝，适合直接处理 Mushroom 的类别属性。
- **逻辑回归**：对 One-Hot 特征加权并输出概率，提供稳定的线性分类基准。
- **RBF-SVM**：通过最大化间隔与 RBF 核学习非线性边界，用于检验复杂边界是否带来收益。
- **[Ionosphere 占位：四种算法的原理、超参数与数据适配理由]**
- **无监督组件**：[Mushroom Apriori 或 Ionosphere SimpleKMeans/EM 占位：算法、参数与用途]。

## 5 Model Training

### 5.1 Model Initialization and Configuration

- 全局设置：`seed=42`；poisonous/正类编码方向；统一分层划分。
- 说明传统模型没有统一的 epoch/batch 设置，不使用神经网络式训练参数。

| 数据集 | 模型 | 固定参数 | 搜索参数与范围 | 最终/逐折参数位置 |
|---|---|---|---|---|
| Mushroom | ZeroR | 默认多数类规则 | 无 | 无 |
| Mushroom | J48-top9 | `C=0.25, M=2` | 折内 InfoGain top9 | J48 模型卡 |
| Mushroom | 逻辑回归 | L2、lbfgs、max_iter=5000 | `C=[0.01,0.1,1,10,100]` | holdout：C=10；CV 逐折记录 |
| Mushroom | RBF-SVM | RBF、decision_function 计算 AUC | `C=[0.1,1,10,100]`；`gamma=[scale,0.001,0.01,0.1]` | holdout：C=1、gamma=scale |
| Ionosphere | [模型 1] | [占位] | [占位] | [占位] |
| Ionosphere | [模型 2] | [占位] | [占位] | [占位] |
| Ionosphere | [模型 3] | [占位] | [占位] | [占位] |
| Ionosphere | [模型 4] | [占位] | [占位] | [占位] |

### 5.2 Training and Evaluation Protocol

- 分层 10 折交叉验证：报告各折及汇总指标。
- 分层 80/20：holdout 仅用于最终独立评估。
- sklearn 模型采用外层 10 折、内层 5 折调参；Weka 监督过滤器放入 `FilteredClassifier`。
- 曲线统一采用学习曲线，说明传统模型不统一提供逐批次 loss。

## 6 Results and Evaluation

### 6.1 Mushroom Results

- 主表：ZeroR、J48-top9、逻辑回归、RBF-SVM 的 Accuracy、Precision、Recall、F1、ROC-AUC。
- 图 3：四种模型 F1/ROC-AUC 对比。
- 图 4：代表模型混淆矩阵与 ROC 曲线；每图配 2–3 句解读。
- 核心结果：J48-top9、逻辑回归和 RBF-SVM 的 F1/AUC 均满分并列；ZeroR 有毒类 F1=0。
- 择优：按 F1 → ROC-AUC → 简单/快速，推荐逻辑回归；J48-top9 为最佳可解释替代。
- 补充 J48 五方案消融：top8 的少量漏检与 CFS 的 80 条漏检，说明属性数量不是唯一决定因素。

### 6.2 Ionosphere Results

- **[Ionosphere 占位：四模型统一指标表、混淆矩阵、ROC/AUC、学习曲线]**
- **[Ionosphere 占位：逐图 2–3 句解读与最优模型选择]**
- **[Ionosphere 占位：预处理/特征选择消融结果]**

### 6.3 Cross-dataset Comparison

| 对比维度 | Mushroom | Ionosphere | 对结果的影响 |
|---|---|---|---|
| 样本与维度 | 8124；21 类别属性 | [占位] | [占位] |
| 类别分布 | 近似平衡 | [占位] | [占位] |
| 预处理 | 类别编码/树模型原生输入 | [占位] | [占位] |
| 最优模型及 F1 | 逻辑回归（满分并列后择优） | [占位] | [占位] |
| 复杂模型是否必要 | RBF-SVM 无额外收益 | [占位] | [占位] |

- 明确回答“为什么模型 A 在一个数据集优胜、在另一个数据集不占优”。
- 区分共同规律与数据集特有能力，不把满分结果外推到现实应用。

### 6.4 Unsupervised Component

- **[占位：Apriori 或 SimpleKMeans/EM 的参数、结果表/图与解释]**
- 分类模型比较与无监督结果分开陈述，不混用指标。

## 7 Conclusion and Future Work

- 回答三个研究问题，概括两个数据集各自最优模型及选择理由。
- 局限性：基准数据规模与结构、工具间折索引差异、单次 holdout 的不确定性、结果外推限制。
- 效度威胁：预处理泄露防控、概率输出差异、跨工具运行时间不可直接比较。

### 7.1 Future Work

- 在更多规模和类别不平衡的数据集上验证结论。
- 采用统一实现的重复交叉验证与统计检验。
- 研究概率校准、阈值调整和更严格的成本敏感评估。
- **[Ionosphere 占位：针对性未来工作]**

## References and Data Provenance

- 两个 UCI 数据集的页面、DOI/ID、原始提供者、许可/使用约束。
- Weka、scikit-learn、NumPy、pandas、matplotlib 等工具文档或论文。
- J48、逻辑回归、SVM、交叉验证及无监督算法的相关文献。
- 统一引用编号与正文对应，例如 `[1]`。
