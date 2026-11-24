## Question 1: Choosing an Advertisement

### (a) Design, test, and hypotheses

The response is an ordinal reaction score: higher values indicate a more favourable response, but equal numerical intervals cannot be assumed. The explanatory factor, advertisement, has three independent groups (Red, White, and Blue); different consumers viewed only one advertisement. The sample sizes are 11, 13, and 10, respectively (N = 34).

A Kruskal–Wallis rank-sum test is appropriate for comparing the three independent groups using the ordinal information without assuming normally distributed scores. Let F_R, F_W, and F_B denote the population score distributions. The hypotheses are H₀: F_R = F_W = F_B versus H₁: at least one distribution differs. If group distributions have a similar shape, this can be interpreted as a test of location; otherwise it is an omnibus test of distributional differences. The test does not establish that every pair differs or identify a particular differing pair.

### (b) Descriptive and inferential results

All 34 supplied scores were analysed as given; there were no missing, invalid, or duplicated observations and none were excluded or imputed. Table 1 summarises the scores. Since the scale is ordinal, medians and interquartile ranges are especially interpretable; means and standard deviations are included as supplementary summaries.

| Advertisement | n | Mean | SD | Median | Q1 | Q3 | IQR | Min | Max |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Red | 11 | 81.818 | 8.716 | 80.0 | 76.500 | 84.500 | 8.000 | 71 | 98 |
| White | 13 | 84.846 | 11.539 | 87.0 | 79.000 | 92.000 | 13.000 | 55 | 99 |
| Blue | 10 | 74.500 | 6.721 | 74.0 | 69.250 | 80.000 | 10.750 | 65 | 85 |

![Reaction scores by advertisement. Points represent consumers; boxes show medians and interquartile ranges.](report/assignment3_outputs/figures/q1_advertisements.png)

White has the highest sample mean and median, while Blue has the lowest. White also shows the greatest spread; its low score of 55 was retained as an observed response, not treated as an invalid value.

The Kruskal–Wallis test gives H(2) = 8.202, p = 0.017. At α = 0.05, reject H₀: there is evidence that consumer reaction-score distributions are not all the same across the three advertisements. The mean ranks are Red 17.773, White 22.577, and Blue 10.600. This omnibus result alone does not prove that White differs significantly from either Red or Blue.

### (c) Recommendation and limits of the overall test

White is the most defensible first choice if the objective is the most favourable typical response: it has the highest observed median (87) and mean (84.846), and the overall test indicates a difference among the advertisements. This is a descriptive recommendation, not evidence that White is statistically superior to Red. White also has the widest observed variability (SD = 11.539; IQR = 13), including one unusually low response. Red, with the smallest IQR (8), is a reasonable more-consistent alternative if avoiding strongly negative reactions is important.

The significant overall test establishes only that the three score distributions are not all identical. It neither identifies which pairs differ nor shows that the advertisement with the highest sample mean is significantly better than every other advertisement. Such claims would require follow-up pairwise comparisons with a multiplicity adjustment (for example, Dunn comparisons with Holm adjustment); these were not required and were not conducted. No claim that a single advertisement caused the observed population difference should be made beyond the study's sampling and assignment design.

## Question 2: Chick Weight by Feed Type

### (a) Hypotheses and assumptions

Let μ₁, …, μ₆ denote the population mean chick weights for casein, horsebean, linseed, meatmeal, soybean, and sunflower feed. The hypotheses for the one-way ANOVA are H₀: μ₁ = μ₂ = ⋯ = μ₆ versus H₁: at least one population mean differs.

The study uses individual chicks as the experimental units and assigns them to feed groups; the analysis treats chick weights as independent observations. The ANOVA also assumes approximately normal within-group errors and equal population variances. The residual normal Q–Q plot shows only a mild right-tail departure, which is not strong evidence against approximate normality. Group standard deviations range from 38.626 to 64.901 (largest/smallest = 1.680), and the residuals-versus-fitted plot shows broadly similar spread across groups; equal variance is therefore reasonable for this analysis. These plots are diagnostic evidence, not proof that the assumptions hold.

### (b) Plot, ANOVA table, and conclusion

![Chick weight by feed type.](report/assignment3_outputs/figures/q2_feed_boxplot.png)

![ANOVA residual diagnostics for the feed model.](report/assignment3_outputs/figures/q2_anova_diagnostics.png)

The sample means are highest for sunflower (328.917 g) and casein (323.583 g); horsebean is substantially lower. The one-way ANOVA results are:

| Source | df | Sum of squares | Mean square | F | p-value |
|:--|--:|--:|--:|--:|--:|
| Feed | 5 | 231129 | 46226 | 15.365 | < 0.001 |
| Residuals | 65 | 195556 | 3009 | — | — |

Because p < 0.001, reject H₀ at α = 0.05. There is strong evidence that mean chick weight is not the same for all six feeds.

### (c) Interpreting the omnibus result

A significant ANOVA does not mean that every feed differs significantly from every other feed. It establishes only that the data provide evidence against equality of all six population means; the result is compatible with some pairs not differing. Likewise, the highest sample mean does not establish that sunflower or casein is significantly better than each other feed. The observed ranking is descriptive, and sampling variability may affect it.

Sunflower and casein had the highest sample means in this sample, but this analysis does not identify which particular feed pairs differ. Pairwise post-hoc comparisons with multiplicity control, such as Tukey's honestly significant difference procedure, would be needed for that purpose. No post-hoc tests were conducted, as they are not required here.

## Question 3: Seven Statistical Studies

For each study below, α = 0.05. The seven questions are separate; no adjustment across studies is required. All results were checked against a fresh R session.

### Study A — Mean log salaries by league

**Design and test.** The response is log annual salary, a continuous variable, compared between two independent groups (American and National League players). After excluding missing or non-positive salaries, n = 263 (139 American, 124 National). A Welch two-sample t-test compares population mean log salaries without requiring equal variances. H₀: μ_A = μ_N; H₁: μ_A ≠ μ_N.

**Results and conclusion.** Mean log salaries were 5.933 (SD 0.897) for American League players and 5.921 (SD 0.884) for National League players. Welch's t-test gave t = 0.104, df ≈ 258.43, p = 0.917. Fail to reject H₀: these data do not provide evidence of a difference in population mean log salary between leagues.

### Study B — Paired log tuition and room-and-board costs

**Design and test.** Each of 777 colleges with positive, non-missing values contributes both out-of-state tuition and room-and-board cost. The paired difference is d = log(Outstate) − log(Room.Board). A paired t-test evaluates H₀: μ_d = 0 against H₁: μ_d ≠ 0.

**Results and conclusion.** The mean difference was 0.828 (SD 0.304). The paired test gave t(776) = 75.774, p < 0.001. Reject H₀: the population mean log costs differ, with out-of-state tuition higher on average. The mean log difference corresponds to a ratio of geometric means of approximately exp(0.828) = 2.29; it is not an arithmetic-mean cost ratio.

### Study C — Probability tuition exceeds room-and-board cost

**Design and test.** Among colleges where the two costs differ (n = 777), the response is the binary sign of the cost difference. The exact binomial sign test requires neither normality nor symmetry. H₀: P(Outstate > Room.Board) = 0.5; H₁: this probability differs from 0.5.

**Results and conclusion.** Tuition exceeded room-and-board cost for 767 of the 777 colleges; the other 10 had lower tuition, and no costs were tied. The exact two-sided binomial test gives p < 0.001. Reject H₀: among non-tied colleges, tuition is more often the larger cost. This is a statement about direction/frequency, unlike Study B, which tests the mean magnitude of paired log differences.

### Study D — MPG distributions for American and Japanese cars

**Design and test.** MPG is a continuous ratio-scale response measured on independent American (n = 245) and Japanese (n = 79) cars. The question concerns distributions, so the two-sample Wilcoxon rank-sum (Mann–Whitney) test is used. H₀: the distributions are identical; H₁: they differ. A rank-sum result does not, without additional shape assumptions, establish a pure location shift or a difference in medians.

**Results and conclusion.** The sample medians were 18.5 mpg (American) and 31.6 mpg (Japanese). The rank-sum test gave W = 2456.5, p < 0.001. A supplementary two-sample Kolmogorov–Smirnov test gave D = 0.608, p < 0.001 (asymptotic approximation with ties). Reject H₀: there is evidence that the mpg distributions differ; descriptively, Japanese cars have higher mpg in this sample.

### Study E — Goodness of fit for college type

**Design and test.** This is a one-sample categorical goodness-of-fit question for public/private status, tested against the specified 0.5/0.5 model (not assumed to be a known fact). H₀: both category probabilities are 0.5; H₁: they are not both 0.5. An exact two-sided binomial test evaluates the private-college probability.

**Results and conclusion.** The observed counts were 565 private and 212 public colleges. The exact test gave 565 successes in 777 trials, p < 0.001. Reject H₀: the observed frequencies are inconsistent with the equal-probability model, with more private than public colleges in this dataset.

### Study F — College type and high top-10% share

**Design and test.** Private/public status and the binary indicator High = (Top10perc ≥ 50) form a 2 × 2 table. The threshold is specified in the research question. A chi-square test of independence tests H₀: the variables are independent versus H₁: they are associated.

**Results and conclusion.** The proportions classified High were 12.2% among private colleges and 6.6% among public colleges. The test gave χ²(1) = 5.083, p = 0.024. Reject H₀: the variables are associated in these data. Unlike Study E's one-variable goodness-of-fit question, Study F tests association between two variables. Association does not demonstrate a causal effect of private-college status; confounding factors such as selectivity, tuition, and applicants' socioeconomic background may contribute to the relationship.

### Study G — MPG variance across origins

**Design and test.** MPG is compared across three independent groups: American (n = 245), European (n = 68), and Japanese (n = 79) cars. Levene's test compares variability across groups without requiring normality; this version is centred on group medians (`center = median`). H₀: σ²_A = σ²_E = σ²_J; H₁: at least one population variance differs.

**Results and conclusion.** The sample variances were 41.479, 43.299, and 37.089, respectively. Median-centred Levene's test gave F(2, 389) = 0.086, p = 0.918. Fail to reject H₀: there is no evidence in these data that mpg variance differs across the three origins.
