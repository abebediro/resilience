"""
Copula-based correlated failure analysis (Section VI-C).

Evaluates the Gaussian copula extension (Eq. 2) across
correlation values rho in [0, 0.6].
"""

import numpy as np
from typing import Dict, List
from models.composition import copula_resilience, system_resilience
from models.system import SpaceResilienceModel
from calibration.parameters import ParameterSet


def copula_sweep(rho_values: np.ndarray = None,
                 n_samples: int = 10000,
                 eval_year: float = 10.0,
                 params: ParameterSet = None,
                 rng: np.random.Generator = None) -> Dict:
    """
    Sweep copula correlation parameter and measure resilience impact.

    Parameters
    ----------
    rho_values : array
        Correlation values to test.
    n_samples : int
        MC samples per rho value (paper uses 50,000).
    eval_year : float
        Year at which to evaluate.

    Returns
    -------
    dict with rho, R_system, R_independent, delta_pct arrays
    """
    if rho_values is None:
        rho_values = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    if params is None:
        params = ParameterSet()
    if rng is None:
        rng = np.random.default_rng(42)

    # Run baseline to get state at eval_year
    model = SpaceResilienceModel(params)
    res = model.simulate(T=eval_year + 1, dt=0.25)
    idx = np.argmin(np.abs(res["time"] - eval_year))
    state = res["states"][idx]

    S_prep, S_resist, S_restore, S_adapt, S_supply, _ = state

    # Independence baseline
    R_indep = system_resilience(S_prep, S_resist, S_restore, S_adapt,
                                S_supply, params.get_xi())

    results_rho = []
    for rho in rho_values:
        R_cop = copula_resilience(
            S_prep, S_resist, S_restore, S_adapt, S_supply,
            rho=rho, xi=params.get_xi(), n_samples=n_samples, rng=rng
        )
        delta = (R_cop - R_indep) / R_indep * 100
        results_rho.append({
            "rho": rho,
            "R_copula": R_cop,
            "R_independent": R_indep,
            "delta_pct": delta,
            "overestimation_pct": -delta,
        })

    return {
        "rho_values": rho_values,
        "results": results_rho,
        "state_at_eval": state,
        "eval_year": eval_year,
    }


def copula_strategy_impact(rho: float = 0.4,
                           n_samples: int = 5000,
                           params: ParameterSet = None,
                           rng: np.random.Generator = None) -> Dict:
    """
    Evaluate how copula correlation affects strategy rankings.

    Tests whether holistic strategy remains superior under correlation.
    """
    if params is None:
        params = ParameterSet()
    if rng is None:
        rng = np.random.default_rng(42)

    strategies = ["baseline", "resistance", "supply_chain", "holistic"]
    model = SpaceResilienceModel(params)

    results = {}
    for strat in strategies:
        res = model.simulate_strategy(strat, T=15.0)
        idx10 = np.argmin(np.abs(res["time"] - 10))
        state = res["states"][idx10]

        R_indep = system_resilience(state[0], state[1], state[2], state[3],
                                    state[4], params.get_xi())
        R_cop = copula_resilience(state[0], state[1], state[2], state[3],
                                  state[4], rho=rho, xi=params.get_xi(),
                                  n_samples=n_samples, rng=rng)
        results[strat] = {
            "R_independent": R_indep,
            "R_copula": R_cop,
            "reduction_pct": (R_indep - R_cop) / R_indep * 100,
        }

    # Check if holistic still dominates
    holistic_still_best = all(
        results["holistic"]["R_copula"] >= results[s]["R_copula"]
        for s in strategies if s != "holistic"
    )

    return {
        "rho": rho,
        "strategy_results": results,
        "holistic_still_best": holistic_still_best,
    }


def print_copula_results(sweep: Dict):
    """Print copula sweep results table."""
    print(f"\nCopula Analysis at Year {sweep['eval_year']:.0f}")
    print("-" * 55)
    print(f"{'rho':>6} {'R_copula':>10} {'R_indep':>10} {'Overest.':>10}")
    print("-" * 55)
    for r in sweep["results"]:
        print(f"{r['rho']:>6.2f} {r['R_copula']:>10.4f} "
              f"{r['R_independent']:>10.4f} {r['overestimation_pct']:>+9.1f}%")
    print("-" * 55)
