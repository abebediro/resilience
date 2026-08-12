# Viasat KA-SAT Case Study (Appendix D)

## D.1 Estimated pre-attack posture

| Dimension | Estimated value | 80% credible range | Basis |
|---|---|---|---|
| Preparedness | 0.31 | [0.25, 0.37] | Limited public intelligence on modem vulnerabilities; no prior warnings |
| Resistance | 0.28 | [0.22, 0.34] | Consumer-grade modem security; absence of hardware-level hardening |
| Restoration | 0.22 | [0.17, 0.27] | No remote recovery capability; manual replacement required |
| Adaptation | 0.18 | [0.14, 0.22] | Limited learning from prior incidents; no major previous attacks |
| Supply Chain | 0.35 | [0.29, 0.41] | Moderate visibility within consumer-oriented supply chain |

## D.2 Prediction intervals and validation

| Metric | Prediction | 95% PI | Observed |
|---|---|---|---|
| Recovery to 90% service | 47 days | [33, 61] days | ~45 days |
| Initial breach extent | 62% | [55%, 70%] | ~62% |
| Attack success prob. | 0.73 | [0.65, 0.80] | Confirmed |

## D.3 Likelihood ratio test

| Statistic | Value |
|---|---|
| Log-likelihood (null model L0) | -124.3 |
| Log-likelihood (alternative L1) | -118.0 |
| Likelihood ratio (lambda) | 12.6 |
| Degrees of freedom | 2 |
| p-value | <0.01 |

Rejection of H0 confirms structural dependencies improve model fit.

## D.4 Quantitative validation metrics

| Metric | Value |
|---|---|
| Theil's U statistic | 0.82 |
| MAPE | 4.4% |
| RMSE | 5.1 days |
| Mean bias error | +2.3 days |
| Correlation (pred. vs. realizations) | r = 0.91, p < 0.001 |

## D.5 Sensitivity to estimation assumptions

| Scenario | Recovery | Attack prob. | Breach |
|---|---|---|---|
| Baseline | 47 days | 73% | 62% |
| Pre-attack est. +/-20% | +/-8% var. | +/-5% var. | +/-6% var. |
| Alt. incident definitions | 3.9-5.2% MAPE | --- | --- |
