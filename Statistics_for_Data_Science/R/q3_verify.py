# ============================================================
# CDS533 A3 Q3 — 七项研究 Python 复现（与 R 对账用）
# 作者：何铭恩（Q3 负责人）
# 说明：本脚本用 scipy 复现 R 的统计量，作为 R 代码的数值对账
# ============================================================
import pandas as pd
import numpy as np
from scipy import stats

pd.set_option('display.float_format', lambda x: f'{x:.6f}')

print("=" * 70)

# ---------- 数据准备 ----------
auto = pd.read_csv('data/Auto.csv')
college = pd.read_csv('data/College.csv')
hitters = pd.read_csv('data/Hitters.csv')

# Study A: Hitters
hitters_salary = hitters[hitters['Salary'].notna() & (hitters['Salary'] > 0)].copy()
hitters_salary['log_salary'] = np.log(hitters_salary['Salary'])
AL = hitters_salary[hitters_salary['League'] == 'A']['log_salary']
NL = hitters_salary[hitters_salary['League'] == 'N']['log_salary']

print("STUDY A: 两联赛 log(Salary) 比较（两独立样本 t 检验）")
print(f"  AL: n={len(AL)}, mean={AL.mean():.6f}, sd={AL.std(ddof=1):.6f}")
print(f"  NL: n={len(NL)}, mean={NL.mean():.6f}, sd={NL.std(ddof=1):.6f}")
# Welch t-test（R 默认）
tA, pA = stats.ttest_ind(AL, NL, equal_var=False)
print(f"  Welch t = {tA:.6f}, df = (Welch), p = {pA:.6f}")
# 等方差版本（df 对应）
tA2, pA2 = stats.ttest_ind(AL, NL, equal_var=True)
dfA2 = len(AL) + len(NL) - 2
print(f"  等方差 t = {tA2:.6f}, df = {dfA2}, p = {pA2:.6f}")
print()

# Study B: College 配对 log 比较
college_costs = college[(college['Outstate'].notna()) & (college['Room.Board'].notna()) &
                        (college['Outstate'] > 0) & (college['Room.Board'] > 0)].copy()
college_costs['log_tuition'] = np.log(college_costs['Outstate'])
college_costs['log_living'] = np.log(college_costs['Room.Board'])
diff = college_costs['log_tuition'] - college_costs['log_living']

print("STUDY B: log(Outstate) vs log(Room.Board) 配对 t 检验")
print(f"  n = {len(diff)}, mean diff = {diff.mean():.6f}, sd diff = {diff.std(ddof=1):.6f}")
tB, pB = stats.ttest_rel(college_costs['log_tuition'], college_costs['log_living'])
print(f"  配对 t = {tB:.6f}, df = {len(diff)-1}, p = {pB:.6f}")
print()

# Study C: 符号检验（binomial）
# 题目：在 Outstate 与 Room.Board 不相等的学院中，Outstate>Room.Board 的概率是否=0.5
differ = college_costs[college_costs['Outstate'] != college_costs['Room.Board']]
n_diff = len(differ)
n_greater = (differ['Outstate'] > differ['Room.Board']).sum()

print("STUDY C: 符号检验（Outstate > Room.Board 的比例 vs 0.5）")
print(f"  两成本不相等的学院数 n = {n_diff}")
print(f"  Outstate > Room.Board 的学院数 = {n_greater}")
# 二项检验（双侧）
pC = stats.binomtest(n_greater, n_diff, 0.5, alternative='two-sided').pvalue
print(f"  二项检验（双侧）p = {pC:.6f}")
print()

# Study D: Auto mpg 美/日 分布比较
cars_two = auto[auto['origin'].isin([1, 3])].copy()
cars_two['origin_group'] = cars_two['origin'].map({1: 'American', 3: 'Japanese'})
mpg_am = cars_two[cars_two['origin_group'] == 'American']['mpg']
mpg_jp = cars_two[cars_two['origin_group'] == 'Japanese']['mpg']

print("STUDY D: mpg 分布 美/日 比较（Mann-Whitney U）")
print(f"  American: n={len(mpg_am)}, median={mpg_am.median():.3f}, mean={mpg_am.mean():.3f}")
print(f"  Japanese: n={len(mpg_jp)}, median={mpg_jp.median():.3f}, mean={mpg_jp.mean():.3f}")
uD, pD = stats.mannwhitneyu(mpg_am, mpg_jp, alternative='two-sided')
print(f"  Mann-Whitney U = {uD:.6f}, p = {pD:.6f}")
print()

# Study E: 公私校频率 vs 0.5
private_counts = college['Private'].value_counts()
n_yes = private_counts.get('Yes', 0)
n_no = private_counts.get('No', 0)
n_tot = n_yes + n_no

print("STUDY E: 公私校频率 vs 0.5（二项检验）")
print(f"  Private Yes = {n_yes}, No = {n_no}, 总计 = {n_tot}")
pE_binom = stats.binomtest(n_yes, n_tot, 0.5, alternative='two-sided').pvalue
print(f"  二项检验（双侧）p = {pE_binom:.6f}")
# 卡方拟合优度
exp_each = n_tot / 2
chiE = sum((obs - exp_each)**2 / exp_each for obs in [n_yes, n_no])
pE_chi = stats.chi2.sf(chiE, 1)
print(f"  卡方拟合优度 chi2 = {chiE:.6f}, df = 1, p = {pE_chi:.6f}")
print()

# Study F: Private × Top10 关联
college['top10_group'] = np.where(college['Top10perc'] >= 50, 'High', 'Lower')
ct = pd.crosstab(college['Private'], college['top10_group'])
print("STUDY F: Private × Top10 关联（卡方独立性）")
print(ct)
print(f"  列联表（行=Private, 列=top10_group, High/Lower）")
chiF, pF, dfF, expF = stats.chi2_contingency(ct, correction=False)
print(f"  卡方独立性 chi2 = {chiF:.6f}, df = {dfF}, p = {pF:.6f}")
# 各单元格比例
ct_prop = pd.crosstab(college['Private'], college['top10_group'], normalize='index')
print("  行比例（Private 内 High 比例）:")
print(ct_prop)
print()

# Study G: 三产地 mpg 方差齐性（Levene）
auto2 = auto.copy()
origin_map = {1: 'American', 2: 'European', 3: 'Japanese'}
auto2['origin_group'] = auto2['origin'].map(origin_map)
groups = [auto2[auto2['origin_group'] == g]['mpg'].values for g in ['American', 'European', 'Japanese']]
n_g = [len(g) for g in groups]

print("STUDY G: 三产地 mpg 方差齐性（Levene）")
for g, n in zip(['American', 'European', 'Japanese'], n_g):
    print(f"  {g}: n={n}")
# Levene 以 median 为中心（更稳健，R car::leveneTest 默认 center=median）
W_med, pG_med = stats.levene(*groups, center='median')
W_mean, pG_mean = stats.levene(*groups, center='mean')
print(f"  Levene (median) W = {W_med:.6f}, p = {pG_med:.6f}")
print(f"  Levene (mean)   W = {W_mean:.6f}, p = {pG_mean:.6f}")
# 各组方差
print("  各组 mpg 方差:")
for g, name in zip(groups, ['American', 'European', 'Japanese']):
    print(f"    {name}: var = {np.var(g, ddof=1):.3f}, sd = {np.std(g, ddof=1):.3f}")
print()

print("=" * 70)
