# Question 2 — Chick weight by feed type (draft)

## (a) Population parameters, hypotheses and assumptions

Let μ₁, …, μ₆ denote the population mean chick weights (in grams) for the six
feed types (casein, horsebean, linseed, meatmeal, soybean, sunflower). The
hypotheses are

- H₀: μ₁ = μ₂ = ⋯ = μ₆ (all feed types have the same population mean weight);
- H₁: there exists at least one pair i ≠ j with μᵢ ≠ μⱼ (not all means are equal).

Note that H₁ claims only that *at least one* pair of means differs — it does
not claim that every pair differs.

**Independence.** Chicks were randomly assigned to the six feed groups, so
individual measurements carry no systematic relationship (e.g., no confounding
by litter or cohort). This assumption is supported by the study design.

**Normality.** The residuals from the fitted ANOVA model are examined with a
Normal Q–Q plot (Figure 2, right panel). The points follow the reference line
closely, with only mild right-tail departure, so the within-group weights are
treated as approximately normal.

**Homogeneity of variance.** The six group standard deviations range from
38.626 g (horsebean) to 64.901 g (meatmeal), giving a max/min SD ratio of
1.680 (< 2), and the residuals-vs-fitted plot (Figure 2, left panel) shows a
similar vertical spread of residuals across all six feed groups. The
equal-variance assumption is therefore considered acceptable.

## (b) Plot, ANOVA table and decision

**Figure 1** (report/q2_boxplot.png) shows boxplots of chick weight for each
feed type. Sunflower and casein clearly have the highest median weights, while
horsebean is far below the rest; group spreads are broadly comparable.

The one-way ANOVA table (R `aov`, α = 0.05):

| Source    | Df | Sum Sq  | Mean Sq | F       | Pr(>F)   |
| --------- | -- | ------- | ------- | ------- | -------- |
| feed      | 5  | 231129  | 46226   | 15.365  | < 0.001  |
| Residuals | 65 | 195556  | 3009    |         |          |

Since p < 0.001 < α = 0.05, we reject H₀. There is very strong evidence
(F(5, 65) = 15.365, p < 0.001) that the population mean chick weights are not
all equal across the six feed types — feed type is associated with substantial
differences in average chick weight.

## (c) Why the claim is not justified

The claim has two parts, and neither follows from a significant ANOVA.

1. *"A significant ANOVA means every feed type differs significantly from
   every other feed type."* The F statistic aggregates the squared deviations
   of **all** group means from the grand mean and compares the total with
   within-group noise. It detects that between-group variation overall exceeds
   noise — i.e. that **at least one pair** of means differs — but it carries
   no information about *which* pair, or *how many* pairs differ. The data are
   entirely consistent with a situation in which only one feed (e.g. the best)
   differs from the other five, which are mutually equal.

2. *"The feed with the highest sample mean is therefore significantly better
   than all the others."* The sample mean ranking reflects the observed
   sample, and the highest observed mean may partly be sampling variability —
   the ANOVA output contains no quantity that certifies any particular feed as
   the population best. Moreover, "significantly better than **all** others"
   requires the highest-mean feed to be compared against *each* of the other
   five feeds individually, and no such pairwise tests were performed.

A defensible conclusion is: there is very strong evidence that feed type
affects mean chick weight; descriptively, sunflower (sample mean 328.917 g)
and casein (323.583 g) achieved the highest average weights, but it cannot be
asserted from the ANOVA alone that any single feed is significantly superior
to the others. To identify which particular pairs of feeds differ, post-hoc
pairwise multiple comparisons (e.g. Tukey's HSD, which controls the
family-wise error rate) would be required. Such tests are not conducted here,
as they are outside the scope of this question.
