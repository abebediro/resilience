"""
System resilience composition via conditional probability (Eq. 1).

Implements:
- Sequential defense-in-depth composition
- Supply chain modulation of effective capacities
- Copula extension for correlated failures (Eq. 2)
- Properties from Theorem 1 and Lemma 1
"""

import numpy as np
from scipy import stats


def supply_chain_modulation(R_i: float, xi_i: float, S_supply: float) -> float:
    """
    Compute effective capacity modulated by supply chain (Eq. below Eq.1).

    R_i^eff(t) = R_i(t) * [1 - xi_i * (1 - S_supply(t))]

    Parameters
    ----------
    R_i : float
        Raw dimensional capacity.
    xi_i : float
        Supply chain cascade coefficient for dimension i.
    S_supply : float
        Current supply chain security level.

    Returns
    -------
    float
        Effective capacity after supply chain modulation.
    """
    return R_i * (1.0 - xi_i * (1.0 - S_supply))


def system_resilience(R_prep: float, R_resist: float, R_restore: float,
                      R_adapt: float, S_supply: float,
                      xi: np.ndarray = None) -> float:
    """
    Compute system resilience via conditional probability composition (Eq. 1).

    Uses compact form: R_system = 1 - prod(1 - R_i^eff)

    Parameters
    ----------
    R_prep, R_resist, R_restore, R_adapt : float
        Raw dimensional capacities in [0, 1].
    S_supply : float
        Supply chain security level in [0, 1].
    xi : np.ndarray, optional
        Cascade coefficients [xi_prep, xi_resist, xi_restore, xi_adapt].
        Default: [0.42, 0.68, 0.31, 0.25].

    Returns
    -------
    float
        System resilience in [0, 1].
    """
    if xi is None:
        xi = np.array([0.42, 0.68, 0.31, 0.25])

    R_raw = np.array([R_prep, R_resist, R_restore, R_adapt])
    R_eff = np.array([supply_chain_modulation(R_raw[i], xi[i], S_supply)
                      for i in range(4)])

    # Compact form (Eq. 3): R_system = 1 - prod(1 - R_i^eff)
    R_sys = 1.0 - np.prod(1.0 - np.clip(R_eff, 0, 1))
    return np.clip(R_sys, 0, 1)


def system_resilience_from_state(state: np.ndarray, xi: np.ndarray = None) -> float:
    """
    Compute system resilience from state vector.

    Parameters
    ----------
    state : np.ndarray
        [S_prep, S_resist, S_restore, S_adapt, S_supply, S_threat]
    xi : np.ndarray, optional
        Cascade coefficients.

    Returns
    -------
    float
        System resilience.
    """
    return system_resilience(state[0], state[1], state[2], state[3],
                             state[4], xi)


def copula_resilience(R_prep: float, R_resist: float, R_restore: float,
                      R_adapt: float, S_supply: float, rho: float,
                      xi: np.ndarray = None, n_samples: int = 10000,
                      rng: np.random.Generator = None) -> float:
    """
    Copula-extended system resilience (Eq. 2).

    Uses Gaussian copula with equicorrelation rho to model
    common-cause failures.

    Parameters
    ----------
    rho : float
        Common-cause failure correlation in [0, 1].
    n_samples : int
        Monte Carlo samples for copula integration.
    rng : np.random.Generator
        Random number generator.

    Returns
    -------
    float
        Copula-adjusted system resilience.
    """
    if rho == 0:
        return system_resilience(R_prep, R_resist, R_restore, R_adapt,
                                 S_supply, xi)
    if rng is None:
        rng = np.random.default_rng()
    if xi is None:
        xi = np.array([0.42, 0.68, 0.31, 0.25])

    R_raw = np.array([R_prep, R_resist, R_restore, R_adapt])
    R_eff = np.array([supply_chain_modulation(R_raw[i], xi[i], S_supply)
                      for i in range(4)])
    R_eff = np.clip(R_eff, 1e-10, 1.0 - 1e-10)

    # Build equicorrelation matrix
    corr = np.full((4, 4), rho)
    np.fill_diagonal(corr, 1.0)

    # Generate correlated normal samples
    Z = rng.multivariate_normal(np.zeros(4), corr, size=n_samples)
    U = stats.norm.cdf(Z)  # Uniform marginals

    # For each sample, dimension i fails if U_i > R_i^eff
    failures = U > R_eff[np.newaxis, :]  # (n_samples, 4)
    all_fail = failures.all(axis=1)
    R_sys = 1.0 - all_fail.mean()

    return float(np.clip(R_sys, 0, 1))


def supply_chain_leverage(R_raw: np.ndarray, xi: np.ndarray,
                          S_supply: float) -> float:
    """
    Compute supply chain leverage factor L (Lemma 1).

    L = sum_j (prod_{k!=j} q_k) * R_j * xi_j / max_i{...}

    Returns
    -------
    float
        Leverage factor L >= 1.
    """
    R_eff = np.array([supply_chain_modulation(R_raw[i], xi[i], S_supply)
                      for i in range(4)])
    q = 1.0 - np.clip(R_eff, 0, 1)

    channels = np.zeros(4)
    for j in range(4):
        prod_others = np.prod(q[np.arange(4) != j])
        channels[j] = prod_others * R_raw[j] * xi[j]

    total = channels.sum()
    max_single = channels.max()
    if max_single == 0:
        return 1.0
    return total / max_single


def verify_composition_properties(R_eff: np.ndarray) -> dict:
    """
    Verify Theorem 1 properties for given effective capacities.

    Returns dict of booleans for each property.
    """
    R_eff = np.clip(R_eff, 0, 1)
    q = 1.0 - R_eff
    R_sys = 1.0 - np.prod(q)

    results = {}

    # (1) Order invariance
    perms = [np.random.permutation(R_eff) for _ in range(100)]
    R_perms = [1.0 - np.prod(1.0 - p) for p in perms]
    results["order_invariant"] = np.allclose(R_perms, R_sys)

    # (1) Monotonicity: dR/dR_i >= 0
    monot = all(np.prod(q[np.arange(4) != i]) >= 0 for i in range(4))
    results["monotone"] = monot

    # (3) Bounds
    results["bounded"] = 0 <= R_sys <= 1

    # (2) Joint concavity: off-diagonal Hessian <= 0
    concave = True
    for i in range(4):
        for j in range(i + 1, 4):
            H_ij = -np.prod(q[np.array([k for k in range(4) if k not in (i, j)])])
            if H_ij > 1e-12:
                concave = False
    results["jointly_concave"] = concave

    # (4) Super-additivity check
    delta = 0.05
    R_sys_base = 1.0 - np.prod(q)
    sum_individual = 0
    for i in range(4):
        R_mod = R_eff.copy()
        R_mod[i] += delta
        R_mod = np.clip(R_mod, 0, 1)
        sum_individual += (1.0 - np.prod(1.0 - R_mod)) - R_sys_base

    R_joint = R_eff + delta
    R_joint = np.clip(R_joint, 0, 1)
    R_sys_joint = 1.0 - np.prod(1.0 - R_joint)
    delta_joint = R_sys_joint - R_sys_base

    results["super_additive"] = delta_joint > sum_individual

    return results
