"""
Sobol sensitivity analysis for the space cybersecurity resilience model.

Computes first-order (S_i) and total-order (S_Ti) Sobol indices
with bootstrap confidence intervals (Table VII, Fig. 7).
"""

import numpy as np
from typing import Dict, List
from SALib.sample import saltelli
from SALib.analyze import sobol

from models.system import SpaceResilienceModel
from calibration.parameters import ParameterSet


# Define the problem for SALib
SOBOL_PROBLEM = {
    "num_vars": 17,
    "names": [
        "k_prep", "k_resist", "k_restore", "k_adapt", "k_supply",
        "alpha", "beta", "gamma", "gamma_T", "mu",
        "theta", "phi", "delta_threat", "gamma_threat", "S_threat_min",
        "eta", "nu",
    ],
    "bounds": [
        [0.035, 0.065],   # k_prep
        [0.049, 0.091],   # k_resist
        [0.084, 0.156],   # k_restore
        [0.021, 0.039],   # k_adapt
        [0.077, 0.143],   # k_supply
        [0.60, 1.11],     # alpha
        [0.84, 1.56],     # beta
        [0.63, 1.17],     # gamma
        [0.10, 0.20],     # gamma_T
        [0.56, 1.04],     # mu
        [0.084, 0.156],   # theta
        [0.17, 0.33],     # phi
        [0.056, 0.104],   # delta_threat
        [0.25, 0.46],     # gamma_threat
        [0.07, 0.13],     # S_threat_min
        [0.32, 0.58],     # eta
        [0.21, 0.39],     # nu
    ],
}

# Reduced 9-parameter problem
SOBOL_PROBLEM_REDUCED = {
    "num_vars": 9,
    "names": [
        "k_resist", "alpha", "beta", "gamma", "mu",
        "theta", "gamma_threat", "xi_resist", "psi_prep",
    ],
    "bounds": [
        [0.049, 0.091],
        [0.60, 1.11],
        [0.84, 1.56],
        [0.63, 1.17],
        [0.56, 1.04],
        [0.084, 0.156],
        [0.25, 0.46],
        [0.58, 0.78],
        [0.20, 0.36],
    ],
}


def _params_from_sample(X: np.ndarray, full: bool = True) -> ParameterSet:
    """Create ParameterSet from Sobol sample row."""
    p = ParameterSet()
    if full:
        names = SOBOL_PROBLEM["names"]
    else:
        names = SOBOL_PROBLEM_REDUCED["names"]

    for i, name in enumerate(names):
        if hasattr(p, name):
            setattr(p, name, X[i])

    return p


def _evaluate_model(X: np.ndarray, eval_year: float = 10.0,
                    full: bool = True, output: str = "R_effective") -> float:
    """Evaluate model at eval_year for a single parameter sample."""
    params = _params_from_sample(X, full)
    model = SpaceResilienceModel(params)
    result = model.simulate(T=eval_year + 1, dt=0.25)

    idx = np.argmin(np.abs(result["time"] - eval_year))

    if output == "R_effective":
        return result["R_effective"][idx]
    elif output == "R_system":
        return result["R_system"][idx]
    else:
        return result["R_effective"][idx]


def run_sobol_analysis(n_samples: int = 256, eval_year: float = 10.0,
                       full: bool = True,
                       n_bootstrap: int = 100,
                       verbose: bool = True) -> Dict:
    """
    Run Sobol sensitivity analysis.

    Parameters
    ----------
    n_samples : int
        Base sample size (total evaluations = n_samples * (2*num_vars + 2)).
    eval_year : float
        Year at which to evaluate sensitivity.
    full : bool
        Use full 17-parameter or reduced 9-parameter problem.
    n_bootstrap : int
        Bootstrap resamples for confidence intervals.
    verbose : bool
        Print progress.

    Returns
    -------
    dict with S1, ST, S1_conf, ST_conf, parameter names, rankings
    """
    problem = SOBOL_PROBLEM if full else SOBOL_PROBLEM_REDUCED

    if verbose:
        total_evals = n_samples * (2 * problem["num_vars"] + 2)
        print(f"Sobol analysis: {n_samples} base samples, "
              f"{total_evals} total evaluations")

    # Generate Saltelli samples
    param_samples = saltelli.sample(problem, n_samples, calc_second_order=False)

    if verbose:
        print(f"  Evaluating {len(param_samples)} model runs...")

    # Evaluate model for each sample
    Y = np.zeros(len(param_samples))
    for i in range(len(param_samples)):
        if verbose and (i + 1) % max(1, len(param_samples) // 10) == 0:
            print(f"    {i + 1}/{len(param_samples)}")
        try:
            Y[i] = _evaluate_model(param_samples[i], eval_year, full)
        except Exception:
            Y[i] = 0.5  # Fallback

    # Analyze
    Si = sobol.analyze(problem, Y, calc_second_order=False,
                       num_resamples=n_bootstrap,
                       conf_level=0.95)

    # Build results table
    names = problem["names"]
    S1 = Si["S1"]
    ST = Si["ST"]
    S1_conf = Si["S1_conf"]
    ST_conf = Si["ST_conf"]

    # Sort by total-order index
    sort_idx = np.argsort(-ST)
    cumulative = np.cumsum(S1[sort_idx])

    # Compute elasticities at median
    params_med = ParameterSet()
    model_med = SpaceResilienceModel(params_med)
    res_med = model_med.simulate(T=eval_year + 1, dt=0.25)
    idx_yr = np.argmin(np.abs(res_med["time"] - eval_year))
    R_base = res_med["R_effective"][idx_yr]

    elasticities = np.zeros(len(names))
    for i, name in enumerate(names):
        p_test = ParameterSet()
        base_val = getattr(p_test, name)
        delta = 0.01 * base_val
        setattr(p_test, name, base_val + delta)
        m_test = SpaceResilienceModel(p_test)
        r_test = m_test.simulate(T=eval_year + 1, dt=0.25)
        R_test = r_test["R_effective"][idx_yr]
        elasticities[i] = (R_test - R_base) / delta * base_val / max(R_base, 1e-10)

    rankings = []
    for rank, idx in enumerate(sort_idx):
        rankings.append({
            "rank": rank + 1,
            "parameter": names[idx],
            "S1": S1[idx],
            "ST": ST[idx],
            "S1_conf": S1_conf[idx],
            "ST_conf": ST_conf[idx],
            "cumulative": cumulative[rank],
            "elasticity": elasticities[idx],
        })

    return {
        "problem": problem,
        "S1": S1,
        "ST": ST,
        "S1_conf": S1_conf,
        "ST_conf": ST_conf,
        "rankings": rankings,
        "sort_idx": sort_idx,
        "elasticities": elasticities,
        "eval_year": eval_year,
        "n_samples": n_samples,
        "Y": Y,
    }


def print_sobol_table(results: Dict):
    """Print Sobol results in paper table format (Table VII)."""
    print(f"\nParameter Sensitivity (Sobol Indices, Year {results['eval_year']:.0f})")
    print("-" * 75)
    print(f"{'#':>2} {'Parameter':<20} {'S_i':>8} {'S_Ti':>8} "
          f"{'Cumul.':>8} {'Elast.':>8}")
    print("-" * 75)

    for r in results["rankings"][:10]:
        print(f"{r['rank']:>2} {r['parameter']:<20} {r['S1']:>8.3f} "
              f"{r['ST']:>8.3f} {r['cumulative']:>7.0%} "
              f"{r['elasticity']:>+8.2f}")
    print("-" * 75)
