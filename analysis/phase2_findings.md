# Phase 2: Exploratory Analysis — Training Load, Weather, and Performance

Notebook-based exploratory analysis of one year of training data (Sept 2025 –
Sept 2026), examining three questions before any of this is promoted into
persisted dbt models or a predictive layer.

## 1. TSB vs Performance

Question: does higher Training Stress Balance (freshness) correlate with better
per-activity performance?

- Efficiency factor vs TSB: n=37, r=-0.119, p=0.493 — not significant.
- Average speed vs TSB, controlling for elevation gain (partial correlation):
  n=36, raw r=0.118 (p=0.493), partial r=0.216 (p=0.213) — not significant, but
  elevation control nearly doubled the apparent relationship in the hypothesized
  direction.

**Conclusion:** Directional, not confirmed. Both tests are underpowered — detecting
a true effect the size observed (r≈0.22) at 80% power would need roughly n≈160+;
current activity-level sample is 36-38. Revisit as training history accumulates.

## 2. Weather vs Training Behavior

Question: does weather affect whether/how you train? Uses full daily grain
(n=363 days, 96 active = 26.4%), not just activity-level records.

- Temperature significantly correlates with training likelihood: max temp
  r=-0.134 (p=0.010), min temp r=-0.141 (p=0.007). Warmer days → lower likelihood
  of training. Real but small (r²≈2%), and confounded by having only one seasonal
  cycle of data — can't separate a true weather effect from other factors that
  also vary by time of year.
- Rain has no detectable effect on training likelihood (chi2 p=0.748). Explained
  by a separate finding: 90% of cycling (35/39 days) happens indoors on the
  trainer regardless of weather, so outdoor conditions rarely gate whether you train.
- Indoor/outdoor choice as a function of weather: not testable — only 4 of 39
  cycling days were outdoors.

**Conclusion:** Weather has, at most, a small effect on whether you train at all;
no evidence it affects indoor/outdoor choice (data too sparse to test).

## 3. Efficiency / Power Progression

A 5-week complete training gap (Jan 27 – Feb 28, 2026) splits the data into
pre-gap (Sep-Dec 2025, n≈9) and post-gap (Mar-Sep 2026, n≈29) segments.

- EF down 28% (1.161→0.839, t=3.408, p=0.008) and weighted_avg_watts down 27%
  (166.1→120.5, t=4.509, p=0.001) — both highly significant.
- Decoupling — the one metric independent of chosen intensity/FTP, since it
  measures HR drift within a single ride regardless of effort — essentially
  unchanged (4.86→5.71, t=-0.450, p=0.658). Not significant.
- Confound identified: intensity (-27%) and training_load (-44%) also dropped
  post-gap while duration didn't (36→40 min) — rides got easier, not shorter.

**Conclusion:** No reliable evidence of underlying fitness/durability loss from
the break. Strong evidence of a sustained shift to lower-intensity training since
returning (through September, no sign of reverting). A structured FTP test would
give a direct answer this observational data can't.

## Cross-cutting takeaways

- Sample size is the binding constraint for activity-level questions: power/EF/
  decoupling are populated on only ~30-40 of 126 activities. Daily-grain questions
  (weather/behavior) are far better powered (n=363) since they don't depend on
  those sparse fields.
- Two data-quality/definitional issues surfaced and were addressed: `outdoor_activity_count`
  mislabeling non-cycling indoor activities as "outdoor" (fixed in `mart_daily_training`),
  and `ftp_at_activity` clarified as your current FTP setting, not a historical
  per-activity snapshot (documentation only — not fixable, the source data doesn't
  carry historical FTP).

## Next

Phase 3: predictive modeling (training-load forecasting).