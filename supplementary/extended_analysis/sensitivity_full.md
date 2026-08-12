# Full Sensitivity Analysis (Appendix C)

Condensed headline numbers appear in the core supplement (§IV). This
file has the complete tables.

## C.1 Sobol sensitivity indices with 95% CI

| Rank | Parameter | S_i | S_Ti | 95% CI (S_Ti) |
|---|---|---|---|---|
| 1 | theta (Adversary Learning) | 0.284 | 0.382 | [0.351, 0.413] |
| 2 | xi_resist (SC Cascade) | 0.195 | 0.287 | [0.262, 0.312] |
| 3 | k_resist (Resist. Decay) | 0.152 | 0.216 | [0.194, 0.238] |
| 4 | psi_prep (Adapt. Amplif.) | 0.089 | 0.148 | [0.131, 0.165] |
| 5 | gamma (Radiation Sens.) | 0.072 | 0.112 | [0.098, 0.126] |
| 6 | k_prep (Prep. Decay) | 0.058 | 0.089 | [0.077, 0.101] |
| 7 | alpha (Latency Sens.) | 0.048 | 0.075 | [0.064, 0.086] |
| 8 | beta (Inaccess. Penalty) | 0.032 | 0.053 | [0.044, 0.062] |
| 9 | k_restore (Rest. Decay) | 0.025 | 0.042 | [0.034, 0.050] |
| 10 | k_supply (SC Decay) | 0.019 | 0.031 | [0.024, 0.038] |

## C.2 Rank stability (bootstrap resampling)

| Rank | Parameter | Stability prob. | 95% CI |
|---|---|---|---|
| 1 | theta | 0.98 | [0.96, 0.99] |
| 2 | xi_resist | 0.96 | [0.94, 0.98] |
| 3 | k_resist | 0.95 | [0.93, 0.97] |
| 4 | psi_prep | 0.88 | [0.85, 0.91] |
| 5 | gamma | 0.84 | [0.81, 0.87] |
| 6 | k_prep | 0.79 | [0.75, 0.83] |
| 7 | alpha | 0.74 | [0.70, 0.78] |
| 8 | beta | 0.71 | [0.67, 0.75] |

## C.3 Robustness classification (bootstrap confidence)

| Finding | Class | 95% CI (class) | Supporting runs |
|---|---|---|---|
| Logistic growth pattern | ROBUST | [ROBUST, ROBUST] | 94% |
| Holistic strategy superiority | ROBUST | [ROBUST, ROBUST] | 98% |
| Early investment compounding | ROBUST | [ROBUST, ROBUST] | 96% |
| Supply chain leverage effect | ROBUST | [MODERATE, ROBUST] | 89% |
| Red Queen effect erosion >15% | ROBUST | [MODERATE, ROBUST] | 91% |
| Adaptation amplification >2x | ROBUST | [MODERATE, ROBUST] | 87% |
| Adaptation delayed returns | MODERATE | [MODERATE, MODERATE] | 75% |
| Intelligence > Technology | MODERATE | [FRAGILE, MODERATE] | 71% |
| Resistance dominant (years 1-5) | MODERATE | [FRAGILE, MODERATE] | 68% |
| Resistance as top short-term factor | FRAGILE | [FRAGILE, FRAGILE] | 62% |
| Radiation dominates resistance | FRAGILE | [FRAGILE, FRAGILE] | 58% |

## C.4 Effect sizes for key strategy comparisons

| Comparison | Abs. delta | Cohen's d | CLES | Signif. |
|---|---|---|---|---|
| Holistic vs. Baseline | 0.10 | 1.69 | 0.88 | Large |
| Holistic vs. Resistance-foc. | 0.05 | 0.85 | 0.73 | Large |
| Holistic vs. Supply-foc. | 0.06 | 1.01 | 0.76 | Large |
| Holistic vs. Restoration-foc. | 0.07 | 1.18 | 0.80 | Large |
| Holistic vs. Preparedness-foc. | 0.08 | 1.37 | 0.83 | Large |
| Holistic vs. Adaptation-foc. | 0.07 | 1.19 | 0.80 | Large |
| Resistance vs. Supply | 0.01 | 0.16 | 0.55 | Small |
| Resistance vs. Restoration | 0.02 | 0.33 | 0.59 | Medium |
| Resistance vs. Preparedness | 0.03 | 0.52 | 0.64 | Medium |
| Resistance vs. Adaptation | 0.02 | 0.34 | 0.60 | Medium |

## C.5 Practical significance thresholds

| Metric | Small | Medium | Large |
|---|---|---|---|
| Abs. difference in R_system | <0.02 | 0.02-0.05 | >0.05 |
| Relative improvement (%) | <5% | 5%-10% | >10% |
| Cohen's d | <0.2 | 0.2-0.5 | >0.5 |
| CLES | <0.55 | 0.55-0.64 | >0.64 |
