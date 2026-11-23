# Question 2 — Chick weight by feed type (draft)

## (a) Hypotheses and assumptions

Let μ₁, …, μ₆ be the population mean chick weights for the six feeds
(casein, horsebean, linseed, meatmeal, soybean, sunflower).

- H₀: μ₁ = μ₂ = ⋯ = μ₆
- H₁: at least one pair of means differs

H₁ does not say every pair differs.

**Independence.** Chicks were randomly assigned to feed groups, so
measurements are independent.

**Normality.** The Normal Q–Q plot of the residuals (Figure 2, right) follows
the reference line with mild right-tail departure, so normality is reasonable.

**Homogeneity of variance.** Group SDs range from 38.626 to 64.901; the
max/min ratio is 1.680 (< 2). The residuals-vs-fitted plot (Figure 2, left)
shows similar spread across groups. Equal variances are reasonable.

## (b) Plot, ANOVA table and decision

**Figure 1** (report/q2_boxplot.png) shows weight by feed type. Sunflower and
casein have the highest means; horsebean is far below the rest.

One-way ANOVA (α = 0.05):

| Source    | Df | Sum Sq | Mean Sq | F      | Pr(>F)  |
| --------- | -- | ------ | ------- | ------ | ------- |
| feed      | 5  | 231129 | 46226   | 15.365 | < 0.001 |
| Residuals | 65 | 195556 | 3009    |        |         |

p < 0.001 < 0.05, so we reject H₀. There is strong evidence (F(5, 65) =
15.365, p < 0.001) that mean chick weights differ among the six feeds.

## (c) Why the claim is not justified

1. *"A significant ANOVA means every feed differs from every other feed."* The
   F statistic sums the squared deviations of all group means from the grand
   mean. It shows that between-group variation exceeds noise, i.e. at least
   one pair of means differs. It does not show which pair or how many. The
   data are consistent with only one feed differing from the other five.

2. *"The feed with the highest sample mean is significantly better than all
   the others."* The sample mean ranking may reflect sampling variability; the
   ANOVA gives no result for any single feed. Also, "better than all others"
   requires comparing the top feed with each of the other five feeds, and no
   pairwise tests were done.

Defensible conclusion: feed type affects mean chick weight. Sunflower (mean
328.917 g) and casein (323.583 g) have the highest sample means, but we cannot
say any feed is significantly better than the others. To find which pairs
differ, post-hoc pairwise tests (e.g. Tukey's HSD) with multiplicity control
are needed. They are not done here, as the question does not require them.
