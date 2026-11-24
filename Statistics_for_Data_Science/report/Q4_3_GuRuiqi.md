# Question 4, item 3 — a Gaussian GLM for streaming performance

**Ruiqi Gu (顾瑞祺)** — Role 5, Q4 modelling lead

The report answers the question in the order the question asks it: Section 0 sets out the input file and
the question, then Item 3(a) predictor reasoning, Item 3(b) correlation and multicollinearity, Item 3(c)
model specification and selection, Item 3(d) diagnostics and prediction, and Item 3(e) the conclusion
with the justification for the model. `Q4_GLM.R` is laid out in the same order, so the script can be read
beside the report, and every number here comes from it and can be reproduced by running it.

| Marked requirement | Where it is answered |
|:---------------------------------|:----------------------------------------------------------|
| (a) Predictor reasoning [6] | Item 3(a), Table 1, one row per candidate column |
| (b) Correlation and multicollinearity [4] | Item 3(b), correlation matrix and Table 2 (VIF) |
| (c) Model specification and selection [7], with two coefficients and their 95% CIs | Item 3(c)(i) response scale, family and link; 3(c)(ii) the nested comparison; 3(c)(iii) final formula, coefficients and CIs |
| (d) Diagnostics and prediction [6] | Item 3(d)(i) plots and statistics; 3(d)(ii) the prediction and its interval |
| (e) Conclusion and model justification [4], 200–300 words | Item 3(e)(i) and 3(e)(ii) the justification; 3(e)(iii) the conclusion, 290 words |
| The input file and the question, which the brief does not mark | Section 0 |

---

## 0. Setup: the input file and the question, before item 3

The analysis file is `data/QQ_Music_clean.csv` (n = 842, 25 columns), written by `Q4_EDA.R` and
included in this package. It removes two records from the raw 844: one duplicate on title, artist and
stream total, and one whose `streams` value is field-shifted and therefore has no usable response;
nothing was imputed. The response used here is `log10_streams`, a column already in that file.

The question being answered is the one set out in Item 1(b):

> How strongly is a song's streaming performance on QQ Music, measured as log10 streams, associated
> with the platform exposure it receives — how many QQ Music playlists it appears in and whether it
> appears on the QQ Music charts — compared with its audio characteristics, once release timing and
> the number of contributing artists are held constant?

The lab answer keys run every analysis through the same six steps — look at Y, plot, fit in R, read
3S, check, report. This part keeps that order: step 1 is Item 1(b) together with the response
discussion that opens Item 3(c), step 2 is the EDA figures of Item 1(a) plus the fitted curve in
Figure 2 here, step 3 is Item 3(c)(ii), step 4 is the 3S block in Item 3(c)(iii), step 5 is Item 3(d)(i)
and step 6 is Item 3(e).

---

## Item 3(a) — Which predictors enter, and why [6 marks]

Two variables need a word before the decisions, because their names mislead. `in_QQ_charts` and
`in_apple_charts` are described in the data dictionary as indicators, but they hold counts (0–147 and
0–275), so they are treated as counts. `qq_playlists` is a count spanning 31 to 52,898 and is entered on
the log scale.

**Table 1. Predictor decisions.**

| Variable | Decision | Reason |
|:--------------------------|:------------|:------------------------------------------------------|
| `log10(qq_playlists)` | in | The exposure measure the team controls, and the strongest correlate of the response (ρ = 0.829). The log form is empirical: the raw count gives AIC = 807.8 and adjusted R² = 0.411, against AIC = 416.4 and 0.630 in log form |
| `charted_qq` | in | The second exposure channel, acting at a different margin: a song can sit in thousands of playlists without charting. The count form was rejected on evidence — replacing the indicator with `log1p(qq_charts)` raises AIC from 405.4 to 432.3 and lowers adjusted R² from 0.6357 to 0.6238 |
| `release_year` | in | Streams are a cumulative stock, so a 1975 record has had five decades to accumulate. Omitting it would confound every other coefficient |
| `artist_count` | in | A plausible distribution advantage; blocked with `release_year` so that the joint contribution of release context can be tested |
| `danceability`, `valence`, `energy`, `acousticness`, `speechiness`, `instrumentalness` | in | The six 0–100 audio scores, the block the question is built around. They enter together and are tested jointly, since dropping any of them in advance would beg the question |
| `bpm`, `mode` | in | The two remaining audio descriptors, kept so that "audio characteristics" means the whole recorded sound rather than only the scores. `mode` is a two-level factor, `bpm` a count |
| `liveness` | out | The seventh score and the only audio variable left out: r = −0.050 (ρ = −0.063) with the response, the weakest of the nine, and Item 2 had already recorded it as considered but not entered. Leaving it out keeps the joint audio test at 8 degrees of freedom instead of 9 |
| `track_name`, `artist_name` | out | Identifiers. Artist identity would need hundreds of fixed effects or a random effect, which is outside this model |
| `release_month`, `release_day` | out | No mechanism links a calendar day to cumulative streams; any effect would proxy promotion scheduling |
| `key` | out | Missing for 10.6% of records, and its 11 observed levels would cost 10 degrees of freedom for a weak hypothesis |
| `apple_playlists`, `apple_charts` | out | Collinear with their QQ counterparts (0.712 and 0.555) and not actionable for the QQ Music team |
| `charted_apple`, `collab` | out | Derived binaries of variables already decided on. `charted_apple` is `apple_charts` > 0, an Apple-side channel only weakly tied to `charted_qq` (r = 0.158) and outside the research question; `collab` is `artist_count` > 1 and correlates 0.815 with the count it is built from, so it adds no information |
| `decade`, `artist_group` | out | Groupings built for the two descriptive panels of item 1(a), not variables in their own right: they recode `release_year` and `artist_count`, both of which enter in their measured form |
| `streams` untransformed | out | Two records sit over three orders of magnitude below the median and the raw-scale residuals are heteroscedastic |

---

## Item 3(b) — Correlation and multicollinearity [4 marks]

Thirteen predictors are numeric, giving a 13 × 13 matrix and 78 pairs, with the response excluded. The
median absolute correlation is 0.067, and only three pairs exceed |r| = 0.5: `qq_playlists` with
`apple_playlists` (0.712), `energy` with `acousticness` (−0.595), `qq_charts` with `apple_charts`
(0.555). The first and third are the same mechanism measured on two platforms; the second is
structural, since an acoustic recording is low-energy by construction. The two categorical
predictors, `charted_qq` and `mode`, cannot enter a correlation matrix; they are assessed as dummy
columns in the VIF below.

Restricted to the twelve terms that actually enter the candidate model, `energy` with `acousticness` is
the only pair above 0.5 and 0.595 is the largest absolute correlation of any kind, so the two platform
pairs are a property of variables that are excluded anyway.

VIF was computed on the full candidate model, which is the most conservative case because every
predictor is in it at once.

**Table 2. VIF for the full candidate model (course threshold: 5).**

| Term | VIF | Term | VIF |
|:---------------------------|---------:|:---------------------------|---------:|
| energy | 1.871 | speechiness | 1.098 |
| acousticness | 1.734 | charted_qq (Yes) | 1.076 |
| valence | 1.502 | artist_count | 1.065 |
| danceability | 1.470 | bpm | 1.052 |
| release_year | 1.337 | instrumentalness | 1.034 |
| log10(qq_playlists) | 1.244 | mode (Minor) | 1.032 |

Nothing approaches 5, so the estimates are not inflated by collinearity. The cross-platform pair is
removed by design rather than by trial and error: `apple_*` never enters the primary model, which keeps
the exposure coefficient interpretable as a QQ-specific association. `energy` and `acousticness` are
correlated but both have VIF below 2, so neither needs dropping; a structural pair of that kind is
better handled by testing the eight audio terms as a block, which is what Item 3(c) does.

---

## Item 3(c) — Model specification and selection [7 marks]

### 3(c)(i) Response scale, family and link

A Gaussian family with an identity link is used, fitted with `lm()` on log10 streams. Three things rule
out an untransformed fit: the response spans six orders of magnitude (2,762 to 3.70 billion), its raw
histogram is a single bin, and its relationship with playlist count is straight only in logs. A Poisson
or negative-binomial model was considered and rejected on the variance: Var/mean for `streams` is
6.4 × 10⁸, which no count model accommodates, and streams are a cumulative total rather than events in a
fixed exposure window.

`glm()` with `family = gaussian(link = "identity")` returns the same fit — the script fits both and
`all.equal()` comes back TRUE for the coefficients and for the deviance — so the choice between the two
functions is notation rather than substance. `glm()` reappears in Item 3(e) with a binomial family and a
logit link, where the family does the work.

The link is the identity rather than a log link, because the logarithm has already been applied to the
response: the constant-variance assumption is being made on the log scale, where the residuals of the
final model (Figure 1) show a flat spread. A log link on raw `streams` would instead assume a constant
variance in streams, contradicted by a range that runs from 2,762 to 3.70 billion.

A coefficient on this scale is an approximate proportional change: 0.10 corresponds to about 10% more
streams.

### 3(c)(ii) The nested comparison

Three nested models were compared, so that each block can be tested in the order the question implies.

```
M1: log10(streams) ~ log10(qq_playlists) + charted_qq
M2: M1 + release_year + artist_count
M3: M2 + danceability + energy + valence + acousticness
       + speechiness + instrumentalness + bpm + mode
```

**Table 3. Model comparison** (k = number of predictors; residual SE is on the log10 scale).

| Model | k | R² | Adjusted R² | AIC | BIC | Residual SE |
|:--------------------------|---:|-----------:|------------:|-----------:|-----------:|------------:|
| M1 exposure only | 2 | 0.6308 | 0.6300 | 416.41 | 435.35 | 0.3089 |
| M2 + timing/artist | 4 | 0.6374 | 0.6357 | **405.35** | **433.77** | 0.3065 |
| M3 + audio features | 12 | 0.6425 | 0.6373 | 409.47 | 475.77 | 0.3059 |

M1 → M2: F(2, 837) = 7.549, p < 0.001, so the controls belong. M2 → M3: F(8, 829) = 1.473, p = 0.163,
so the eight audio features add nothing jointly. They buy 0.005 of R² while raising AIC by 4.1 and
BIC by 42.0, and all three criteria point the same way. **M2 is the final model.**

This is the answer to the research question rather than a technicality: the audio block is not merely
non-significant, it is jointly indistinguishable from noise once exposure is present. That bounds how
much a content-based recommender could add on top of distribution information.

### 3(c)(iii) The final model, its coefficients and their intervals

**Final model (M2).**

*log10(streams) = 3.758 + 0.670·log10(qq_playlists) + 0.159·charted_qq + 0.001·release_year − 0.048·artist_count*

Fitted as `log10_streams ~ log_playlists + charted_qq + release_year + artist_count`, where
`log_playlists = log10(qq_playlists)` and `charted_qq` is a two-level factor.

F(4, 837) = 367.8, p < 0.001; R² = 0.637; residual SE = 0.307 on 837 df.

**Table 4. Final model coefficients.**

| Term | Estimate | SE | t | p | 95% CI |
|:------------------------------|-----------:|----------:|----------:|----------:|:--------------------------|
| (Intercept) | 3.758 | 2.155 | 1.74 | 0.082 | (−0.472, 7.987) |
| log10(qq_playlists) | 0.670 | 0.020 | 33.56 | < 0.001 | (0.631, 0.709) |
| charted_qq (Yes vs No) | 0.159 | 0.022 | 7.35 | < 0.001 | (0.117, 0.201) |
| release_year | 0.001 | 0.001 | 1.15 | 0.250 | (−0.001, 0.003) |
| artist_count | −0.048 | 0.013 | −3.78 | < 0.001 | (−0.073, −0.023) |

**Read: 3S.** The two coefficients the question turns on, read the way the lab answer keys read them:
sign, size on the response scale, and certainty.

**3S for the two coefficients.**

| 3S | `log10(qq_playlists)` | `charted_qq` (Yes vs No) |
|:---------|:--------------------------------------------------------|:--------------------------------------------------------|
| **Sign** | β̂ = 0.670, positive | β̂ = 0.159, positive |
| **Size** | 10% more playlists goes with 1.066× the streams, i.e. **6.6% more** (95% CI 6.2% to 7.0%); a doubling with 1.591×, i.e. 59.1% | **1.442×** the streams, i.e. **44.2% more** (95% CI 30.8% to 59.0%) |
| **Sure** | t = 33.56, p < 0.001 | t = 7.35, p < 0.001 |

Neither number is a change in streams: 0.670 and 0.159 are changes in log10 streams, so "0.670 more
streams" would be wrong. On the response scale the effects are 6.6% and 44.2%, which is how they are
reported below.

**Playlist exposure.** Holding chart presence, release year and artist count fixed, and with playlists
already in logs, the coefficient is an elasticity: 10% more playlists goes with 6.6% more streams, and a
doubling with 59.1%. The confidence limits translate to between 6.2% and 7.0% per 10%, so both the
direction and the magnitude are well determined. This is the largest effect in the model by a wide
margin.

**Chart presence.** Holding playlist count and the controls fixed, a song on at least one QQ chart is
associated with 44.2% more streams (95% CI 30.8% to 59.0%). The direction is precise; the size is
pinned down only to within a factor of about two. The comparison is also a strong one, since charting
and playlist placement move together in practice.

**Controls.** `release_year` is not significant once exposure is controlled (p = 0.250), which is
informative rather than disappointing: on its own the year slope is −0.012 per year (p < 0.001), but
pre-2010 records sit in a median of 13,893 playlists against 2,045 for later ones, so the era pattern
works through distribution rather than through age. `artist_count` is negative
and significant, at −10.4% per extra artist. That is counter-intuitive and is taken up in the
conclusion.

The playlist coefficient is stable across specifications (0.667 in M1, 0.670 in M2, 0.675 in M3), so
the headline result does not depend on which of the three models is chosen.

---

## Item 3(d) — Diagnostics and prediction [6 marks]

### 3(d)(i) Diagnostics

**Figure 1. Diagnostic plots for the final model.**

![Figure 1](figures/fig7_diagnostics.png){width=6.2in}

**Linearity and variance.** The residuals-versus-fitted smoother is not quite flat. Averaged in
eighths of the fitted range, the mean residual is +0.10 in the lowest eighth, dips to −0.13 just
below the middle of the range, and is back to +0.02 in the highest: a shallow U. A quadratic term in `log_playlists`
confirms it is detectable (F(1, 836) = 9.63, p = 0.002) with a positive coefficient, so the fit is
slightly too straight — the slope is right on average, the curvature is not modelled. Its size is
small — R² rises from 0.6374 to 0.6415, the residual SE falls from 0.307 to 0.305 and AIC by 7.6 —
and the fitted values move by 5% or less between 1,000 and 5,000 playlists, by 11% at 20,000, and by
28–31% only at 100 and 50,000, outside the central 98% of the distribution, where 8 and 3 songs sit.
The linear-in-logs form is kept, because a single elasticity is the quantity the question asks about
and the misfit lives in the tails; the shallow curve is carried into the limitations rather than
fitted away.

Constant variance holds: the scale-location plot is flat apart from three isolated points, and
Breusch-Pagan does not reject (LM = 6.11, df = 4, p = 0.191). Two further specification checks. An
interaction between chart presence and playlist count is not supported (F(1, 836) = 0.07, p = 0.789),
so the chart effect is additive as assumed. And the response scale is supported directly: the same
four predictors fitted to untransformed `streams` give a residual standard error of 3.6 × 10⁸ against
a mean of 5.4 × 10⁸ — 68% of the mean — with R² down to 0.617, the comparison behind the choice made
in Item 3(c)(i).

**Normality.** The Q-Q plot follows the line through the body of the distribution and departs at both
tails; Shapiro-Wilk rejects normality (W = 0.787, p < 0.001). The departure comes from the two
catalogue recordings with under 10⁷ streams: the lower of them, *Que Vuelvas* (2,762 streams), sits
4.77 log units below its fitted value. Normality matters for the small-sample behaviour of the t and
F tests rather than for the estimates themselves, and with 837 residual degrees of freedom the tests
are not sensitive to this departure.

**Influence.** No observation reaches a Cook's distance of 1; the largest is 0.180 for *Jhoome Jo
Pathaan*, a high-leverage record with no visible effect on the coefficients and well below the 0.5 rule
of thumb. Seven studentized residuals exceed 3 in absolute value, five of them negative. Deleting them
was therefore unnecessary, and would have removed genuine hits.

### 3(d)(ii) Prediction

Take a plausible song whose profile sits inside the observed range of every predictor in the final
model: playlists run from 31 to 52,898, release year from 1942 to 2023, contributing artists from one
to eight, and chart presence is a 0/1 indicator. The profile used is a 2022 single by one artist, in
5,000 QQ Music playlists (the 71st percentile) and on the QQ charts.

- predicted log10 streams 8.801, i.e. about **633 million**;
- 95% confidence interval for the mean response of such songs: (8.768, 8.835), 586–684 million;
- 95% prediction interval for this individual song: (8.199, 9.404), **158 million to 2.54 billion**.

**Table 5. Predictions for three exposure profiles** (all 2022, one artist).

| Profile | Playlists | Predicted streams | 95% prediction interval |
|:---------------------------------|------------:|-----------------------:|:-------------------------------|
| Low exposure, not charted | 300 | 66.6 million | 16.6 – 267.4 million |
| Reference, charted | 5,000 | 633.0 million | 158.0 – 2,535.4 million |
| High exposure, charted | 20,000 | 1,602.8 million | 399.3 – 6,433.7 million |

The two intervals answer different questions and the difference between them is the honest part of
the result. The confidence interval says how well the average outcome for this profile is pinned
down, and it is narrow because 842 records determine a mean well. The prediction interval says where
one new song would fall, and it spans a factor of sixteen, so for a single song that is the interval to
quote. A point forecast of 633 million is therefore better reported as "somewhere between about 160
million and 2.5 billion", which is a statement about the song-to-song variation the model leaves in
place.

**Figure 2. Fitted relationship and coefficient estimates.**

![Figure 2](figures/fig8_coefficients_and_prediction.png){width=6.2in}

Panel (a) shows the fitted curve and prediction band across the observed playlist range: straight in
log-log space, with the band widening only slightly at the extremes.

---

## Item 3(e) — Conclusion and model justification [4 marks]

### 3(e)(i) Justification 1: the ranking survives a change of response scale

Item 1(b) rejected a hit/not-hit outcome for the main question because the cut-off is arbitrary. It is
still useful as a check that the ranking of predictors does not depend on the choice of response
scale. Defining a hit as streams above the 75th percentile (701,997,830; 211 songs, 25.1%) and
refitting the same four predictors with a logit link gives `log10(qq_playlists)` 7.003 (SE 0.576,
p < 0.001), `charted_qq` 1.015 (p < 0.001), `release_year` 0.034 (p = 0.003) and `artist_count`
−0.519 (p = 0.010), with McFadden pseudo-R² = 0.621. A doubling of playlist count multiplies the odds
of being a hit by about 130 (10^2.11). The same variables come out in the same order with the same
signs, so the substantive conclusion is not an artefact of the log-linear specification.

### 3(e)(ii) Justification 2: why this model rather than a larger or a different one

The choice is supported on three counts, each tested where it was reported. The four-parameter model is
preferred by all three selection criteria at once, adjusted R², AIC and BIC, and by a nested F test that
cannot reject the audio block (p = 0.163), so the eight extra terms are not earning their place — the
parsimonious model is also the one that generalises better. Collinearity cannot be blamed for that
result: no VIF exceeds 1.9, and the largest correlation among the twelve terms that enter is −0.595
between `energy` and `acousticness`, both of which stay because neither is redundant on its own. And
the coefficients are stable: the playlist elasticity moves only between 0.667 and 0.675 across the
three specifications, and the ranking is unchanged under a logit link on a binary outcome.

What the model cannot do is identify a causal effect. Playlist placement follows popularity as well as
causing it, so the coefficients describe differences between songs rather than the return on a
decision.

### 3(e)(iii) Conclusion

Across 842 songs, this report asked how strongly a song's streaming performance on QQ Music is
associated with the exposure it receives, compared with its own audio characteristics, once release
timing and artist count are held constant. The answer is exposure, by a wide margin. The two exposure
variables alone explain 63.0% of the variation in log10 streams. Adding the eight audio features raises
R² by 0.005, fails a joint F test (F(8, 829) = 1.47, p = 0.163) and worsens both AIC and BIC, so the
four-parameter model without audio content is preferred: playlist count (β = 0.670), chart presence
(β = 0.159), release year and artist count (β = −0.048), with R² = 0.637.

In practical terms, 10% more playlist placement goes with 6.6% more streams and appearing on a chart
with 44% more, while no audio characteristic shows a meaningful association on its own. For the QQ
Music team this bounds what content-based prediction can add beyond distribution signals.

Three limitations should be kept in view. The design is cross-sectional and observational, and
playlist placement is plausibly a consequence of popularity as much as a cause, so these are
associations rather than the returns from adding a song to a playlist. Streams are cumulative and the
sample is dominated by recent releases, so the weak release-year coefficient after adjustment is not
evidence that a song's age is irrelevant. And the model leaves 36% of the variance unexplained, its
residuals keep a shallow curve and its Q–Q plot departs in both tails, and the prediction interval
spans a factor of sixteen, so a point forecast carries real uncertainty; the negative artist-count
coefficient is also counter-intuitive and probably reflects unrecorded genre differences rather than a
penalty for collaboration.

---

## Appendix — files and how to run

| File | Contents |
|---|---|
| `Q4_GLM.R` | this part, in the order of 3(a) to 3(e): predictor evidence, correlation and VIF, specification and selection, diagnostics, prediction, the logit check. Base R only |
| `tables/correlation_pairs.csv` | the three predictor pairs above \|r\| = 0.5 quoted in Item 3(b) |
| `tables/vif.csv` | Table 2, VIF for the full candidate model |
| `tables/model_comparison.csv` | Table 3, the three nested models |
| `tables/final_coefficients.csv` | Table 4, estimate, SE, t, p and 95% CI per term |
| `tables/prediction.csv` | Table 5, the three profiles with prediction intervals |
| `data/QQ_Music_clean.csv` | the 842-row analysis file, included so that `Q4_GLM.R` runs on its own |
| `figures/` | `fig7_diagnostics.png` and `fig8_coefficients_and_prediction.png` are the two used here, at 300 dpi |

Table 1 is the one table the script does not write, since each row is a decision rather than a result;
every number quoted in it is printed by the corresponding block of Item 3(a).

The file names in `figures/` follow the order in which the scripts draw them, not the figure numbers of
this report: `fig7_diagnostics.png` is Figure 1 here and `fig8_coefficients_and_prediction.png` is
Figure 2. `Q4_EDA.R` — items 1 and 2, the script that writes `data/QQ_Music_clean.csv` — is not needed
to run this part, because the clean file is included here.

Run `Q4_GLM.R` from the folder that holds `data/`; base R on R 4.6.1, no packages to install. Sourced in
RStudio it draws the two figures in the Plots pane and writes nothing, so the PNG files already in
`figures/` stay as they are; run with `Rscript` it writes them again and refreshes `tables/`. The switch
is the `preview` line near the top of the script.
