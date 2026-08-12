# Investment Cost Functions (Appendix J)

## J.1 Space component cost premiums

| Component type | Terrestrial cost | Space cost | Premium | Source |
|---|---|---|---|---|
| Commercial off-the-shelf (COTS) | $1.00 | $1.80 | +80% | BAE Systems catalog 2021 |
| Radiation-hardened (30 krad) | $1.00 | $2.20 | +120% | Microchip price list 2022 |
| Radiation-hardened (100 krad) | $1.00 | $3.50 | +250% | Microchip price list 2022 |
| Radiation-hardened (300 krad) | $1.00 | $5.00 | +400% | Honeywell data sheet |
| MIL-STD-883 qualified | $1.00 | $1.60 | +60% | Cobham data 2021 |
| Space-grade encryption module | $1.00 | $1.40 | +40% | Vendor quotes (n=3) |
| FPGA with radiation tolerance | $1.00 | $2.20 | +120% | Xilinx space-grade catalog |
| Secure boot hardware | $1.00 | $2.50 | +150% | Microchip |
| Hardware security module (HSM) | $1.00 | $3.00 | +200% | Vendor quotes |
| Rad-hardened memory | $1.00 | $4.00 | +300% | BAE Systems |

## J.2 Cost function validation against known program costs

| Program | Model ($M) | Actual ($M) | Error | Source |
|---|---|---|---|---|
| GPS III (security segment) | 124 | 131 | -5.3% | GAO report |
| MUOS (ground segment) | 87 | 82 | +6.1% | Navy budget |
| Commercial GEO (typical) | 12 | 11.5 | +4.3% | Operator data |
| SmallSat LEO constellation | 4.2 | 4.5 | -6.7% | Industry avg. |
| Military SATCOM terminal | 2.8 | 2.6 | +7.7% | DoD procurement |
| Rad-hard processor dev. | 15 | 16 | -6.3% | BAE Systems |

Average absolute error: **5.7%**

## J.3 Learning curve parameters by dimension

| Dimension | Learning rate | Progress ratio | Half cost |
|---|---|---|---|
| Preparedness (software) | 85% | 0.85 | 4.3 doublings |
| Resistance (hardware) | 92% | 0.92 | 8.3 doublings |
| Restoration (software) | 87% | 0.87 | 5.0 doublings |
| Adaptation (process) | 90% | 0.90 | 6.6 doublings |
| Supply Chain (mgmt.) | 88% | 0.88 | 5.4 doublings |
