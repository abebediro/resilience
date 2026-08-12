# Epistemic Provenance of Equations and Parameters (Appendix O)

Classification of each model component as a **mechanistic assumption**
(functional form chosen on theoretical grounds or by AICc form-selection),
a **data-estimable/constrained** quantity, or an **expert prior**,
separating what rests on observation from what rests on assumption.

| Component | Status | Basis |
|---|---|---|
| Resilience composition | Mechanistic | Defense-in-depth / reliability theory |
| Super-additivity, L>=1 | Mechanistic (proved) | Any positive parameterization (core supplement §I) |
| Latency form sqrt(tau) | Data-selected | AICc vs. alternatives |
| Radiation exponent 1.9 | Data-constrained | TID range 1.8-2.2 (CMOS literature) |
| Restoration exponent 1.4 | Data-constrained | 12 paired recovery events |
| k_resist, k_prep, gamma, alpha, beta, k_supply | Data-estimable | Practically identifiable (core supplement §II) |
| theta, xi_resist | Mixed | High-sens.; data-constrained, prior-informed |
| phi, delta_threat, gamma_threat, mu, k_restore | Expert prior | Structural but not practical |
| gamma_T, eta, nu | Expert prior | Weakly ident.; fixed in primary model |
| Human-factor multiplier | Assumed prior | Static Beta; simplification |
| Geopolitical shock; C1-C3 | Scenario | Stress-tests, not fitted (`operational_constraints.md`) |

## Level separability

The five dimensions are **normalized capability stocks** X_i in [0,1]
(fractions of an idealized best-practice capability), not raw
heterogeneous quantities; normalization is the deliberate commensuration
step. Level collapse is prevented structurally by direct separability
(dF_in,i/dS_j = dF_out,i/dS_j = 0 for i != j); cross-level influence
enters only through two named channels (adaptation amplification;
supply-chain modulation). The disaggregation experiment
(`additional_derivations.md` L.10) bounds aggregation error at +/-10%.
