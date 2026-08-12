"""
Comparative strategy analysis (Table VI, Section V-D).

Compares baseline, single-dimension, and holistic investment strategies.
"""

import numpy as np
from typing import Dict, List
from models.system import SpaceResilienceModel
from calibration.parameters import ParameterSet, WEIGHT_SCENARIOS


STRATEGIES = [
    "baseline", "preparedness", "resistance", "restoration",
    "adaptation", "supply_chain", "holistic", "balanced",
]


def run_strategy_comparison(T: float = 20.0, dt: float = 0.25,
                            enhancement: float = 0.30,
                            params: ParameterSet = None) -> Dict:
    """
    Run all strategies and compare outcomes (Table VI).

    Parameters
    ----------
    T : float
        Horizon (years).
    enhancement : float
        Fractional boost for single-dimension strategies.
    params : ParameterSet
        Model parameters.

    Returns
    -------
    dict mapping strategy -> simulation results + summary metrics
    """
    if params is None:
        params = ParameterSet()

    model = SpaceResilienceModel(params)
    results = {}

    for strat in STRATEGIES:
        res = model.simulate_strategy(strat, enhancement=enhancement, T=T, dt=dt)
        # Extract key metrics
        yr5 = np.argmin(np.abs(res["time"] - 5))
        yr10 = np.argmin(np.abs(res["time"] - 10))
        yr15 = np.argmin(np.abs(res["time"] - 15))
        yr20 = np.argmin(np.abs(res["time"] - 20))

        res["metrics"] = {
            "yr5_R_eff": res["R_effective"][yr5],
            "yr10_R_eff": res["R_effective"][yr10],
            "yr15_R_eff": res["R_effective"][yr15],
            "yr20_R_eff": res["R_effective"][yr20],
            "yr5_R_sys": res["R_system"][yr5],
            "yr10_R_sys": res["R_system"][yr10],
            "yr15_R_sys": res["R_system"][yr15],
            "yr20_R_sys": res["R_system"][yr20],
        }
        results[strat] = res

    return results


def print_strategy_table(results: Dict):
    """Print strategy comparison table (Table VI format)."""
    baseline_yr10 = results["baseline"]["metrics"]["yr10_R_eff"]

    print("\nStrategy Performance Comparison")
    print("-" * 65)
    print(f"{'Strategy':<18} {'Yr 5':>8} {'Yr 10':>8} {'Yr 15':>8} "
          f"{'Yr 20':>8} {'Δ vs base':>10}")
    print("-" * 65)

    for strat in STRATEGIES:
        m = results[strat]["metrics"]
        delta = (m["yr10_R_eff"] - baseline_yr10) / baseline_yr10 * 100
        label = strat.replace("_", " ").title()
        print(f"{label:<18} {m['yr5_R_eff']:>8.3f} {m['yr10_R_eff']:>8.3f} "
              f"{m['yr15_R_eff']:>8.3f} {m['yr20_R_eff']:>8.3f} "
              f"{delta:>+9.1f}%")
    print("-" * 65)


def dimensional_enhancement_analysis(T: float = 20.0,
                                     enhancement: float = 0.30,
                                     params: ParameterSet = None) -> Dict:
    """
    Analyze sub-dimensional enhancements within each dimension.

    Tests 30% enhancement of each dimension's sub-variables.
    """
    if params is None:
        params = ParameterSet()

    model = SpaceResilienceModel(params)
    baseline = model.simulate(T=T)

    yr10 = np.argmin(np.abs(baseline["time"] - 10))
    baseline_R = baseline["R_system"][yr10]

    enhancements = {}

    # Test each dimension with boosted weight
    for i, dim in enumerate(["preparedness", "resistance", "restoration",
                             "adaptation", "supply_chain"]):
        w = params.get_weights()
        w[i] *= (1 + enhancement)
        w /= w.sum()
        res = model.simulate(T=T, weights=w)
        R_enhanced = res["R_system"][yr10]
        gain = (R_enhanced - baseline_R) / baseline_R * 100
        enhancements[dim] = {
            "R_system_yr10": R_enhanced,
            "gain_pct": gain,
            "trajectory": res["R_system"],
        }

    return {
        "baseline_R_yr10": baseline_R,
        "enhancements": enhancements,
        "time": baseline["time"],
    }


def ahp_weight_sensitivity(T: float = 20.0, params: ParameterSet = None) -> Dict:
    """
    Test robustness across 4 AHP weight scenarios.

    Returns Friedman test statistic and per-scenario results.
    """
    if params is None:
        params = ParameterSet()

    scenario_results = {}

    for name, weights in WEIGHT_SCENARIOS.items():
        model = SpaceResilienceModel(params)
        res = model.simulate(T=T, weights=weights / weights.sum())
        yr10 = np.argmin(np.abs(res["time"] - 10))
        scenario_results[name] = {
            "R_system_yr10": res["R_system"][yr10],
            "R_effective_yr10": res["R_effective"][yr10],
            "trajectory": res["R_system"],
            "time": res["time"],
        }

    return scenario_results


def compute_super_additivity(params: ParameterSet = None) -> Dict:
    """
    Empirically verify super-additivity (Theorem 1, Property 4).

    Compares joint enhancement to sum of individual enhancements.
    """
    if params is None:
        params = ParameterSet()

    model = SpaceResilienceModel(params)
    T = 15.0
    baseline = model.simulate(T=T)
    yr10 = np.argmin(np.abs(baseline["time"] - 10))
    R_base = baseline["R_system"][yr10]

    # Individual enhancements
    delta = 0.30
    sum_individual = 0.0
    individual_gains = {}

    for i, dim in enumerate(["preparedness", "resistance", "restoration",
                             "adaptation", "supply_chain"]):
        w = params.get_weights()
        w[i] *= (1 + delta)
        w /= w.sum()
        res = model.simulate(T=T, weights=w)
        gain = res["R_system"][yr10] - R_base
        sum_individual += gain
        individual_gains[dim] = gain

    # Joint enhancement (holistic)
    res_joint = model.simulate_strategy("holistic", enhancement=delta, T=T)
    joint_gain = res_joint["R_system"][yr10] - R_base

    return {
        "baseline_R": R_base,
        "individual_gains": individual_gains,
        "sum_individual": sum_individual,
        "joint_gain": joint_gain,
        "super_additive": joint_gain > sum_individual,
        "super_additive_margin": joint_gain - sum_individual,
        "ratio": joint_gain / max(sum_individual, 1e-10),
    }
