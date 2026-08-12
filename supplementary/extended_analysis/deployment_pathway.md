# Pathway to Closed-Loop Deployment (Appendix R)

## Three-stage deployment

**Stage 1 (instantiation):** an operator initializes the five stocks
from an internal posture assessment using the coding rubric
(`../02_incident_dataset/coding_manual.md`), inheriting calibrated
priors.

**Stage 2 (assimilation):** as telemetry, incident, and recovery
records accrue, parameters update online via sequential Bayesian
inference (particle/ensemble filtering), progressively replacing expert
priors with operator-specific posteriors.

**Stage 3 (closed-loop validation):** a registered prospective protocol
(2025-2027) issues sealed, dated predictions of resilience trajectories
and recovery times for participating missions, scored against
subsequent outcomes, converting retrodiction into out-of-sample,
telemetry-grounded validation.

## Deployment stages and data requirements

| Stage | Mechanism | Data requirement |
|---|---|---|
| 1 Instantiation | Posture coding -> initial stocks; calibrated priors | One-time assessment (coding rubric) |
| 2 Assimilation | Sequential Bayesian / ensemble filtering | Ongoing telemetry, incident, recovery logs |
| 3 Closed-loop validation | Registered sealed predictions vs. outcomes | Prospective mission cohort, 2025-2027 |

**Telemetry concession:** raw attack traces and recovery logs are
largely classified or proprietary and unobtainable for an open study,
which is why the load-bearing claims are structural and
calibration-independent, and all quantitative magnitudes are reported
as model-conditional.
