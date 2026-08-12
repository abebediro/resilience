"""
Historical incident dataset - the actual coded corpus from the paper.

Sources:
- Appendix H.3: disclosed incident catalog (63 of 70; 7 member-confidential
  incidents are withheld at item level per Space-ISAC disclosure terms)
- Appendix S.4: anchored per-dimension implication scores in [0,1]
  (the model-input matrix), coded per the S.3 convention, kappa = 0.82

Dimension order everywhere: [Prep, Res, Rest, Adapt, Supply]
"""

import numpy as np

# (id, year, primary, secondary, severity 1-5)
CATALOG = [
    (1, 2007, "Res", "Prep", 4), (2, 2007, "Res", None, 3),
    (3, 2008, "Res", None, 4), (4, 2009, "Rest", "Res", 3),
    (5, 2009, "Res", None, 3), (6, 2009, "Rest", "Res", 2),
    (7, 2010, "Res", None, 3), (8, 2011, "Prep", "Rest", 3),
    (9, 2011, "Res", "Prep", 2), (10, 2012, "Res", None, 2),
    (11, 2012, "Supply", "Res", 3), (12, 2012, "Prep", None, 1),
    (13, 2013, "Res", None, 3), (14, 2013, "Res", "Prep", 4),
    (15, 2013, "Res", "Rest", 3), (16, 2014, "Res", None, 3),
    (17, 2014, "Res", "Prep", 4), (18, 2014, "Res", None, 2),
    (19, 2015, "Res", "Prep", 4), (20, 2015, "Res", "Rest", 3),
    (21, 2015, "Res", None, 3), (22, 2016, "Res", "Adapt", 4),
    (23, 2016, "Res", None, 2), (24, 2016, "Supply", "Res", 3),
    (25, 2017, "Res", None, 2), (26, 2017, "Res", "Prep", 2),
    (27, 2017, "Res", "Supply", 3), (28, 2018, "Res", None, 3),
    (29, 2018, "Rest", "Res", 2), (30, 2018, "Res", "Adapt", 2),
    (31, 2018, "Res", "Prep", 3), (32, 2019, "Res", None, 2),
    (33, 2019, "Res", None, 1), (34, 2019, "Adapt", "Res", 3),
    (35, 2019, "Res", "Prep", 3), (36, 2020, "Res", None, 1),
    (37, 2020, "Rest", "Prep", 3), (38, 2020, "Supply", "Prep", 4),
    (39, 2020, "Res", "Prep", 4), (40, 2020, "Res", None, 3),
    (41, 2021, "Rest", "Prep", 3), (42, 2021, "Res", None, 2),
    (43, 2021, "Rest", "Res", 2), (44, 2021, "Supply", "Res", 4),
    (45, 2021, "Prep", "Res", 2), (46, 2021, "Res", None, 3),
    (47, 2021, "Res", "Rest", 2), (48, 2021, "Res", "Prep", 2),
    (49, 2022, "Supply", "Res", 5), (50, 2022, "Res", None, 4),
    (51, 2022, "Res", "Rest", 3), (52, 2022, "Res", None, 3),
    (53, 2022, "Supply", "Res", 4), (54, 2022, "Res", "Prep", 3),
    (55, 2022, "Res", None, 2), (56, 2022, "Rest", "Res", 2),
    (57, 2022, "Supply", "Prep", 1), (58, 2022, "Rest", "Res", 2),
    (59, 2022, "Res", None, 3), (60, 2022, "Res", "Supply", 3),
    (61, 2022, "Rest", "Res", 2), (62, 2022, "Supply", "Prep", 4),
    (63, 2022, "Prep", "Res", 2),
]

# Appendix S.4 model-input matrix: [Prep, Res, Rest, Adapt, Supply]
IMPLICATION_MATRIX = np.array([
    [0.75, 1.00, 0.00, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.00, 1.00, 0.00, 0.00, 0.00], [0.00, 0.50, 0.75, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.00], [0.00, 0.25, 0.50, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.00], [0.75, 0.00, 0.50, 0.00, 0.00],
    [0.25, 0.50, 0.00, 0.00, 0.00], [0.00, 0.50, 0.00, 0.00, 0.00],
    [0.00, 0.50, 0.00, 0.00, 0.75], [0.25, 0.00, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.00], [0.75, 1.00, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.50, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.75, 1.00, 0.00, 0.00, 0.00], [0.00, 0.50, 0.00, 0.00, 0.00],
    [0.75, 1.00, 0.00, 0.00, 0.00], [0.00, 0.75, 0.50, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.75, 0.00],
    [0.00, 0.50, 0.00, 0.00, 0.00], [0.00, 0.50, 0.00, 0.00, 0.75],
    [0.00, 0.50, 0.00, 0.00, 0.00], [0.25, 0.50, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.50], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.00, 0.25, 0.50, 0.00, 0.00], [0.00, 0.50, 0.00, 0.25, 0.00],
    [0.50, 0.75, 0.00, 0.00, 0.00], [0.00, 0.50, 0.00, 0.00, 0.00],
    [0.00, 0.25, 0.00, 0.00, 0.00], [0.00, 0.50, 0.00, 0.75, 0.00],
    [0.50, 0.75, 0.00, 0.00, 0.00], [0.00, 0.25, 0.00, 0.00, 0.00],
    [0.50, 0.00, 0.75, 0.00, 0.00], [0.75, 0.00, 0.00, 0.00, 1.00],
    [0.75, 1.00, 0.00, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.50, 0.00, 0.75, 0.00, 0.00], [0.00, 0.50, 0.00, 0.00, 0.00],
    [0.00, 0.25, 0.50, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 1.00],
    [0.50, 0.25, 0.00, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.00, 0.50, 0.25, 0.00, 0.00], [0.25, 0.50, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 1.00], [0.00, 1.00, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.50, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 1.00], [0.50, 0.75, 0.00, 0.00, 0.00],
    [0.00, 0.50, 0.00, 0.00, 0.00], [0.00, 0.25, 0.50, 0.00, 0.00],
    [0.25, 0.00, 0.00, 0.00, 0.25], [0.00, 0.25, 0.50, 0.00, 0.00],
    [0.00, 0.75, 0.00, 0.00, 0.00], [0.00, 0.75, 0.00, 0.00, 0.50],
    [0.00, 0.25, 0.50, 0.00, 0.00], [0.75, 0.00, 0.00, 0.00, 1.00],
    [0.50, 0.25, 0.00, 0.00, 0.00],
])

YEARS = np.array([c[1] for c in CATALOG])
SEVERITIES = np.array([c[4] for c in CATALOG], dtype=float)
PRIMARY = [c[2] for c in CATALOG]
SECONDARY = [c[3] for c in CATALOG]


def get_dataset():
    """Return the coded corpus as arrays.

    Returns dict:
      implications: (63,5) per-dimension scores in [0,1]
      severity_norm: (63,) severity/5 in [0,1]
      years, primary, secondary
    """
    return {
        "implications": IMPLICATION_MATRIX.copy(),
        "severity": SEVERITIES.copy(),
        "severity_norm": SEVERITIES / 5.0,
        "years": YEARS.copy(),
        "primary": list(PRIMARY),
        "secondary": list(SECONDARY),
        "n": len(CATALOG),
        "kappa": 0.82,
        "note": "63 disclosed of 70; 7 member-confidential withheld (App. H)",
    }
