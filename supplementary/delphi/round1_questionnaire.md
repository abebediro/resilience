# Delphi Round 1 Questionnaire (Complete)

**Space Cybersecurity Resilience Parameters**

## Instructions

Thank you for participating in this expert elicitation. Your judgments
will calibrate a System Dynamics model of space cybersecurity resilience.

For each parameter, please provide:
- Your best point estimate (single most likely value)
- An 80% credible interval [5th, 95th percentile is requested; the
  central 80% is retained]
- Brief rationale for your estimate

**Interpreting 80% credible intervals:** Example: if you estimate
`k_prep = 0.05` with 80% CI `[0.03, 0.08]`, you believe there is a 10%
chance the true value is below 0.03, an 80% chance it lies between 0.03
and 0.08, and a 10% chance it is above 0.08.

**Seed (calibration) variables:** Eleven seed questions of known value
are interleaved below (marked `[SEED]`). These are used to compute each
respondent's statistical accuracy and informativeness for Cooke
performance weighting. Please answer them with the same interval format;
do not look up the answers.

**Guidance material:** Refer to the accompanying "Parameter Definitions
and Examples" document for the physical interpretation, literature-based
reference ranges, worked examples, and space-specific considerations for
each item. Each question is phrased operationally; a symbol-to-question
map is provided in the appendix to that document so that no respondent
reasons over raw model symbols.

---

## Section 1 — Capability Decay
*(annual fractional loss without reinvestment)*

- **Q1** `[k_prep]` Without renewal, what annual fraction of a
  threat-intelligence / preparedness advantage becomes obsolete? (yr⁻¹)
- **Q2** `[k_resist]` Without renewal, what annual fraction of a
  hardening / resistance capability is lost to obsolescence and
  component aging? (yr⁻¹)
- **Q3** `[k_restore]` Annual fractional decay of an autonomous-restoration
  capability as software and procedures age? (yr⁻¹)
- **Q4** `[k_adapt]` Annual fractional decay of institutional learning /
  adaptation capacity? (yr⁻¹)
- **Q5** `[k_supply]` Annual fractional decay of supply-chain assurance
  as vendors, parts, and provenance turn over? (yr⁻¹)
- **Q6** `[SEED]` Published GPS modernization cycle: average years
  between successive operational GPS satellite block upgrades? (years)

## Section 2 — Environmental Sensitivity
*(multipliers on decay)*

- **Q7** `[alpha]` Latency sensitivity: relative increase in decay per
  unit sqrt(round-trip delay in seconds)? (dimensionless)
- **Q8** `[beta]` Inaccessibility penalty: relative increase in
  restoration difficulty per unit normalized orbital distance, exponent
  applied separately? (dimensionless)
- **Q9** `[gamma]` Radiation sensitivity: relative increase in
  resistance decay per unit normalized cumulative dose? (dimensionless)
- **Q10** `[gamma_T]` Thermal-cycling sensitivity: relative increase in
  resistance decay per unit normalized thermal amplitude? (dimensionless)
- **Q11** `[mu]` Preparedness superlinear exponent offset (decay scales
  as S^(1+mu))? (dimensionless)
- **Q12** `[SEED]` Total ionizing dose at which a typical COTS CMOS
  device shows first functional degradation? (krad)
- **Q13** `[SEED]` GEO round-trip communication latency? (milliseconds)

## Section 3 — Adversary Co-evolution

- **Q14** `[theta]` Adversary learning rate: speed at which a capable
  adversary recovers a lost advantage after a defensive improvement
  (half-recovery time converted to yr⁻¹)?
- **Q15** `[phi]` Adversary capability amplification from external
  (state) investment? (dimensionless, [0,1])
- **Q16** `[delta_threat]` Annual obsolescence rate of attack techniques?
  (yr⁻¹)
- **Q17** `[gamma_threat]` Maximum fraction of effective resilience an
  adapted adversary can erode? (dimensionless, [0,1])
- **Q18** `[S_threat_min]` Minimum baseline adversary capability that
  always persists? (dimensionless, [0,1])
- **Q19** `[SEED]` Reported time from public disclosure to
  in-the-wild exploitation for a typical high-severity vulnerability?
  (days)

## Section 4 — Supply Chain

- **Q20** `[eta]` Supply-chain risk sensitivity: relative increase in
  supply-chain decay per unit aggregate risk index? (dimensionless)
- **Q21** `[nu]` Supply-chain complexity sensitivity: relative increase
  in decay per unit structural complexity (per additional tier)?
  (dimensionless)
- **Q22** `[xi_prep]` Fraction of PREPAREDNESS effectiveness lost when
  supply-chain security is zero? ([0,1])
- **Q23** `[xi_resist]` Fraction of RESISTANCE effectiveness lost when
  supply-chain security is zero? ([0,1])
- **Q24** `[xi_restore]` Fraction of RESTORATION effectiveness lost when
  supply-chain security is zero? ([0,1])
- **Q25** `[xi_adapt]` Fraction of ADAPTATION effectiveness lost when
  supply-chain security is zero? ([0,1])
- **Q26** `[SEED]` Typical number of distinct supplier tiers in a
  modern satellite bus program? (count)

## Section 5 — Adaptation Amplification and Learning

- **Q27** `[psi_prep]` Amplification of preparedness investment per
  unit adaptation capacity (log-time scaled)? ([0,1])
- **Q28** `[psi_res]` Amplification of resistance investment per unit
  adaptation? ([0,1])
- **Q29** `[psi_rest]` Amplification of restoration investment per unit
  adaptation? ([0,1])
- **Q30** `[psi_supply]` Amplification of supply-chain investment per
  unit adaptation? ([0,1])
- **Q31** `[tau_prep]` Learning time constant for preparedness (years
  to ~63% of max)?
- **Q32** `[tau_res]` Learning time constant for resistance? (years)
- **Q33** `[tau_rest]` Learning time constant for restoration? (years)
- **Q34** `[tau_supply]` Learning time constant for supply chain?
  (years)
- **Q35** `[SEED]` Published organizational "learning curve" progress
  ratio for complex hardware (cost reduction per doubling of cumulative
  units)? (%)

## Section 6 — Initial Conditions
*(typical pre-launch posture, new program)*

- **Q36** `[S_prep(0)]` Initial preparedness capability (0–1)?
- **Q37** `[S_resist(0)]` Initial resistance capability (0–1)?
- **Q38** `[S_restore(0)]` Initial restoration capability (0–1)?
- **Q39** `[S_adapt(0)]` Initial adaptation capability (0–1)?
- **Q40** `[S_supply(0)]` Initial supply-chain security (0–1)?

## Section 7 — Relative Importance
*(for AHP weights)*

- **Q41** Provide pairwise importance judgments (Saaty 1–9 scale) for
  the five dimensions {Preparedness, Resistance, Restoration,
  Adaptation, Supply Chain} with respect to overall mission
  cybersecurity resilience.

---
*End of Round 1. Estimated completion time: 35–45 minutes.*
