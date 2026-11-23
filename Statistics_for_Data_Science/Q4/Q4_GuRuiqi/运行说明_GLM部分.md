# Q4(c) GLM 部分 · 运行说明

**顾瑞祺** — Role 5（Q4 建模）。本包只含 part (c)：变量理由、共线性、模型比较与选择、系数解释、
残差诊断、预测与敏感性检验、结论。

## 怎么跑

在**包含 `data/` 的这一层目录**里执行：

```r
source("Q4_GLM.R")     # 或 Rscript Q4_GLM.R
```

- 只用 base R，**不需要装任何包**，R ≥ 4.2 即可（本机 R 4.6.1）。
- `data/QQ_Music_clean.csv`（842 行 × 25 列）已随包附带，**不必先跑 part (a) 的脚本**。
- 脚本开头有路径回退：从别的目录 `source()` 也能找到 `data/`，不会把结果写到当前工作目录。

## 会产出什么

| 位置 | 内容 |
|---|---|
| `tables/model_comparison.csv` | 三个嵌套模型的 R²、调整 R²、AIC、BIC、残差 SE（报告 Table 3） |
| `tables/final_coefficients.csv` | 最终模型系数、SE、t、p、95% CI（报告 Table 4） |
| `tables/vif.csv` | 全模型 VIF（降序，报告 Table 2） |
| `tables/prediction.csv` | 三种曝光画像的预测值、95% 预测区间、均值 CI（报告 Table 5） |
| `tables/correlation_pairs.csv` | 预测变量之间 \|r\| > 0.5 的三对（Item 3(b) 正文引用） |
| `figures/fig7_diagnostics.png` | 残差四联图（Figure 1） |
| `figures/fig8_coefficients_and_prediction.png` | 拟合曲线 + 系数 CI 森林图（Figure 2） |

在 RStudio 里 Source 时 `preview <- interactive()` 为 TRUE，两张图只画到 Plots 面板，**不会覆盖**
`figures/` 里的 PNG；用 `Rscript` 运行时才重写 PNG 与 CSV。

## 文档

- 提交正文：`Q4_Part_c_GLM_GuRuiqi.docx`（同内容 Markdown 版为 `.md`，便于改动）。
- 图号说明：本报告正文里是 Figure 1、Figure 2，合稿里是 Figure 8、Figure 9；文件名 `fig7_`、`fig8_` 是脚本出图顺序，与报告编号无关。
- `Q4_EDA.R`（part (a)(b)）不在本包内，在贺浩东的包里；本包已带清洗后的 CSV，独立可跑。
