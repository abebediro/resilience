# Operational Constraints (Appendix P)

Three hard constraints bound the dynamics to physically and
economically admissible regimes.

## (C1) Bounded defensive budget

Per-dimension investment is drawn from a finite annual budget B(t) with
space-grade unit-cost premiums pi_i (`cost_functions.md`):

    sum_i( pi_i * V_i(t) ) <= B(t),   V_i(t) >= 0

so reallocation toward one dimension withdraws from others, making the
holistic-vs-specialized comparison a genuine constrained trade-off.
Orbital maintenance and retrofit growth (~5%/yr, restoration) is
charged against B(t).

**Not yet implemented** in the Python reference model
(`../03_code/python/resilience_model.py`) — that implementation runs
the unconstrained investment streams. Wiring in C1 requires adding a
budget-simplex projection step before the per-dimension investment
splits.

## (C2) Finite adversary resources

The adversary growth term is capped, converting unbounded escalation
into logistic escalation:

    dS_threat/dt = theta * R_system * (1 + phi*I_adversary)
                   * (1 - S_threat/A_max) - delta_threat * S_threat

with A_max in [0.85, 1.0], bounding the Red Queen tax rather than
letting it diverge. **This one is implemented** in the reference model
via the `use_adversary_cap` / `A_max` parameters.

## (C3) Satellite replacement cycles

A refresh operator resets hardware-bearing stocks at epochs {t_r} with
cycle length T_cyc in [5,15] years:

    S_i(t_r+) = (1 - zeta_i) * S_i(t_r-) + zeta_i * S_i^launch

zeta_i in [0,1] is the renewed fraction; replacement partially escapes
aging decay but re-incurs supply-chain exposure and pre-launch cost.
**Not yet implemented** in the Python reference model.

## Constraint-scenario effects on quantitative outputs (model-conditional)

| Constraint | Effect | Note |
|---|---|---|
| C1 budget simplex | Yr-10 holistic advantage 11.6% -> 9.4% | Sign preserved in 97% of runs |
| C2 adversary cap | Yr-20 Red Queen tax bounded ~4.3x | vs. unbounded ~5.1x |
| C2 adversary cap | Long-run erosion bounded <24% | Attacker-budget-limited ceiling |
| C3 replacement (T_cyc=5) | Mean resilience +4%, cost +22% | T_cyc becomes a decision variable |

All six robust findings persist under the constrained model;
constraints tighten quantitative trajectories without overturning
structural results.
