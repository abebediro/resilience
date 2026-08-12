"""
Prior-perturbation robustness (Appendix Q.1): adverse joint shift setting
the three cross-background-divergent parameters (Appendix N) to their
extremes: government-high theta=0.15, vendor-low eta=0.38, operator-high
gamma=0.98. Verifies policy conclusions survive.
"""

import numpy as np
from copy import deepcopy
from typing import Dict
from calibration.parameters import ParameterSet, ADVERSE_PRIOR_SHIFT
from models.system import SpaceResilienceModel
from models.composition import supply_chain_leverage


def run_adverse_shift(base: ParameterSet = None) -> Dict:
    if base is None:
        base = ParameterSet()

    adverse = deepcopy(base)
    for k, v in ADVERSE_PRIOR_SHIFT.items():
        setattr(adverse, k, v)

    results = {}
    for label, p in [("baseline", base), ("adverse_joint_shift", adverse)]:
        m = SpaceResilienceModel(p)
        b = m.simulate_strategy("baseline", T=15)
        h = m.simulate_strategy("holistic", T=15)
        i10 = np.argmin(np.abs(b["time"] - 10))
        adv = (h["R_effective"][i10] - b["R_effective"][i10]) / b["R_effective"][i10] * 100
        erosion = (b["R_system"][i10] - b["R_effective"][i10]) / b["R_system"][i10] * 100
        st = b["states"][i10]
        L = supply_chain_leverage(np.array([st[0], st[1], st[2], st[3]]),
                                  p.get_xi(), st[4])
        results[label] = {"holistic_advantage_yr10": adv,
                          "red_queen_erosion_yr10": erosion,
                          "supply_chain_leverage": L}

    a = results["adverse_joint_shift"]
    results["conclusions_survive"] = {
        "holistic_still_positive": a["holistic_advantage_yr10"] > 0,
        "leverage_still_gt_1": a["supply_chain_leverage"] > 1.0,
        "erosion_still_gt_10pct": a["red_queen_erosion_yr10"] > 10.0,
    }
    return results
