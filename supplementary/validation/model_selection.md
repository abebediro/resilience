# Model Validation Test Results (Appendix B, full)

Headline validation numbers are in the core supplement (§III). This
file has the complete diagnostics.

## B.1 Extreme condition test outcomes

See `../03_code/extreme_conditions_tests.md` for the full TC01-TC08
table (all eight tests pass).

## B.2 Statistical model selection (functional form)

| Functional form | Delta AIC | Delta BIC | LR test |
|---|---|---|---|
| Linear (M1) | 12.5 | 10.3 | p < 0.001 |
| Exponential (M2) | 2.1 | 1.8 | p = 0.12 |
| Superlinear (M3) | 0 | 0 | Reference |

## B.3 Hypothesis testing of key relationships

| Hypothesis | Statistic | df | p-value | Conclusion |
|---|---|---|---|---|
| H0: mu=0 vs. H1: mu>0 | t = 6.67 | 68 | p << 0.001 | Reject H0 |
| H0: theta=0 vs. H1: theta>0 | t = 6.67 | 68 | p << 0.001 | Reject H0 |
| H0: xi_res=0 vs. H1: xi_res>0 | t = 13.6 | 68 | p << 0.001 | Reject H0 |

## B.4 Cross-validation performance (10-fold)

| Model | RMSE | MAE | MAPE (%) |
|---|---|---|---|
| Proposed SD model (full) | 0.42 | 0.31 | 12.4 |
| Proposed SD model (9-parameter) | 0.45 | 0.33 | 13.1 |
| Benchmark 1 (Linear additive) | 0.59 | 0.45 | 18.6 |
| Benchmark 2 (Static Power-Law) | 0.48 | 0.36 | 14.7 |
| Benchmark 3 (Resilience triangle) | 0.55 | 0.42 | 16.1 |

## B.5 Posterior predictive checks

| Metric | Value |
|---|---|
| Posterior predictive p-value | 0.37 |
| Observed data coverage within 80% PI | 74% |
| Observed data coverage within 95% PI | 93% |

Interpretation: p = 0.37 indicates no significant discrepancy between
model and data.

## B.6 Monte Carlo convergence diagnostics (Gelman-Rubin)

| Output | Yr 5 | Yr 10 | Yr 15 | Yr 20 |
|---|---|---|---|---|
| R_system | 1.002 | 1.001 | 1.001 | 1.002 |
| R_effective | 1.003 | 1.002 | 1.001 | 1.002 |
| Preparedness | 1.001 | 1.001 | 1.002 | 1.002 |
| Resistance | 1.002 | 1.001 | 1.001 | 1.003 |

All R-hat < 1.01, confirming chain convergence (4 chains, 2000 warmup,
4000 sampling iterations).

## B.7 Validation design against narrative fitting

Three nested safeguards guard against validation degenerating into
post-hoc fitting of known history:

1. **Temporal split** — incidents from 2007-2017 (n=48) calibrate the
   model; incidents from 2018-2022 (n=22) are held out, with parameters
   re-estimated on the calibration set only and frozen before
   evaluation.
2. **Blind subset** — eight held-out incidents verified (via session
   transcripts) never to have been discussed in any Delphi round.
3. **Pre-registered criteria** — the reconstruction success thresholds
   (`../02_incident_dataset/coding_manual.md`) were fixed before
   evaluation.

| Evaluation | N | RMSE | MAPE | r |
|---|---|---|---|---|
| Calibration (2007-2017) | 48 | 0.39 | 11.1% | 0.81 |
| Temporal hold-out (2018-2022) | 22 | 0.48 | 14.8% | 0.72 |
| Blind subset (never discussed) | 8 | 0.51 | --- | 0.68 |
| 10-fold CV (full corpus) | 70 | 0.42 | 12.4% | 0.78 |

All six robust qualitative findings survive the temporally split
calibration.
