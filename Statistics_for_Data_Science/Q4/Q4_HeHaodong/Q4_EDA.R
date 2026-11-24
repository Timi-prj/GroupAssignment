# CDS533, Q4 items 1-2: QQ Music EDA
# Haodong He 贺浩东, 3162500, role 4


# working folder, the one holding data/
path <- "."

# if sourced from elsewhere, use this file's folder instead
if (!file.exists(file.path(path, "data/QQ_Music.csv"))) {
  f <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(f)) path <- dirname(normalizePath(f))
}
if (!file.exists(file.path(path, "data/QQ_Music.csv")))
  stop("data/QQ_Music.csv not found. setwd() to the folder that holds it.")
for (d in c("figures", "tables")) dir.create(file.path(path, d), showWarnings = FALSE)

library(skimr)
library(DataExplorer)
library(psych)

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

# moment skewness, same as psych::skew and e1071 type 3
skew <- function(x) {
  x <- x[!is.na(x)]
  sum((x - mean(x))^3) / length(x) / sd(x)^3
}


# ===========================================================================
# 0. data prep  (Tables 1-2)
# ===========================================================================

dat <- read.csv(file.path(path, "data/QQ_Music.csv"), fileEncoding = "UTF-8-BOM",
                stringsAsFactors = FALSE, check.names = FALSE)

dim(dat)                      # 844 x 21
str(dat)
colSums(is.na(dat))

# in_* columns look like flags but hold counts
sapply(dat[c("in_QQ_playlists", "in_QQ_charts", "in_apple_playlists",
             "in_apple_charts")], range)

# key: empty string for missing, so it reads as 12 levels
length(unique(dat$key)); table(dat$key, useNA = "ifany")

# 15 names are awkward in a formula, so rename once through a lookup (Table 1)
old <- c("artist(s)_name", "released_year", "released_month", "released_day",
         "in_QQ_playlists", "in_QQ_charts", "in_apple_playlists",
         "in_apple_charts", "danceability_%", "valence_%", "energy_%",
         "acousticness_%", "instrumentalness_%", "liveness_%", "speechiness_%")
new <- c("artist_name", "release_year", "release_month", "release_day",
         "qq_playlists", "qq_charts", "apple_playlists", "apple_charts",
         "danceability", "valence", "energy", "acousticness",
         "instrumentalness", "liveness", "speechiness")
names(dat)[match(old, names(dat))] <- new

write.csv(data.frame(raw = c("track_name", old, "streams", "bpm", "key", "mode",
                             "artist_count"),
                     analysis = c("track_name", new, "streams", "bpm", "key",
                                  "mode", "artist_count")),
          file.path(path, "tables/column_map.csv"), row.names = FALSE)

# 844 -> 842, three rules
n_raw <- nrow(dat)

dat$streams <- suppressWarnings(as.numeric(dat$streams))          # rule 1
bad_streams <- dat[is.na(dat$streams), c("track_name", "artist_name", "streams")]
n_bad <- nrow(bad_streams)          # value set to NA, no row dropped
n1 <- nrow(dat)                     # rule 1 removes nothing

k   <- paste(tolower(dat$track_name), tolower(dat$artist_name), dat$streams)
dup <- duplicated(k) & !is.na(dat$streams)
dup_row <- dat[dup, c("track_name", "artist_name", "streams")]
dat <- dat[!dup, ]                                                # rule 2
n2 <- nrow(dat)

dat <- dat[!is.na(dat$streams) & dat$streams > 0, ]               # rule 3
n3 <- nrow(dat)

dat$key[!is.na(dat$key) & trimws(dat$key) == ""] <- NA            # rule 4

nrow(dat)                     # 842

# Table 2: the two rows leave through rules 2 and 3, not through rule 1
removed <- data.frame(step = 0:3, rule = c("Raw file", "Non-numeric streams set to missing",
                                           "Duplicate on title + artist + streams removed",
                                           "Missing response excluded"),
                      rows_affected = c(NA, n_bad, n1 - n2, n2 - n3),
                      rows_left = c(n_raw, n1, n2, n3))
removed
write.csv(removed, file.path(path, "tables/records_removed.csv"), row.names = FALSE)

# the two rows, and the same-title pairs that stay
bad_streams          # Love Grows, audio string shifted into the streams column
dup_row              # About Damn Time, Lizzo
tt   <- tolower(dat$track_name)
keep <- dat[tt %in% tt[duplicated(tt)], c("track_name", "artist_name", "streams")]
grp  <- split(seq_len(nrow(keep)), tolower(keep$track_name))
c(titles_kept = length(grp),
  different_artist = sum(sapply(grp, function(i)
    length(unique(tolower(keep$artist_name[i]))) > 1)),
  same_artist = sum(sapply(grp, function(i)
    length(unique(tolower(keep$artist_name[i]))) == 1)))
keep[order(tolower(keep$track_name)), ]

# derived columns
dat$log10_streams <- log10(dat$streams)
dat$charted_qq    <- as.integer(dat$qq_charts > 0)
dat$charted_apple <- as.integer(dat$apple_charts > 0)
dat$collab        <- as.integer(dat$artist_count > 1)
dat$decade        <- factor(paste0(floor(dat$release_year / 10) * 10, "s"))
dat$artist_group  <- factor(pmin(dat$artist_count, 4), levels = 1:4,
                            labels = c("1", "2", "3", "4+"))
dat$mode          <- factor(dat$mode, levels = c("Major", "Minor"))

# consistency checks, all zero
pct <- c("danceability", "valence", "energy", "acousticness",
         "instrumentalness", "liveness", "speechiness")
c(streams  = sum(dat$streams <= 0),
  bpm      = sum(dat$bpm < 40 | dat$bpm > 220),
  pct      = sum(sapply(dat[pct], function(x) any(x < 0 | x > 100))),
  date     = sum(is.na(as.Date(sprintf("%d-%02d-%02d", dat$release_year,
                                       dat$release_month, dat$release_day)))),
  counts   = sum(dat$qq_playlists < 0 | dat$qq_charts < 0 |
                   dat$apple_playlists < 0 | dat$apple_charts < 0),
  key      = sum(is.na(dat$key)),
  mode     = sum(is.na(dat$mode)))

# missing key: how much, and does it track streams
c(missing_key = sum(is.na(dat$key)), share = mean(is.na(dat$key)))
round(tapply(dat$log10_streams, is.na(dat$key), mean), 3)
round(mean(dat$qq_charts == 0), 3)          # 43.5% of songs chart nowhere


# ===========================================================================
# 1(a) distributions and relationships
# ===========================================================================

# ---------------------------------------------------------------------------
# 1(a)(i) step 1: skim() -> Table 3, Figure 1
# ---------------------------------------------------------------------------

skim_tab <- as.data.frame(skim(dat))
skim_tab
# glyphs differ by locale, drop the column to keep the CSV byte-stable
skim_tab$numeric.hist <- NULL
write.csv(skim_tab, file.path(path, "tables/skim_summary.csv"), row.names = FALSE,
          fileEncoding = "UTF-8")

# 21 numeric, 3 factor, 3 character
table(sapply(dat, function(x) if (is.numeric(x)) "numeric" else class(x)))

# skewness column of Table 3, from our own function
tab3 <- c("streams", "log10_streams", "qq_playlists", "qq_charts", "apple_playlists",
          "apple_charts", "artist_count", "release_year", "bpm", "danceability",
          "valence", "energy", "acousticness", "instrumentalness", "liveness",
          "speechiness")
round(sapply(dat[tab3], skew), 3)

# mean against median, plus the zero shares behind two rows
round(mean(dat$qq_playlists) / median(dat$qq_playlists), 2)
round(c(released_2020 = mean(dat$release_year >= 2020),
        instrumental_zero = mean(dat$instrumentalness == 0)), 3)

# Figure 1: response, raw and logged
open_fig("figures/fig1_response_distribution.png", 9, 3.6)
par(mfrow = c(1, 2), mar = c(4.2, 4.4, 3.4, 1), mgp = c(2.4, 0.7, 0), las = 1)

hist(dat$streams / 1e6, breaks = 60, col = "#9DB4CE", border = "white",
     main = "(a) Streams, original scale", xlab = "Streams (millions)",
     ylab = "Number of songs")
mtext(sprintf("skewness = %.1f;  range %.0f - %.0f million", skew(dat$streams),
              min(dat$streams) / 1e6, max(dat$streams) / 1e6), side = 3,
      line = 0.35, cex = 0.78, col = "grey30")

hist(dat$log10_streams, breaks = 30, freq = FALSE, col = "#9DB4CE",
     border = "white", main = "(b) log10(streams)",
     xlab = expression(log[10]("streams")), ylab = "Density")
curve(dnorm(x, mean(dat$log10_streams), sd(dat$log10_streams)),
      add = TRUE, col = "#C0504D", lwd = 2)
mtext(sprintf("skewness = %.2f; left tail = two records below 10^7",
              skew(dat$log10_streams)), side = 3, line = 0.35, cex = 0.78,
      col = "grey30")
close_fig()


# ---------------------------------------------------------------------------
# 1(a)(ii) step 2: create_report()
# ---------------------------------------------------------------------------

create_report(dat, y = "log10_streams", output_file = "eda_report.html",
              output_dir = file.path(path, "figures"),
              report_title = "QQ Music: EDA report")


# ---------------------------------------------------------------------------
# 1(a)(iii) step 3: diagnose() -> Table 4, Figure 2
# ---------------------------------------------------------------------------

# raw numeric columns only, no derived or calendar ones
num <- setdiff(names(dat)[sapply(dat, is.numeric)],
               c("log10_streams", "charted_qq", "charted_apple", "collab",
                 "release_month", "release_day"))

library(dlookr)

diagnose(dat)

# these two plots need dlookr's own text rendering
if (preview) { plot_outlier(dat); plot_na_pareto(dat) }

# dlookr turns showtext on at 96 dpi, which shrinks text after this point
showtext::showtext_auto(FALSE)

outl <- diagnose_outlier(dat[num])
outl <- outl[, c("variables", "outliers_cnt", "outliers_ratio",
                 "outliers_mean", "without_mean")]
outl$outliers_ratio <- round(outl$outliers_ratio / 100, 3)   # dlookr gives percent

outl[order(-outl$outliers_ratio), ]
colSums(is.na(dat))

write.csv(outl, file.path(path, "tables/iqr_outliers.csv"), row.names = FALSE)

# Figure 2: IQR shares
ord <- outl[outl$outliers_cnt > 0, ]
ord <- ord[order(ord$outliers_ratio), ]

open_fig("figures/fig_eda_outliers.png", 8, 3.6)
par(mar = c(4.2, 8.2, 3.6, 1.2), mgp = c(2.5, 0.7, 0), las = 1)
bp <- barplot(100 * ord$outliers_ratio, horiz = TRUE, col = "#9DB4CE", border = NA,
              names.arg = ord$variables, cex.names = 0.82, xaxt = "n",
              xlim = c(0, 100 * max(ord$outliers_ratio) * 1.28),
              main = "Records outside 1.5 IQR, by variable",
              xlab = "Percent of records")
axis(1, at = seq(0, 20, 5))
text(100 * ord$outliers_ratio, bp, labels = ord$outliers_cnt, pos = 4, cex = 0.75,
     col = "grey25")
mtext("count at each bar end; bpm, danceability, valence, acousticness: none",
      side = 3, line = 0.1, cex = 0.7, col = "grey30")
close_fig()


# ---------------------------------------------------------------------------
# 1(a)(iv) step 4: pairs.panels() -> Figures 3-7, Tables 5-6
# ---------------------------------------------------------------------------

panel <- c("log10_streams", "qq_playlists", "qq_charts", "apple_playlists",
           "release_year", "artist_count", "danceability", "energy",
           "acousticness", "speechiness")

open_fig("figures/fig_eda_pairs.png", 9.5, 9.5)          # Figure 3
pairs.panels(dat[panel],
             method   = "pearson",
             hist.col = "#2C7FB8",
             density  = TRUE,
             ellipses = TRUE,
             lm       = TRUE,
             stars    = TRUE,
             cex.cor  = 0.9,
             main     = "QQ Music -- pairwise relationships")
close_fig()

# Figure 4: playlist exposure
open_fig("figures/fig2_platform_exposure.png", 9, 3.8)
par(mfrow = c(1, 2), mar = c(4.4, 4.4, 3.2, 1), mgp = c(2.5, 0.7, 0), las = 1, pch = 16,
    col = rgb(0, 0, 0, 0.22), cex = 0.45)

plot(dat$qq_playlists, dat$log10_streams, log = "x", xaxt = "n",
     main = "(a) QQ Music playlist count", xlab = "Playlists containing the song",
     ylab = expression(log[10]("streams")))
axis(1, at = c(100, 1000, 10000), labels = c("100", "1,000", "10,000"))
lines(lowess(dat$qq_playlists, dat$log10_streams, f = 0.6), col = "#C0504D", lwd = 2)
text(min(dat$qq_playlists), max(dat$log10_streams),
     sprintf("Pearson r = %.2f\nSpearman rho = %.2f",
             cor(dat$qq_playlists, dat$log10_streams),
             cor(dat$qq_playlists, dat$log10_streams, method = "spearman")),
     adj = c(0, 1), cex = 0.8, col = "grey15")

plot(dat$apple_playlists + 1, dat$log10_streams, log = "x", xaxt = "n",
     main = "(b) Apple Music playlist count", xlab = "Playlists containing the song (+1)",
     ylab = expression(log[10]("streams")))
axis(1, at = c(1, 11, 101), labels = c("0", "10", "100"))
lines(lowess(dat$apple_playlists + 1, dat$log10_streams, f = 0.6),
      col = "#C0504D", lwd = 2)
text(max(dat$apple_playlists + 1), min(dat$log10_streams),
     sprintf("Pearson r = %.2f\nSpearman rho = %.2f",
             cor(dat$apple_playlists, dat$log10_streams),
             cor(dat$apple_playlists, dat$log10_streams, method = "spearman")),
     adj = c(1, 0), cex = 0.8, col = "grey15")
close_fig()

# Figure 5: audio features (one record at 3.4, hence ylim 6-9.7)
feat <- c(danceability = "Danceability (%)", energy = "Energy (%)",
          valence = "Valence (%)", acousticness = "Acousticness (%)",
          speechiness = "Speechiness (%)", instrumentalness = "Instrumentalness (%)")
open_fig("figures/fig4_audio_features.png", 9.5, 5.8)
par(mfrow = c(2, 3), mar = c(3.0, 3.9, 2.6, 0.7), oma = c(0, 0, 2.4, 0),
    mgp = c(2.0, 0.6, 0), las = 1, pch = 16, col = rgb(0, 0, 0, 0.22),
    cex = 0.42, cex.axis = 0.85)
left_col <- c("danceability", "acousticness")
for (v in names(feat)) {
  plot(dat[[v]], dat$log10_streams, main = feat[v], xlab = "",
       ylab = if (v %in% left_col) expression(log[10]("streams")) else "",
       ylim = c(6, 9.7))
  lines(lowess(dat[[v]], dat$log10_streams, f = 0.8), col = "#C0504D", lwd = 2)
  text(max(dat[[v]]), 9.66, sprintf("r = %.2f", cor(dat[[v]], dat$log10_streams)),
       adj = c(1, 1), cex = 0.85, col = "grey15")
}
mtext("Audio features against log10(streams): the lowess trend is flat in every panel",
      side = 3, outer = TRUE, line = 0.5, cex = 0.95, font = 2, col = "black")
close_fig()

# Figure 6: decade and artist count
open_fig("figures/fig5_release_and_collaboration.png", 9, 3.8)
par(mfrow = c(1, 2), mar = c(4.6, 4.4, 2.8, 1), mgp = c(2.5, 0.7, 0), cex.axis = 0.85)

dec_dat <- subset(dat, decade != "1940s")
dec_dat$decade <- droplevels(dec_dat$decade)
boxplot(log10_streams ~ decade, data = dec_dat, col = "#9DB4CE", border = "grey30",
        main = "(a) By release decade", xlab = "",
        ylab = expression(log[10]("streams")), las = 1, outline = FALSE, xaxt = "n")
axis(1, at = seq_along(levels(dec_dat$decade)), labels = levels(dec_dat$decade),
     las = 2, cex.axis = 0.8, tick = FALSE)

boxplot(log10_streams ~ artist_group, data = dat, col = "#C4D6A8", border = "grey30",
        main = "(b) By number of artists", xlab = "Number of contributing artists",
        ylab = expression(log[10]("streams")), las = 1, outline = FALSE)
close_fig()

# Figure 7: chart presence
open_fig("figures/fig6_chart_presence.png", 9, 3.8)
par(mfrow = c(1, 2), mar = c(3.6, 4.4, 2.8, 1), mgp = c(2.5, 0.7, 0), cex.axis = 0.85)

boxplot(log10_streams ~ charted_qq, data = dat, col = c("grey78", "#4F81BD"),
        border = "grey30", main = "(a) QQ Music chart presence", xlab = "",
        ylab = expression(log[10]("streams")),
        names = c("Not on any chart", "On >=1 chart"), las = 1, outline = FALSE)

boxplot(log10_streams ~ charted_apple, data = dat, col = c("grey78", "#9BBB59"),
        border = "grey30", main = "(b) Apple Music chart presence", xlab = "",
        ylab = expression(log[10]("streams")),
        names = c("Not on any chart", "On >=1 chart"), las = 1, outline = FALSE)
close_fig()

# Table 5: each predictor against log10(streams)
cor_vars <- c("qq_playlists", "qq_charts", "apple_playlists", "apple_charts",
              "release_year", "artist_count", "bpm", "danceability", "valence",
              "energy", "acousticness", "instrumentalness", "liveness", "speechiness")

r   <- sapply(dat[cor_vars], cor, y = dat$log10_streams, use = "complete.obs")
rho <- sapply(dat[cor_vars], cor, y = dat$log10_streams, use = "complete.obs",
              method = "spearman")
cor_y <- round(cbind(pearson = r, spearman = rho)[order(-abs(r)), ], 3)
cor_y
write.csv(cor_y, file.path(path, "tables/association_with_response.csv"))

# Table 6: predictor pairs above |r| = 0.5 (lab screen; VIF cutoff is 5)
M   <- cor(dat[cor_vars], use = "pairwise.complete.obs")
hit <- which(upper.tri(M) & abs(M) >= 0.5, arr.ind = TRUE)
coll <- data.frame(var1 = rownames(M)[hit[, 1]], var2 = colnames(M)[hit[, 2]],
                   r = round(M[hit], 3))
coll <- coll[order(-abs(coll$r)), ]
coll                          # the order Table 6 uses
write.csv(coll, file.path(path, "tables/collinear_pairs.csv"), row.names = FALSE)

# median streams by group, in millions
round(tapply(dat$streams, dat$charted_qq, median) / 1e6, 1)
round(tapply(dat$streams, dat$charted_apple, median) / 1e6, 1)
round(tapply(dat$streams, dat$collab, median) / 1e6, 1)
round(tapply(dat$log10_streams, dat$decade, median), 3)
table(dat$charted_qq); table(dat$charted_apple); table(dat$collab)


# ---------------------------------------------------------------------------
# 1(a)(v) numbers quoted in the findings
# ---------------------------------------------------------------------------

# response: range, quartiles, skew, tails
range(dat$streams)
round(quantile(dat$log10_streams, c(0.01, 0.25, 0.5, 0.75)), 3)
round(c(skew_raw = skew(dat$streams), skew_log = skew(dat$log10_streams)), 3)
sum(dat$log10_streams < 7)                    # the two records below 10^7

# exposure: linear or only monotone
round(c(pearson = cor(dat$qq_playlists, dat$log10_streams),
        spearman = cor(dat$qq_playlists, dat$log10_streams, method = "spearman")), 3)

# audio block, by absolute r
audio <- c("danceability", "energy", "valence", "acousticness", "speechiness",
           "instrumentalness", "liveness")
round(sort(abs(r[audio]), decreasing = TRUE), 3)

# release timing
round(tapply(dat$log10_streams, dat$decade, median), 3)
round(median(dat$streams[dat$release_year >= 2020]) / 1e6, 1)
round(median(dat$streams[dat$release_year < 2020]) / 1e6, 1)

# chart-group ratio on each platform
q <- tapply(dat$streams, dat$charted_qq, median) / 1e6
a <- tapply(dat$streams, dat$charted_apple, median) / 1e6
round(c(qq_ratio = q[2] / q[1], apple_ratio = a[2] / a[1],
        apple_on_chart = mean(dat$charted_apple)), 3)


# ===========================================================================
# 1(b) research question
# ===========================================================================
# the question is a sentence; what follows is the check behind each choice

# qq_charts is 43.5% zeros, too skewed to enter as a count
round(c(zeros = mean(dat$qq_charts == 0), mean = mean(dat$qq_charts),
        max = max(dat$qq_charts)), 3)

# the indicator beats the count
round(c(indicator = cor(dat$charted_qq, dat$log10_streams),
        count = cor(dat$qq_charts, dat$log10_streams)), 3)

# identifiers and the incomplete column
length(unique(dat$artist_name))
round(c(missing_key = sum(is.na(dat$key)), share = mean(is.na(dat$key))), 3)

# Apple columns out: they repeat the QQ mechanism
round(M[c("qq_playlists", "qq_charts"), c("apple_playlists", "apple_charts")], 3)


# ===========================================================================
# 2. variable roles
# ===========================================================================
# Table 7 is a judgement table; this gives the class, levels and range
# behind each row

sapply(dat, class)
sapply(dat[sapply(dat, is.factor)], nlevels)
length(unique(na.omit(dat$key)))              # 11 observed keys
range(dat$artist_count)                       # 1-8, a discrete count
round(sapply(dat[pct], range))                # the seven scores, bounded 0-100
range(dat$bpm)
range(dat$release_year)


# ===========================================================================
# appendix: the clean file item 3 reads
# ===========================================================================

out <- dat[, c("track_name", "artist_name", "artist_count", "release_year",
               "release_month", "release_day", "qq_playlists", "qq_charts",
               "apple_playlists", "apple_charts", "streams", "log10_streams",
               "charted_qq", "charted_apple", "collab", "bpm", "key", "mode",
               "danceability", "valence", "energy", "acousticness",
               "instrumentalness", "liveness", "speechiness")]
write.csv(out, file.path(path, "data/QQ_Music_clean.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
dim(out)                # 842 x 25
