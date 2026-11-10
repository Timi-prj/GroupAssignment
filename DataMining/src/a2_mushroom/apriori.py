from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from eda import ARTIFACTS, ROOT, load_data

MIN_SUPPORT = 0.20
MIN_CONFIDENCE = 0.80
MAX_LEN = 3


def apriori(transactions: list[frozenset[str]], min_support: float, max_len: int) -> dict[frozenset[str], float]:
    n_transactions = len(transactions)
    counts = Counter(item for transaction in transactions for item in transaction)
    supports = {
        frozenset([item]): count / n_transactions
        for item, count in counts.items()
        if count / n_transactions >= min_support
    }
    current = sorted(supports, key=lambda itemset: sorted(itemset))
    all_supports = dict(supports)

    for size in range(2, max_len + 1):
        candidates = set()
        for left_index, left in enumerate(current):
            for right in current[left_index + 1 :]:
                candidate = left | right
                if len(candidate) != size:
                    continue
                # Apriori 剪枝：只要一个子集不频繁，当前组合就不可能频繁。
                if all(frozenset(subset) in all_supports for subset in combinations(candidate, size - 1)):
                    candidates.add(candidate)
        counts = Counter(
            candidate
            for transaction in transactions
            for candidate in candidates
            if candidate <= transaction
        )
        supports = {
            itemset: count / n_transactions
            for itemset, count in counts.items()
            if count / n_transactions >= min_support
        }
        if not supports:
            break
        all_supports.update(supports)
        current = sorted(supports, key=lambda itemset: sorted(itemset))
    return all_supports


def class_rules(supports: dict[frozenset[str], float], min_confidence: float) -> pd.DataFrame:
    records = []
    for itemset, support in supports.items():
        for consequent in [frozenset(["class=e"]), frozenset(["class=p"])]:
            if not consequent <= itemset:
                continue
            antecedent = itemset - consequent
            if not antecedent:
                continue
            confidence = support / supports[antecedent]
            if confidence < min_confidence:
                continue
            consequent_support = supports[consequent]
            records.append(
                {
                    "antecedent": " & ".join(sorted(antecedent)),
                    "consequent": next(iter(consequent)),
                    "antecedent_size": len(antecedent),
                    "support": support,
                    "confidence": confidence,
                    "lift": confidence / consequent_support,
                }
            )
    return pd.DataFrame(records).sort_values(
        ["lift", "confidence", "support"], ascending=False, ignore_index=True
    )


def save_plot(rules: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, class_name, color in zip(axes, ["class=e", "class=p"], ["#4C78A8", "#E45756"]):
        selected = rules.loc[rules["consequent"] == class_name].head(10).iloc[::-1]
        labels = selected["antecedent"] + " -> " + selected["consequent"]
        bars = ax.barh(labels, selected["lift"], color=color)
        ax.bar_label(bars, fmt="%.3f", padding=3)
        ax.set(title=f"Top rules for {class_name}", xlabel="Lift", xlim=(0, selected["lift"].max() * 1.18))
        ax.tick_params(axis="y", labelsize=9)
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle("Mushroom Apriori association rules (support >= 0.20, confidence >= 0.80)")
    fig.tight_layout()
    fig.savefig(output / "apriori_top_rules.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def rule_list(rules: pd.DataFrame, class_name: str) -> str:
    selected = rules.loc[rules["consequent"] == class_name].head(5)
    return "\n".join(
        f"- `{row.antecedent} → {row.consequent}`：Support={row.support:.4f}，Confidence={row.confidence:.4f}，Lift={row.lift:.4f}。"
        for row in selected.itertuples()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "mushroom_preprocessed.arff")
    args = parser.parse_args()
    output = ARTIFACTS / "apriori"
    output.mkdir(parents=True, exist_ok=True)
    frame = load_data(args.data)
    transactions = [
        frozenset(f"{column}={value}" for column, value in row.items())
        for _, row in frame.iterrows()
    ]
    supports = apriori(transactions, MIN_SUPPORT, MAX_LEN)
    itemsets = pd.DataFrame(
        [
            {"itemset": " & ".join(sorted(itemset)), "length": len(itemset), "support": support}
            for itemset, support in supports.items()
        ]
    ).sort_values(["length", "support"], ascending=[True, False], ignore_index=True)
    itemsets.to_csv(output / "frequent_itemsets.csv", index=False)
    rules = class_rules(supports, MIN_CONFIDENCE)
    rules.to_csv(output / "class_association_rules.csv", index=False)
    for class_name, filename in [("class=e", "edible_rules.csv"), ("class=p", "poisonous_rules.csv")]:
        rules.loc[rules["consequent"] == class_name].to_csv(output / filename, index=False)
    save_plot(rules, output)
    (output / "run_config.json").write_text(
        json.dumps(
            {
                "instances": len(frame),
                "min_support": MIN_SUPPORT,
                "min_confidence": MIN_CONFIDENCE,
                "max_itemset_length": MAX_LEN,
                "frequent_itemsets": len(itemsets),
                "class_rules": len(rules),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    summary = f"""# Mushroom Apriori 结果摘要

以 Support≥{MIN_SUPPORT:.2f}、Confidence≥{MIN_CONFIDENCE:.2f}、最大项集长度 {MAX_LEN} 挖掘到 {len(itemsets)} 个频繁项集，其中 {len(rules)} 条为后件指向 `class=e/p` 的关联规则。

![Apriori Top 规则](apriori_top_rules.png)

## 可食类别 Top 规则（按 Lift 排序）

{rule_list(rules, 'class=e')}

## 有毒类别 Top 规则（按 Lift 排序）

{rule_list(rules, 'class=p')}

Lift>1 表示属性组合与类别正相关；Confidence 表示该条件下类别出现的比例。规则反映当前数据的共现关系，不证明因果关系，也不应与分类模型直接比较 F1。完整规则见 `class_association_rules.csv`。
"""
    (output / "results_summary.md").write_text(summary, encoding="utf-8")
    print(f"Apriori: {len(itemsets)} frequent itemsets, {len(rules)} class rules; saved to {output}")


if __name__ == "__main__":
    main()
