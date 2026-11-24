# CDS533, Q4 item 3: Gaussian GLM for QQ Music streams
# Ruiqi Gu 顾瑞祺, role 5, Q4 modelling lead


# working folder, the one holding data/
path <- "."

# if sourced from elsewhere, use this file's folder instead
if (!file.exists(file.path(path, "data/QQ_Music_clean.csv"))) {
  f <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(f)) path <- dirname(normalizePath(f))
}
if (!file.exists(file.path(path, "data/QQ_Music_clean.csv")))
  stop("data/QQ_Music_clean.csv not found. Run Q4_EDA.R first, or setwd() to it.")
for (d in c("figures", "tables")) dir.create(file.path(path, d), showWarnings = FALSE)

RES <- 300
preview <- interactive()          # TRUE -> Plots pane, FALSE -> PNG in figures/

open_fig <- function(file, w, h) {
  if (preview) {
    par(mfrow = c(1, 1), oma = c(0, 0, 0, 0), mar = c(5.1, 4.1, 4.1, 2.1),
        mgp = c(3, 1, 0), las = 0, pch = 1, col = "black", cex = 1, cex.axis = 1)
  } else {
    png(file.path(path, file), width = w * RES, height = h * RES, res = RES)
  }
}
close_fig <- function() if (!preview) invisible(dev.off())


# ===========================================================================
# 0. setup: the input file and the observed ranges
# ===========================================================================

dat <- read.csv(file.path(path, "data/QQ_Music_clean.csv"), fileEncoding = "UTF-8",
                stringsAsFactors = FALSE)

dim(dat)
sum(is.na(dat$streams))
range(dat$streams)                       # 2,762 to 3.70 billion
mean(dat$streams^2) / mean(dat$streams) - mean(dat$streams)   # Var/mean, 6.4e8

# playlists straight only in logs, charts as a factor
dat$log_playlists <- log10(dat$qq_playlists)
dat$charted_qq    <- factor(dat$charted_qq, levels = c(0, 1),
                            labels = c("No", "Yes"))

# ranges of the final predictors, needed in 3(d)(ii)
sapply(dat[c("qq_playlists", "release_year", "artist_count")], range)


# ===========================================================================
# 3(a) which predictors enter, and why
# ===========================================================================

# in_QQ_charts and in_apple_charts read as flags but hold counts
sapply(dat[c("qq_playlists", "qq_charts", "apple_playlists", "apple_charts")], range)
length(unique(na.omit(dat$key)))          # 11 observed levels, 10.6% missing
round(mean(is.na(dat$key)), 3)

# the six columns excluded rather than tested, and what each relates to
round(c(apple_playlists = cor(dat$qq_playlists, dat$apple_playlists),
        apple_charts   = cor(dat$qq_charts, dat$apple_charts),
        charted_apple  = cor(as.integer(dat$charted_qq), dat$charted_apple),
        collab         = cor(dat$collab, dat$artist_count),
        liveness       = cor(dat$liveness, dat$log10_streams),
        liveness_rho   = cor(dat$liveness, dat$log10_streams, method = "spearman")), 3)

# the chosen form, with the two rejected encodings beside it so AIC compares
# on the same response and the same controls
form4  <- log10_streams ~ log_playlists + charted_qq + release_year + artist_count
m2     <- lm(form4, data = dat)                                  # chosen form
m2_cnt <- lm(log10_streams ~ log_playlists + log1p(qq_charts) + release_year +
               artist_count, data = dat)                         # count, not indicator

# exposure block on its own, in logs and as a raw count
m1     <- lm(log10_streams ~ log_playlists + charted_qq, data = dat)
m1_raw <- lm(log10_streams ~ qq_playlists + charted_qq, data = dat)

# Table 1 evidence column
enc <- data.frame(
  form   = c("playlists: log", "playlists: raw", "charts: indicator", "charts: count"),
  AIC    = round(c(AIC(m1), AIC(m1_raw), AIC(m2), AIC(m2_cnt)), 1),
  adj_R2 = round(c(summary(m1)$adj.r.squared, summary(m1_raw)$adj.r.squared,
                   summary(m2)$adj.r.squared, summary(m2_cnt)$adj.r.squared), 4))
enc


# ===========================================================================
# 3(b) correlation and multicollinearity
# ===========================================================================

# 13 numeric predictors, response left out: 13 x 13, so 78 pairs
num <- c("qq_playlists", "apple_playlists", "qq_charts", "apple_charts",
         "danceability", "energy", "valence", "acousticness", "speechiness",
         "instrumentalness", "bpm", "release_year", "artist_count")
R <- cor(dat[num])
length(num); length(num) * (length(num) - 1) / 2
round(median(abs(R[upper.tri(R)])), 3)         # median absolute r

R[lower.tri(R, diag = TRUE)] <- NA
hi <- which(abs(R) > 0.5, arr.ind = TRUE)
corr_pairs <- data.frame(a = rownames(R)[hi[, 1]], b = colnames(R)[hi[, 2]],
                         r = round(R[hi], 3))
corr_pairs                                       # the three pairs above 0.5
write.csv(corr_pairs, file.path(path, "tables/correlation_pairs.csv"), row.names = FALSE)

# VIF on the full candidate model, every predictor in at once
m3 <- lm(log10_streams ~ log_playlists + charted_qq + release_year + artist_count +
           danceability + energy + valence + acousticness + speechiness +
           instrumentalness + bpm + mode, data = dat)

X   <- model.matrix(m3)[, -1]
vif <- sapply(seq_len(ncol(X)),
              function(j) 1 / (1 - summary(lm(X[, j] ~ X[, -j]))$r.squared))
vif <- data.frame(term = colnames(X), VIF = round(vif, 3))
vif <- vif[order(-vif$VIF), ]
vif
write.csv(vif, file.path(path, "tables/vif.csv"), row.names = FALSE)

# same screen on the terms that actually enter
Rm <- cor(X); Rm[lower.tri(Rm, diag = TRUE)] <- NA
max(abs(Rm), na.rm = TRUE)                        # 0.595 among entered terms


# ===========================================================================
# 3(c) model specification and selection
# ===========================================================================

# ---------------------------------------------------------------------------
# 3(c)(i) response scale, family, link
# ---------------------------------------------------------------------------

# same predictors on the raw response, for the log-scale argument
raw_fit <- lm(streams ~ log_playlists + charted_qq + release_year + artist_count,
              data = dat)
round(c(sigma = summary(raw_fit)$sigma, mean_streams = mean(dat$streams),
        sigma_over_mean = summary(raw_fit)$sigma / mean(dat$streams)), 3)
round(summary(raw_fit)$r.squared, 3)

# gaussian + identity gives the same fit as lm()
gm <- glm(log10_streams ~ log_playlists + charted_qq + release_year + artist_count,
          family = gaussian(link = "identity"), data = dat)
all.equal(coef(gm), coef(m2))            # TRUE
all.equal(deviance(gm), deviance(m2))    # TRUE


# ---------------------------------------------------------------------------
# 3(c)(ii) nested comparison
# ---------------------------------------------------------------------------

summary(m1)
summary(m2)
summary(m3)

anova(m1, m2)      # timing and artist block
anova(m2, m3)      # audio block
AIC(m1, m2, m3)
BIC(m1, m2, m3)

fits <- list(m1, m2, m3)
cmp <- data.frame(
  model  = c("M1 exposure only", "M2 + timing/artist", "M3 + audio features"),
  k      = sapply(fits, function(m) length(coef(m)) - 1),
  R2     = round(sapply(fits, function(m) summary(m)$r.squared), 4),
  adj_R2 = round(sapply(fits, function(m) summary(m)$adj.r.squared), 4),
  AIC    = round(sapply(fits, AIC), 4),
  BIC    = round(sapply(fits, BIC), 4),
  RMSE   = round(sapply(fits, function(m) summary(m)$sigma), 4))
cmp
write.csv(cmp, file.path(path, "tables/model_comparison.csv"), row.names = FALSE)


# ---------------------------------------------------------------------------
# 3(c)(iii) final model, coefficients, intervals
# ---------------------------------------------------------------------------

final <- m2                     # chosen on AIC, BIC and the F tests

b     <- coef(final)
ci    <- confint(final)
s     <- summary(final)$coefficients

coefs <- data.frame(term = rownames(s), estimate = s[, 1], se = s[, 2],
                    t = s[, 3], p = s[, 4], ci_low = ci[, 1], ci_high = ci[, 2])
coefs[, 2:7] <- round(coefs[, 2:7], 4)
coefs
write.csv(coefs, file.path(path, "tables/final_coefficients.csv"), row.names = FALSE)

# the model as a whole
summary(final)$fstatistic
round(c(R2 = summary(final)$r.squared, adj_R2 = summary(final)$adj.r.squared,
        sigma = summary(final)$sigma), 4)

# 10^(beta*log10(f)) turns a log coefficient into a percentage (3S "size" row)
pct <- function(beta, factor) (10^(beta * log10(factor)) - 1) * 100
data.frame(change = c("QQ playlists x2", "QQ playlists +10%", "On a chart (Yes vs No)"),
           pct = round(c(pct(b["log_playlists"], 2), pct(b["log_playlists"], 1.1),
                         pct(b["charted_qqYes"], 10)), 1))

# the same two at the confidence limits
round(c(playlists_per_10pct_low  = pct(ci["log_playlists", 1], 1.1),
        playlists_per_10pct_high = pct(ci["log_playlists", 2], 1.1),
        charted_low  = pct(ci["charted_qqYes", 1], 10),
        charted_high = pct(ci["charted_qqYes", 2], 10)), 1)

# artist_count on the response scale: one extra artist
round(100 * (10^b["artist_count"] - 1), 1)

# release_year: strong on its own, gone once exposure is in
summary(lm(log10_streams ~ release_year, data = dat))$coefficients
tapply(dat$qq_playlists, dat$release_year <= 2010, median)

# playlist coefficient across the three models
round(c(M1 = coef(m1)["log_playlists"], M2 = coef(m2)["log_playlists"],
        M3 = coef(m3)["log_playlists"]), 3)


# ===========================================================================
# 3(d) diagnostics and prediction
# ===========================================================================

# ---------------------------------------------------------------------------
# 3(d)(i) diagnostics
# ---------------------------------------------------------------------------

open_fig("figures/fig7_diagnostics.png", 8, 7)          # Figure 1 of the report
par(mfrow = c(2, 2), mar = c(4.2, 4.2, 2.4, 1.2), cex = 0.85)
plot(final, which = 1:4, col = "#1F4E79", pch = 16, cex = 0.45)
close_fig()

res <- residuals(final)
shapiro.test(res)

# Breusch-Pagan
mf  <- model.frame(final)
aux <- lm(I(res^2) ~ ., data = mf[, -1])
bp  <- nrow(mf) * summary(aux)$r.squared
c(LM = bp, df = ncol(mf) - 1, p = pchisq(bp, df = ncol(mf) - 1, lower.tail = FALSE))

cd <- cooks.distance(final)
c(max_cook = max(cd), D_above_1 = sum(cd > 1),
  song = dat$track_name[as.integer(rownames(mf))[which.max(cd)]])
rs <- rstandard(final)
c(above_3 = sum(abs(rs) > 3), negative = sum(rs < -3))
data.frame(song = dat$track_name[which.min(res)], fitted = fitted(final)[which.min(res)],
           residual = min(res))                  # 4.77 log units below its fitted value

# is the line straight enough? mean residual in eighths of the fitted range
bins <- cut(fitted(final), quantile(fitted(final), seq(0, 1, 0.125)), include.lowest = TRUE)
round(tapply(residuals(final), bins, mean), 3)

# a quadratic in log_playlists, and what it would buy
m2q <- update(final, . ~ . + I(log_playlists^2))
anova(final, m2q)
round(c(R2_final = summary(final)$r.squared, R2_quad = summary(m2q)$r.squared,
        AIC_final = AIC(final), AIC_quad = AIC(m2q),
        sigma_final = summary(final)$sigma, sigma_quad = summary(m2q)$sigma), 4)

# where the two fits disagree, as a percentage of the fitted streams
ndq <- data.frame(log_playlists = log10(c(100, 300, 1000, 5000, 10000, 20000, 50000)),
                  charted_qq = factor("Yes", levels = c("No", "Yes")),
                  release_year = 2022, artist_count = 1)
data.frame(playlists = c(100, 300, 1000, 5000, 10000, 20000, 50000),
           pct_diff = round(100 * (10^predict(m2q, ndq) / 10^predict(final, ndq) - 1), 1))
c(below_100 = sum(dat$qq_playlists < 100), above_50000 = sum(dat$qq_playlists > 50000))

# is the chart effect additive?
anova(final, update(final, . ~ . + log_playlists:charted_qq))


# ---------------------------------------------------------------------------
# 3(d)(ii) prediction
# ---------------------------------------------------------------------------

new_song <- data.frame(
  profile       = c("Low exposure: 300 playlists, not charted",
                    "Reference: 5,000 playlists, charted",
                    "High exposure: 20,000 playlists, charted"),
  playlists     = c(300, 5000, 20000),
  charted       = c("No", "Yes", "Yes"),
  log_playlists = log10(c(300, 5000, 20000)),
  charted_qq    = factor(c("No", "Yes", "Yes"), levels = c("No", "Yes")),
  release_year  = 2022, artist_count = 1)

pi  <- predict(final, newdata = new_song, interval = "prediction", level = 0.95)
ci2 <- predict(final, newdata = new_song, interval = "confidence", level = 0.95)
round(mean(dat$qq_playlists <= 5000) * 100)   # the reference profile sits at the 71st percentile

pred <- data.frame(profile = new_song$profile, playlists = new_song$playlists,
                   charted = new_song$charted,
                   fit_log10 = round(pi[, 1], 3), pi_low_log10 = round(pi[, 2], 3),
                   pi_high_log10 = round(pi[, 3], 3),
                   fit_millions = round(10^pi[, 1] / 1e6, 3),
                   pi_low_millions = round(10^pi[, 2] / 1e6, 3),
                   pi_high_millions = round(10^pi[, 3] / 1e6, 3))
pred
round(10^ci2 / 1e6, 3)           # mean-response interval
round(10^(pi[2, 3] - pi[2, 2]), 1)   # width of the prediction interval, as a factor

write.csv(pred, file.path(path, "tables/prediction.csv"), row.names = FALSE)

# Figure 2 of the report: fitted curve with its band, and the coefficients
grid <- exp(seq(log(min(dat$qq_playlists)), log(max(dat$qq_playlists)), length.out = 150))
nd   <- data.frame(log_playlists = log10(grid),
                   charted_qq    = factor("Yes", levels = c("No", "Yes")),
                   release_year  = 2022, artist_count = 1)
band <- predict(final, newdata = nd, interval = "prediction", level = 0.95)

open_fig("figures/fig8_coefficients_and_prediction.png", 10.5, 4.4)
par(mfrow = c(1, 2), mar = c(3.9, 4.6, 3.2, 1), mgp = c(2.6, 0.7, 0))

plot(dat$qq_playlists, dat$streams, log = "xy", type = "n", xaxt = "n", yaxt = "n",
     main = "(a) Fitted streams against playlist count",
     xlab = "QQ Music playlists (log scale)", ylab = "Streams (log scale)")
polygon(c(grid, rev(grid)), 10^c(band[, 2], rev(band[, 3])),
        col = "grey88", border = NA)
points(dat$qq_playlists, dat$streams, pch = 16, cex = 0.35, col = rgb(0, 0, 0, 0.14))
lines(grid, 10^band[, 1], col = "#C0504D", lwd = 2)
axis(1, at = c(100, 1000, 10000), labels = c("100", "1,000", "10,000"))
axis(2, at = 10^c(3, 5, 7, 9), labels = c("1k", "100k", "10M", "1B"), las = 1)
mtext("band = 95% prediction interval (charted, 2022, one artist)", side = 3,
      line = 0.3, cex = 0.78, col = "grey30")

cf <- coefs[-1, ]
cf <- cf[order(cf$estimate), ]
par(mar = c(3.9, 6.4, 3.2, 1))
y  <- seq_len(nrow(cf))
plot(cf$estimate, y, xlim = range(cf$ci_low, cf$ci_high), yaxt = "n", pch = 16,
     col = "#C0504D", cex = 1.3, main = "(b) Coefficients and 95% CIs",
     xlab = "Estimate (log10 scale)", ylab = "")
segments(cf$ci_low, y, cf$ci_high, y, col = "#1F4E79", lwd = 2)
abline(v = 0, lty = 2, col = "grey40")
axis(2, at = y, labels = cf$term, las = 1, cex.axis = 0.9)
close_fig()


# ===========================================================================
# 3(e) conclusion and model justification
# ===========================================================================

# ---------------------------------------------------------------------------
# 3(e)(i) the ranking under a different response scale
# ---------------------------------------------------------------------------

thr <- quantile(dat$streams, 0.75)   # top quarter
dat$hit <- as.integer(dat$streams >= thr)
round(c(threshold = thr, hits = sum(dat$hit), share = mean(dat$hit)), 3)

hit <- glm(hit ~ log_playlists + charted_qq + release_year + artist_count,
           family = binomial, data = dat)
summary(hit)
round(exp(cbind(OR = coef(hit), confint(hit))), 3)
1 - as.numeric(logLik(hit) / logLik(update(hit, . ~ 1)))   # McFadden R2
10^(coef(hit)["log_playlists"] * log10(2))                 # odds ratio for a doubling


# ---------------------------------------------------------------------------
# 3(e)(ii) the selection summary
# ---------------------------------------------------------------------------

cmp                                     # adjusted R2, AIC and BIC favour M2
anova(m2, m3)                           # the audio block fails the F test
max(vif$VIF); max(abs(Rm), na.rm = TRUE)
round(c(M1 = coef(m1)["log_playlists"], M2 = coef(m2)["log_playlists"],
        M3 = coef(m3)["log_playlists"]), 3)
