from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from eda import ARTIFACTS

MODEL_NAMES = {
    "logistic_regression": "逻辑回归",
    "rbf_svm": "RBF-SVM",
    "knn": "KNN",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def params_text(params: dict) -> str:
    return "、".join(f"`{key.removeprefix('classifier__')}={value}`" for key, value in params.items())


def model_card(name: str) -> str:
    output = ARTIFACTS / name
    holdout = read_json(output / "holdout_metrics.json")
    cv = read_json(output / "cv_summary.json")
    folds = pd.read_csv(output / "cv_fold_metrics.csv")
    title = MODEL_NAMES[name]
    if name == "logistic_regression":
        principle = "逻辑回归将 One-Hot 特征的加权和映射为有毒类别的概率，以 0.5 为分类阈值。L2 正则约束系数规模，降低过拟合风险。"
        suitability = "数据有 8124 条样本、21 个名义属性，One-Hot 后为 115 个二元特征，规模适合稳定的线性模型。它可检验各属性的线性加权是否足以区分两类，并提供易解释的基准。"
        limitation = "模型不能直接表达未显式构造的属性交互；若类别边界依赖复杂组合，线性假设可能限制表现。"
        params = "| solver | lbfgs（sklearn 默认） |\n| penalty | L2（sklearn 默认） |\n| max_iter | 5000 |\n| C | 内层 5 折从 0.01、0.1、1、10、100 中选择 |"
    elif name == "rbf_svm":
        principle = "RBF-SVM 寻找间隔较大的分类边界，并通过径向基核度量样本相似度，从而学习非线性边界。预测类别由决策函数符号确定，AUC 使用连续决策分数。"
        suitability = "8124 条样本和 115 个 One-Hot 特征属于中小规模高维稀疏输入，RBF 核可以学习逻辑回归未显式表达的属性交互，形成线性与非线性的直接对照。"
        limitation = "蘑菇属性没有大小关系，必须先正确编码；C 和 gamma 会影响边界复杂度，因此必须在训练折内调参，且模型系数不像逻辑回归那样直观。"
        params = "| kernel | RBF |\n| C | 内层 5 折从 0.1、1、10、100 中选择 |\n| gamma | 内层 5 折从 scale、0.001、0.01、0.1 中选择 |\n| probability | False；AUC 使用 decision_function |"
    else:
        principle = "KNN 计算待测样本与训练样本的 Euclidean 距离，由最近的 k 个邻居投票决定类别。AUC 使用有毒邻居的比例；distance 权重让更近的邻居贡献更大。"
        suitability = "One-Hot 后，两样本 Euclidean 距离的平方等于不同类别取值数的两倍，因此该距离能直接反映名义属性差异。k 和权重只在训练折内选择，与已有模型使用完全相同的划分。"
        limitation = "KNN 没有压缩训练数据的参数学习过程，预测时需保留训练样本并计算距离，数据增大时预测成本较高；无关属性也会稀释距离。方法参考 https://doi.org/10.56705/ijodas.v5i3.199 ，但该文数据版本不同，不直接引用其分数。"
        params = "| metric | Euclidean |\n| n_neighbors | 内层 5 折从 1–20 中选择 |\n| weights | 内层 5 折从 uniform、distance 中选择 |\n| AUC 输入 | predict_proba 的有毒类别比例 |"
    return f"""# {title}模型卡：Mushroom

## 原理与适用性

{principle}

{suitability}

## 超参数

| 参数 | 设置 |
|---|---|
{params}

所有输入特征在训练折内 One-Hot，`handle_unknown='ignore'`；正类为 poisonous（1），随机种子为 42。内层调参以 F1 选优。

## 实际参数与结果

- 80/20 训练部分选出的参数：{params_text(holdout['best_params'])}。
- 10 折外层各折参数见 `cv_fold_metrics.csv`，没有使用完整数据统一调参。
- Holdout F1={holdout['metrics']['f1']:.6f}，ROC-AUC={holdout['metrics']['roc_auc']:.6f}。
- 外层 10 折 F1={cv['metrics']['f1']['mean']:.6f} ± {cv['metrics']['f1']['std']:.6f}，ROC-AUC={cv['metrics']['roc_auc']['mean']:.6f} ± {cv['metrics']['roc_auc']['std']:.6f}。
- 各外层折训练耗时合计 {folds['seconds'].sum():.2f} 秒；硬件与软件版本见 `run_metadata.json`。

## 局限

{limitation}
"""


def figure_interpretations(name: str) -> str:
    output = ARTIFACTS / name
    title = MODEL_NAMES[name]
    holdout = read_json(output / "holdout_metrics.json")
    predictions = pd.read_csv(output / "holdout_predictions.csv")
    tn = int(((predictions.y_true == 0) & (predictions.y_pred == 0)).sum())
    fp = int(((predictions.y_true == 0) & (predictions.y_pred == 1)).sum())
    fn = int(((predictions.y_true == 1) & (predictions.y_pred == 0)).sum())
    tp = int(((predictions.y_true == 1) & (predictions.y_pred == 1)).sum())
    f1_curve = pd.read_csv(output / f"{name}_mushroom_f1_learning_curve.csv").iloc[-1]
    auc_curve = pd.read_csv(output / f"{name}_mushroom_roc_auc_learning_curve.csv").iloc[-1]
    gap = f1_curve.train_mean - f1_curve.validation_mean
    return f"""## {title}

### 学习曲线

文件：`../{name}/{name}_mushroom_curve.png`

最大训练规模下，验证 F1 为 {f1_curve.validation_mean:.6f}，训练与验证 F1 均值差为 {gap:.6f}；验证 ROC-AUC 为 {auc_curve.validation_mean:.6f}。两条曲线用于判断样本规模和泛化差距，不表示神经网络式逐批次 loss。

### 混淆矩阵

文件：`../{name}/{name}_mushroom_confusion_matrix.png`

独立测试集上 TN={tn}、FP={fp}、FN={fn}、TP={tp}，其中 FN 表示有毒蘑菇被误判为可食。对应 F1={holdout['metrics']['f1']:.6f}，应与交叉验证结果一起解读，避免只凭一次切分下结论。

### ROC 曲线

文件：`../{name}/{name}_mushroom_roc.png`

独立测试集 ROC-AUC 为 {holdout['metrics']['roc_auc']:.6f}，衡量模型对有毒与可食样本的排序能力。AUC 不使用固定 0.5 阈值，因此与混淆矩阵反映的是不同方面。
"""


def main() -> None:
    # 汇总脚本不重新训练模型，只读取实验产物，统一生成模型卡、对比表和图文摘要。
    summary_dir = ARTIFACTS / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    records = []
    holdouts = {}
    cvs = {}
    for name, title in MODEL_NAMES.items():
        output = ARTIFACTS / name
        holdout = read_json(output / "holdout_metrics.json")
        cv = read_json(output / "cv_summary.json")
        holdouts[name] = holdout
        cvs[name] = cv
        (output / "model_card.md").write_text(model_card(name), encoding="utf-8")
        records.append(
            {
                "model": title,
                "holdout_accuracy": holdout["metrics"]["accuracy"],
                "holdout_precision": holdout["metrics"]["precision"],
                "holdout_recall": holdout["metrics"]["recall"],
                "holdout_f1": holdout["metrics"]["f1"],
                "holdout_roc_auc": holdout["metrics"]["roc_auc"],
                "cv_accuracy_mean": cv["metrics"]["accuracy"]["mean"],
                "cv_accuracy_std": cv["metrics"]["accuracy"]["std"],
                "cv_precision_mean": cv["metrics"]["precision"]["mean"],
                "cv_precision_std": cv["metrics"]["precision"]["std"],
                "cv_recall_mean": cv["metrics"]["recall"]["mean"],
                "cv_recall_std": cv["metrics"]["recall"]["std"],
                "cv_f1_mean": cv["metrics"]["f1"]["mean"],
                "cv_f1_std": cv["metrics"]["f1"]["std"],
                "cv_roc_auc_mean": cv["metrics"]["roc_auc"]["mean"],
                "cv_roc_auc_std": cv["metrics"]["roc_auc"]["std"],
            }
        )
    # 将两种模型的同名指标整理到一张表，便于直接比较 holdout 与交叉验证结果。
    comparison = pd.DataFrame(records)
    comparison.to_csv(summary_dir / "model_comparison.csv", index=False)
    ranked = sorted(
        MODEL_NAMES,
        key=lambda name: (
            cvs[name]["metrics"]["f1"]["mean"],
            cvs[name]["metrics"]["roc_auc"]["mean"],
        ),
        reverse=True,
    )
    winner = MODEL_NAMES[ranked[0]]
    tied = all(
        cvs[name]["metrics"][metric]["mean"] == cvs[ranked[0]]["metrics"][metric]["mean"]
        for name in MODEL_NAMES
        for metric in ["f1", "roc_auc"]
    )
    selection = f"两模型 F1 与 ROC-AUC 完全并列，按小组约定的第三项标准选择更简单、更快的 **{winner}**" if tied else f"按 F1、再按 ROC-AUC 排序为 **{winner}** 优先"
    table_rows = "\n".join(
        f"| {row['model']} | {row['holdout_f1']:.6f} | {row['holdout_roc_auc']:.6f} | {row['cv_f1_mean']:.6f} ± {row['cv_f1_std']:.6f} | {row['cv_roc_auc_mean']:.6f} ± {row['cv_roc_auc_std']:.6f} |"
        for row in records
    )
    eda = read_json(ARTIFACTS / "eda" / "data_profile.json")
    interpretations = "\n\n".join(figure_interpretations(name) for name in MODEL_NAMES)
    content = f"""# A2 Mushroom 结果摘要

## 数据探索

数据包含 {eda['instances']} 条样本和 {eda['input_features']} 个名义输入特征，One-Hot 后为 {eda['one_hot_input_dimensions']} 个二元特征。edible 为 {eda['class_counts']['e']} 条（{eda['class_proportions']['e']:.2%}），poisonous 为 {eda['class_counts']['p']} 条（{eda['class_proportions']['p']:.2%}），类别近似平衡，因此不采用重采样或类别权重。当前预处理文件无缺失值和完全重复行；特征分布图同时显示若干取值极少或高度集中的属性，建模时不应把类别字母当作有顺序的数值。

探索图：`../eda/class_balance.png`、`../eda/feature_distributions.png`；探索生成入口：`../../../src/a2_mushroom/eda.py`。

## 模型对比

| 模型 | Holdout F1 | Holdout ROC-AUC | 10 折 F1（均值 ± 标准差） | 10 折 ROC-AUC（均值 ± 标准差） |
|---|---:|---:|---:|---:|
{table_rows}

基于外层 10 折均值，{selection}。这里不宣称折间差异具有统计显著性；如需显著性结论，应由全组统一进行适当统计检验。满分只说明该基准数据集在当前协议下易被区分，不代表模型可直接用于现实蘑菇鉴定。

完整 accuracy、precision、recall 见 `model_comparison.csv`，逐折参数和指标见各模型目录。

# 图表解读

{interpretations}
"""
    (summary_dir / "results_summary.md").write_text(content, encoding="utf-8")
    print(f"Summary saved to {summary_dir}")


if __name__ == "__main__":
    main()
