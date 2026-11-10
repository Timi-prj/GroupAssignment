from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, learning_curve
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC

from eda import ARTIFACTS, ROOT, SEED, load_data


def model_spec(name: str) -> tuple[Pipeline, dict[str, list]]:
    if name == "logistic_regression":
        classifier = LogisticRegression(max_iter=5000, random_state=SEED)
        grid = {"classifier__C": [0.01, 0.1, 1, 10, 100]}
    elif name == "rbf_svm":
        classifier = SVC(kernel="rbf")
        grid = {
            "classifier__C": [0.1, 1, 10, 100],
            "classifier__gamma": ["scale", 0.001, 0.01, 0.1],
        }
    elif name == "knn":
        # One-Hot 后 Euclidean 距离的平方等于不同类别取值数的两倍，适合比较名义属性差异。
        classifier = KNeighborsClassifier(metric="euclidean")
        grid = {
            "classifier__n_neighbors": list(range(1, 21)),
            "classifier__weights": ["uniform", "distance"],
        }
    else:
        raise ValueError(f"Unknown model: {name}")
    # One-Hot 把无序类别展开为二元列，避免把类别字母误当成有大小关系的数字。
    # Pipeline 让每次交叉验证只用当前训练折拟合编码器，防止验证折的类别信息泄露。
    pipeline = Pipeline(
        [
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ("classifier", classifier),
        ]
    )
    return pipeline, grid


def metric_values(y_true: pd.Series, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def tune(pipeline: Pipeline, grid: dict[str, list], x: pd.DataFrame, y: pd.Series) -> GridSearchCV:
    # 网格搜索只在传入的训练数据上做内层 5 折：按 F1 选参数，再用全部训练数据重训。
    # 外层 10 折或 holdout 测试集不参与选参，因此评估结果不会被调参过程“偷看”。
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    search = GridSearchCV(
        pipeline,
        grid,
        scoring="f1",
        cv=inner,
        n_jobs=-1,
        refit=True,
        return_train_score=True,
    )
    search.fit(x, y)
    return search


def save_holdout_plots(
    name: str,
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    output: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay(
        confusion_matrix(y_true, y_pred), display_labels=["edible", "poisonous"]
    ).plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title(f"{name} - holdout confusion matrix")
    fig.tight_layout()
    fig.savefig(output / f"{name}_mushroom_confusion_matrix.png", dpi=200)
    plt.close(fig)

    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot(fpr, tpr, label=f"ROC-AUC = {auc:.6f}", color="#E45756")
    ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
    ax.set(
        title=f"{name} - holdout ROC curve",
        xlabel="False positive rate",
        ylabel="True positive rate",
        xlim=(0, 1),
        ylim=(0, 1.02),
    )
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output / f"{name}_mushroom_roc.png", dpi=200)
    plt.close(fig)


def save_learning_curves(
    name: str,
    pipeline: Pipeline,
    best_params: dict,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    output: Path,
) -> None:
    # 横轴是训练样本数，纵轴是不同样本规模下交叉验证的 F1/AUC，不是训练轮次。
    # 训练与验证分数的差距用于观察泛化；它不同于 mini-batch 每批更新时记录的 loss。
    pipeline.set_params(**best_params)
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, scoring, title in zip(axes, ["f1", "roc_auc"], ["F1", "ROC-AUC"]):
        sizes, train_scores, validation_scores = learning_curve(
            pipeline,
            x_train,
            y_train,
            train_sizes=np.linspace(0.2, 1.0, 5),
            cv=inner,
            scoring=scoring,
            n_jobs=-1,
        )
        curve = pd.DataFrame(
            {
                "train_size": sizes,
                "train_mean": train_scores.mean(axis=1),
                "train_std": train_scores.std(axis=1),
                "validation_mean": validation_scores.mean(axis=1),
                "validation_std": validation_scores.std(axis=1),
            }
        )
        curve.to_csv(output / f"{name}_mushroom_{scoring}_learning_curve.csv", index=False)
        for values, label, color in [
            (train_scores, "Training", "#4C78A8"),
            (validation_scores, "Validation", "#E45756"),
        ]:
            mean = values.mean(axis=1)
            std = values.std(axis=1)
            ax.plot(sizes, mean, "o-", label=label, color=color)
            ax.fill_between(sizes, mean - std, mean + std, alpha=0.15, color=color)
        lower = max(0.0, min(train_scores.min(), validation_scores.min()) - 0.02)
        ax.set(title=title, xlabel="Training instances", ylabel=title, ylim=(lower, 1.01))
        ax.legend(loc="lower right")
        ax.grid(alpha=0.2)
    fig.suptitle(f"{name} - mushroom learning curves")
    fig.tight_layout()
    fig.savefig(output / f"{name}_mushroom_curve.png", dpi=200)
    plt.close(fig)


def run_model(name: str, frame: pd.DataFrame, data_path: Path) -> None:
    start = time.perf_counter()
    output = ARTIFACTS / name
    output.mkdir(parents=True, exist_ok=True)
    x = frame.drop(columns="class")
    # 把“有毒”设为正类 p=1，可食 e=0；这样 recall、F1 和 AUC 都围绕识别有毒蘑菇解释。
    y = frame["class"].map({"e": 0, "p": 1})
    source_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    profile = json.loads((ARTIFACTS / "eda" / "data_profile.json").read_text(encoding="utf-8"))
    if profile["source_sha256"] != source_hash or profile["instances"] != len(frame):
        raise ValueError("Saved EDA/splits do not match --data; rerun eda.py with the same --data first")

    holdout = pd.read_csv(ARTIFACTS / "splits" / "holdout_80_20_seed42.csv")
    train_idx = holdout.loc[holdout["split"] == "train", "row_index"].to_numpy()
    test_idx = holdout.loc[holdout["split"] == "test", "row_index"].to_numpy()
    pipeline, grid = model_spec(name)
    search = tune(pipeline, grid, x.iloc[train_idx], y.iloc[train_idx])
    y_pred = search.predict(x.iloc[test_idx])
    # AUC 只需能排序正负样本的连续分数；decision_function 到分类边界的带符号距离即可，
    # SVM 不必额外拟合概率，分数越高表示越倾向有毒类别。
    if hasattr(search.best_estimator_, "decision_function"):
        y_score = search.decision_function(x.iloc[test_idx])
    else:
        y_score = search.predict_proba(x.iloc[test_idx])[:, 1]
    metrics = metric_values(y.iloc[test_idx], y_pred, y_score)
    write_json(
        output / "holdout_metrics.json",
        {"model": name, "protocol": "stratified 80/20", "best_params": search.best_params_, "metrics": metrics},
    )
    pd.DataFrame(search.cv_results_).to_csv(output / "holdout_grid_search.csv", index=False)
    pd.DataFrame(
        {"row_index": test_idx, "y_true": y.iloc[test_idx].to_numpy(), "y_pred": y_pred, "y_score": y_score}
    ).to_csv(output / "holdout_predictions.csv", index=False)
    save_holdout_plots(name, y.iloc[test_idx], y_pred, y_score, output)
    save_learning_curves(name, pipeline, search.best_params_, x.iloc[train_idx], y.iloc[train_idx], output)

    fold_map = pd.read_csv(ARTIFACTS / "splits" / "stratified_10fold_seed42.csv")
    fold_records = []
    cv_predictions = []
    for fold in range(10):
        fold_start = time.perf_counter()
        test_idx = fold_map.loc[fold_map["fold"] == fold, "row_index"].to_numpy()
        train_idx = fold_map.loc[fold_map["fold"] != fold, "row_index"].to_numpy()
        pipeline, grid = model_spec(name)
        search = tune(pipeline, grid, x.iloc[train_idx], y.iloc[train_idx])
        y_pred = search.predict(x.iloc[test_idx])
        if hasattr(search.best_estimator_, "decision_function"):
            y_score = search.decision_function(x.iloc[test_idx])
        else:
            y_score = search.predict_proba(x.iloc[test_idx])[:, 1]
        fold_metrics = metric_values(y.iloc[test_idx], y_pred, y_score)
        fold_records.append(
            {
                "fold": fold,
                "train_instances": len(train_idx),
                "test_instances": len(test_idx),
                "best_params": json.dumps(search.best_params_, sort_keys=True),
                "seconds": time.perf_counter() - fold_start,
                **fold_metrics,
            }
        )
        pd.DataFrame(search.cv_results_).to_csv(output / f"fold_{fold:02d}_grid_search.csv", index=False)
        cv_predictions.append(
            pd.DataFrame(
                {
                    "row_index": test_idx,
                    "fold": fold,
                    "y_true": y.iloc[test_idx].to_numpy(),
                    "y_pred": y_pred,
                    "y_score": y_score,
                }
            )
        )
        print(f"{name}: fold {fold + 1}/10 complete", flush=True)
    fold_frame = pd.DataFrame(fold_records)
    fold_frame.to_csv(output / "cv_fold_metrics.csv", index=False)
    pd.concat(cv_predictions).sort_values("row_index").to_csv(output / "cv_predictions.csv", index=False)
    metric_names = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    summary = {
        "model": name,
        "protocol": "stratified outer 10-fold with inner 5-fold tuning",
        "metrics": {
            metric: {
                "mean": float(fold_frame[metric].mean()),
                "std": float(fold_frame[metric].std(ddof=1)),
            }
            for metric in metric_names
        },
    }
    write_json(output / "cv_summary.json", summary)
    write_json(
        output / "run_metadata.json",
        {
            "seed": SEED,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "source_sha256": source_hash,
            "elapsed_seconds": time.perf_counter() - start,
        },
    )
    print(f"{name}: completed in {time.perf_counter() - start:.1f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "mushroom_preprocessed.arff")
    parser.add_argument("--models", nargs="+", choices=["logistic_regression", "rbf_svm", "knn"], default=["logistic_regression", "rbf_svm", "knn"])
    args = parser.parse_args()
    frame = load_data(args.data)
    for name in args.models:
        run_model(name, frame, args.data)


if __name__ == "__main__":
    main()
