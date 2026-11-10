from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "artifacts/a2_mushroom/apriori/class_association_rules.csv"
DEFAULT_OUTPUT = ROOT / "artifacts/a2_mushroom/apriori/apriori_rule_network.png"


def arc_positions(items: list[str], center: tuple[float, float], radius: float,
                  start: float, end: float) -> dict[str, tuple[float, float]]:
    angles = [math.radians(start + (end - start) * i / (len(items) - 1)) for i in range(len(items))]
    return {
        item: (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
        for item, angle in zip(items, angles)
    }


def wrap_label(label: str) -> str:
    attribute, value = label.split("=", 1)
    replacements = {
        "stalk-surface-above-ring": "stalk-surface-\nabove-ring",
        "stalk-surface-below-ring": "stalk-surface-\nbelow-ring",
        "spore-print-color": "spore-print-\ncolor",
    }
    return f"{replacements.get(attribute, attribute)}={value}"


def draw_network(rules: pd.DataFrame, output: Path) -> None:
    selected = pd.concat([
        rules.loc[rules["consequent"] == class_name].head(5)
        for class_name in ["class=e", "class=p"]
    ], ignore_index=True)
    edges = []
    for row in selected.itertuples():
        for item in row.antecedent.split(" & "):
            edges.append((item, row.consequent, row.support))

    edible_items = sorted({source for source, target, _ in edges if target == "class=e"} - {"ring-number=o"})
    poisonous_items = sorted({source for source, target, _ in edges if target == "class=p"} - {"ring-number=o"})
    positions = {"class=e": (-1.55, 0), "class=p": (1.55, 0), "ring-number=o": (0, 1.25)}
    positions.update(arc_positions(edible_items, (-1.55, 0), 1.0, 70, 290))
    positions.update(arc_positions(poisonous_items, (1.55, 0), 1.0, -110, 110))

    support_totals = {}
    for source, _, support in edges:
        support_totals[source] = support_totals.get(source, 0) + support
    support_totals["class=e"] = sum(row.support for row in selected.itertuples() if row.consequent == "class=e")
    support_totals["class=p"] = sum(row.support for row in selected.itertuples() if row.consequent == "class=p")

    colors = {"class=e": "#3978A8", "class=p": "#C84C45"}
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#FAFAF8")
    ax.set_facecolor("#FAFAF8")

    for source, target, support in edges:
        start, end = positions[source], positions[target]
        rad = 0.10 if target == "class=e" else -0.10
        arrow = FancyArrowPatch(
            start,
            end,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=0.8 + support * 7,
            color=colors[target],
            alpha=0.38,
            shrinkA=24,
            shrinkB=34,
            zorder=1,
        )
        ax.add_patch(arrow)

    for node, (x, y) in positions.items():
        is_class = node.startswith("class=")
        size = 3900 if is_class else 850 + support_totals[node] * 2800
        color = colors.get(node, "#E5D7C5")
        ax.scatter(x, y, s=size, color=color, edgecolor="white", linewidth=2.2, zorder=3)
        label = "Edible\n(class=e)" if node == "class=e" else "Poisonous\n(class=p)" if node == "class=p" else wrap_label(node)
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=11 if is_class else 8.4,
            fontweight="bold" if is_class else "normal",
            color="white" if is_class else "#393633",
            linespacing=1.15,
            zorder=4,
        )

    ax.text(0, 1.76, "Mushroom Apriori Association Network", ha="center", fontsize=23, fontweight="bold", color="#292725")
    ax.text(
        0,
        1.60,
        "Top 5 rules per class, ranked by lift  |  Arrows point from antecedents to class",
        ha="center",
        fontsize=11.5,
        color="#68635D",
    )
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=colors["class=e"], markersize=12, label="Edible rules"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=colors["class=p"], markersize=12, label="Poisonous rules"),
        Line2D([0], [0], color="#77716A", linewidth=1.4, label="Lower support"),
        Line2D([0], [0], color="#77716A", linewidth=3.0, label="Higher support"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=4, frameon=False, fontsize=10)
    ax.text(0, -1.54, "Node size reflects the total support of the displayed rules connected to each node.", ha="center", fontsize=9.5, color="#77716A")
    ax.set_xlim(-2.85, 2.85)
    ax.set_ylim(-1.65, 1.9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.06)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw_network(pd.read_csv(args.input), args.output)
    print(f"Saved association network to {args.output}")


if __name__ == "__main__":
    main()
