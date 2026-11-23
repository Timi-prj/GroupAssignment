if (!requireNamespace("ggplot2", quietly = TRUE)) {
  stop("Package 'ggplot2' is required for the figures. ",
       "Install it with install.packages(\"ggplot2\").", call. = FALSE)
}
library(ggplot2)

if (!dir.exists("figures")) dir.create("figures", showWarnings = FALSE)

banner <- function(x) cat("\n", strrep("-", 74), "\n", x, "\n",
                          strrep("-", 74), "\n", sep = "")

red   <- c(80, 80, 78, 81, 72, 85, 96, 84, 71, 75, 98)
white <- c(75, 55, 98, 92, 86, 78, 87, 79, 88, 87, 85, 94, 99)
blue  <- c(72, 76, 70, 77, 68, 82, 85, 81, 65, 69)

ads <- data.frame(
  score = c(red, white, blue),
  advertisement = factor(
    rep(c("Red", "White", "Blue"), times = c(length(red), length(white), length(blue))),
    levels = c("Red", "White", "Blue")
  )
)

banner("1. DATA AND DATA-QUALITY CHECK")
cat("Observations read :", nrow(ads), "\n")
cat("Missing values    :", sum(is.na(ads$score)), "\n")
cat("Non-positive score:", sum(ads$score <= 0), "\n")
print(table(ads$advertisement))
cat("\nAll 34 scores are valid positive integers. No observation is excluded,\n")
cat("imputed or modified; the supplied data are analysed exactly as given.\n")

banner("2. DESCRIPTIVE STATISTICS BY ADVERTISEMENT")

desc <- function(x) {
  c(n        = length(x),
    mean     = mean(x),
    sd       = sd(x),
    median   = median(x),
    q1       = unname(quantile(x, 0.25)),
    q3       = unname(quantile(x, 0.75)),
    iqr      = IQR(x),
    min      = min(x),
    max      = max(x),
    variance = var(x),
    skewness = mean((x - mean(x))^3) / sd(x)^3)
}

desc_table <- t(sapply(split(ads$score, ads$advertisement), desc))
print(round(desc_table, 3))

cat("\nVariance ratio (largest / smallest) =",
    round(max(desc_table[, "variance"]) / min(desc_table[, "variance"]), 3), "\n")
cat("SD ratio      (largest / smallest) =",
    round(max(desc_table[, "sd"]) / min(desc_table[, "sd"]), 3), "\n")

banner("3. ASSUMPTION DIAGNOSTICS")

cat("3.1 Normality within each group (Shapiro-Wilk)\n")
sw <- sapply(split(ads$score, ads$advertisement),
             function(x) unname(shapiro.test(x)$p.value))
print(round(sw, 3))
cat("Note: with n = 10-13 these tests have very low power, so a non-significant\n")
cat("      result does not establish normality. The White group is the closest to\n")
cat("      rejection (p = 0.094) and contains an extreme low score of 55.\n")

cat("\n3.2 Equal variances (Brown-Forsythe / median-centred Levene)\n")

z <- abs(ads$score - ave(ads$score, ads$advertisement, FUN = median))
bf <- summary(aov(z ~ ads$advertisement))[[1]]
cat("Brown-Forsythe F =", round(bf[["F value"]][1], 3),
    "  df =", bf[["Df"]][1], "and", bf[["Df"]][2],
    "  p =", round(bf[["Pr(>F)"]][1], 3), "\n")

banner("4. KRUSKAL-WALLIS RANK-SUM TEST")

kw <- kruskal.test(score ~ advertisement, data = ads)
print(kw)

H  <- unname(kw$statistic)
df <- unname(kw$parameter)
p  <- kw$p.value
N  <- nrow(ads)

cat("\nTest statistic H   :", round(H, 3), "\n")
cat("Degrees of freedom :", df, "\n")
cat("p-value            :", ifelse(p < 0.001, "< 0.001", sprintf("%.3f", p)), "\n")
cat("Decision (alpha=.05):", ifelse(p < 0.05, "Reject H0", "Fail to reject H0"), "\n")

cat("\nMean rank by advertisement (expected rank under H0 = (N+1)/2 =",
    (N + 1) / 2, ")\n")
mean_ranks <- tapply(rank(ads$score), ads$advertisement, mean)
print(round(mean_ranks, 3))
cat("\nRank-sum T_i by advertisement:\n")
print(tapply(rank(ads$score), ads$advertisement, sum))

eps2 <- H / ((N^2 - 1) / (N + 1))
cat("\nEffect size epsilon-squared =", round(eps2, 3), "\n")
cat("(guidelines: 0.01 small, 0.06 medium, 0.14 large)\n")

banner("5. SENSITIVITY CHECKS")

cat("5.1 One-way ANOVA on the raw scores (parametric cross-check only)\n")
print(summary(aov(score ~ advertisement, data = ads)))

cat("\n5.2 Permutation tests (20,000 reshuffles; seed fixed for reproducibility)\n")
set.seed(2026)
B <- 20000

perm_H <- numeric(B)
perm_F <- numeric(B)
for (b in seq_len(B)) {
  g_b          <- sample(ads$advertisement)
  perm_H[b]    <- unname(kruskal.test(ads$score ~ g_b)$statistic)
  perm_F[b]    <- summary(aov(ads$score ~ g_b))[[1]][["F value"]][1]
}
F_obs <- summary(aov(score ~ advertisement, data = ads))[[1]][["F value"]][1]

cat("Kruskal-Wallis permutation p =",
    sprintf("%.3f", (sum(perm_H >= H) + 1) / (B + 1)), "\n")
cat("ANOVA          permutation p =",
    sprintf("%.3f", (sum(perm_F >= F_obs) + 1) / (B + 1)), "\n")
cat("(exact Monte Carlo fractions:",
    sum(perm_H >= H) + 1, "/", B + 1, "and",
    sum(perm_F >= F_obs) + 1, "/", B + 1, ")\n")

banner("6. FIGURES")

pal <- c(Red = "#C0392B", White = "#8D99AE", Blue = "#1F6FB2")

p1 <- ggplot(ads, aes(x = advertisement, y = score, fill = advertisement)) +
  geom_boxplot(width = 0.52, outlier.shape = NA, alpha = 0.45,
               colour = "grey20", linewidth = 0.5) +
  geom_jitter(width = 0.09, height = 0, size = 2.1, alpha = 0.8,
              colour = "grey15", shape = 16) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3.0,
               fill = "white", colour = "black", stroke = 1.0) +
  scale_fill_manual(values = pal) +
  scale_y_continuous(breaks = seq(50, 100, 10), limits = c(48, 102)) +
  labs(x = "Advertisement shown",
       y = "Ordered reaction score (higher = more favourable)") +
  theme_bw(base_size = 11) +
  theme(legend.position   = "none",
        panel.grid.minor  = element_blank(),
        panel.border      = element_rect(colour = "grey40", linewidth = 0.5),
        axis.text         = element_text(colour = "grey15"),
        axis.title        = element_text(colour = "grey10"))

ggsave("figures/Q1_fig1_boxplot.png", p1, width = 6.3, height = 3.05, dpi = 300)

p2 <- ggplot(ads, aes(x = score, fill = advertisement)) +
  geom_histogram(binwidth = 5, boundary = 50, closed = "left",
                 colour = "white", linewidth = 0.3, alpha = 0.9) +
  geom_vline(data = aggregate(score ~ advertisement, data = ads, FUN = mean),
             aes(xintercept = score), linetype = "dashed",
             colour = "grey15", linewidth = 0.4) +
  facet_wrap(~ advertisement, nrow = 1) +
  scale_fill_manual(values = pal) +
  scale_x_continuous(breaks = seq(50, 100, 10)) +
  labs(x = "Ordered reaction score", y = "Frequency") +
  theme_bw(base_size = 10) +
  theme(legend.position  = "none",
        panel.grid.minor = element_blank(),
        panel.border     = element_rect(colour = "grey40", linewidth = 0.5),
        strip.background = element_rect(fill = "grey94", colour = "grey40"),
        strip.text       = element_text(colour = "grey10"),
        axis.text        = element_text(colour = "grey15"))

ggsave("figures/Q1_fig2_histograms.png", p2, width = 6.9, height = 2.7, dpi = 300)

cat("Saved: figures/Q1_fig1_boxplot.png\n")
cat("Saved: figures/Q1_fig2_histograms.png\n")

write.csv(round(desc_table, 3), "figures/Q1_descriptives.csv", row.names = TRUE)
cat("Saved: figures/Q1_descriptives.csv\n")

banner("END OF QUESTION 1")
