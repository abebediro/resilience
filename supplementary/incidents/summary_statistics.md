# Incident Dataset — Summary Statistics (n = 70)

All statistics below are computed over the full corpus of 70 coded
incidents: 63 disclosed (`incident_catalog.csv`) plus 7 Space-ISAC
member-confidential incidents (see `NOTE_confidential.md`).

## By year and severity

| Year | S1 | S2 | S3 | S4 | S5 | Total | Mean Sev. |
|---|---|---|---|---|---|---|---|
| 2007 | 0 | 0 | 1 | 1 | 0 | 2 | 3.5 |
| 2008 | 0 | 0 | 0 | 1 | 0 | 1 | 4.0 |
| 2009 | 0 | 1 | 2 | 0 | 0 | 3 | 2.7 |
| 2010 | 0 | 0 | 1 | 0 | 0 | 1 | 3.0 |
| 2011 | 0 | 1 | 1 | 0 | 0 | 2 | 2.5 |
| 2012 | 0 | 0 | 2 | 1 | 0 | 3 | 3.3 |
| 2013 | 0 | 0 | 2 | 1 | 0 | 3 | 3.3 |
| 2014 | 0 | 1 | 1 | 1 | 0 | 3 | 3.0 |
| 2015 | 0 | 0 | 2 | 1 | 0 | 3 | 3.3 |
| 2016 | 0 | 1 | 2 | 0 | 0 | 3 | 2.7 |
| 2017 | 0 | 2 | 1 | 0 | 0 | 3 | 2.3 |
| 2018 | 1 | 1 | 2 | 0 | 0 | 4 | 2.3 |
| 2019 | 1 | 2 | 2 | 0 | 0 | 5 | 2.2 |
| 2020 | 1 | 2 | 2 | 2 | 0 | 7 | 2.7 |
| 2021 | 1 | 4 | 3 | 2 | 0 | 10 | 2.6 |
| 2022 | 0 | 4 | 6 | 5 | 2 | 17 | 3.3 |
| **Total** | **4** | **19** | **30** | **15** | **2** | **70** | **2.9** |

## By primary dimension

| Dimension | Count | Percentage | Mean severity |
|---|---|---|---|
| Resistance | 39 | 55.7% | 2.8 |
| Restoration | 12 | 17.1% | 2.4 |
| Preparedness | 8 | 11.4% | 2.1 |
| Mixed/Multiple | 6 | 8.6% | 3.2 |
| Supply Chain | 3 | 4.3% | 4.3 |
| Adaptation | 2 | 2.9% | 2.0 |

## Secondary dimension appearances

| Dimension | Count | Pct. of incidents |
|---|---|---|
| Resistance | 18 | 25.7% |
| Preparedness | 10 | 14.3% |
| Restoration | 8 | 11.4% |
| Supply Chain | 5 | 7.1% |
| Adaptation | 3 | 4.3% |
| None | 26 | 37.1% |

## By region

| Region | Count | Percentage |
|---|---|---|
| North America | 24 | 34.3% |
| Europe | 22 | 31.4% |
| Asia-Pacific | 12 | 17.1% |
| Middle East | 6 | 8.6% |
| Global/Multiple | 4 | 5.7% |
| South America | 2 | 2.9% |

## By target type

| Target type | Count | Percentage |
|---|---|---|
| Ground Station | 24 | 34.3% |
| Communications (SATCOM) | 22 | 31.4% |
| Positioning (GPS/GNSS) | 12 | 17.1% |
| Satellite (direct) | 8 | 11.4% |
| Supply Chain | 4 | 5.7% |

## Model validation against the dataset

| Metric | Actual | Predicted | Correlation |
|---|---|---|---|
| Mean severity (2007–2012) | 3.2 | 3.1 | r = 0.82 |
| Mean severity (2013–2017) | 2.7 | 2.8 | r = 0.79 |
| Mean severity (2018–2022) | 2.6 | 2.5 | r = 0.85 |
| Resistance incidents (%) | 55.7% | 52.3% | — |
| Supply chain incidents (%) | 4.3% | 5.1% | — |
| Restoration incidents (%) | 17.1% | 18.2% | — |

Model-predicted risk is derived from the inverse of R_effective.
