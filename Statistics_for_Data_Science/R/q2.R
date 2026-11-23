# ============================================================
# CDS533 Assignment 3 — Question 2
# One-way ANOVA: chick weight by feed type (chickwts)
# Run from the project root:  Rscript R/q2.R
# ============================================================

# ---------- (a) Design, hypotheses and assumption checks ----------

data(chickwts)  # built-in data frame: weight (g), feed (6-level factor)
str(chickwts)

# Descriptive statistics per feed group
feed_n    <- tapply(chickwts$weight, chickwts$feed, length)
feed_mean <- tapply(chickwts$weight, chickwts$feed, mean)
feed_sd   <- tapply(chickwts$weight, chickwts$feed, sd)
desc_stats <- round(rbind(n = feed_n, mean = feed_mean, sd = feed_sd), 3)
print(desc_stats)

# Homogeneity of variance — rule-of-thumb check on SDs
sd_ratio <- max(feed_sds <- feed_sd) / min(feed_sds)
cat(sprintf("max/min SD ratio = %.3f\n", sd_ratio))

# ---------- (b) Labelled plot and one-way ANOVA ----------

library(ggplot2)

p <- ggplot(chickwts, aes(x = feed, y = weight)) +
  geom_boxplot() +
  labs(title = "Chick weight by feed type",
       x = "Feed type",
       y = "Weight (grams)") +
  theme_minimal()
ggsave("report/q2_boxplot.png", plot = p, width = 7, height = 4.5, dpi = 300)

fit <- aov(weight ~ feed, data = chickwts)
print(summary(fit))  # ANOVA table: Df, Sum Sq, Mean Sq, F, Pr(>F)

# ---------- Diagnostic evidence for the assumptions ----------

png("report/q2_diagnostics.png", width = 2400, height = 1200, res = 300)
par(mfrow = c(1, 2))
plot(fit, which = 1)  # Residuals vs fitted  -> homogeneity of variance
plot(fit, which = 2)  # Normal Q-Q           -> normality
dev.off()
