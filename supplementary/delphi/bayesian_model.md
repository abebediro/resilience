# Bayesian Hierarchical Aggregation Model

Expert judgments were aggregated under a Bayesian hierarchical
(random-effects) model with Cooke performance weighting derived from the
eleven seed variables:

```
theta_hat_j ~ Normal(theta, sigma_j^2 + tau^2)      # expert likelihood
theta       ~ pi_0(theta)                            # weakly informative prior
tau         ~ HalfCauchy(0, 0.5)                     # between-expert heterogeneity
```

where `theta_hat_j` is expert `j`'s point estimate, `sigma_j` is the
standard deviation derived from their 80% credible interval, `pi_0` is a
weakly informative prior, and `tau` captures between-expert
heterogeneity.

Each expert's contribution is weighted by a normalized Cooke score
`w_e ∝ C_e · I_e`:
- `C_e` — calibration score, from seed-variable statistical accuracy
- `I_e` — informativeness, from interval tightness

**Estimation:** Hamiltonian Monte Carlo, 4 chains, 2000 warmup, 4000
sampling iterations. Convergence confirmed at R-hat < 1.01 for all
parameters; effective sample sizes exceeded 8000.

## Panel composition sensitivity (leave-one-out)

| Parameter | Max influence | Mean influence | Expert (max) |
|---|---|---|---|
| k_prep | 0.062 | 0.028 | E06 |
| k_resist | 0.058 | 0.024 | E09 |
| k_restore | 0.071 | 0.031 | E04 |
| k_adapt | 0.083 | 0.035 | E06 |
| k_supply | 0.054 | 0.022 | E13 |
| alpha | 0.042 | 0.018 | E09 |
| beta | 0.048 | 0.021 | E01 |
| gamma | 0.038 | 0.016 | E07 |
| gamma_T | 0.052 | 0.023 | E04 |
| mu | 0.061 | 0.027 | E09 |
| theta | 0.072 | 0.032 | E09 |
| xi_resist | 0.044 | 0.019 | E06 |

Maximum influence across all parameters is 0.083 — no single expert
dominates the aggregated estimates.

## AHP analysis (relative dimension weights)

See `ahp_pairwise.csv` for the geometric-mean pairwise matrix and
derived weights. Consistency: lambda_max = 5.36, CI = 0.09, CR = 0.08
(acceptable, CR < 0.10).

**Kendall's W (expert rank agreement across the five dimensions):**
W = 0.72, chi-squared = 43.2, p < 0.001 — strong agreement on relative
dimension importance (Resistance > Restoration > Preparedness >
Supply Chain > Adaptation for all but 3 experts).

## Parameter correlation (Round 1, selected pairs)

| | k_prep | k_resist | k_restore | theta | gamma_threat | beta | xi_resist |
|---|---|---|---|---|---|---|---|
| k_prep | 1.00 | 0.62 | 0.58 | 0.45 | 0.38 | 0.29 | 0.41 |
| k_resist | 0.62 | 1.00 | 0.71 | 0.52 | 0.44 | 0.35 | 0.53 |
| k_restore | 0.58 | 0.71 | 1.00 | 0.49 | 0.41 | 0.38 | 0.47 |
| theta | 0.45 | 0.52 | 0.49 | 1.00 | 0.67 | 0.28 | 0.39 |
| gamma_threat | 0.38 | 0.44 | 0.41 | 0.67 | 1.00 | 0.22 | 0.33 |
| beta | 0.29 | 0.35 | 0.38 | 0.28 | 0.22 | 1.00 | 0.31 |
| xi_resist | 0.41 | 0.53 | 0.47 | 0.39 | 0.33 | 0.31 | 1.00 |

Correlations > 0.5 indicate systematic relationships in expert
judgments (notably within the decay-rate family and between theta and
gamma_threat, both adversary-co-evolution parameters).
