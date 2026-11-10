# A2 开发说明

## 技术方案

Python + pandas + scikit-learn + matplotlib。ARFF 解析采用项目现有 scipy 的 `arff.loadarff`，避免新增依赖。数据探索、划分生成、训练评估分别提供命令入口。

模型 Pipeline 由 `OneHotEncoder(handle_unknown='ignore')` 和分类器组成，保证编码器仅在对应训练数据拟合。One-Hot 输出保留稀疏格式，不对二元特征额外标准化。逻辑回归采用 `LogisticRegression(max_iter=5000, random_state=42)`，RBF-SVM 采用 `SVC(kernel='rbf')`。补充模型采用 `KNeighborsClassifier(metric='euclidean')`，搜索 `n_neighbors=1..20` 和 `weights=['uniform','distance']`。One-Hot 后的 Euclidean 距离只反映类别取值差异，无需对二元列做 Z-score。

KNN 方法参考 Admojo 等（2024）对蘑菇可食性二分类的研究：https://doi.org/10.56705/ijodas.v5i3.199 。该文使用二次整理的混合类型数据，结果不能直接搬到本项目；仅借鉴 One-Hot、Euclidean 距离与 k 值搜索方法。

## 运行结构

- `src/a2_mushroom/eda.py`：数据读取、统计核验、探索图和固定划分。
- `src/a2_mushroom/experiment.py`：折内调参、独立切分与嵌套交叉验证、学习曲线、预测和图表。
- `src/a2_mushroom/summarize.py`：从机器可读结果生成对比表、模型卡和图表解读。

所有输出位于 `artifacts/a2_mushroom/`。训练结果保存为 JSON/CSV，图保存为 PNG，确保汇总内容可追溯到原始输出。

## 复现命令

在项目根目录依次运行：

```bash
python src/a2_mushroom/eda.py
python src/a2_mushroom/experiment.py
python src/a2_mushroom/summarize.py
```

默认使用项目根目录的 `data/mushroom_preprocessed.arff`。可通过 `--data` 指定其他路径；实验入口支持 `--models logistic_regression rbf_svm knn` 以分模型重跑。

## 验证记录

- 首次完整实验成功完成：两个模型均完成 80/20 评估和外层 10 折、内层 5 折调参。
- 两模型在 holdout 与 10 折中的 F1、ROC-AUC 均为 1.0；混淆矩阵均为 TN=842、FP=0、FN=0、TP=783。
- 已验证每个模型有 1625 条独立测试预测、8124 条不重复的交叉验证预测和 10 条逐折指标记录；模型卡、三类结果图与汇总文件齐全。
- 独立对抗性代码审查未发现数据泄露、索引、正类或指标计算错误；随后补充数据哈希校验、并列模型选择说明和完整学习曲线纵轴。
- 环境：Windows 11、Python 3.14.6、pandas 3.0.3、NumPy 2.4.6、SciPy 1.18.0、scikit-learn 1.9.0。
- 原两模型指标来自首次完整成功实验；按用户要求不再进行耗时复跑。
- 补充 KNN 已完成 80/20 和外层 10 折、内层 5 折评估；所有外层折均选择 `k=1、weights='uniform'`，F1 与 ROC-AUC 均为 1.0。独立代码审查确认其划分、调参与指标实现无泄露或计算错误。
