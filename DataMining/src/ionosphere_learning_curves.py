from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, learning_curve, train_test_split
from sklearn.tree import DecisionTreeClassifier

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "deliverables" / "Ionoshpere_dataprocess&J48" / "ionosphere_preprocessed.arff"
OUTPUT = ROOT / "artifacts" / "ionosphere" / "unified_curves"


def save_curve(name: str, estimator, x: pd.DataFrame, y: pd.Series) -> None:
    train_idx, _ = train_test_split(
        np.arange(len(x)), test_size=0.2, random_state=SEED, stratify=y
    )
    x_train = x.iloc[train_idx]
    y_train = y.iloc[train_idx]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, scoring, title in zip(axes, ["f1", "roc_auc"], ["F1", "ROC-AUC"]):
        sizes, train_scores, validation_scores = learning_curve(
            estimator,
            x_train,
            y_train,
            train_sizes=np.linspace(0.2, 1.0, 5),
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
        )
        pd.DataFrame(
            {
                "train_size": sizes,
                "train_mean": train_scores.mean(axis=1),
                "train_std": train_scores.std(axis=1),
                "validation_mean": validation_scores.mean(axis=1),
                "validation_std": validation_scores.std(axis=1),
            }
        ).to_csv(OUTPUT / f"{name}_ionosphere_{scoring}_learning_curve.csv", index=False)
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
    fig.suptitle(f"{name} - ionosphere learning curves")
    fig.tight_layout()
    fig.savefig(OUTPUT / f"{name}_ionosphere_curve.png", dpi=200)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data, _ = arff.loadarff(DATA)
    frame = pd.DataFrame(data)
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(
                lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
            )
    x = frame.drop(columns="class")
    y = frame["class"].map({"bad": 0, "good": 1})
    models = {
        "J48": DecisionTreeClassifier(
            random_state=SEED, min_samples_leaf=2, min_samples_split=4
        ),
        "Logistic": LogisticRegression(C=1e8, max_iter=5000, random_state=SEED),
    }
    for name, estimator in models.items():
        save_curve(name, estimator, x, y)
    (OUTPUT / "README.json").write_text(
        json.dumps(
            {
                "purpose": "Unify figure types for models shared across datasets; not formal model comparison metrics.",
                "seed": SEED,
                "protocol": "80/20 stratified training subset, inner stratified 5-fold learning curve",
                "J48": "Python DecisionTree approximation: min_samples_leaf=2, min_samples_split=4",
                "Logistic": "Python visualization with C=1e8 to approximate Weka ridge=1e-8",
                "source": str(DATA.relative_to(ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Unified Ionosphere curves saved to {OUTPUT}")


if __name__ == "__main__":
    main()
