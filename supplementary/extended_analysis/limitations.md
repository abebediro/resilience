# Comprehensive Limitations (Appendix F)

## F.1 Limitation inventory with impact magnitudes

| Limitation | Description | Impact magnitude | Mitigation |
|---|---|---|---|
| D1: Small sample | 70 incidents over 15 years | High; +/-20-25% uncertainty | Bayesian regularization; posterior checks; 9-parameter primary model |
| E1: Geographic concentration | 12 of 15 experts Western-affiliated | Medium; +/-10-15% variation | Cross-background divergence test (`cross_background.md`); prior-perturbation robustness (core supplement §IV) |
| S1: Dimensional aggregation | Each dimension as single normalized stock | Medium; +/-10% error | Direct separability; disaggregation experiment (`additional_derivations.md` L.10) |
| S2: Human factors | Reduced-form multiplicative factor only | Medium; +/-20% variability | Implicit calibration; sensitivity analysis |
| S3: Geopolitical exogenous | Geopolitics as scenario input | Medium-High for long-term | Shock module; finite-adversary cap (`operational_constraints.md`) |
| S4: Continuous approximation | Incidents are discrete events | Low-Medium; +/-10% mean | SDE validation; annual aggregation |
| S5: Stationarity | Parameters constant over 20 years | High for year-20 projections | Sequential updating pathway (`deployment_pathway.md`) |
| C1: Market data vintage | Costs from 2020-2024 data | Medium; +/-15-25% | Relative comparisons; scenario analysis |
| P1: Reporting precision | Values are medians, not exact | Low-Medium | Credible ranges; Monte Carlo propagation |

## F.2 Additional limitations

- **Correlated failures:** the baseline composition assumes conditional
  independence. A Gaussian copula extension (`additional_derivations.md`
  L.11) shows that at rho=0.4 the holistic advantage falls to ~8.5% and
  resilience drops ~12-15%, while qualitative conclusions and strategy
  rankings are preserved.
- **Validation circularity:** validation uses incidents that partly
  informed parameter priors. The blind subset and the temporal split
  (see `../validation/model_selection.md`) bound this effect; estimated
  out-of-sample predictive power is r ~ 0.68-0.72.
- **Retrodictive scope:** validation is incident-level and retrodictive;
  telemetry-grade closed-loop validation awaits the prospective protocol
  (`deployment_pathway.md`).
- **Black swan events:** the model is calibrated to severity 1-5
  incidents and cannot predict catastrophic events outside the
  historical record.

## F.3 Future research priorities

| Direction | Sample size / power | Uncertainty reduction | Limitation addressed |
|---|---|---|---|
| Empirical calibration | n >= 150 events; power 0.80 | 50-70% | D1 |
| Non-Western expert panel | 10-15 additional experts | 30-40% | E1 |
| Disaggregated sub-model | 30-50 scenarios | 20-30% | S1 |
| Human factors submodel | 50-75 scenarios; power 0.80 | 20-30% | S2 |
| Geopolitical coupling | 3-5 case studies | 30-50% (long-term) | S3 |
| Prospective validation | n >= 50 incidents; power 0.80 | 40-60% | All |
