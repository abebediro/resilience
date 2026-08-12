"""
Adversary dynamics and the Red Queen effect.

Implements:
- Adversary capability evolution (Eq. 11)
- Effective resilience erosion (Eq. 12)
- Geopolitical shock extension (Eq. 13)
- Red Queen equilibrium (Theorem 2)
- Red Queen tax (Corollary 1)
"""

import numpy as np


def dS_threat_dt(S_threat: float, R_system: float, theta: float,
                 phi: float, I_adversary: float,
                 delta_threat: float) -> float:
    """
    Adversary capability evolution (Eq. 11).

    dS_threat/dt = theta * R_system * (1 + phi * I_adversary) - delta_threat * S_threat

    Key mechanism: R_system appears in growth term — stronger defenses
    stimulate more sophisticated attacks.
    """
    growth = theta * R_system * (1.0 + phi * I_adversary)
    decay = delta_threat * S_threat
    return growth - decay


def effective_resilience(R_system: float, S_threat: float,
                         gamma_threat: float, S_threat_min: float) -> float:
    """
    Effective resilience after adversary erosion (Eq. 12).

    R_system^eff = R_system * [1 - gamma_threat * (S_threat - S_min)/(1 - S_min)]
    """
    if S_threat <= S_threat_min:
        return R_system
    erosion = gamma_threat * (S_threat - S_threat_min) / (1.0 - S_threat_min)
    return R_system * max(0.0, 1.0 - erosion)


def geopolitical_shock_investment(t: float, I_baseline: float = 1.0,
                                  scenario: str = "steady") -> float:
    """
    Adversary investment with geopolitical shocks (Eq. 13).

    Scenarios:
    - "steady": I = I_baseline (no shocks)
    - "single_escalation": Major spike at t=5, decay lambda=0.3
    - "sustained": Periodic shocks every 3 years
    """
    if scenario == "steady":
        return I_baseline

    elif scenario == "single_escalation":
        t_shock = 5.0
        delta_I = 2.0 * I_baseline
        lam = 0.3
        if t >= t_shock:
            return I_baseline + delta_I * np.exp(-lam * (t - t_shock))
        return I_baseline

    elif scenario == "sustained":
        delta_I = 0.5 * I_baseline
        lam = 0.1
        period = 3.0
        total = I_baseline
        n_shocks = int(t / period)
        for k in range(1, n_shocks + 1):
            t_k = k * period
            if t >= t_k:
                total += delta_I * np.exp(-lam * (t - t_k))
        return total

    return I_baseline


def red_queen_equilibrium(theta: float, phi: float, I_bar: float,
                          delta_threat: float, gamma_threat: float,
                          S_threat_min: float) -> dict:
    """
    Compute Red Queen equilibrium (Theorem 2).

    Returns dict with equilibrium values and stability analysis.
    """
    kappa = theta * (1.0 + phi * I_bar) / delta_threat

    # Contraction condition
    contraction = gamma_threat * kappa / (1.0 - S_threat_min)
    is_contractive = contraction < 1.0

    # Fixed-point iteration to find equilibrium
    R_sys = 0.85  # Initial guess
    for _ in range(100):
        S_threat_star = kappa * R_sys
        erosion = gamma_threat * max(0, S_threat_star - S_threat_min) / (1.0 - S_threat_min)
        R_sys_new = R_sys * (1.0 - erosion)
        # Self-consistency: effective resilience determines R_system which determines threat
        # We solve for the fixed point of the effective resilience
        R_sys = 0.5 * R_sys + 0.5 * (R_sys_new / max(1e-10, 1.0 - erosion))
        R_sys = np.clip(R_sys, 0, 1)

    S_threat_star = kappa * R_sys

    # Stability eigenvalue
    dR_dS = -R_sys * gamma_threat / (1.0 - S_threat_min)
    eigenvalue = theta * (1.0 + phi * I_bar) * dR_dS - delta_threat
    is_stable = eigenvalue < 0

    # Stability condition
    stability_lhs = delta_threat
    stability_rhs = theta * (1 + phi * I_bar) * R_sys * gamma_threat / (1 - S_threat_min)

    return {
        "kappa": kappa,
        "S_threat_star": S_threat_star,
        "R_system_star": R_sys,
        "R_eff_star": effective_resilience(R_sys, S_threat_star,
                                           gamma_threat, S_threat_min),
        "contraction_factor": contraction,
        "is_contractive": is_contractive,
        "eigenvalue": eigenvalue,
        "is_stable": is_stable,
        "stability_margin": stability_lhs - stability_rhs,
    }


def red_queen_tax(R_target_eff: float, theta: float, phi: float,
                  I_bar: float, delta_threat: float,
                  gamma_threat: float) -> float:
    """
    Compute Red Queen investment tax (Corollary 1).

    Additional investment proportional to:
    gamma_threat * theta * (1+phi*I_bar) / delta_threat * R_target / (1-gamma_threat)
    """
    coeff = gamma_threat * theta * (1.0 + phi * I_bar) / delta_threat
    return coeff * R_target_eff / (1.0 - gamma_threat)


def red_queen_erosion_pct(R_technical: float, S_threat: float,
                          gamma_threat: float, S_threat_min: float) -> float:
    """Compute erosion percentage between technical and effective resilience."""
    R_eff = effective_resilience(R_technical, S_threat, gamma_threat, S_threat_min)
    if R_technical == 0:
        return 0.0
    return (R_technical - R_eff) / R_technical * 100.0


def dS_threat_dt_capped(S_threat: float, R_system: float, theta: float,
                        phi: float, I_adversary: float,
                        delta_threat: float, A_max: float) -> float:
    """
    Resource-capped adversary evolution (Eq. adversary_cap, constraint C2).

    dS/dt = theta*R*(1+phi*I)*(1 - S/A_max) - delta*S

    Converts unbounded escalation into saturating (logistic) escalation
    with ceiling A_max in [0.85, 1.0], bounding the Red Queen tax.
    """
    growth = theta * R_system * (1.0 + phi * I_adversary) * max(0.0, 1.0 - S_threat / A_max)
    return growth - delta_threat * S_threat
