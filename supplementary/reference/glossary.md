# Glossary of Terms (Appendix M)

**Adaptation** — Meta-capability for organizational learning that
amplifies the effectiveness of all other dimensions through better
processes, after-action reviews, and knowledge management.

**Adversary Co-evolution** — Process by which threat capability grows
in response to defensive improvement, producing a Red Queen dynamic.

**AHP** — Analytic Hierarchy Process; derives dimension weights from
pairwise comparisons, used to set baseline investment allocation.

**Cascade Coefficient (xi_i)** — Fraction of dimension i's
effectiveness lost when supply-chain security is zero.

**Complementarity** — Property whereby combined dimensions produce
super-additive returns, so holistic strategies outperform specialized
ones.

**Credible Interval** — Range containing the true parameter value with
80% probability, derived from Delphi elicitation.

**Decay Rate (k_i)** — Annual fractional loss of capability without
reinvestment.

**Delphi Method** — Structured multi-round expert elicitation with
controlled feedback, used to calibrate parameters.

**Effective Resilience** — Operational resilience remaining after
adversary-adaptation erosion.

**Environmental Amplification (A_env,i)** — Multiplier on decay from
space-specific stressors (radiation, latency, inaccessibility, thermal
cycling).

**Holistic Strategy** — Balanced investment across all five dimensions;
outperforms specialized strategies by roughly 8-16% (model-conditional).

**Identifiability** — Whether data can constrain a parameter to a
finite, prior-narrowing interval; distinct from sensitivity.

**Leverage Factor (L)** — Ratio of supply-chain elasticity to
direct-dimension elasticity; structurally >=1, averaging ~1.47.

**Logistic Growth** — S-curve trajectory with foundation, acceleration,
and maturation phases.

**Meta-Capacity** — Second-order capability modifying first-order
effectiveness; Adaptation is the only meta-capacity.

**Phase Transition** — Shift in the dominant feedback loop: Foundation
-> Acceleration -> Maturation -> Red Queen.

**Preparedness** — Anticipatory capacity (threat intelligence,
technology awareness, architectural foresight) with superlinear decay.

**Red Queen Effect** — Continuous investment required to maintain
position as adversaries adapt.

**Red Queen Tax** — Additional investment to hold effective resilience
constant as adversary capability grows; bounded under the
finite-adversary cap (`../04_extended_analysis/operational_constraints.md`).

**Resistance** — Active countermeasures (controls, radiation hardening,
communication security); highest AHP weight (0.462).

**Restoration** — Self-healing capability; most sensitive to adaptation
amplification (psi_rest=0.35).

**Robustness Classification** — Categorization of findings by Monte
Carlo consistency: >90% ROBUST, 70-90% MODERATE, <70% FRAGILE.

**Sensitivity** — Share of output variance attributable to a parameter
(Sobol); distinct from identifiability.

**Sobol Sensitivity** — Variance-based method identifying theta,
xi_resist, k_resist as most influential.

**Supply Chain Security** — Component integrity, vendor security,
provenance; cascades via xi_i, highest on Resistance (xi_resist=0.68).

**System Resilience** — Composite from the conditional-probability
composition of dimensional success, in [0,1].

**Well-Posedness** — Existence of a unique, bounded, non-negative
solution for all time (Picard-Lindelof; core supplement §I).
