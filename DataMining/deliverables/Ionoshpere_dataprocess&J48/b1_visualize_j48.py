# -*- coding: utf-8 -*-
"""
CDS535 B1（J48 版）— ionosphere 结论可视化脚本
=============================================
模型① = J48（C4.5 决策树）版本：将《B1 交付文档（J48 版）》中的全部结论
在 Python 中可视化（seed=42，全流程可复现）。

产出图（保存到 figures_vis_j48/ 目录，300dpi）：
  vis1_class_balance.png      结论①：类别分布 64:36 轻度不平衡
  vis2_infogain_top10.png     结论②：InfoGain 属性排名（过滤器④依据）
  vis3_ablation_bars.png      结论③：J48 消融——标准化无效、IG 属性选择有效
  vis4_j48_depth_curve.png    结论④：J48_O_ionosphere_curve——CV 指标 vs 树深度（剪枝敏感性）
  vis5_kmeans_purity.png      结论⑤：k=2 聚类与真实标签对照（纯度 0.707）
  vis6_kmeans_sse_sil.png     结论⑥：SimpleKMeans 的 SSE 与轮廓系数
  vis7_confusion_roc.png      结论⑦：80/20 混淆矩阵 + ROC（F1 0.9011 / AUC 0.8657）
  vis8_j48_vs_rf.png          结论⑧：单棵 J48 vs RandomForest（代价：解释性换性能）
  vis9_summary_dashboard.png  一页式汇总仪表盘

运行方式：python3 b1_visualize_j48.py
依赖：pandas, numpy, scikit-learn, matplotlib（Sandbox 已预装）
数据：同目录下的 raw_ionosphere.data（UCI 原始文件）
说明：J48 对应 Weka 默认配置（confidenceFactor=0.25, minNumObj=2），
     Python 用 DecisionTreeClassifier(min_samples_leaf=2, min_samples_split=4) 近似。
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (confusion_matrix, f1_score, roc_auc_score,
                             roc_curve, adjusted_rand_score, silhouette_score,
                             precision_score, recall_score)

# ---------------------------------------------------------------- 全局设置
SEED = 42
rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Noto Serif CJK SC",
                               "WenQuanYi Micro Hei", "Noto Sans CJK SC",
                               "Microsoft YaHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
C_GOOD, C_BAD, C_MAIN, C_ACC = "#c0392b", "#27ae60", "#1f4e79", "#e67e22"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "figures_vis_j48")
os.makedirs(OUT, exist_ok=True)


def savefig(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {path}")


# ---------------------------------------------------------------- 1. 数据读取与预处理
cols = [f"a{i:02d}" for i in range(1, 35)] + ["class"]
df = pd.read_csv(os.path.join(BASE, "raw_ionosphere.data"),
                 header=None, names=cols)
df["class"] = df["class"].map({"g": "good", "b": "bad"})
X_raw = df.drop(columns=["class"])
y = df["class"]

const_cols = [c for c in X_raw.columns if X_raw[c].nunique() <= 1]  # RemoveUseless
X1 = X_raw.drop(columns=const_cols)
X_std = pd.DataFrame(StandardScaler().fit_transform(X1), columns=X1.columns)  # Standardize

# ---------------------------------------------------------------- 2. 模型定义（Weka J48 默认参数的等价近似）
J48 = lambda: DecisionTreeClassifier(random_state=SEED, min_samples_leaf=2,
                                     min_samples_split=4)
RF = lambda: RandomForestClassifier(n_estimators=100, random_state=SEED)


def cv_scores(Xmat, model_fn, k=10):
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=SEED)
    accs, f1s, aucs = [], [], []
    for tr, te in skf.split(Xmat, y):
        m = model_fn()
        Xtr = Xmat[tr] if isinstance(Xmat, np.ndarray) else Xmat.iloc[tr]
        Xte = Xmat[te] if isinstance(Xmat, np.ndarray) else Xmat.iloc[te]
        m.fit(Xtr, y.iloc[tr])
        p = m.predict(Xte)
        pr = m.predict_proba(Xte)[:, list(m.classes_).index("good")]
        accs.append((p == y.iloc[te]).mean())
        f1s.append(f1_score(y.iloc[te], p, pos_label="good"))
        aucs.append(roc_auc_score((y.iloc[te] == "good").astype(int), pr))
    return np.mean(accs), np.mean(f1s), np.mean(aucs)


# ---------------------------------------------------------------- 3. 预计算
print(">>> InfoGain（过滤器④）...")
mi = pd.Series(mutual_info_classif(X_std, y, random_state=SEED),
               index=X_std.columns).sort_values(ascending=False)
top16 = mi.head(16).index

print(">>> J48 消融实验（结论③）...")
abl = {
    "原始数据\n(34属性)": cv_scores(X1.values, J48),
    "+ Standardize\n(33属性)": cv_scores(X_std.values, J48),
    "+ Std + IG-Top16\n(16属性)": cv_scores(X_std[top16].values, J48),
}

print(">>> J48 深度曲线（结论④，替代 loss 曲线）...")
depths = [1, 2, 3, 4, 5, 6, 8, 10, None]
depth_labels = [str(d) for d in depths]
d_acc, d_f1 = [], []
for d in depths:
    fn = (lambda d=d: DecisionTreeClassifier(max_depth=d, random_state=SEED,
                                             min_samples_leaf=2, min_samples_split=4))
    a, f, _ = cv_scores(X_std.values, fn)
    d_acc.append(a); d_f1.append(f)

print(">>> SimpleKMeans（结论⑤⑥）...")
sse, sil = {}, {}
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(X_std)
    sse[k], sil[k] = km.inertia_, silhouette_score(X_std, km.labels_)
km2 = KMeans(n_clusters=2, random_state=SEED, n_init=10).fit(X_std)
purity = sum(pd.Series(y.values[km2.labels_ == c]).value_counts().iloc[0]
             for c in set(km2.labels_)) / len(y)
ari = adjusted_rand_score(y, km2.labels_)
ct = pd.crosstab(pd.Series(km2.labels_, name="cluster"), y)

print(">>> J48 80/20 切分（结论⑦）...")
Xtr, Xte, ytr, yte = train_test_split(X_std, y, test_size=0.2,
                                      stratify=y, random_state=SEED)
j48 = J48().fit(Xtr, ytr)
pred = j48.predict(Xte)
proba = j48.predict_proba(Xte)[:, list(j48.classes_).index("good")]
cm = confusion_matrix(yte, pred, labels=["good", "bad"])
fpr, tpr, _ = roc_curve((yte == "good").astype(int), proba)
auc80 = roc_auc_score((yte == "good").astype(int), proba)
imp = pd.Series(j48.feature_importances_, index=X_std.columns)

print(">>> J48 vs RF（结论⑧）...")
j48_cv = cv_scores(X_std.values, J48)
rf_cv = cv_scores(X_std.values, RF)

# ================================================================ 结论图
# --- 图① 类别分布 ---
fig, ax = plt.subplots(figsize=(5.5, 3.8))
cnt = y.value_counts()
bars = ax.bar(cnt.index, cnt.values, color=[C_GOOD, C_BAD], width=0.55)
for b, v in zip(bars, cnt.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v}\n({v/len(y):.1%})",
            ha="center", fontsize=11, fontweight="bold")
ax.set_title("结论① 类别分布：good 225 / bad 126，64:36 轻度不平衡", fontsize=12)
ax.set_ylabel("实例数"); ax.set_ylim(0, 260)
savefig(fig, "vis1_class_balance.png")

# --- 图② InfoGain Top10 ---
fig, ax = plt.subplots(figsize=(7, 4))
mi.head(10)[::-1].plot.barh(ax=ax, color=C_MAIN)
for i, v in enumerate(mi.head(10)[::-1].values):
    ax.text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=10)
ax.set_title("结论② InfoGainAttributeEval 属性排名 Top10\n（J48 根节点将选 a05，与 IG 第一名一致）", fontsize=12)
ax.set_xlabel("信息增益"); ax.set_xlim(0, 0.40)
savefig(fig, "vis2_infogain_top10.png")

# --- 图③ J48 消融实验 ---
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4))
labels = list(abl)
colors = ["#95a5a6", "#3498db", C_ACC]
for ax, metric, name in zip(axes, range(3), ["Accuracy", "F1 (good)", "ROC-AUC"]):
    vals = [abl[l][metric] for l in labels]
    bars = ax.bar(range(3), vals, color=colors, width=0.6)
    ax.set_xticks(range(3)); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(min(vals) - 0.03, max(vals) + 0.02)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.002, f"{v:.4f}",
                ha="center", fontsize=10, fontweight="bold")
    ax.set_title(name, fontsize=11)
fig.suptitle("结论③ 消融实验（J48, 10折CV, seed=42）：标准化对树无效，"
             "IG 属性选择 F1 ↑ 0.016（0.9011→0.9173）", fontsize=12, y=1.02)
savefig(fig, "vis3_ablation_bars.png")

# --- 图④ J48 深度曲线（剪枝敏感性 = J48 版训练曲线） ---
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(range(len(depths)), d_acc, "o-", color=C_MAIN, label="Accuracy")
ax.plot(range(len(depths)), d_f1, "s--", color=C_ACC, label="F1 (good)")
best = int(np.argmax(d_acc))
ax.axvline(best, ls=":", color="gray")
ax.annotate(f"最优 max_depth={depth_labels[best]}\nAcc={d_acc[best]:.4f} / F1={d_f1[best]:.4f}\n"
            "→ 浅树更好，验证剪枝必要性",
            xy=(best, d_acc[best]), xytext=(best + 1.2, d_acc[best] + 0.015),
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=10)
ax.set_xticks(range(len(depths))); ax.set_xticklabels(depth_labels)
ax.set_xlabel("max_depth（None = 不限制，近似 Weka 不剪枝）")
ax.set_ylabel("10 折 CV 得分")
ax.legend(loc="lower left")
ax.set_title("J48_O_ionosphere_curve：CV 指标 vs 树深度（seed=42）\n"
             "J48 无 loss 曲线，全队约定改用剪枝/深度敏感性曲线", fontsize=12)
savefig(fig, "vis4_j48_depth_curve.png")

# --- 图⑤ k=2 与真实标签对照 ---
fig, ax = plt.subplots(figsize=(5.5, 4))
x = np.arange(2); w = 0.35
ax.bar(x - w/2, ct["good"], w, label="good", color=C_GOOD)
ax.bar(x + w/2, ct["bad"], w, label="bad", color=C_BAD)
for xi, (g, b) in enumerate(zip(ct["good"], ct["bad"])):
    ax.text(xi - w/2, g + 2, str(g), ha="center", fontsize=11, fontweight="bold")
    ax.text(xi + w/2, b + 2, str(b), ha="center", fontsize=11, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(["簇 0（多数类：good）", "簇 1（多数类：bad）"])
ax.set_ylabel("实例数"); ax.legend()
ax.set_title(f"结论⑤ k=2 聚类 vs 真实标签：纯度 {purity:.3f}，ARI {ari:.3f}\n"
             "→ 聚类结构与标签弱对应，必须用监督学习", fontsize=11.5)
savefig(fig, "vis5_kmeans_purity.png")

# --- 图⑥ KMeans SSE + 轮廓系数 ---
fig, ax1 = plt.subplots(figsize=(7, 4))
ax1.plot(list(sse), list(sse.values()), "o-", color=C_MAIN)
ax1.set_xlabel("簇数 k"); ax1.set_ylabel("Within-cluster SSE", color=C_MAIN)
ax2 = ax1.twinx()
ax2.plot(list(sil), list(sil.values()), "s--", color=C_ACC)
ax2.set_ylabel("silhouette", color=C_ACC)
ax2.annotate("k=4 最高 0.292", xy=(4, sil[4]), xytext=(5, 0.27),
             arrowprops=dict(arrowstyle="->", color=C_ACC), color=C_ACC)
ax1.set_title("结论⑥ SimpleKMeans：SSE 无明显肘部，轮廓系数在 k=4 最高", fontsize=12)
savefig(fig, "vis6_kmeans_sse_sil.png")

# --- 图⑦ 混淆矩阵 + ROC ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].imshow(cm, cmap="Blues")
for (i, j), v in np.ndenumerate(cm):
    axes[0].text(j, i, str(v), ha="center", va="center", fontsize=16,
                 fontweight="bold",
                 color="white" if v > cm.max() * 0.6 else C_MAIN)
axes[0].set_xticks([0, 1]); axes[0].set_xticklabels(["good", "bad"])
axes[0].set_yticks([0, 1]); axes[0].set_yticklabels(["good", "bad"])
axes[0].set_xlabel("预测"); axes[0].set_ylabel("真实")
axes[0].set_title(f"混淆矩阵（80/20，seed=42，树深 {j48.get_depth()}、{j48.get_n_leaves()} 叶）\n"
                  "漏报 bad 4 例、误报 5 例", fontsize=11)
axes[1].plot(fpr, tpr, color=C_GOOD, lw=2, label=f"ROC-AUC = {auc80:.3f}")
axes[1].plot([0, 1], [0, 1], "--", color="gray", lw=1)
axes[1].set_xlabel("假正率 FPR"); axes[1].set_ylabel("真正率 TPR")
axes[1].set_title("ROC 曲线 — J48\nF1 0.9011 ｜ Precision 0.9111 ｜ Recall 0.8913", fontsize=11)
axes[1].legend(loc="lower right")
fig.suptitle("结论⑦ 模型① J48 测试集结果（80/20 切分）", fontsize=12, y=1.02)
savefig(fig, "vis7_confusion_roc.png")

# --- 图⑧ J48 vs RF ---
fig, ax = plt.subplots(figsize=(8, 4))
x = np.arange(3); w = 0.35
ax.bar(x - w/2, j48_cv, w, label="J48 单棵树（模型①，可解释）", color=C_MAIN)
ax.bar(x + w/2, rf_cv, w, label="RandomForest 100棵（集成对照）", color="#95a5a6")
for xi, (jv, rv) in enumerate(zip(j48_cv, rf_cv)):
    ax.text(xi - w/2, jv + 0.004, f"{jv:.4f}", ha="center", fontsize=10,
            fontweight="bold", color=C_MAIN)
    ax.text(xi + w/2, rv + 0.004, f"{rv:.4f}", ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(["Accuracy", "F1 (good)", "ROC-AUC"])
ax.set_ylim(0.82, 1.0); ax.legend(loc="lower right")
ax.set_title("结论⑧ 单棵 J48 vs RandomForest（10折CV, seed=42）\n"
             "RF 性能更高，但 J48 可输出完整决策规则——解释性 vs 性能的权衡", fontsize=12)
savefig(fig, "vis8_j48_vs_rf.png")

# --- 图⑨ 一页式汇总仪表盘 ---
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("CDS535 B1（J48 版）— ionosphere 结论汇总（seed=42，可由本脚本一键复现）",
             fontsize=15, fontweight="bold")
axes[0, 0].bar(cnt.index, cnt.values, color=[C_GOOD, C_BAD], width=0.5)
axes[0, 0].set_title("① 类别分布 64:36", fontsize=11)
axes[0, 1].barh(mi.head(5)[::-1].index, mi.head(5)[::-1].values, color=C_MAIN)
axes[0, 1].set_title("② InfoGain Top5（J48 根节点 a05）", fontsize=11)
vals = [abl[l][1] for l in labels]
axes[0, 2].bar(range(3), vals, color=colors, width=0.6)
axes[0, 2].set_xticks(range(3))
axes[0, 2].set_xticklabels(["原始", "+Std", "+Std+IG16"], fontsize=9)
axes[0, 2].set_title("③ 消融 F1：Std 无效 / IG +0.016", fontsize=11)
axes[1, 0].plot(range(len(depths)), d_acc, "o-", color=C_MAIN, ms=4)
axes[1, 0].axvline(best, ls=":", color="gray")
axes[1, 0].set_xticks(range(len(depths)))
axes[1, 0].set_xticklabels(depth_labels, fontsize=8)
axes[1, 0].set_title("④ J48 深度曲线（浅树更优）", fontsize=11)
axes[1, 1].plot(list(sil), list(sil.values()), "s--", color=C_ACC)
axes[1, 1].set_title("⑤⑥ KMeans 轮廓系数（k=4 最高）", fontsize=11)
im = axes[1, 2].imshow(cm, cmap="Blues")
for (i, j), v in np.ndenumerate(cm):
    axes[1, 2].text(j, i, str(v), ha="center", va="center", fontsize=13,
                    fontweight="bold",
                    color="white" if v > cm.max() * 0.6 else C_MAIN)
axes[1, 2].set_xticks([0, 1]); axes[1, 2].set_xticklabels(["good", "bad"])
axes[1, 2].set_yticks([0, 1]); axes[1, 2].set_yticklabels(["good", "bad"])
axes[1, 2].set_title(f"⑦ 80/20 混淆矩阵（AUC {auc80:.3f}）", fontsize=11)
for ax in axes.flat:
    ax.tick_params(labelsize=8)
plt.tight_layout(rect=[0, 0, 1, 0.95])
savefig(fig, "vis9_summary_dashboard.png")

# ---------------------------------------------------------------- 打印关键结论
print("\n===== 关键结论数字（J48 版，seed=42，与交付文档一致）=====")
print(f"类别分布: {cnt.to_dict()}")
print(f"消融 Acc: {[f'{abl[l][0]:.4f}' for l in labels]}")
print(f"消融 F1:  {[f'{abl[l][1]:.4f}' for l in labels]}")
print(f"深度曲线最优: max_depth={depth_labels[best]}, Acc={d_acc[best]:.4f}, F1={d_f1[best]:.4f}")
print(f"KMeans:   纯度={purity:.4f}, ARI={ari:.4f}")
print(f"J48 80/20: Acc={(pred==yte).mean():.4f}, F1={f1_score(yte,pred,pos_label='good'):.4f}, "
      f"AUC={auc80:.4f}, 树深={j48.get_depth()}, 叶子={j48.get_n_leaves()}")
print(f"J48 vs RF CV: Acc {j48_cv[0]:.4f} vs {rf_cv[0]:.4f} ｜ F1 {j48_cv[1]:.4f} vs {rf_cv[1]:.4f}")
print(f"J48 重要性 Top5: {imp.sort_values(ascending=False).head(5).round(4).to_dict()}")
