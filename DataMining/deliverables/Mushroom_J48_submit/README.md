# CDS 535 · Mushroom 数据集 J48 五方案对比 —— 交付说明

数据：UCI Mushroom，8,124 条（4,208 e 可食 / 3,916 p 有毒），22 个预测属性全为标称型。
工具：Weka 3.8.7（`E:/Weka/Weka-3-8-7/weka.jar`，内置 JRE 25）。
协议：分层 10 折交叉验证（`-x 10 -s 42`）为主口径；另加固定分层 80/20 留出（train 6,499 / test 1,625，同 seed 42）做一次外部复核。

## 一、结果速查（10 折 CV，seed 42）

| 方案 | 属性数 | 准确率 | 漏检 p→e | 误报 e→p | 叶 / 节点 | 建模耗时 |
|---|---|---|---|---|---|---|
| J48-all22 | 21 | 100.0000 % | 0 | 0 | 25 / 30 | 0.18 s |
| J48-top8 | 8 | 99.9015 % | 8 | 0 | 27 / 31 | 0.24 s |
| J48-top9 | 9 | 100.0000 % | 0 | 0 | 28 / 33 | 0.25 s |
| J48-cfs | 4 | 99.0153 % | 80 | 0 | 17 / 21 | 0.27 s |
| J48-wrapper | 5 | 100.0000 % | 0 | 0 | 32 / 37 | 3.79 s |

（build 为单次实测，同机波动约 ±0.05 s，只用于量级比较。）

**80/20 复核**（1,625 条测试段，漏检 / 准确率）：0 → 100.0000 %、2 → 99.8769 %、0 → 100.0000 %、15 → 99.0769 %、0 → 100.0000 %，名次与 CV 一致（CFS 末位、三组满分并列）。但该口径只能分辨 CFS 量级的差距：top-8 只错 2 条，配对 McNemar p = 0.50，区分不了 99.90 % 与 100 %；后者由 CV 折外汇总的 8 : 0（p = 0.0078）支撑。

**结论**：五组差异只出现在「有毒判成可食」这一侧；属性少 ≠ 效果差（Wrapper 用 5 个属性就到 100 %，top-8 用 8 个反而漏 8 条），关键是属性互补性。推荐 top-9（9 属性、100 %、成本与全属性同量级），不建议 CFS（4 属性换来 80 条毒菇漏检）。

## 二、目录结构

```
Mushroom_J48_submit/
├─ README.md                              本文件
├─ Mushroom_J48_五方案对比_精简总结.docx     正文（6 节，4 图 3 表）
├─ 01_data/
│   ├─ mushroom_raw.arff                  原始数据（8,124 × 23，stalk-root 2,480 个 ?）
│   ├─ mushroom_clean.arff                五组实验的输入（8,124 × 22，缺失已补、veil-type 已删）
│   ├─ mushroom_clean_ranked.arff         按 InfoGain 排序、不删列（观察用）
│   ├─ mushroom_clean_binary.arff         NominalToBinary 版（仅供 SMO / Logistic）
│   └─ splits/                            80/20 分层留出（StratifiedRemoveFolds -N 5 -F 1 -S 42，第 1 份为测试段）
│       ├─ mushroom_train80.arff          6,499 条
│       └─ mushroom_test20.arff           1,625 条（841 e + 784 p）
├─ 02_results/
│   ├─ cv10/        五组 10 折 CV 输出（J48-<方案>_cv10.txt）
│   ├─ holdout/     五组 80/20 留出输出（J48-<方案>_holdout.txt，测试段只评一次）
│   ├─ models/      五组在全部 8,124 条上训练的 .model
│   └─ evidence/    five_schemes_seed42.json（五组 CV + 80/20 指标、配对 McNemar 结果）、J48-raw_nofilter.txt（raw 直跑的对照，证明预处理对树零影响）
└─ 03_figs/
    ├─ index.html                        20 张单图索引（需与同级 PNG 一起打开）
    ├─ 五方案单图_单文件版.html             20 张图已内嵌，单独转发即可
    ├─ 五方案单图对照.pdf                  同内容的 PDF
    ├─ J48-<方案>_mushroom_<图类型>.png    4 类图 × 5 方案 = 20 张
    ├─ tree/J48-<方案>_tree.png           五棵树的截图
    └─ cv10_seed42.png                    Weka 里 10 折 + seed 42 的设置截图
```

## 三、五个方案的 Weka 实现（命令可直接复跑）

每条命令都与 `02_results/` 下对应结果文件**第一行完全一致**——结果文件自带 provenance，无需再另外记录参数。前置变量：

```
set WEKA=E:/Weka/Weka-3-8-7/weka.jar
```

| 方案 | 命令（`-x 10 -s 42 -t 01_data/mushroom_clean.arff` 为公共后缀） |
|---|---|
| ① 全属性 | `java -cp %WEKA% weka.classifiers.trees.J48 -C 0.25 -M 2` |
| ② top-8 | `... weka.classifiers.meta.FilteredClassifier -F "weka.filters.supervised.attribute.AttributeSelection -E weka.attributeSelection.InfoGainAttributeEval -S \"weka.attributeSelection.Ranker -N 8\"" -W weka.classifiers.trees.J48` |
| ③ top-9 | 同 ②，把 `-N 8` 改成 `-N 9` |
| ④ CFS | 同 ②，`-E weka.attributeSelection.CfsSubsetEval -S "weka.attributeSelection.BestFirst -D 1 -N 5"` |
| ⑤ Wrapper | 同 ②，`-E "weka.attributeSelection.WrapperSubsetEval -B weka.classifiers.trees.J48 -F 5 -T 0.01 -R 1"` |

完整的、可直接粘贴的一行（以 top-8 为例）：

```
java -cp E:/Weka/Weka-3-8-7/weka.jar weka.classifiers.meta.FilteredClassifier -F "weka.filters.supervised.attribute.AttributeSelection -E weka.attributeSelection.InfoGainAttributeEval -S \"weka.attributeSelection.Ranker -N 8\"" -W weka.classifiers.trees.J48 -c last -x 10 -s 42 -t 01_data/mushroom_clean.arff
```

**80/20 留出复核**：把公共后缀 `-x 10 -s 42 -t 01_data/mushroom_clean.arff` 换成 `-T 01_data/splits/mushroom_test20.arff -t 01_data/splits/mushroom_train80.arff`（留出不需要折数，`holdout/` 下五个结果文件的第一行就是这种形式）。

**GUI 等价操作**：`Preprocess` 打开 `mushroom_clean.arff` → `Classify` → `Choose` 选上表对应的 classifier → `Test options` 选 `Cross-validation, Folds = 10` → `More options…` 把 `Random seed for cross-validation` 改成 **42**（默认 1）→ `Start`。

## 四、预处理做了什么、为什么这么做

1. `ReplaceMissingValues`：stalk-root 的 2,480 个 `?` 用该列众数 `b` 补齐（缺失 → 0）。
2. `RemoveUseless -M 99`：删掉单值列 `veil-type`（22 → 21 个预测属性）。
3. `AttributeSelection`（InfoGainAttributeEval + Ranker，`numToSelect = -1`）：**只排序、不删列**，用来确认 odor 第 1、spore-print-color 第 2。真正的降维放在建模阶段，由 `FilteredClassifier` 在每一折的训练折内重选，避免跨折泄露。
4. （可选）`NominalToBinary`：只给 SMO / Logistic 用；J48、RandomForest、NaiveBayes 原生支持标称属性，不必跑。

**这套预处理对 J48 的实际贡献是 0 分**：拿未处理的 raw（含 2,480 个 `?`）直接跑 J48，得到的树与清洗后逐字相同，同为 25 叶 / 30 节点、100 %（`02_results/evidence/J48-raw_nofilter.txt`）。它的价值在于统一输入、让需要数值输入的模型可跑，而不是提分。

## 五、本版相对旧文件夹改了什么

| 旧 | 新 | 原因 |
|---|---|---|
| `result_j48` / `result_J48_Cfs` / … | `02_results/cv10/J48-<方案>_cv10.txt` | 命名统一；文件第一行即生成本身所用的完整命令（含 `-s 42`），评审可直接复跑核对 seed |
| `J48.model` / `J48_InfoGain+Rankertop8.model` | `02_results/models/J48-<方案>.model` | 去掉 `+`、`=` 等 URL 不安全字符；由本目录命令重新训练导出，与结果一一对应 |
| `step2_…arff` / `step3_…arff` / `step4_…arff` | `mushroom_clean.arff` / `_ranked` / `_binary` | 文件名含 `+`、全角括号、超长，命令行下必须转义；改成 ASCII 短名 |
| `step1_…Remove.arff` | 不再提交 | 它与 step2 是两条并列路径（手工删第 16 列 vs `RemoveUseless` 自动删），结果同一份，留着只会让人误以为是流水线 |
| `step3` 说明「去掉低增益的冗余特征」 | 改为「只排序、不删列」 | 文件里 `Ranker` 参数就是 `-N -1`，其实一个属性都没删，原描述与文件矛盾 |
| 预处理顺序「先删列、后补缺失」 | 改为「先补缺失、后删列」 | 与文件 relation 名 `ReplaceMissingValues-RemoveUseless` 一致；顺序反了 `RemoveUseless` 的判定会变 |
| `J48_IndoGainTOP9_TREE.png` | `03_figs/tree/J48-top9_tree.png` | 拼写错误 + 命名统一 |
| `FOLDS=10&SEED=42.png` | `03_figs/cv10_seed42.png` | 文件名含 `&`、`=`，邮件/URL 中会被截断 |
| `…/index.html`（仅相对路径引图） | 保留 `index.html`，另加 `五方案单图_单文件版.html` | 原版只发 html 会全部裂图；单文件版把 20 张图 base64 内嵌 |
| `组长用_精简总结.zip`（内含旧版 md） | 不再提交，改为整包 `Mushroom_J48_submit.zip` | 旧 zip 里的 md 是过期版本，与 docx 内容不一致 |
| `mushroom_raw.arff` 尾部 3 行裸 `%` | 已删除 | 按行统计会读成 8,127 条，与 8,124 对不上 |
| 文档首行「组长用 · 精简总结」 | 改为「CDS 535 Data Mining · 小组项目报告」 | 内部标注不该出现在提交文档里 |
| 正文「80/20 留出协议下名次完全一致」 | 改为「名次与 CV 一致（CFS 末位、三组并列）」，并注明该口径对 8 条以内差异无统计效力 | 原句是全称结论：1,625 条测试段上 top-8 只错 2 条，配对 McNemar p = 0.50，该协议只能确认 CFS 量级的差距；区分 99.90 % 与 100 % 要靠 CV 折外汇总的 8 : 0（p = 0.0078） |

## 六、已知限制（主动写明，免得被问）

- 属性子集是**在每个训练折内重选**的，所以五组的「属性数」是各折结果的名义值；全量数据上选中的属性名单见正文第三节。
- `-A`（概率平滑）保持关闭，叶子只输出 0/1 概率，因此 ROC 是直角阶梯、Lift 曲线退化为两点连线。这是 J48 默认行为的直接后果，不是绘图错误；若要连续概率曲线，需另开 `-A` 或改用 NaiveBayes / Logistic。
- 数据集本身近似线性可分，五组准确率都挤在 99 %–100 %，差异主要体现在 80 条 vs 8 条的漏检量级上；继续调参收益极小，瓶颈在特征而不在模型。
- 两个口径各有盲区：10 折 CV 每折都既当过训练集也当过测试集，属于「交叉验证意义上的」泛化估计，不是严格的一次性盲测；80/20 留出是真盲测，但测试段只有 1,625 条，只能分辨 CFS 量级的差距（15 条 vs 0 条），对 8 条以内的差异没有统计效力。所以「top-8 比全属性差」这个结论由 CV 折外汇总的 McNemar 检验（8 : 0，p = 0.0078）支撑，留出只作为方向一致的旁证。
