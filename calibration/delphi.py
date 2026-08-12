"""
Bayesian hierarchical aggregation for Delphi expert elicitation (Eq. 15).

Implements simplified version of the Bayesian hierarchical model:
  theta_j ~ N(theta, sigma_j^2 + tau^2)
  theta ~ pi_0(theta)
  tau ~ half-Cauchy(0, 0.5)

Uses Gibbs sampling approximation (no external MCMC library needed).
"""

import numpy as np
from typing import List, Tuple, Dict
from calibration.parameters import PARAMETER_TABLE


def generate_synthetic_expert_data(n_experts: int = 15,
                                   rng: np.random.Generator = None) -> Dict:
    """
    Generate synthetic expert elicitation data matching paper description.

    15 experts across 4 categories:
    - Satellite operators (n=5, avg 14.2 yr)
    - Academic researchers (n=4, 11.8 yr)
    - Government representatives (n=3, 16.5 yr)
    - Security vendors (n=3, 9.3 yr)

    Returns dict with expert estimates for each parameter.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    categories = (
        [("operator", 14.2)] * 5 +
        [("academic", 11.8)] * 4 +
        [("government", 16.5)] * 3 +
        [("vendor", 9.3)] * 3
    )

    expert_data = {}
    for param in PARAMETER_TABLE:
        estimates = []
        for cat, experience in categories:
            # Category-specific bias
            bias = {"operator": 0.0, "academic": 0.05, "government": -0.03,
                    "vendor": 0.02}[cat]
            # Experience reduces variance
            var_scale = max(0.5, 1.0 - experience / 30.0)
            sigma = param.cv * param.value * var_scale
            est = rng.normal(param.value * (1 + bias), sigma)
            est = max(est, param.value * 0.1)  # Floor
            ci_width = sigma * 1.28  # 80% CI
            estimates.append({
                "category": cat,
                "experience": experience,
                "estimate": est,
                "ci_lower": est - ci_width,
                "ci_upper": est + ci_width,
                "sigma": sigma,
            })
        expert_data[param.symbol] = {
            "true_value": param.value,
            "estimates": estimates,
        }

    return expert_data


def bayesian_aggregate(estimates: List[float], sigmas: List[float],
                       prior_mean: float = None, prior_sigma: float = None,
                       n_samples: int = 4000, n_chains: int = 4,
                       rng: np.random.Generator = None) -> Dict:
    """
    Bayesian hierarchical aggregation via Gibbs sampling.

    Model:
      theta_j ~ N(theta, sigma_j^2 + tau^2)
      theta ~ N(prior_mean, prior_sigma^2)
      tau ~ half-Cauchy(0, 0.5)

    Parameters
    ----------
    estimates : list of float
        Expert point estimates.
    sigmas : list of float
        Expert-reported uncertainties.
    prior_mean : float
        Prior mean (default: mean of estimates).
    prior_sigma : float
        Prior std (default: 2 * std of estimates).
    n_samples : int
        MCMC samples per chain.
    n_chains : int
        Number of chains.

    Returns
    -------
    dict with posterior_mean, posterior_std, ci_80, samples, R_hat, ESS
    """
    if rng is None:
        rng = np.random.default_rng(42)

    n = len(estimates)
    y = np.array(estimates)
    s = np.array(sigmas)

    if prior_mean is None:
        prior_mean = np.mean(y)
    if prior_sigma is None:
        prior_sigma = 2.0 * np.std(y)

    all_samples = []
    for chain in range(n_chains):
        theta = rng.normal(np.mean(y), np.std(y))
        tau = abs(rng.standard_cauchy()) * 0.5
        samples = np.zeros(n_samples)

        for s_idx in range(n_samples):
            # Update theta given tau
            total_var = s**2 + tau**2
            weights = 1.0 / total_var
            w_sum = weights.sum() + 1.0 / prior_sigma**2
            weighted_mean = (np.sum(weights * y) + prior_mean / prior_sigma**2) / w_sum
            post_var = 1.0 / w_sum
            theta = rng.normal(weighted_mean, np.sqrt(post_var))

            # Update tau via MH step
            tau_prop = abs(tau + rng.normal(0, 0.1))
            log_lik_cur = -0.5 * np.sum((y - theta)**2 / (s**2 + tau**2) +
                                         np.log(s**2 + tau**2))
            log_lik_prop = -0.5 * np.sum((y - theta)**2 / (s**2 + tau_prop**2) +
                                          np.log(s**2 + tau_prop**2))
            # Half-Cauchy prior
            log_prior_cur = -np.log(1 + (tau / 0.5)**2)
            log_prior_prop = -np.log(1 + (tau_prop / 0.5)**2)

            if rng.uniform() < np.exp(min(0, (log_lik_prop + log_prior_prop) -
                                           (log_lik_cur + log_prior_cur))):
                tau = tau_prop

            samples[s_idx] = theta

        all_samples.append(samples)

    all_samples = np.array(all_samples)  # (n_chains, n_samples)
    combined = all_samples[:, n_samples // 2:].flatten()  # Discard warmup

    # R-hat diagnostic
    chain_means = all_samples[:, n_samples // 2:].mean(axis=1)
    chain_vars = all_samples[:, n_samples // 2:].var(axis=1)
    B = (n_samples // 2) * np.var(chain_means)
    W = np.mean(chain_vars)
    V_hat = ((n_samples // 2 - 1) * W + B) / (n_samples // 2)
    R_hat = np.sqrt(V_hat / W) if W > 0 else 1.0

    # Effective sample size (simple estimate)
    ESS = len(combined)  # Simplified

    return {
        "posterior_mean": np.mean(combined),
        "posterior_std": np.std(combined),
        "posterior_median": np.median(combined),
        "ci_80": (np.percentile(combined, 10), np.percentile(combined, 90)),
        "ci_95": (np.percentile(combined, 2.5), np.percentile(combined, 97.5)),
        "samples": combined,
        "R_hat": R_hat,
        "ESS": ESS,
    }


def run_full_delphi_aggregation(rng: np.random.Generator = None) -> Dict:
    """
    Run Bayesian aggregation for all parameters.

    Returns dict of parameter_symbol -> aggregation results.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    expert_data = generate_synthetic_expert_data(rng=rng)
    results = {}

    for param in PARAMETER_TABLE:
        data = expert_data[param.symbol]
        estimates = [e["estimate"] for e in data["estimates"]]
        sigmas = [e["sigma"] for e in data["estimates"]]

        agg = bayesian_aggregate(
            estimates, sigmas,
            prior_mean=param.value,
            prior_sigma=param.cv * param.value * 2,
            rng=rng
        )
        results[param.symbol] = {
            "parameter": param,
            "aggregation": agg,
        }

    return results


def leave_one_out_influence(estimates: List[float], sigmas: List[float],
                            rng: np.random.Generator = None) -> np.ndarray:
    """
    Leave-one-out analysis: influence of each expert on posterior mean.

    Returns array of influence scores (max should be < ~0.1).
    """
    if rng is None:
        rng = np.random.default_rng(42)

    full = bayesian_aggregate(estimates, sigmas, rng=rng)
    full_mean = full["posterior_mean"]

    influences = np.zeros(len(estimates))
    for i in range(len(estimates)):
        loo_est = [e for j, e in enumerate(estimates) if j != i]
        loo_sig = [s for j, s in enumerate(sigmas) if j != i]
        loo = bayesian_aggregate(loo_est, loo_sig, rng=rng)
        influences[i] = abs(loo["posterior_mean"] - full_mean) / full_mean

    return influences
