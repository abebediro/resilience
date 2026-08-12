# Cross-Background Prior Divergence Analysis (Appendix N)

To test whether expert background produced systematically different
priors, elicited values were decomposed by the four stakeholder
categories (operators, academics, government, vendors) and group-median
equality was tested with the Kruskal-Wallis H test (Bonferroni
correction across 17 parameters, family-wise alpha=0.05). Three
parameters diverged significantly; the remaining fourteen did not.
Because the divergent parameters are also high-sensitivity (see
`sensitivity_full.md`), their divergence is propagated through the
prior-perturbation analysis (core supplement §IV) rather than averaged
away.

## Parameters with significant between-group divergence

| Param. | Operator | Academic | Government | Vendor | H (p) | Driver |
|---|---|---|---|---|---|---|
| theta | 0.12 | 0.10 | **0.15** | 0.11 | 9.6 (.022) | Government higher |
| eta | 0.47 | 0.46 | 0.49 | **0.38** | 8.9 (.031) | Vendor lower |
| gamma | **0.98** | 0.85 | 0.90 | 0.86 | 8.1 (.044) | Operator higher |

All three significant at Bonferroni-corrected p<0.05. The remaining 14
parameters showed no significant between-group difference.

The Western-affiliation skew (12 of 15 experts) is bounded by the
prior-perturbation analysis (core supplement §IV), in which the
cross-background extremes feed the adverse-shift scenario.
