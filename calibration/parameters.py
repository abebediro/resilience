"""
Calibrated Parameter Set (Table V / Appendix A.10) with uncertainty bounds.

Updated to match the revised paper (Diro, An & Tullu):
- Initial conditions from Appendix A.10
- AHP weights from Appendix A.11 (geometric-mean matrix, CR=0.08)
- Operational constraints C1-C3 (Section constraints / Appendix P)
- 9-parameter primary specification (Appendix E)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Parameter:
    name: str
    symbol: str
    value: float
    unit: str
    ci_80: Tuple[float, float]
    cv: float
    source: str
    ident_class: str = "Practical"  # Practical | Structural | Weak

    def sample(self, rng: np.random.Generator = None) -> float:
        if rng is None:
            rng = np.random.default_rng()
        sigma = self.cv * abs(self.value)
        if sigma == 0:
            return self.value
        log_mu = np.log(self.value) - 0.5 * np.log(1 + (sigma / self.value) ** 2)
        log_sigma = np.sqrt(np.log(1 + (sigma / self.value) ** 2))
        return rng.lognormal(log_mu, log_sigma)


@dataclass
class ParameterSet:
    """Complete calibrated parameter set for the model."""

    # Decay rates (yr^-1) - Table V
    k_prep: float = 0.05
    k_resist: float = 0.07
    k_restore: float = 0.12
    k_adapt: float = 0.03
    k_supply: float = 0.11

    # Environmental sensitivities
    alpha: float = 0.85
    beta: float = 1.20
    gamma: float = 0.90
    gamma_T: float = 0.15
    mu: float = 0.80

    # Adversary dynamics
    theta: float = 0.12
    phi: float = 0.25
    delta_threat: float = 0.08
    gamma_threat: float = 0.35
    S_threat_min: float = 0.10

    # Supply chain
    eta: float = 0.45
    nu: float = 0.30

    # Cascade coefficients
    xi_resist: float = 0.68
    xi_prep: float = 0.42
    xi_restore: float = 0.31
    xi_adapt: float = 0.25

    # Adaptation amplification
    psi_prep: float = 0.28
    psi_resist: float = 0.22
    psi_restore: float = 0.35
    psi_supply: float = 0.18

    # Learning time constants (yr)
    tau_prep: float = 2.5
    tau_resist: float = 3.0
    tau_restore: float = 2.0
    tau_supply: float = 4.0

    # Human reliability factor
    alpha_H: float = 4.2
    beta_H: float = 1.8

    # AHP weights - Appendix A.11 geometric-mean matrix (CR=0.08)
    w_prep: float = 0.153
    w_resist: float = 0.462
    w_restore: float = 0.231
    w_adapt: float = 0.058
    w_supply: float = 0.096

    # Geopolitical shock
    I_baseline: float = 1.0
    geopolitical_scenario: str = "steady"

    # ---- Operational constraints C1-C3 (Appendix P) ----
    # C1: Bounded budget with space-grade cost premiums pi_i
    constrain_budget: bool = False
    pi_prep: float = 1.0
    pi_resist: float = 1.8            # +80% space-qualified blend
    pi_restore_base: float = 1.0
    pi_restore_growth: float = 0.05   # +5%/yr retrofit growth
    pi_adapt_base: float = 1.0
    pi_adapt_maturity_disc: float = 0.30
    pi_supply: float = 1.45           # +45%/tier blend

    # C2: Finite adversary resources (logistic cap, Eq. adversary_cap)
    use_adversary_cap: bool = True
    A_max: float = 0.975        # calibrated: reproduces main-text erosion 18-21%

    # C3: Satellite replacement cycles (Eq. replacement)
    T_cyc: float = 0.0                # 0 = disabled; else in [5,15] yr
    zeta_prep: float = 0.10
    zeta_resist: float = 0.80
    zeta_restore: float = 0.60
    zeta_adapt: float = 0.05
    zeta_supply: float = 0.70
    replacement_cost_frac: float = 0.22  # +22% cumulative cost at T_cyc=5

    # Initial conditions - Appendix A.10 (Round 3 final)
    S_prep_0: float = 0.15
    S_resist_0: float = 0.20
    S_restore_0: float = 0.12
    S_adapt_0: float = 0.08
    S_supply_0: float = 0.10
    S_threat_0: float = 0.10

    total_budget: float = 5.0  # $M/yr

    # Global normalization converting $M streams into stock inflows [0,1]/yr.
    # Calibrated so the baseline trajectory tracks Appendix I.4 targets
    # (R_sys(10)~0.86, logistic saturation by yr 15-20). The printed
    # Appendix I/K code and the published trajectory table are mutually
    # inconsistent without this normalization; see README Reproduction Notes.
    investment_scale: float = 0.20

    def get_initial_state(self) -> np.ndarray:
        return np.array([self.S_prep_0, self.S_resist_0, self.S_restore_0,
                         self.S_adapt_0, self.S_supply_0, self.S_threat_0])

    def get_weights(self) -> np.ndarray:
        w = np.array([self.w_prep, self.w_resist, self.w_restore,
                      self.w_adapt, self.w_supply])
        return w / w.sum()

    def get_xi(self) -> np.ndarray:
        return np.array([self.xi_prep, self.xi_resist, self.xi_restore, self.xi_adapt])

    def get_psi(self) -> np.ndarray:
        return np.array([self.psi_prep, self.psi_resist, self.psi_restore, self.psi_supply])

    def get_tau_learn(self) -> np.ndarray:
        return np.array([self.tau_prep, self.tau_resist, self.tau_restore, self.tau_supply])

    def get_zeta(self) -> np.ndarray:
        return np.array([self.zeta_prep, self.zeta_resist, self.zeta_restore,
                         self.zeta_adapt, self.zeta_supply])

    def cost_premiums(self, t: float, S_adapt: float) -> np.ndarray:
        """C1 premium vector pi_i(t) per dimension."""
        pi_restore = self.pi_restore_base * (1.0 + self.pi_restore_growth) ** t
        pi_adapt = max(0.5, self.pi_adapt_base * (1.0 - self.pi_adapt_maturity_disc * S_adapt))
        return np.array([self.pi_prep, self.pi_resist, pi_restore, pi_adapt, self.pi_supply])

    def to_dict(self) -> Dict[str, float]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, (int, float))}


PARAMETER_TABLE = [
    Parameter("Preparedness decay", "k_prep", 0.05, "yr^-1", (0.035, 0.065), 0.28, "Delphi (operators)", "Practical"),
    Parameter("Resistance decay", "k_resist", 0.07, "yr^-1", (0.049, 0.091), 0.24, "Delphi (vendors)", "Practical"),
    Parameter("Restoration decay", "k_restore", 0.12, "yr^-1", (0.084, 0.156), 0.31, "Delphi (operators)", "Structural"),
    Parameter("Adaptation decay", "k_adapt", 0.03, "yr^-1", (0.021, 0.039), 0.35, "Delphi (academics)", "Structural"),
    Parameter("Supply chain decay", "k_supply", 0.11, "yr^-1", (0.077, 0.143), 0.29, "Delphi (government)", "Practical"),
    Parameter("Latency sensitivity", "alpha", 0.85, "--", (0.60, 1.11), 0.22, "Delphi + lit.", "Practical"),
    Parameter("Inaccessibility", "beta", 1.20, "--", (0.84, 1.56), 0.26, "Operator data", "Practical"),
    Parameter("Radiation sensitivity", "gamma", 0.90, "--", (0.63, 1.17), 0.21, "NASA data", "Practical"),
    Parameter("Thermal sensitivity", "gamma_T", 0.15, "--", (0.10, 0.20), 0.18, "NASA data", "Weak"),
    Parameter("Superlinear exponent", "mu", 0.80, "--", (0.56, 1.04), 0.25, "Delphi", "Structural"),
    Parameter("Adversary learning", "theta", 0.12, "yr^-1", (0.084, 0.156), 0.33, "Delphi (all)", "Practical"),
    Parameter("Adversary amplification", "phi", 0.25, "--", (0.17, 0.33), 0.28, "Delphi", "Structural"),
    Parameter("Threat decay", "delta_threat", 0.08, "yr^-1", (0.056, 0.104), 0.26, "Delphi", "Structural"),
    Parameter("Max threat impact", "gamma_threat", 0.35, "--", (0.25, 0.46), 0.27, "Delphi", "Structural"),
    Parameter("Min threat capability", "S_threat_min", 0.10, "--", (0.07, 0.13), 0.19, "Delphi", "Practical"),
    Parameter("SC risk sensitivity", "eta", 0.45, "--", (0.32, 0.58), 0.24, "Delphi", "Weak"),
    Parameter("Complexity sensitivity", "nu", 0.30, "--", (0.21, 0.39), 0.26, "Delphi", "Weak"),
]

# 9-parameter primary specification (Appendix E.3)
PRIMARY_9 = ["theta", "xi_resist", "k_resist", "k_prep", "gamma",
             "alpha", "beta", "k_supply", "psi_prep"]


def sample_parameters(rng: np.random.Generator = None,
                      primary_only: bool = False) -> ParameterSet:
    """Sample a parameter set from approximate posteriors.

    primary_only=True implements the 9-parameter primary specification:
    only PRIMARY_9 vary; all others stay at posterior medians.
    """
    if rng is None:
        rng = np.random.default_rng()
    params = ParameterSet()
    for p in PARAMETER_TABLE:
        if primary_only and p.symbol not in PRIMARY_9:
            continue
        if hasattr(params, p.symbol):
            setattr(params, p.symbol, p.sample(rng))
    if primary_only:
        for sym, val, cv in [("psi_prep", 0.28, 0.10), ("xi_resist", 0.68, 0.07)]:
            sigma = cv * val
            log_mu = np.log(val) - 0.5 * np.log(1 + (sigma / val) ** 2)
            log_s = np.sqrt(np.log(1 + (sigma / val) ** 2))
            setattr(params, sym, rng.lognormal(log_mu, log_s))
    return params


# Six AHP weighting scenarios (Section robustness_classification)
WEIGHT_SCENARIOS = {
    "ahp_appendix":       np.array([0.153, 0.462, 0.231, 0.058, 0.096]),
    "main_text":          np.array([0.18, 0.32, 0.22, 0.15, 0.13]),
    "balanced":           np.array([0.20, 0.20, 0.20, 0.20, 0.20]),
    "adaptation_focused": np.array([0.15, 0.20, 0.15, 0.30, 0.20]),
    "resistance_focused": np.array([0.10, 0.45, 0.20, 0.10, 0.15]),
    "data_informed":      np.array([0.14, 0.40, 0.24, 0.08, 0.14]),
}

# Adverse joint prior shift (Appendix Q.1): cross-background extremes
ADVERSE_PRIOR_SHIFT = {"theta": 0.15, "eta": 0.38, "gamma": 0.98}
