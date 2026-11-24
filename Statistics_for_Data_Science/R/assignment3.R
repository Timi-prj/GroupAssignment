# CDS533 Assignment 3 — integrated reproducible analysis
# Run from the project root: Rscript --vanilla R/assignment3.R
# Outputs are isolated in report/assignment3_outputs/ to preserve member plots.

options(stringsAsFactors = FALSE, scipen = 0)

# ----- Project paths and output helpers -----
project_root <- getwd()
if (!file.exists(file.path(project_root, "data", "QQ_Music.csv"))) {
  stop("Run this script from the project root (data/QQ_Music.csv not found).")
}
out_dir <- file.path(project_root, "report", "assignment3_outputs")
fig_dir <- file.path(out_dir, "figures")
tab_dir <- file.path(out_dir, "tables")
for (d in c(out_dir, fig_dir, tab_dir)) dir.create(d, recursive = TRUE, showWarnings = FALSE)
log_file <- file.path(out_dir, "analysis_log.txt")
sink(log_file, split = TRUE)
on.exit(sink(), add = TRUE)

section <- function(x) cat("\n\n", paste(rep("=", 76), collapse = ""), "\n", x,
                           "\n", paste(rep("=", 76), collapse = ""), "\n", sep = "")
write_table <- function(x, name, row.names = FALSE) {
  write.csv(x, file.path(tab_dir, name), row.names = row.names, fileEncoding = "UTF-8")
}

# ----- Q1: advertisement response -----
section("Q1 — Choosing an advertisement")
red <- c(80,80,78,81,72,85,96,84,71,75,98)
white <- c(75,55,98,92,86,78,87,79,88,87,85,94,99)
blue <- c(72,76,70,77,68,82,85,81,65,69)
ads <- data.frame(score = c(red, white, blue),
                  advertisement = factor(rep(c("Red","White","Blue"),
                    times = c(length(red),length(white),length(blue))),
                    levels = c("Red","White","Blue")))
cat("Design: ordered response score in three independent advertisement groups; no missing or excluded observations.\n")
desc1 <- do.call(rbind, lapply(split(ads$score, ads$advertisement), function(x)
  c(n=length(x), mean=mean(x), sd=sd(x), median=median(x), Q1=quantile(x,.25),
    Q3=quantile(x,.75), min=min(x), max=max(x))))
print(round(desc1, 3)); write_table(data.frame(advertisement=rownames(desc1), desc1), "q1_descriptives.csv")
q1 <- kruskal.test(score ~ advertisement, data=ads)
print(q1)
cat("H0: the score distributions/rank locations are the same across the three ads; H1: at least one differs.\n")
cat("At alpha=.05: ", if (q1$p.value < .05) "reject H0" else "fail to reject H0",
    "; this omnibus result does not identify which individual ads differ. Recommend using the strongest descriptive performance cautiously, not as proof of pairwise superiority.\n", sep="")
if (requireNamespace("ggplot2", quietly=TRUE)) {
  p <- ggplot2::ggplot(ads, ggplot2::aes(advertisement, score, fill=advertisement)) +
    ggplot2::geom_boxplot(alpha=.45, outlier.shape=NA) +
    ggplot2::geom_jitter(width=.08, alpha=.75) +
    ggplot2::labs(title="Ordered reaction score by advertisement", x="Advertisement", y="Score") +
    ggplot2::theme_minimal()
  ggplot2::ggsave(file.path(fig_dir,"q1_advertisements.png"), p, width=7, height=4.5, dpi=300)
} else cat("Plot skipped: package ggplot2 is not available.\n")

# ----- Q2: one-way ANOVA -----
section("Q2 — Chick weight by feed")
data("chickwts", package="datasets")
feed_desc <- do.call(rbind, lapply(split(chickwts$weight, chickwts$feed), function(x)
  c(n=length(x), mean=mean(x), sd=sd(x), median=median(x))))
print(round(feed_desc,3)); write_table(data.frame(feed=rownames(feed_desc),feed_desc),"q2_feed_descriptives.csv")
cat("Design: independent experimental units per the study setup; response weight is continuous. Assumptions: independent errors, approximately normal within-group residuals, and common variances; inspect diagnostics below.\n")
fit2 <- aov(weight ~ feed, data=chickwts)
print(anova(fit2))
cat("H0: all six population mean weights are equal; H1: at least one differs.\n")
cat("ANOVA decision at alpha=.05: ", if (anova(fit2)[1,"Pr(>F)"] < .05) "reject H0" else "fail to reject H0",
    ". Significance establishes only some mean difference, not that every pair differs or that the highest sample mean is significantly best; pairwise follow-up would be needed.\n",sep="")
png(file.path(fig_dir,"q2_feed_boxplot.png"),width=2100,height=1350,res=300)
boxplot(weight ~ feed,data=chickwts,col="lightsteelblue",main="Chick weight by feed type",xlab="Feed type",ylab="Weight (g)"); dev.off()
png(file.path(fig_dir,"q2_anova_diagnostics.png"),width=2400,height=1200,res=300)
par(mfrow=c(1,2)); plot(fit2,which=1); plot(fit2,which=2); dev.off()

# ----- Q3: seven studies -----
section("Q3 — Seven studies")
if (!requireNamespace("ISLR2", quietly=TRUE)) stop("Q3 requires ISLR2 (installation is intentionally not attempted).")
if (!requireNamespace("car", quietly=TRUE)) stop("Q3 Study G requires car (installation is intentionally not attempted).")
# A: log salary by league, Welch two-sample t test
hitters <- as.data.frame(ISLR2::Hitters)
h <- subset(hitters, !is.na(Salary) & Salary > 0 & !is.na(League))
h$log_salary <- log(h$Salary)
section("Q3 A — League difference in mean log salary")
print(aggregate(log_salary~League,h,function(x)c(n=length(x),mean=mean(x),sd=sd(x))))
qa <- t.test(log_salary~League,data=h,var.equal=FALSE); print(qa)
cat("H0: population mean log salaries are equal; H1: they differ.\n")
# B: paired t test, log cost difference
college <- as.data.frame(ISLR2::College)
cost <- subset(college, is.finite(Outstate) & is.finite(Room.Board) & Outstate>0 & Room.Board>0)
diff_log <- log(cost$Outstate)-log(cost$Room.Board)
section("Q3 B — Paired mean log-cost difference")
cat("Complete positive-cost college pairs:",length(diff_log),"; mean difference:",mean(diff_log),"; SD:",sd(diff_log),"\n")
qb <- t.test(log(cost$Outstate),log(cost$Room.Board),paired=TRUE); print(qb)
cat("H0: mean paired log difference is zero; H1: it is nonzero.\n")
# C: sign test on unequal raw costs, no normality or symmetry assumption
unequal <- cost$Outstate != cost$Room.Board
n_c <- sum(unequal); greater_c <- sum(cost$Outstate[unequal]>cost$Room.Board[unequal])
section("Q3 C — Sign test among unequal costs")
cat("Unequal pairs:",n_c,"; tuition greater:",greater_c,"\n")
qc <- binom.test(greater_c,n_c,p=.5); print(qc)
cat("H0: among unequal pairs, probability tuition is greater is 0.5. This tests direction/probability, unlike B's mean log magnitude; results can differ.\n")
# D: rank-sum comparison plus direct two-sample distribution test
cars <- as.data.frame(ISLR2::Auto)
cars2 <- subset(cars, origin %in% c(1,3) & is.finite(mpg))
cars2$origin_group <- factor(cars2$origin,levels=c(1,3),labels=c("American","Japanese"))
section("Q3 D — MPG distributions: American vs Japanese cars")
print(aggregate(mpg~origin_group,cars2,function(x)c(n=length(x),mean=mean(x),median=median(x),sd=sd(x))))
qd_rank <- wilcox.test(mpg~origin_group,data=cars2,exact=FALSE,correct=FALSE); print(qd_rank)
qd_dist <- ks.test(cars2$mpg[cars2$origin_group=="American"],cars2$mpg[cars2$origin_group=="Japanese"]); print(qd_dist)
cat("H0: the two MPG distributions are equal; H1: they differ. Wilcoxon rank-sum detects rank/stochastic-location differences and is not a universal test of distribution shape; the two-sample KS test directly compares empirical distributions. MPG is rounded/discrete, so KS's continuous-distribution calibration is approximate with ties.\n")
# E: goodness-of-fit to specified equal probabilities
section("Q3 E — Public/private frequency vs specified 0.5 model")
counts_e <- table(college$Private); print(counts_e)
qe <- binom.test(unname(counts_e["Yes"]),sum(counts_e),p=.5); print(qe)
cat("H0: public and private have probability 0.5 each (a tested model, not assumed fact); H1: probabilities differ.\n")
# F: association with the pre-specified 50% Top10 threshold
section("Q3 F — Private status and high Top10 share association")
valid_f <- !is.na(college$Private) & !is.na(college$Top10perc)
top_group <- factor(ifelse(college$Top10perc[valid_f]>=50,"High","Lower"),levels=c("Lower","High"))
tab_f <- table(college$Private[valid_f],top_group); print(tab_f); print(round(prop.table(tab_f,1),3))
qf <- chisq.test(tab_f,correct=FALSE); print(qf)
cat("H0: private status and high Top10 share are independent; H1: associated. This is an association question, unlike E's one-variable frequency model, and cannot establish a causal effect.\n")
# G: median-centred Levene test, nonnormality robust multi-group variance comparison
cars3 <- subset(cars, origin %in% 1:3 & is.finite(mpg))
cars3$origin_group <- factor(cars3$origin,levels=1:3,labels=c("American","European","Japanese"))
section("Q3 G — MPG variability across three origins")
print(aggregate(mpg~origin_group,cars3,function(x)c(n=length(x),variance=var(x),sd=sd(x))))
qg <- car::leveneTest(mpg~origin_group,data=cars3,center=median); print(qg)
cat("H0: population variances are equal across origins; H1: at least one differs. Levene test is centred on group medians (Brown–Forsythe form), avoiding a normality requirement.\n")
q3_results <- data.frame(study=c("A Welch t","B paired t","C sign/binomial","D Wilcoxon rank sum","D KS distribution","E binomial GOF","F chi-square association","G median Levene"),
 statistic=c(unname(qa$statistic),unname(qb$statistic),unname(qc$statistic),unname(qd_rank$statistic),unname(qd_dist$statistic),unname(qe$statistic),unname(qf$statistic),qg[1,"F value"]),
 p_value=c(qa$p.value,qb$p.value,qc$p.value,qd_rank$p.value,qd_dist$p.value,qe$p.value,qf$p.value,qg[1,"Pr(>F)"]))
write_table(q3_results,"q3_test_summary.csv")

# ----- Q4: self-contained raw data cleaning, EDA and GLM -----
section("Q4 — QQ Music cleaning, EDA and Gaussian model")
raw <- read.csv(file.path(project_root,"data","QQ_Music.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE,check.names=FALSE)
cat("Raw rows:",nrow(raw),"columns:",ncol(raw),"\n")
old <- c("artist(s)_name","released_year","released_month","released_day","in_QQ_playlists","in_QQ_charts","in_apple_playlists","in_apple_charts","danceability_%","valence_%","energy_%","acousticness_%","instrumentalness_%","liveness_%","speechiness_%")
new <- c("artist_name","release_year","release_month","release_day","qq_playlists","qq_charts","apple_playlists","apple_charts","danceability","valence","energy","acousticness","instrumentalness","liveness","speechiness")
names(raw)[match(old,names(raw))] <- new
raw$streams <- suppressWarnings(as.numeric(raw$streams))
n_raw <- nrow(raw); bad_stream_rows <- sum(is.na(raw$streams))
key <- tolower(raw$track_name); artist <- tolower(raw$artist_name)
dup <- duplicated(paste(key,artist,raw$streams,sep="\r")) & !is.na(raw$streams)
n_dup <- sum(dup); raw <- raw[!dup,]
n_after_dup <- nrow(raw)
raw <- raw[!is.na(raw$streams)&raw$streams>0,]
raw$key[!is.na(raw$key)&trimws(raw$key)==""] <- NA
cat("Cleaning: nonnumeric streams set missing:",bad_stream_rows,"(not imputed); duplicate title+artist+streams removed:",n_dup,"; missing/nonpositive response rows excluded:",n_after_dup-nrow(raw),"; final n:",nrow(raw),". Missing key retained and not imputed.\n")
clean <- raw
clean$log10_streams <- log10(clean$streams)
clean$charted_qq <- as.integer(clean$qq_charts>0)
clean$charted_apple <- as.integer(clean$apple_charts>0)
clean$collab <- as.integer(clean$artist_count>1)
clean$decade <- factor(paste0(floor(clean$release_year/10)*10,"s"))
clean$artist_group <- factor(pmin(clean$artist_count,4),levels=1:4,labels=c("1","2","3","4+"))
clean$mode <- factor(clean$mode,levels=c("Major","Minor"))
write.csv(clean,file.path(out_dir,"qq_music_clean.csv"),row.names=FALSE,fileEncoding="UTF-8")
clean_counts <- data.frame(step=c("raw","nonnumeric response marked missing","duplicate removed","missing/nonpositive response excluded","final"),rows=c(n_raw,bad_stream_rows,n_dup,n_after_dup-nrow(clean),nrow(clean)))
write_table(clean_counts,"q4_cleaning_audit.csv")

# Auditable summaries
num_vars <- names(clean)[vapply(clean,is.numeric,logical(1))]
summ <- do.call(rbind,lapply(num_vars,function(v){x<-clean[[v]];data.frame(variable=v,n=sum(!is.na(x)),missing=sum(is.na(x)),mean=mean(x,na.rm=TRUE),sd=sd(x,na.rm=TRUE),median=median(x,na.rm=TRUE),min=min(x,na.rm=TRUE),max=max(x,na.rm=TRUE))}))
write_table(summ,"q4_numeric_summary.csv")
cat("Numeric summary saved to tables/q4_numeric_summary.csv; key missing:",sum(is.na(clean$key)),"\n")
# Five informative EDA panels in one figure (distribution, exposure, chart groups, release and audio)
png(file.path(fig_dir,"q4_eda_overview.png"),width=3000,height=2100,res=300)
par(mfrow=c(2,3),mar=c(4,4,2.6,1))
hist(clean$log10_streams,breaks=30,col="lightsteelblue",main="Log10 streams",xlab="log10(streams)")
plot(log10(clean$qq_playlists),clean$log10_streams,pch=16,col=rgb(0,0,0,.2),xlab="log10(QQ playlists)",ylab="log10(streams)",main="QQ playlist exposure"); lines(lowess(log10(clean$qq_playlists),clean$log10_streams),col="red",lwd=2)
boxplot(log10_streams~charted_qq,data=clean,names=c("No chart","On chart"),main="QQ chart presence",ylab="log10(streams)")
boxplot(log10_streams~decade,data=clean,las=2,cex.axis=.7,main="Release decade",ylab="log10(streams)")
plot(clean$danceability,clean$log10_streams,pch=16,col=rgb(0,0,0,.2),xlab="Danceability (%)",ylab="log10(streams)",main="Audio feature"); lines(lowess(clean$danceability,clean$log10_streams),col="red",lwd=2)
boxplot(log10_streams~artist_group,data=clean,main="Artist count",xlab="Artists",ylab="log10(streams)")
dev.off()

# Candidate-predictor correlation screen excluding response
corr_vars <- c("qq_playlists","apple_playlists","qq_charts","apple_charts","danceability","energy","valence","acousticness","speechiness","instrumentalness","bpm","release_year","artist_count")
cor_mat <- cor(clean[corr_vars],use="pairwise.complete.obs")
cor_pairs <- which(upper.tri(cor_mat)&abs(cor_mat)>=.5,arr.ind=TRUE)
cor_tab <- data.frame(var1=rownames(cor_mat)[cor_pairs[,1]],var2=colnames(cor_mat)[cor_pairs[,2]],r=cor_mat[cor_pairs])
write_table(cor_tab,"q4_predictor_correlations_ge_0.5.csv")
clean$log_playlists <- log10(clean$qq_playlists)
clean$charted_qq_f <- factor(clean$charted_qq,levels=c(0,1),labels=c("No","Yes"))
# Candidate models; same rows/response for fair comparisons
m1 <- lm(log10_streams~log_playlists+charted_qq_f,data=clean)
m2 <- lm(log10_streams~log_playlists+charted_qq_f+release_year+artist_count,data=clean)
m3 <- lm(log10_streams~log_playlists+charted_qq_f+release_year+artist_count+danceability+energy+valence+acousticness+speechiness+instrumentalness+bpm+mode,data=clean)
model_cmp <- data.frame(model=c("M1 exposure","M2 + release year and artist count","M3 + audio features"),n=nrow(clean),R2=sapply(list(m1,m2,m3),function(m)summary(m)$r.squared),adjusted_R2=sapply(list(m1,m2,m3),function(m)summary(m)$adj.r.squared),AIC=sapply(list(m1,m2,m3),AIC),BIC=sapply(list(m1,m2,m3),BIC),RMSE=sapply(list(m1,m2,m3),function(m)summary(m)$sigma))
print(model_cmp); write_table(model_cmp,"q4_model_comparison.csv")
cat("M2 adds timing and artist count; M3 adds audio features. Compare fit criteria and nested F tests; selection is associational, not causal.\n")
print(anova(m1,m2)); print(anova(m2,m3))
# Report full model's VIF (dummy-coded design matrix)
X <- model.matrix(m3)[,-1,drop=FALSE]
vif <- sapply(seq_len(ncol(X)),function(j){others<-X[,-j,drop=FALSE];if(ncol(others)==0)1 else 1/(1-summary(lm(X[,j]~others))$r.squared)})
vif_tab <- data.frame(term=colnames(X),VIF=as.numeric(vif)); write_table(vif_tab,"q4_vif.csv")
final <- m2
cf <- summary(final)$coefficients; ci <- confint(final)
coef_tab <- data.frame(term=rownames(cf),estimate=cf[,1],std_error=cf[,2],statistic=cf[,3],p_value=cf[,4],ci_low=ci[,1],ci_high=ci[,2])
print(coef_tab); write_table(coef_tab,"q4_final_coefficients.csv")
cat("Coefficient interpretation: playlist effect is on log10(streams) per tenfold increase in QQ playlists (because predictor is log10); chart coefficient compares charted vs not charted conditional on other model terms. Report 95% CIs as conditional mean-scale intervals.\n")
# Explicitly correct logit odds-ratio calculation from audit: exp(beta * log(2)) for a doubling
clean$hit <- as.integer(clean$streams>=quantile(clean$streams,.75))
logit_fit <- glm(hit~log_playlists+charted_qq_f+release_year+artist_count,family=binomial(link="logit"),data=clean)
logit_beta <- coef(logit_fit)["log_playlists"]
or_double <- exp(logit_beta*log10(2))
logit_tab <- data.frame(term=names(coef(logit_fit)),estimate=coef(logit_fit),OR_per_unit=exp(coef(logit_fit)),OR_playlist_doubling=NA_real_)
logit_tab$OR_playlist_doubling[logit_tab$term=="log_playlists"] <- or_double
print(logit_tab); cat(sprintf("Correct logit odds ratio for doubling QQ playlists: exp(beta * log10(2)) = %.3f (NOT 10^(beta*log10(2))).\n",or_double))
write_table(logit_tab,"q4_logit_odds_ratios.csv")

png(file.path(fig_dir,"q4_model_diagnostics.png"),width=2400,height=1800,res=300)
par(mfrow=c(2,2)); plot(final,which=1:4); dev.off()
# Numerical checks accompanying the diagnostic plots.
print(summary(final)$fstatistic)
aux <- lm(residuals(final)^2 ~ log_playlists + charted_qq_f + release_year + artist_count, data=clean)
lm_stat <- nobs(aux) * summary(aux)$r.squared
print(c(BP=lm_stat, df=4, p=pchisq(lm_stat,4,lower.tail=FALSE)))
print(shapiro.test(residuals(final)))
print(anova(final, update(final, . ~ . + I(log_playlists^2))))
print(anova(final, update(final, . ~ . + log_playlists:charted_qq_f)))
print(c(max_Cook=max(cooks.distance(final)), studentized_over_3=sum(abs(rstudent(final))>3)))
# Range-valid scenario: 2022, one artist, 5,000 playlists, charted.
newdata <- data.frame(log_playlists=log10(5000),charted_qq_f=factor("Yes",levels=c("No","Yes")),release_year=2022,artist_count=1)
pred <- predict(final,newdata,interval="prediction",level=.95)
mean_ci <- predict(final,newdata,interval="confidence",level=.95)
print(mean_ci); print(10^mean_ci)
cat("Reference profile prediction on log10 outcome (95% prediction interval):\n"); print(pred)
pred_tab <- data.frame(log10_fit=pred[1],pi_low_log10=pred[2],pi_high_log10=pred[3],geometric_fit_streams=10^pred[1],pi_low_backtransformed=10^pred[2],pi_high_backtransformed=10^pred[3])
write_table(pred_tab,"q4_reference_prediction.csv")
cat("Back-transformed prediction interval describes a single observation under the lognormal working model; it is not an interval for arithmetic mean streams.\n")

section("Completion and artifact index")
cat("Audit log: ",log_file,"\n",sep="")
cat("Tables: ",tab_dir,"\n",sep="")
cat("Figures: ",fig_dir,"\n",sep="")
sink()
