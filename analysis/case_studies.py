"""
Case studies: Viasat KA-SAT (2022) and Starlink RF Interference (2022).

Retrodictive alignment analysis (Section VII).
"""

import numpy as np
from typing import Dict
from models.composition import system_resilience
from models.adversary import effective_resilience
from calibration.parameters import ParameterSet


def viasat_case_study(params: ParameterSet = None) -> Dict:
    """
    Case Study 1: 2022 Viasat KA-SAT Disruption (Table IX).

    Pre-attack posture:
    - Preparedness: 0.31 [0.25, 0.37] - No prior modem warnings
    - Resistance: 0.28 [0.22, 0.34] - Consumer-grade security
    - Restoration: 0.22 [0.17, 0.27] - No remote recovery
    - Adaptation: 0.18 [0.14, 0.22] - Limited prior incidents
    - Supply Chain: 0.35 [0.29, 0.41] - Multi-vendor chain

    Observed outcomes:
    - Attack confirmed successful
    - Recovery ~45 days
    - ~40,000 modems affected (~62% breach extent)
    """
    if params is None:
        params = ParameterSet()

    # Pre-attack posture (Table IX)
    posture = {
        "preparedness": {"est": 0.31, "ci": (0.25, 0.37), "basis": "No prior modem warnings"},
        "resistance": {"est": 0.28, "ci": (0.22, 0.34), "basis": "Consumer-grade security"},
        "restoration": {"est": 0.22, "ci": (0.17, 0.27), "basis": "No remote recovery"},
        "adaptation": {"est": 0.18, "ci": (0.14, 0.22), "basis": "Limited prior incidents"},
        "supply_chain": {"est": 0.35, "ci": (0.29, 0.41), "basis": "Multi-vendor chain"},
    }

    S_p = posture["preparedness"]["est"]
    S_r = posture["resistance"]["est"]
    S_t = posture["restoration"]["est"]
    S_a = posture["adaptation"]["est"]
    S_c = posture["supply_chain"]["est"]

    # Compute system resilience
    xi = params.get_xi()
    R_sys = system_resilience(S_p, S_r, S_t, S_a, S_c, xi)

    # Attack success probability (complement of resilience)
    attack_prob = 1.0 - R_sys

    # Predicted breach extent based on supply chain cascade
    breach_extent = (1 - S_c) * params.xi_resist + (1 - S_r) * 0.3
    breach_extent = np.clip(breach_extent, 0, 1)

    # Recovery time model: base 30 days, scaled by inaccessibility
    base_recovery = 30.0  # days
    inaccess_penalty = 1.0 + params.beta * (1.0 - S_t)
    predicted_recovery = base_recovery * inaccess_penalty

    # 95% prediction intervals via Monte Carlo
    rng = np.random.default_rng(42)
    n_mc = 5000
    recovery_samples = []
    breach_samples = []
    attack_samples = []

    for _ in range(n_mc):
        sp = rng.uniform(*posture["preparedness"]["ci"])
        sr = rng.uniform(*posture["resistance"]["ci"])
        st = rng.uniform(*posture["restoration"]["ci"])
        sa = rng.uniform(*posture["adaptation"]["ci"])
        sc = rng.uniform(*posture["supply_chain"]["ci"])

        R = system_resilience(sp, sr, st, sa, sc, xi)
        attack_samples.append(1.0 - R)

        b = (1 - sc) * params.xi_resist + (1 - sr) * 0.3
        breach_samples.append(np.clip(b, 0, 1))

        rec = base_recovery * (1.0 + params.beta * (1.0 - st))
        recovery_samples.append(rec)

    attack_samples = np.array(attack_samples)
    breach_samples = np.array(breach_samples)
    recovery_samples = np.array(recovery_samples)

    # Likelihood ratio test (simplified)
    # Compare full model vs independence (no supply chain cascade)
    R_indep = 1.0 - (1 - S_p) * (1 - S_r) * (1 - S_t) * (1 - S_a)
    ll_full = -0.5 * ((attack_prob - 0.73)**2 / 0.1**2 +
                       (predicted_recovery - 45)**2 / 10**2)
    ll_indep = -0.5 * ((1 - R_indep - 0.73)**2 / 0.1**2 +
                        (30 - 45)**2 / 10**2)
    lr_stat = -2 * (ll_indep - ll_full)

    # Theil's U
    obs = np.array([0.73, 45, 0.62])
    pred = np.array([attack_prob, predicted_recovery, breach_extent])
    U = np.sqrt(np.mean((obs - pred)**2)) / (
        np.sqrt(np.mean(obs**2)) + np.sqrt(np.mean(pred**2)))

    # MAPE
    mape = np.mean(np.abs((obs - pred) / obs)) * 100

    return {
        "posture": posture,
        "model_predictions": {
            "attack_probability": attack_prob,
            "recovery_days": predicted_recovery,
            "breach_extent": breach_extent,
            "R_system": R_sys,
        },
        "observed": {
            "attack_confirmed": True,
            "recovery_days": 45,
            "modems_affected": 40000,
            "breach_extent_approx": 0.62,
        },
        "prediction_intervals_95": {
            "recovery": (np.percentile(recovery_samples, 2.5),
                         np.percentile(recovery_samples, 97.5)),
            "breach": (np.percentile(breach_samples, 2.5),
                       np.percentile(breach_samples, 97.5)),
            "attack_prob": (np.percentile(attack_samples, 2.5),
                            np.percentile(attack_samples, 97.5)),
        },
        "fit_statistics": {
            "theils_U": U,
            "MAPE": mape,
            "LR_statistic": lr_stat,
            "correlation": np.corrcoef(obs, pred)[0, 1],
        },
    }


def starlink_case_study(params: ParameterSet = None) -> Dict:
    """
    Case Study 2: 2022 Starlink RF Interference.

    Higher baseline posture reflecting SpaceX's capabilities:
    - Preparedness: 0.38 [0.31, 0.45]
    - Resistance: 0.52 [0.44, 0.60] (hardened terminals, LEO redundancy)
    - Restoration: 0.41 [0.34, 0.48] (software-updatable)
    - Adaptation: 0.45 [0.38, 0.52] (rapid software iteration)
    - Supply Chain: 0.55 [0.47, 0.63] (vertically integrated)

    Observed: partial, intermittent disruption; fixes within days.
    """
    if params is None:
        params = ParameterSet()

    posture = {
        "preparedness": {"est": 0.38, "ci": (0.31, 0.45),
                         "basis": "Conflict zone operational awareness"},
        "resistance": {"est": 0.52, "ci": (0.44, 0.60),
                       "basis": "Hardened terminals, LEO redundancy"},
        "restoration": {"est": 0.41, "ci": (0.34, 0.48),
                        "basis": "Software-updatable terminals"},
        "adaptation": {"est": 0.45, "ci": (0.38, 0.52),
                       "basis": "Rapid software iteration capability"},
        "supply_chain": {"est": 0.55, "ci": (0.47, 0.63),
                         "basis": "Vertically integrated manufacturing"},
    }

    S_p = posture["preparedness"]["est"]
    S_r = posture["resistance"]["est"]
    S_t = posture["restoration"]["est"]
    S_a = posture["adaptation"]["est"]
    S_c = posture["supply_chain"]["est"]

    xi = params.get_xi()
    R_sys = system_resilience(S_p, S_r, S_t, S_a, S_c, xi)
    attack_prob = 1.0 - R_sys

    # Recovery time (software-based, much faster)
    base_recovery = 5.0  # days (software fix)
    predicted_recovery = base_recovery * (1.0 + 0.3 * (1.0 - S_t))

    # Service degradation
    degradation = (1 - R_sys) * 0.5  # Partial, not catastrophic

    return {
        "posture": posture,
        "model_predictions": {
            "attack_probability": attack_prob,
            "service_degradation": degradation,
            "recovery_days": predicted_recovery,
            "R_system": R_sys,
        },
        "observed": {
            "outcome": "Partial, intermittent disruption",
            "recovery": "Software fixes within days",
            "service_degradation": "Localized, temporary (15-25%)",
        },
        "comparison_with_viasat": {
            "higher_resistance": True,
            "higher_adaptation": True,
            "qualitatively_different_outcome": True,
            "mechanism": "LEO redundancy + rapid software iteration",
        },
    }


def print_case_study(result: Dict, name: str):
    """Print case study results."""
    print(f"\n{'=' * 60}")
    print(f"Case Study: {name}")
    print(f"{'=' * 60}")

    print("\nPre-Attack Posture:")
    for dim, info in result["posture"].items():
        print(f"  {dim.title():<15}: {info['est']:.2f}  "
              f"CI [{info['ci'][0]:.2f}, {info['ci'][1]:.2f}]  "
              f"({info['basis']})")

    print("\nModel Predictions:")
    for key, val in result["model_predictions"].items():
        if isinstance(val, float):
            print(f"  {key:<25}: {val:.3f}")

    if "fit_statistics" in result:
        print("\nFit Statistics:")
        for key, val in result["fit_statistics"].items():
            print(f"  {key:<20}: {val:.3f}")

    if "prediction_intervals_95" in result:
        print("\n95% Prediction Intervals:")
        for key, val in result["prediction_intervals_95"].items():
            print(f"  {key:<15}: [{val[0]:.2f}, {val[1]:.2f}]")


def ahp_posture_index(posture: dict, params=None) -> float:
    """AHP-weighted posture index used in the main text's operational
    comparison (Viasat ~0.27, Starlink ~0.48): sum_i w_i * posture_i
    with Appendix A.11 weights."""
    if params is None:
        from calibration.parameters import ParameterSet
        params = ParameterSet()
    w = params.get_weights()
    order = ["preparedness", "resistance", "restoration", "adaptation", "supply_chain"]
    return float(sum(w[i] * posture[k]["est"] for i, k in enumerate(order)))
