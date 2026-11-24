## Question 4 — QQ Music Streaming Performance

### Data preparation and research question

The analysis uses 842 usable songs from the 844-row source file. One record has a field-shifted, non-numeric value in `streams`; its outcome cannot be recovered and is set to missing, then excluded. One duplicate (same title, artist and stream total) is removed. No values are imputed and no statistical outliers are deleted. The analysis retains the 89 missing `key` values because `key` is not used in the fitted models. The response is `log10_streams = log10(streams)`: raw streams range from 2,762 to 3.70 billion, making a log scale both interpretable in proportional terms and more suitable for an additive mean model. The retained analysis data and figures are referenced from the repository root.

**Research question.** How strongly is QQ Music streaming performance associated with platform exposure—QQ playlist count and QQ chart presence—relative to audio characteristics, after accounting for release timing and the number of contributing artists? The question matters to QQ Music because it contrasts distribution signals that the platform may influence with content-based signals available to recommenders. The observational data support association, not the causal return from assigning a playlist placement.

### Exploratory data analysis

The response has a median of 301.0 million streams (IQR 146.9–702.0 million) and spans six orders of magnitude. `qq_playlists` is strongly right-skewed (median 2,311; maximum 52,898); its association with log streams is stronger by rank (Spearman ρ = 0.829) than by linear correlation (Pearson r = 0.629), indicating a monotone but nonlinear relationship on the raw-count scale. The QQ chart count is zero for 43.5% of songs, so chart presence is represented as an indicator in the model. The audio scores have weak individual associations with log streams (all |r| ≤ 0.108). Release year is strongly rank-associated with the response (ρ = −0.682), reflecting the accumulation of streams over time and the predominance of recent releases (75.1% released in 2020 or later). Songs on a QQ chart have median streams of 404.7 million versus 215.9 million for songs not on a chart. The IQR rule flags high-stream and high-playlist records, but these are plausible hits rather than data errors; they remain in the analysis.

**Figure 4. EDA overview with six informative panels:** response distribution, playlist exposure, chart presence, release decade, danceability, and artist count. Together these panels provide more than five exploratory views; the IQR flags describe extremes and are not used to delete observations.

![Six-panel EDA overview](report/assignment3_outputs/figures/q4_eda_overview.png)

### Variable roles and measurement scales

Roles below are defined against the research question. IV/DV identifies independent/dependent status; predictor/response states the model role. Analysis includes original candidate variables and derived variables used for summaries or plots.

| Variable | Measurement scale / data type | IV / DV | Predictor / response role and treatment |
|---|---|---|---|
| `track_name` | Nominal identifier | Neither | Identifier only; excluded |
| `artist_name` | Nominal identifier | Neither | Identifier only; excluded (563 distinct values) |
| `streams` | Ratio, positive count-like total | DV | Source outcome; transformed to `log10_streams` |
| `log10_streams` | Interval, derived | DV | Primary response |
| `qq_playlists` | Ratio, count | IV | Candidate predictor; entered as `log10(qq_playlists)` |
| `qq_charts` | Ratio, count; 43.5% zeros | IV | Candidate predictor; represented as `charted_qq` indicator |
| `charted_qq` | Nominal binary, derived | IV | Exposure predictor: 1 when `qq_charts > 0` |
| `apple_playlists` | Ratio, count | IV | Excluded; cross-platform analogue, correlated 0.712 with QQ playlists |
| `apple_charts` | Ratio, count | IV | Excluded; cross-platform analogue, correlated 0.555 with QQ chart count |
| `charted_apple` | Nominal binary, derived | IV | Excluded; Apple-side exposure outside the QQ-specific question |
| `release_year` | Interval | IV | Control predictor for time available to accumulate streams |
| `release_month` | Ordinal/cyclical | IV | Excluded; no defensible mechanism for cumulative streams |
| `release_day` | Discrete interval | IV | Excluded; no defensible mechanism for cumulative streams |
| `artist_count` | Ratio, discrete (1–8) | IV | Control predictor |
| `collab` | Nominal binary, derived | IV | Descriptive alternative to artist count; excluded from model |
| `bpm` | Ratio | IV | Audio candidate predictor |
| `mode` | Nominal binary (Major/Minor) | IV | Audio candidate predictor; entered as factor |
| `danceability` | Interval score (0–100) | IV | Audio candidate predictor |
| `energy` | Interval score (0–100) | IV | Audio candidate predictor |
| `valence` | Interval score (0–100) | IV | Audio candidate predictor |
| `acousticness` | Interval score (0–100) | IV | Audio candidate predictor |
| `speechiness` | Interval score (0–100) | IV | Audio candidate predictor |
| `instrumentalness` | Interval score (0–100) | IV | Audio candidate predictor; 90.4% are zero |
| `liveness` | Interval score (0–100) | IV | Considered, not entered; weakest score-response correlation (r = −0.050) |
| `key` | Nominal, 11 observed levels | IV | Excluded; missing for 89 songs and not required by question |
| `decade` | Ordinal grouping derived from year | Neither | Descriptive plot grouping only |
| `artist_group` | Ordinal grouping derived from artist count | Neither | Descriptive plot grouping only |

The audio scores are interval indices without a meaningful natural zero; counts and BPM have meaningful zero points, while calendar year does not. The identifiers label records rather than quantify explanatory attributes. `decade` and `artist_group` are derived grouping variables, not independent analytical predictors.

### Predictor selection and multicollinearity

The candidate exposure predictors are `log10(qq_playlists)` and `charted_qq`, because they represent distinct QQ exposure channels and have the strongest substantive relationship with the response. `release_year` and `artist_count` are controls for stream accumulation and collaboration structure. The eight audio terms—danceability, energy, valence, acousticness, speechiness, instrumentalness, BPM and mode—are included together in the expanded candidate model so their joint contribution can be tested. `liveness` is excluded because it is the weakest of the seven audio scores in the EDA. Track and artist names are identifiers; month/day lack a plausible mechanism; `key` has missing values and many levels. Apple measures are excluded to keep the primary question QQ-specific and avoid duplicating correlated platform exposure. `collab` is a binary recoding of `artist_count`, and `decade` recodes `release_year`, so they add no independent information.

Among numerical predictors, the three pairs with |r| > 0.5 are QQ and Apple playlists (0.712), energy and acousticness (−0.595), and QQ and Apple chart counts (0.555). Within the model candidate set, energy–acousticness is the only pair above 0.5. VIFs for the full candidate model are all below 1.9 (maximum 1.871 for energy; acousticness 1.734), well below the course threshold of 5. Thus the two audio terms can remain for the joint test; the redundant cross-platform measures are omitted by design.

### Model specification, comparison and selection

The response is `log10_streams`. A Gaussian model with identity link is appropriate for an additive mean on the transformed scale; fitting with `lm()` is equivalent to `glm(..., family = gaussian(link = "identity"))`. The log response avoids the six-order raw-scale range and gives coefficients a proportional interpretation. A Poisson or negative-binomial count model is unsuitable for cumulative stream totals: the raw variance-to-mean ratio is 6.4 × 10⁸, and streams are not event counts over a fixed exposure interval.

Three nested models compare exposure, controls and audio in sequence:

- **M1:** `log10_streams ~ log10(qq_playlists) + charted_qq`
- **M2:** M1 plus `release_year + artist_count`
- **M3:** M2 plus `danceability + energy + valence + acousticness + speechiness + instrumentalness + bpm + mode`

| Model | Predictors (k) | R² | Adjusted R² | AIC | BIC | Residual SE |
|---|---:|---:|---:|---:|---:|---:|
| M1: exposure only | 2 | 0.6308 | 0.6300 | 416.41 | 435.35 | 0.3089 |
| M2: plus timing/artist | 4 | 0.6374 | 0.6357 | **405.35** | **433.77** | 0.3065 |
| M3: plus audio | 12 | **0.6425** | **0.6373** | 409.47 | 475.77 | 0.3059 |

Adding timing and artist count improves fit over M1 (F(2, 837) = 7.549, p < 0.001). The audio block does not significantly improve M2 (F(8, 829) = 1.473, p = 0.163). M3 has slightly higher adjusted R² than M2 (0.6373 versus 0.6357), so it would be inaccurate to say M2 wins every criterion. M2 is selected as the more parsimonious specification because it has lower AIC and BIC and the nested test does not establish incremental audio-block improvement; this is a model-selection preference, not proof that audio has no effect or that M2 necessarily generalises better.

**Final model (M2):**

`log10(streams) = 3.758 + 0.670 log10(qq_playlists) + 0.159 charted_qq + 0.001 release_year − 0.048 artist_count`

The overall fit is F(4, 837) = 367.8, p < 0.001, R² = 0.637, with residual SE = 0.307. Holding other terms fixed, a 10% increase in QQ playlist count corresponds to about 6.6% higher streams (β = 0.670; 95% CI 0.631–0.709 on the log10 scale). A song appearing on at least one QQ chart is associated with about 44.2% higher streams than a non-charted song (β = 0.159; 95% CI 0.117–0.201). The association for artist count is negative (β = −0.048; 95% CI −0.073 to −0.023), while release year is not statistically distinguishable from zero after adjustment (p = 0.250). These are conditional associations, not causal effects.

### Diagnostics and prediction

**Figure 5. Diagnostic plots for the selected model.**

![Final model diagnostic plots](report/assignment3_outputs/figures/q4_model_diagnostics.png)

Residual spread is broadly stable: the scale-location plot is mostly flat and the Breusch–Pagan test does not reject constant variance (LM = 6.11, df = 4, p = 0.191). The residual-versus-fitted smoother shows a shallow U-shaped pattern; adding a quadratic playlist term detects curvature (F(1, 836) = 9.63, p = 0.002), but the improvement is modest (R² 0.6374 to 0.6415) and concentrated in extreme playlist counts, so the simpler linear-in-logs elasticity is retained. The Q–Q plot tracks the central residual distribution but departs in both tails; Shapiro–Wilk rejects normality (W = 0.787, p < 0.001), largely due to two catalogue records below 10 million streams. With 837 residual degrees of freedom, coefficient estimates remain useful, but tail-based inference merits caution. No observation has Cook's distance above 1 (maximum 0.180); seven studentized residuals exceed |3| and are retained as plausible songs rather than deleted. A chart-by-playlist interaction is unsupported (F(1, 836) = 0.07, p = 0.789).

For a plausible profile—2022 release, one artist, 5,000 QQ playlists and charted—the fitted response is 8.801 log10 streams. Back-transforming with `10^x` gives approximately 633 million streams as the **conditional geometric-scale point prediction** implied by the fitted log mean. The 95% confidence interval for the conditional mean on the log scale is 8.768–8.835; after back-transformation it is approximately 586–684 million and pertains to the geometric mean, not the arithmetic mean of raw streams. The 95% prediction interval for an individual song is 8.199–9.404, or approximately 158 million–2.54 billion streams. It is much wider because it includes song-to-song residual variation. Thus the prediction interval, not the narrow mean interval, is the appropriate uncertainty statement for an individual track.

### Conclusion (225 words)

Across 842 QQ Music songs, streaming performance is much more closely associated with platform exposure than with measured audio characteristics. The preferred model is a Gaussian identity-link regression for log10 streams, with log10 playlist count, QQ chart presence, release year, and artist count. It is selected for parsimony: adding eight audio terms does not yield a significant nested-model improvement (F(8, 829) = 1.473, p = 0.163), and raises AIC and BIC. M3 does have a marginally higher adjusted R² (0.6373 versus 0.6357), so this is not evidence that audio has no effect; rather, this sample does not establish useful incremental fit from that block. The final model explains 63.7% of variation in log streams. Conditional on the other predictors, 10% more playlist placement corresponds to about 6.6% more streams, and chart presence to about 44% more. The playlist association is stable across candidate specifications, while the adjusted release-year effect is uncertain and the negative artist-count association may reflect unmeasured differences among songs.

These estimates are observational associations, not the causal return to playlist placement: popularity may itself attract playlists and chart exposure. Streams are cumulative, and the sample is dominated by recent releases, complicating comparisons across eras. The model also has a shallow residual curve and non-normal tails, and leaves about 36% of log-scale variation unexplained. For an individual track, the prediction interval is broad (about 158 million to 2.54 billion for the reference profile), so the point estimate should not be treated as a precise forecast. Better causal claims would require longitudinal or randomized exposure data; better forecasts may require genre, marketing, and time-varying popularity measures.
