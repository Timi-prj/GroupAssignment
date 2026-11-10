from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.io import arff
from sklearn.model_selection import StratifiedKFold, train_test_split

SEED = 42
ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "a2_mushroom"


def load_data(path: Path) -> pd.DataFrame:
    # ARFF 同时保存数据和属性定义；loadarff 返回结构化数组及元数据，这里只需前者。
    # 名义值常被读成 bytes，转成普通字符串后才能稳定统计取值和绘图。
    data, _ = arff.loadarff(path)
    frame = pd.DataFrame(data)
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(
                lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
            )
    return frame


def save_eda(frame: pd.DataFrame, data_path: Path) -> None:
    output = ARTIFACTS / "eda"
    output.mkdir(parents=True, exist_ok=True)
    x = frame.drop(columns="class")
    y = frame["class"]
    profile = {
        "source_file": data_path.name,
        "source_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "instances": len(frame),
        "input_features": len(x.columns),
        "feature_names": x.columns.tolist(),
        "feature_types": {column: "nominal" for column in x.columns},
        "class_counts": {key: int(value) for key, value in y.value_counts().items()},
        "class_proportions": {key: float(value) for key, value in y.value_counts(normalize=True).items()},
        "missing_values": int(frame.isna().sum().sum() + (frame == "?").sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "one_hot_input_dimensions": int(x.nunique().sum()),
    }
    (output / "data_profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    cardinality = pd.DataFrame(
        {
            "feature": x.columns,
            "cardinality": [x[column].nunique() for column in x.columns],
            "values": ["|".join(sorted(x[column].unique())) for column in x.columns],
        }
    )
    cardinality.to_csv(output / "feature_cardinality.csv", index=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    counts = y.value_counts().sort_index()
    bars = ax.bar(counts.index, counts.values, color=["#4C78A8", "#E45756"])
    ax.bar_label(bars)
    ax.set(title="Mushroom class balance", xlabel="Class", ylabel="Instances", ylim=(0, counts.max() * 1.15))
    fig.tight_layout()
    fig.savefig(output / "class_balance.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(7, 3, figsize=(16, 25))
    for column, ax in zip(x.columns, axes.flat):
        counts = x[column].value_counts().sort_index()
        ax.bar(counts.index, counts.values, color="#4C78A8")
        ax.set_title(column)
        ax.tick_params(axis="x", labelrotation=45, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
    fig.suptitle("Mushroom nominal feature distributions", fontsize=16, y=1.002)
    fig.tight_layout()
    fig.savefig(output / "feature_distributions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_splits(frame: pd.DataFrame) -> None:
    output = ARTIFACTS / "splits"
    output.mkdir(parents=True, exist_ok=True)
    # 分层划分让训练集、测试集的有毒/可食比例接近原数据，避免随机划分造成类别比例偏差。
    indices = pd.Series(frame.index.to_numpy())
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, random_state=SEED, stratify=frame["class"]
    )
    holdout = pd.concat(
        [
            pd.DataFrame({"row_index": train_idx.to_numpy(), "split": "train"}),
            pd.DataFrame({"row_index": test_idx.to_numpy(), "split": "test"}),
        ]
    ).sort_values("row_index")
    holdout.to_csv(output / "holdout_80_20_seed42.csv", index=False)

    folds = pd.DataFrame({"row_index": indices, "fold": -1})
    splitter = StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED)
    for fold, (_, test_idx) in enumerate(splitter.split(frame, frame["class"])):
        folds.loc[test_idx, "fold"] = fold
    folds.to_csv(output / "stratified_10fold_seed42.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "mushroom_preprocessed.arff")
    args = parser.parse_args()
    frame = load_data(args.data)
    save_eda(frame, args.data)
    save_splits(frame)
    print(f"EDA and splits saved to {ARTIFACTS}")


if __name__ == "__main__":
    main()
