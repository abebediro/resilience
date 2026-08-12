# Incident Coding Manual

Each incident received two coding layers, both coded independently by
two raters with third-rater adjudication of disagreements exceeding
0.25. Inter-rater reliability: Cohen's kappa = 0.82 (see
`../validation/model_selection.md` for the full confusion matrix and
per-subset breakdown).

1. **Overall severity** (1–5) — used for incident description and
   stratification (see `severity_scale` below).
2. **Anchored per-dimension implication score** in [0,1] — used as the
   direct model input (`coding_matrix.csv`). Anchors below.

## Severity scale

| Level | Description | Examples | Coding rules |
|---|---|---|---|
| 1 | Minor, <1 day, limited scope | Brief interruption, isolated impact | <24h; <100 users; no permanent damage; no data loss |
| 2 | Moderate, 1–7 days, regional | Regional outage, recoverable loss | 1–7 days; regional; some recovery; minor damage |
| 3 | Significant, >7 days, national | Multi-day national outage | >7 days; national; component replacement |
| 4 | Major, >30 days, international | International disruption | >30 days; multi-country; permanent damage; mission degraded |
| 5 | Catastrophic, permanent loss | Total asset loss, mission failure | Satellite disabled; mission termination; irrecoverable loss |

## Anchored per-dimension implication scale

Applied independently to each of the five dimensions for every incident.

| Score | Anchor |
|---|---|
| 0.00 | Dimension not implicated; no evidence of relevance to the incident. |
| 0.25 | Marginally implicated; minor or transient degradation, no causal role. |
| 0.50 | Materially implicated; partial failure contributing to but not determining the outcome. |
| 0.75 | Strongly implicated; major failure substantially driving the outcome. |
| 1.00 | Dimension fully overwhelmed; near-total loss of the represented capability. |

## Primary dimension assignment rules

| Dimension | Primary if... | Indicators |
|---|---|---|
| Preparedness | Failure to anticipate/detect despite available intelligence | Missed warnings; ignored disclosures; no situational awareness; known pattern unrecognized |
| Resistance | Attack succeeded despite controls present | Control bypass; vulnerability exploited; insufficient hardening; authentication/encryption defeated |
| Restoration | Controls failed and recovery also failed | No backup/recovery; extended downtime; manual intervention; no spares |
| Adaptation | Repeat of known pattern / failure to learn | Recurrence; re-exploited vulnerability; lessons not applied |
| Supply Chain | Component-level compromise | Counterfeit parts; vendor breach; third-party/software supply-chain attack; hardware trojan |

## Secondary dimension assignment rules

| Dimension | Secondary if... |
|---|---|
| Preparedness | Attack novel but anticipatable; intelligence existed but unshared |
| Resistance | Controls present but insufficient; hardening could have prevented |
| Restoration | Recovery possible but slow; procedures existed but not followed |
| Adaptation | Organization learned but too slowly; partial learning |
| Supply Chain | Supply chain contributed but not root cause |

## Coding convention (mapping severity to the model-input matrix)

For each incident:
- **Primary dimension** receives a severity-scaled anchor:
  severity 1 -> 0.25, severity 2 -> 0.50, severity 3 -> 0.75,
  severity 4-5 -> 1.00.
- **Secondary dimension** (where present) receives one anchor step
  below the primary, floored at 0.25.
- **Remaining dimensions** receive 0.00 unless incident notes indicate
  ambient involvement.

## Pre-registered reconstruction success criterion

A reconstruction is successful if and only if, initialized from the
coded pre-incident posture, the model's 95% predictive interval
contains the observed value on each available outcome axis (attack
success, breach extent, recovery time) *and* the corpus-aggregate fit
satisfies r >= 0.6 and MAPE <= 20%. These thresholds were fixed before
evaluation. On the disclosed corpus the criterion is met at r = 0.78
and MAPE = 12.4%, with 91% of incidents individually within their 95%
predictive interval.
