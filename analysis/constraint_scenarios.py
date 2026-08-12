"""
Operational-constraint scenarios C1-C3 (Section constraint_scenarios /
Appendix P): budget simplex, adversary resource cap, replacement cycles.
"""

import numpy as np
from copy import deepcopy
from typing import Dict
from calibration.parameters import ParameterSet
from models.system import SpaceResilienceModel


def _holistic_advantage(params: ParameterSet, T=15.0) -> float:
    m = SpaceResilienceModel(params)
    b = m.simulate_strategy("baseline", T=T)
    h = m.simulate_strategy("holistic", T=T)
    i10 = np.argmin(np.abs(b["time"] - 10))
    return (h["R_effective"][i10] - b["R_effective"][i10]) / b["R_effective"][i10] * 100


def run_constraint_scenarios(base: ParameterSet = None) -> Dict:
    """Compare unconstrained baseline against C1, C2 (tight cap), C3."""
    if base is None:
        base = ParameterSet()
    out = {}

    # Reference (default: cap at calibrated A_max=0.975, no budget/replacement)
    out["reference"] = {"holistic_advantage_yr10": _holistic_advantage(base)}

    # C1: budget simplex with premiums (zero-sum reallocation)
    p1 = deepcopy(base); p1.constrain_budget = True
    out["C1_budget"] = {"holistic_advantage_yr10": _holistic_advantage(p1)}

    # C2: tight adversary cap (A_max = 0.85, lower bound of stated range)
    p2 = deepcopy(base); p2.use_adversary_cap = True; p2.A_max = 0.85
    m2 = SpaceResilienceModel(p2)
    r2 = m2.simulate(T=20)
    i20 = -1
    erosion20 = (r2["R_system"][i20] - r2["R_effective"][i20]) / r2["R_system"][i20] * 100
    tax20 = r2["R_system"][i20] / max(r2["R_effective"][i20], 1e-9)
    # Uncapped comparison
    pu = deepcopy(base); pu.use_adversary_cap = False
    ru = SpaceResilienceModel(pu).simulate(T=20)
    tax20_unbounded = ru["R_system"][i20] / max(ru["R_effective"][i20], 1e-9)
    out["C2_adversary_cap"] = {
        "erosion_yr20_pct": erosion20,
        "erosion_bounded_below_24pct": erosion20 < 24.0,
        "tax_multiplier_yr20_capped": tax20,
        "tax_multiplier_yr20_unbounded": tax20_unbounded,
    }

    # C3: replacement cycles T_cyc = 5 vs no replacement
    p3 = deepcopy(base); p3.T_cyc = 5.0
    r3 = SpaceResilienceModel(p3).simulate(T=20)
    r0 = SpaceResilienceModel(base).simulate(T=20)
    out["C3_replacement"] = {
        "mean_resilience_no_replacement": float(np.mean(r0["R_effective"])),
        "mean_resilience_Tcyc5": float(np.mean(r3["R_effective"])),
        "resilience_gain_pct": (np.mean(r3["R_effective"]) - np.mean(r0["R_effective"]))
                               / np.mean(r0["R_effective"]) * 100,
        "cost_increase_pct": (r3["cumulative_cost"][-1] - r0["cumulative_cost"][-1])
                             / r0["cumulative_cost"][-1] * 100,
    }
    return out
