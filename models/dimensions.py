"""
Stock-flow equations for the five resilience dimensions.

Each dimension follows: dS_i/dt = F_in,i(t) - F_out,i(t) * A_env,i(t)
(Equation 4 in the paper)
"""

import numpy as np


def adaptation_enhancement(V_i: float, S_adapt: float, psi_i: float,
                           t: float, tau_i: float) -> float:
    """
    Adaptation-enhanced investment effectiveness (Eq. 9).

    V_i^eff(t) = V_i(t) * [1 + psi_i * S_adapt(t) * ln(1 + t/tau_i)]

    Parameters
    ----------
    V_i : float
        Base investment flow.
    S_adapt : float
        Current adaptation stock.
    psi_i : float
        Amplification coefficient.
    t : float
        Current time (years).
    tau_i : float
        Learning time constant (years).

    Returns
    -------
    float
        Enhanced investment flow.
    """
    return V_i * (1.0 + psi_i * S_adapt * np.log(1.0 + t / tau_i))


def dS_prep_dt(S_prep: float, V_tech: float, V_intel: float,
               k_prep: float, mu: float, A_env: float) -> float:
    """
    Preparedness dynamics (Eq. 5).

    dS_prep/dt = (V_tech + V_intel) - k_prep * S_prep^(1+mu) * A_env

    Superlinear exponent (1+mu=1.8) reflects accelerating obsolescence.
    """
    inflow = V_tech + V_intel
    outflow = k_prep * (S_prep ** (1.0 + mu)) * A_env
    return inflow - outflow


def dS_resist_dt(S_resist: float, V_robust: float, V_radhard: float,
                 V_comm: float, k_resist: float, A_env: float) -> float:
    """
    Resistance dynamics (Eq. 6).

    dS_resist/dt = (V_robust + V_radhard + V_comm) - k_resist * S_resist * A_env
    """
    inflow = V_robust + V_radhard + V_comm
    outflow = k_resist * S_resist * A_env
    return inflow - outflow


def dS_restore_dt(S_restore: float, V_auto: float, V_forensic: float,
                  k_restore: float, A_env: float) -> float:
    """
    Restoration dynamics (Eq. 7).

    dS_restore/dt = (V_auto + V_forensic) - k_restore * S_restore * A_env
    """
    inflow = V_auto + V_forensic
    outflow = k_restore * S_restore * A_env
    return inflow - outflow


def dS_adapt_dt(S_adapt: float, V_opt: float, V_improve: float,
                k_adapt: float, A_env: float) -> float:
    """
    Adaptation dynamics (Eq. 8).

    dS_adapt/dt = (V_opt + V_improve) - k_adapt * S_adapt * A_env
    """
    inflow = V_opt + V_improve
    outflow = k_adapt * S_adapt * A_env
    return inflow - outflow


def dS_supply_dt(S_supply: float, V_supply: float, k_supply: float,
                 A_env: float) -> float:
    """
    Supply chain security dynamics (Eq. 10).

    dS_supply/dt = V_supply - k_supply * S_supply * A_env
    """
    inflow = V_supply
    outflow = k_supply * S_supply * A_env
    return inflow - outflow
