from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "deliverables" / "Ionoshpere_dataprocess&J48" / "ionosphere_preprocessed.arff"
OUTPUT = ROOT / "artifacts" / "ionosphere" / "english_figures"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data, _ = arff.loadarff(DATA)
    frame = pd.DataFrame(data)
    frame["class"] = frame["class"].map(lambda value: value.decode("utf-8"))

    counts = frame["class"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4.2))
    bars = ax.bar(counts.index, counts.values, color=["#4C78A8", "#E45756"])
    ax.bar_label(bars)
    ax.set(title="Ionosphere class distribution", xlabel="Class", ylabel="Instances", ylim=(0, 260))
    fig.tight_layout()
    fig.savefig(OUTPUT / "ionosphere_class_balance.png", dpi=220)
    plt.close(fig)

    models = ["Decision Tree", "Random Forest", "Logistic Regression", "RBF-SVM"]
    metrics = {
        "Accuracy": [0.914, 0.937, 0.883, 0.943],
        "F1-score": [0.933, 0.952, 0.914, 0.956],
        "ROC-AUC": [0.907, 0.977, 0.897, 0.980],
    }
    x = np.arange(len(models))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for index, (metric, values) in enumerate(metrics.items()):
        ax.bar(x + (index - 1) * width, values, width, label=metric)
    ax.set_xticks(x, models)
    ax.set_ylim(0.82, 1.01)
    ax.set_ylabel("10-fold CV score")
    ax.set_title("Ionosphere model comparison")
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT / "ionosphere_model_comparison.png", dpi=220)
    plt.close(fig)

    x_data = frame.drop(columns="class")
    y_data = frame["class"]
    x_train, _, y_train, _ = train_test_split(
        x_data, y_data, test_size=0.2, random_state=42, stratify=y_data
    )
    tree = DecisionTreeClassifier(
        random_state=42, min_samples_leaf=2, min_samples_split=4
    ).fit(x_train, y_train)
    fig, ax = plt.subplots(figsize=(22, 10))
    plot_tree(
        tree,
        feature_names=x_data.columns,
        class_names=["bad", "good"],
        filled=True,
        rounded=True,
        impurity=False,
        fontsize=8,
        ax=ax,
    )
    ax.set_title("Ionosphere J48 decision tree (80% training set)")
    fig.tight_layout()
    fig.savefig(OUTPUT / "J48_ionosphere_tree.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"English Ionosphere figures saved to {OUTPUT}")


if __name__ == "__main__":
    main()
