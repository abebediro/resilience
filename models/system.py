"""
Integrated system dynamics model - reference implementation aligned with
Appendix K (Python) / Appendix I (Vensim) of the revised paper, extended
with the operational constraints C1-C3 (Section constraints / Appendix P).

State vector: [S_prep, S_resist, S_restore, S_adapt, S_supply, S_threat]
"""

import numpy as np
from typing import Dict, Optional

from models import environment as env
from models.composition import system_resilience, system_resilience_from_state
from models.adversary import (dS_threat_dt, dS_threat_dt_capped,
                              effective_resilience,
                              geopolitical_shock_investment)
from calibration.parameters import ParameterSet


def _phase(t: float, early: float, mid: float, late: float) -> float:
    """Phase-based investment multiplier (Appendix I eqs 7-8, 15-17, ...)."""
    return early if t < 3 else (mid if t < 8 else late)


class SpaceResilienceModel:
    """Full SD model with phase-based investment, efficiency curves,
    time-varying environment, adaptation amplification, Red Queen coupling,
    and optional constraints C1 (budget premiums), C2 (adversary cap),
    C3 (replacement cycles)."""

    def __init__(self, params: ParameterSet = None):
        self.params = params if params is not None else ParameterSet()

    # ---- Investment streams (Appendix K) ----

    def _streams(self, t: float, weights: np.ndarray, budget: float) -> Dict[str, float]:
        w = weights
        B = budget
        return {
            "tech":     _phase(t, 0.75, 1.0, 1.0) * B * w[0] * 0.5,
            "intel":    _phase(t, 0.5, 0.8, 1.0) * B * w[0] * 0.5,
            "robust":   _phase(t, 2.0, 1.5, 1.0) * B * w[1] * 0.6,
            "radhard":  _phase(t, 1.0, 1.2, 1.0) * B * w[1] * 0.25,
            "comm":     _phase(t, 0.5, 0.8, 1.0) * B * w[1] * 0.15,
            "auto":     _phase(t, 0.8, 1.0, 1.0) * B * w[2] * 0.7,
            "forensic": _phase(t, 0.4, 0.7, 1.0) * B * w[2] * 0.3,
            "opt":      _phase(t, 0.2, 0.5, 1.0) * B * w[3] * 0.6,
            "improve":  _phase(t, 0.1, 0.3, 1.0) * B * w[3] * 0.4,
            "supply":   _phase(t, 0.6, 0.8, 1.0) * B * w[4],
        }

    @staticmethod
    def _efficiencies(t: float, cum_rad: float) -> Dict[str, float]:
        """Investment efficiency curves (Appendix I eqs 9-10, 18, 26-27, 38)."""
        return {
            "tech":     0.8 * (1 - 0.3 * np.exp(-t / 5)),
            "intel":    1.0 * (1 - 0.2 * np.exp(-t / 3)),
            "radhard":  0.9 * (1 - 0.2 * np.exp(-cum_rad / 0.5)),
            "auto":     1.0 * (1 - 0.1 * np.exp(-t / 4)),
            "forensic": 0.7 * (1 + 0.3 * (1 - np.exp(-t / 5))),
            "supply":   0.85 * (1 - 0.15 * np.exp(-t / 4)),
        }

    def _amplification(self, S_adapt: float, t: float) -> np.ndarray:
        """Adaptation amplification 1 + psi_i*A*ln(1+t/tau_i) (Eq. 9 / I eqs 42-45)."""
        p = self.params
        psi = p.get_psi()
        tau = p.get_tau_learn()
        return 1.0 + psi * S_adapt * np.log(1.0 + max(t, 1e-9) / tau)

    # ---- Core derivatives ----

    def derivatives(self, t: float, state: np.ndarray,
                    weights: np.ndarray = None,
                    budget: float = None,
                    hw_age: float = None) -> np.ndarray:
        p = self.params
        state = np.clip(state, 0.0, 1.0)
        prep, resist, restore, adapt, supply, threat = state

        w = weights if weights is not None else p.get_weights()
        B = budget if budget is not None else p.total_budget

        # C1: divide streams by dimension-level cost premiums pi_i(t)
        if p.constrain_budget:
            pi = p.cost_premiums(t, adapt)
        else:
            pi = np.ones(5)

        s = self._streams(t, w, B)
        # C3: hardware stressors depend on ASSET age (resets at replacement);
        # operational stressors (latency, SC risk, complexity) on mission time.
        a = hw_age if hw_age is not None else t
        cum_rad = env.cumulative_radiation(a)
        e = self._efficiencies(t, cum_rad)
        aap, aar, aat, aas = self._amplification(adapt, t)

        # Human reliability factor (Eq. human_reliability): mean of Beta
        H = p.alpha_H / (p.alpha_H + p.beta_H)
        scale = p.investment_scale * H

        lat = env.latency(t)
        thermal = env.thermal_cycle(a)
        D = env.orbital_distance(a)
        sc_risk = env.SC_risk(t)
        g_cplx = env.G_complexity(t)

        # Inflows (Appendix K), scaled to stock units and premium-adjusted
        in_prep = (s["tech"] * e["tech"] + s["intel"] * e["intel"]) * aap * scale / pi[0]
        in_resist = (s["robust"] + s["radhard"] * e["radhard"] + s["comm"]) * aar * scale / pi[1]
        in_restore = (s["auto"] * e["auto"] + s["forensic"] * e["forensic"]) * aat * scale / pi[2]
        in_adapt = (s["opt"] + s["improve"]) * scale / pi[3]
        in_supply = s["supply"] * e["supply"] * aas * scale / pi[4]

        # Outflows (Eqs. preparedness..supply_chain)
        out_prep = p.k_prep * prep ** (1 + p.mu) * (1 + p.alpha * np.sqrt(lat))
        out_resist = p.k_resist * resist * (1 + p.gamma * cum_rad ** 1.9 + p.gamma_T * thermal)
        out_restore = p.k_restore * restore * (1 + p.beta * D ** 1.4)
        out_adapt = p.k_adapt * adapt * (1 + p.alpha * np.sqrt(lat))
        out_supply = p.k_supply * supply * (1 + p.eta * sc_risk + p.nu * g_cplx)

        # System resilience for adversary coupling (Eq. system_resilience)
        R_sys = system_resilience(prep, resist, restore, adapt, supply, p.get_xi())

        # Adversary dynamics: baseline (Eq. threat_evolution) or C2 cap
        I_adv = geopolitical_shock_investment(t, p.I_baseline, p.geopolitical_scenario)
        if p.use_adversary_cap:
            dthreat = dS_threat_dt_capped(threat, R_sys, p.theta, p.phi,
                                          I_adv, p.delta_threat, p.A_max)
        else:
            dthreat = dS_threat_dt(threat, R_sys, p.theta, p.phi,
                                   I_adv, p.delta_threat)

        return np.array([in_prep - out_prep, in_resist - out_resist,
                         in_restore - out_restore, in_adapt - out_adapt,
                         in_supply - out_supply, dthreat])

    # ---- Integration ----

    def rk4_step(self, t, state, dt, weights=None, budget=None, t_repl=0.0):
        def age(tt):
            return tt - t_repl
        k1 = self.derivatives(t, state, weights, budget, age(t))
        k2 = self.derivatives(t + 0.5 * dt, state + 0.5 * dt * k1, weights, budget, age(t + 0.5 * dt))
        k3 = self.derivatives(t + 0.5 * dt, state + 0.5 * dt * k2, weights, budget, age(t + 0.5 * dt))
        k4 = self.derivatives(t + dt, state + dt * k3, weights, budget, age(t + dt))
        return np.clip(state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4), 0.0, 1.0)

    def _apply_replacement(self, state: np.ndarray, launch: np.ndarray) -> np.ndarray:
        """C3 replacement operator (Eq. replacement):
        S_i(t_r+) = (1-zeta_i) S_i(t_r-) + zeta_i S_i^launch.

        S_i^launch is the as-launched posture of the REPLACEMENT asset. A
        replacement built at t_r embodies current practices, so its launch
        posture is the current capability level, S_i^launch = S_i(t_r-)
        (not the original t=0 posture). The zeta blend is therefore
        capability-neutral; the operational effects of replacement are
        (i) the hardware-age reset (cumulative radiation, thermal fatigue,
        orbital aging restart at zero) and (ii) re-incurred supply-chain
        exposure: the fraction zeta_supply of the supply stock is re-exposed
        to integration/provenance risk, applying a transient dip.
        """
        p = self.params
        new = state.copy()
        # supply-chain re-exposure dip on the renewed hardware fraction
        new[4] = state[4] * (1.0 - 0.15 * p.zeta_supply)
        return new

    def simulate(self, T: float = 20.0, dt: float = 0.25,
                 weights: np.ndarray = None, budget: float = None,
                 initial_state: np.ndarray = None) -> Dict:
        p = self.params
        if initial_state is None:
            initial_state = p.get_initial_state()
        launch = initial_state.copy()

        n = int(round(T / dt)) + 1
        times = np.linspace(0, T, n)
        states = np.zeros((n, 6))
        R_system = np.zeros(n)
        R_effective = np.zeros(n)
        cumulative_cost = np.zeros(n)

        xi = p.get_xi()
        state = initial_state.copy()
        states[0] = state
        R_system[0] = system_resilience_from_state(state, xi)
        R_effective[0] = effective_resilience(R_system[0], state[5],
                                              p.gamma_threat, p.S_threat_min)

        B = budget if budget is not None else p.total_budget
        next_replacement = p.T_cyc if p.T_cyc > 0 else np.inf
        t_repl = 0.0  # time of last hardware replacement (C3)

        for i in range(1, n):
            t = times[i - 1]
            state = self.rk4_step(t, state, dt, weights, budget, t_repl)
            # C3: replacement epoch resets hardware age + partial stock refresh
            if times[i] >= next_replacement - 1e-9:
                state = self._apply_replacement(state, launch)
                cumulative_cost[i - 1] += p.replacement_cost_frac * B * p.T_cyc
                t_repl = times[i]
                next_replacement += p.T_cyc
            states[i] = state
            R_system[i] = system_resilience_from_state(state, xi)
            R_effective[i] = effective_resilience(R_system[i], state[5],
                                                  p.gamma_threat, p.S_threat_min)
            cumulative_cost[i] = cumulative_cost[i - 1] + B * dt

        return {"time": times, "states": states, "R_system": R_system,
                "R_effective": R_effective, "cumulative_cost": cumulative_cost,
                "dim_names": ["Preparedness", "Resistance", "Restoration",
                              "Adaptation", "Supply Chain", "Threat"]}

    def simulate_strategy(self, strategy: str, enhancement: float = 0.30,
                          T: float = 20.0, dt: float = 0.25) -> Dict:
        p = self.params
        base_w = p.get_weights()
        B = p.total_budget
        if strategy == "baseline":
            return self.simulate(T, dt, base_w, B)
        if strategy == "holistic":
            return self.simulate(T, dt, base_w, B * (1 + enhancement))
        if strategy == "balanced":
            return self.simulate(T, dt, np.ones(5) / 5.0, B)
        names = ["preparedness", "resistance", "restoration", "adaptation", "supply_chain"]
        if strategy in names:
            i = names.index(strategy)
            w = base_w.copy()
            w[i] *= (1 + enhancement)
            return self.simulate(T, dt, w / w.sum(), B)
        raise ValueError(f"Unknown strategy: {strategy}")


def run_baseline(params: ParameterSet = None) -> Dict:
    return SpaceResilienceModel(params).simulate()
