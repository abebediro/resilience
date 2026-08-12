# Additional Derivations (Appendix L, extended)

The proofs of Theorem 1 (resilience composition), Theorem 2 (Red Queen
equilibrium), Corollary 1 (Red Queen tax), Lemma 1 (supply-chain
leverage), and the well-posedness argument are in the **core
supplement** (§I) — they're needed by reviewers to verify the main-text
claims and stay under the page limit. Everything below is supporting
material that did not need to travel with the manuscript.

## L.2 Phase transition conditions

Phase transitions occur when the dominant eigenvalue of the full-system
Jacobian crosses the imaginary axis. Numerical computation yields three
critical thresholds:

| Parameter | Critical | Calibrated | Margin | Behavior beyond |
|---|---|---|---|---|
| theta | 0.18 | 0.12 | 50% | Sustained oscillation / decline |
| xi_resist | 0.75 | 0.68 | 10% | Catastrophic cascade failure |
| psi_prep | 0.15 | 0.28 | 87% | Failure to escape foundation |

xi_resist has the tightest margin (10%) — the parameter closest to a
qualitative behavior change under the calibrated model.

## L.4 Proof of Theorem (Generalized Stock Dynamics from Axioms)

Axiom 1 (Monotone Decay) gives outflow = f(X)g(E) with f non-decreasing
in X and g non-decreasing in stressors E; Taylor expansion gives
f(X) = delta*X + o(X) and superposition gives g(E) = 1 + sum_j(gamma_j*E_j).
Axiom 2 (Diminishing Returns) gives inflow = I_X(t) * eta_X(X,t) with
eta_X = eta_max - (eta_max - eta_0)*exp(-t/tau). Axiom 5
(Supply-Chain Propagation) gives the factor [1 - xi_X*(1-C)]. Axiom 3
(Cross-Dimensional Dependence) enters through C and through the
adversary dynamics of Axiom 4. The general stock equation is the
minimal form satisfying all axioms.

## L.5 Proof of Theorem (Universality of Logistic Growth)

With dX/dt = I*eta(X) - delta(X)*X and the mean value theorem,
dX/dt = c - b*X - a*X^2 for a = delta'(xi), b = I*eta'(xi) + delta(0),
c = I*eta(0). This Riccati equation has closed-form logistic solution;
the actual trajectory is bounded between the logistic solutions using
extremal a, b, c over [0, X_max].

## L.6 Proof of Theorem (Phase Transition Existence)

Linearizing the coupled (R, A) system, eigenvalues satisfy
lambda^2 - tr(J)*lambda + det(J) = 0. By Perron-Frobenius for
cooperative systems the dominant eigenvalue is real and simple; its
sign changes when tr(J) = dR_dot/dR + dA_dot/dA = 0. With
dA_dot/dA = -delta_threat and the chain rule for dR_dot/dR, the trace
is negative at t=0 and positive for large t, so by the intermediate
value theorem a transition time t* exists.

## L.10 Disaggregation experiment results

Sub-models for resistance disaggregating access controls, encryption
strength, radiation-hardened components, and communication security
were each given their own decay dynamics and cost structure, then
re-aggregated.

| Metric | Value |
|---|---|
| Mean difference in R_system at year 10 | 0.023 (2.7%) |
| 90% of differences within | +/-0.042 (+/-4.9%) |
| Maximum observed difference | 0.087 (10.1%) |
| Correlation (aggregated vs. disaggregated) | r=0.93 |

Aggregation error is bounded within +/-10% for most scenarios,
supporting the reduced-form treatment for strategic analysis.

## L.11 Correlated failure sensitivity

A Gaussian copula imposed positive correlation rho across dimensional
failures. rho=0.4 is the headline case; rho=0.3 is shown for
comparison. Strategy rankings are preserved throughout; extreme
correlation (rho>0.7) would be required to reverse findings,
implausible given the orthogonal selection criteria.

| Metric | Independent | rho=0.3 | rho=0.4 |
|---|---|---|---|
| Holistic strategy advantage | 11.6% | 9.8% | 8.5% |
| 90% CI for advantage | [9.8,13.4] | [7.2,12.4] | [6.1,11.3] |
| Red Queen tax at year 20 | 400% | 385% | 372% |

## L.12 Agent-based model comparison

A simplified NetLogo implementation with 1,000 heterogeneous
defender/adversary agents was compared with the SD model.

| Metric | System Dynamics | Agent-Based |
|---|---|---|
| Computational time (10,000 runs) | 4 hours | 47 hours |
| Coefficient of variation | 12% | 18% |
| Parameter identifiability | High | Low |
| Qualitative agreement | --- | Yes |
| Quantitative difference | --- | +/-15% |

Both approaches reproduce logistic growth and Red Queen erosion; ABM
offers no advantage for the strategic research questions while
imposing substantial computational and identifiability costs.

## L.13 Derivation of the Red Queen tax formula

Effective resilience is
R_eff(t) = R_tech(t) * [1 - gamma_threat*(S_threat(t)-S_threat_min)/(1-S_threat_min)].
To hold R_eff = R*, required technical resilience is
R_tech_req(t) = R* / [1 - gamma_threat*(S_threat(t)-S_threat_min)/(1-S_threat_min)].
With the learning-curve production function I = I_0 * f^-1(R_tech), the
tax is
tau(t) = f^-1(R_tech_req(t)) / f^-1(R*) - 1.
Under the finite-adversary resource cap (`operational_constraints.md`,
C2), S_threat is bounded by A_max, capping the year-20 tax at ~4.3x
(~330%) versus the unbounded ~5.1x (~400%).

## L.14 Environmental degradation multipliers

**Radiation.** From cumulative-damage models dD/dt = k*Dose(t)^n with
n~1.9 for CMOS, integrating with Dose proportional to t gives the
normalized form M_rad = 1 + gamma*R_rad^1.9.

**Thermal cycling.** From Coffin-Manson N_f = C*(Delta T)^-m with
m~2.3 for solder joints, cumulative degradation D proportional to
N*(Delta T)^m normalizes to M_thermal = 1 + gamma_T*Delta T.

**Latency.** From Weber-Fechner scaling, decision quality degrades with
sqrt(tau), giving M_latency = 1 + alpha*sqrt(tau).
