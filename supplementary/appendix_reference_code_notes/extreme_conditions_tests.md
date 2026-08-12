# Extreme Condition Tests (TC01–TC08)

Boundary-adequacy tests confirming the model behaves sensibly at
parameter extremes (Appendix B.1 / I.3 of the supplementary appendices).

| ID | Condition | Expected behavior | Actual result | Pass |
|---|---|---|---|---|
| TC01 | Zero investment (`base=0`) | All stocks decay to zero asymptotically | Prep 0.15->0.02, Resist 0.20->0.03, Restore 0.12->0.01, Adapt 0.08->0.01, Supply 0.10->0.01 at Year 20 | Yes |
| TC02 | Maximum resistance only (`resist_weight=1.0`, others=0) | High short-term R, then decline as adversary adapts | R_eff peaks at 0.81 at Year 8, declines to 0.73 at Year 20 | Yes |
| TC03 | Deep space latency (`latency=10`) | Prep and Adapt severely degraded | Prep outflow +358%, Adapt outflow +358% | Yes |
| TC04 | Perfect supply chain (`SupplyChain_0=1.0`, `supply_inflow=0`) | All dimensions show 15-30% higher effective capacity | Resist +34%, Prep +21%, Restore +15%, Adapt +12% | Yes |
| TC05 | High adversary learning (`theta=0.30`) | R_effective peaks then declines after Year 8 | Peak 0.71 at Year 8, declines to 0.64 at Year 20 | Yes |
| TC06 | No adversary learning (`theta=0`) | No Red Queen effect | R_effective = R_system throughout | Yes |
| TC07 | Maximum radiation (`gamma=2.0`) | Resistance collapses | Resist 0.31 by Year 10 (vs 0.91 baseline) | Yes |
| TC08 | Zero supply chain (`SupplyChain_0=0`, `supply_inflow=0`) | All dimensions severely degraded | Effective Resist 0.06, Prep 0.09 at Year 0 | Yes |

All eight extreme-condition tests pass under the parameterization as
specified in the paper. Note the calibration caveat in `KNOWN_ISSUES.md`
regarding the baseline (non-extreme) trajectory in this reference
implementation.
