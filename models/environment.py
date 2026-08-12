"""
Space environment: time-varying stressor functions per Appendix I (Vensim eqs 12,
20, 21, 29, 40, 41) plus static modifier helpers used by the theory tests.
"""

import numpy as np


# ---- Time-varying environmental drivers (Appendix I) ----

def latency(t: float) -> float:
    """Round-trip delay proxy (s): 0.25 + 0.1*t  (Vensim eq 12)."""
    return 0.25 + 0.1 * t


def cumulative_radiation(t: float) -> float:
    """Normalized cumulative dose: min(1, 0.1*t + 0.02*t^2)  (eq 20)."""
    return min(1.0, 0.1 * t + 0.02 * t * t)


def thermal_cycle(t: float) -> float:
    """Normalized thermal amplitude: 0.5 + 0.05*t  (eq 21)."""
    return 0.5 + 0.05 * t


def orbital_distance(t: float) -> float:
    """Normalized orbital distance: 1 for t<10, then 1 + 0.1*(t-10)  (eq 29)."""
    return 1.0 if t < 10 else 1.0 + 0.1 * (t - 10.0)


def SC_risk(t: float) -> float:
    """Aggregate supply-chain risk index: 0.3 + 0.02*t  (eq 40)."""
    return 0.3 + 0.02 * t


def G_complexity(t: float) -> float:
    """Supply-chain structural complexity: 1.5 + 0.1*t  (eq 41)."""
    return 1.5 + 0.1 * t


# ---- Static modifier helpers (used by theory/tests; Appendix L.14) ----

def latency_modifier(alpha: float, tau_delay: float) -> float:
    """Weber-Fechner latency modifier: alpha*sqrt(tau)."""
    return alpha * np.sqrt(tau_delay)


def radiation_modifier(gamma: float, Phi_rad: float, exponent: float = 1.9) -> float:
    """TID modifier: gamma * Phi^1.9 (empirical CMOS range 1.8-2.2)."""
    return gamma * (Phi_rad ** exponent)


def thermal_modifier(gamma_T: float, delta_T: float) -> float:
    """Coffin-Manson thermal modifier: gamma_T * DeltaT (normalized)."""
    return gamma_T * delta_T


def inaccessibility_modifier(beta: float, D_orbit: float, exponent: float = 1.4) -> float:
    """Inaccessibility modifier: beta * D^1.4 (AICc-selected exponent)."""
    return beta * (D_orbit ** exponent)


class SpaceEnvironment:
    """Aggregated A_env,i(t) >= 1 acceleration factors (Eq. general_stock)."""

    def __init__(self, alpha=0.85, beta=1.20, gamma=0.90, gamma_T=0.15,
                 eta=0.45, nu=0.30):
        self.alpha, self.beta = alpha, beta
        self.gamma, self.gamma_T = gamma, gamma_T
        self.eta, self.nu = eta, nu

    def A_env_prep(self, t: float) -> float:
        return 1.0 + latency_modifier(self.alpha, latency(t))

    def A_env_resist(self, t: float) -> float:
        return (1.0 + radiation_modifier(self.gamma, cumulative_radiation(t))
                + thermal_modifier(self.gamma_T, thermal_cycle(t)))

    def A_env_restore(self, t: float) -> float:
        return 1.0 + inaccessibility_modifier(self.beta, orbital_distance(t))

    def A_env_adapt(self, t: float) -> float:
        return 1.0 + latency_modifier(self.alpha, latency(t))

    def A_env_supply(self, t: float) -> float:
        return 1.0 + self.eta * SC_risk(t) + self.nu * G_complexity(t)
