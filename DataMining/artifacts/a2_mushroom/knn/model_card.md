# KNN模型卡：Mushroom

## 原理与适用性

KNN 计算待测样本与训练样本的 Euclidean 距离，由最近的 k 个邻居投票决定类别。AUC 使用有毒邻居的比例；distance 权重让更近的邻居贡献更大。

One-Hot 后，两样本 Euclidean 距离的平方等于不同类别取值数的两倍，因此该距离能直接反映名义属性差异。k 和权重只在训练折内选择，与已有模型使用完全相同的划分。

## 超参数

| 参数 | 设置 |
|---|---|
| metric | Euclidean |
| n_neighbors | 内层 5 折从 1–20 中选择 |
| weights | 内层 5 折从 uniform、distance 中选择 |
| AUC 输入 | predict_proba 的有毒类别比例 |

所有输入特征在训练折内 One-Hot，`handle_unknown='ignore'`；正类为 poisonous（1），随机种子为 42。内层调参以 F1 选优。

## 实际参数与结果

- 80/20 训练部分选出的参数：`n_neighbors=1`、`weights=uniform`。
- 10 折外层各折参数见 `cv_fold_metrics.csv`，没有使用完整数据统一调参。
- Holdout F1=1.000000，ROC-AUC=1.000000。
- 外层 10 折 F1=1.000000 ± 0.000000，ROC-AUC=1.000000 ± 0.000000。
- 各外层折训练耗时合计 452.10 秒；硬件与软件版本见 `run_metadata.json`。

## 局限

KNN 没有压缩训练数据的参数学习过程，预测时需保留训练样本并计算距离，数据增大时预测成本较高；无关属性也会稀释距离。方法参考 https://doi.org/10.56705/ijodas.v5i3.199 ，但该文数据版本不同，不直接引用其分数。
