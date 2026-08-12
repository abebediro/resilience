"""
Visualization module: generates all figures from the paper.

Figures:
1. Baseline trajectory (Fig. 5)
2. Feedback loop dominance (Fig. 3)
3. Posterior distributions (Fig. 4)
4. Adversary dynamics & Red Queen (Fig. 8, 9)
5. Monte Carlo distributions (Fig. 10)
6. Sensitivity tornado (Fig. 7)
7. Residual analysis (Fig. 5)
8. Strategy comparison
9. Copula analysis
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Embed fonts as TrueType (Type 42) so PDF figures are portable and editable
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
from matplotlib.patches import FancyArrowPatch
import os
from typing import Dict, Optional


# Style configuration
plt.rcParams.update({
    "figure.dpi": 150,
    "figure.figsize": (8, 5),
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
})

COLORS = {
    "prep": "#2196F3",
    "resist": "#F44336",
    "restore": "#4CAF50",
    "adapt": "#FF9800",
    "supply": "#9C27B0",
    "threat": "#E91E63",
    "R_system": "#1565C0",
    "R_effective": "#2E7D32",
    "ci_80": "#90CAF9",
    "ci_95": "#BBDEFB",
}


def plot_baseline_trajectory(result: Dict, save_path: str = None):
    """Fig. 5: Baseline resilience trajectory with credible intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: System & effective resilience
    ax = axes[0]
    t = result["time"]
    ax.plot(t, result["R_system"], color=COLORS["R_system"],
            linewidth=2, label="System Resilience ($R_{system}$)")
    ax.plot(t, result["R_effective"], color=COLORS["R_effective"],
            linewidth=2, linestyle="--", label="Effective Resilience ($R_{eff}$)")
    ax.fill_between(t, result["R_system"], result["R_effective"],
                    alpha=0.15, color=COLORS["threat"], label="Red Queen Erosion")

    # Phase annotations
    ax.axvspan(0, 3, alpha=0.05, color="green", label="Foundation")
    ax.axvspan(3, 8, alpha=0.05, color="orange", label="Acceleration")
    ax.axvspan(8, 20, alpha=0.05, color="purple", label="Maturation")

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Resilience")
    ax.set_title("Baseline Resilience Trajectory")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)

    # Right: Individual dimensions
    ax = axes[1]
    dim_names = ["Preparedness", "Resistance", "Restoration",
                 "Adaptation", "Supply Chain"]
    dim_colors = [COLORS["prep"], COLORS["resist"], COLORS["restore"],
                  COLORS["adapt"], COLORS["supply"]]

    for i, (name, color) in enumerate(zip(dim_names, dim_colors)):
        ax.plot(t, result["states"][:, i], color=color, linewidth=1.5, label=name)

    ax.plot(t, result["states"][:, 5], color=COLORS["threat"],
            linewidth=1.5, linestyle=":", label="Threat Capability")

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Stock Level")
    ax.set_title("Dimensional Trajectories")
    ax.legend(loc="center right", fontsize=9)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_adversary_dynamics(result: Dict, save_path: str = None):
    """Fig. 8 & 9: Red Queen dynamics."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    t = result["time"]

    # Left: Technical vs effective resilience
    ax = axes[0]
    ax.plot(t, result["R_system"], color=COLORS["R_system"],
            linewidth=2, label="Technical Resilience")
    ax.plot(t, result["states"][:, 5], color=COLORS["threat"],
            linewidth=2, linestyle="--", label="Adversary Capability")
    ax.plot(t, result["R_effective"], color=COLORS["R_effective"],
            linewidth=2, linestyle=":", label="Effective Resilience")
    ax.fill_between(t, result["R_system"], result["R_effective"],
                    alpha=0.2, color=COLORS["threat"])

    # Annotate erosion at years 10, 20
    for yr in [10, 15, 20]:
        idx = np.argmin(np.abs(t - yr))
        erosion = (result["R_system"][idx] - result["R_effective"][idx])
        erosion_pct = erosion / max(result["R_system"][idx], 1e-10) * 100
        ax.annotate(f"{erosion_pct:.1f}%", xy=(yr, result["R_effective"][idx]),
                    xytext=(yr + 0.5, result["R_effective"][idx] - 0.08),
                    fontsize=9, color=COLORS["threat"],
                    arrowprops=dict(arrowstyle="->", color=COLORS["threat"]))

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Capability Level")
    ax.set_title("Adversary Co-evolution (Red Queen Effect)")
    ax.legend(loc="center right")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)

    # Right: Red Queen tax (investment multiplier)
    ax = axes[1]
    erosion = np.zeros_like(t)
    for i, ti in enumerate(t):
        R_s = result["R_system"][i]
        R_e = result["R_effective"][i]
        if R_e > 0.01:
            erosion[i] = R_s / R_e
        else:
            erosion[i] = 1.0

    ax.plot(t, erosion, color=COLORS["threat"], linewidth=2)
    ax.fill_between(t, 1, erosion, alpha=0.15, color=COLORS["threat"])
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Investment Multiplier Required")
    ax.set_title("Red Queen Tax: Investment Multiplier")
    ax.set_xlim(0, 20)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_strategy_comparison(results: Dict, save_path: str = None):
    """Strategy comparison bar chart and trajectories."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    strategies = list(results.keys())
    colors_map = {
        "baseline": "#607D8B", "preparedness": COLORS["prep"],
        "resistance": COLORS["resist"], "restoration": COLORS["restore"],
        "adaptation": COLORS["adapt"], "supply_chain": COLORS["supply"],
        "holistic": "#FFD700", "balanced": "#795548",
    }

    # Left: Year-10 comparison bar chart
    ax = axes[0]
    yr10_vals = [results[s]["metrics"]["yr10_R_eff"] for s in strategies]
    bars = ax.barh(range(len(strategies)), yr10_vals,
                   color=[colors_map.get(s, "#999") for s in strategies])
    ax.set_yticks(range(len(strategies)))
    ax.set_yticklabels([s.replace("_", " ").title() for s in strategies])
    ax.set_xlabel("Effective Resilience at Year 10")
    ax.set_title("Strategy Comparison (Year 10)")
    ax.set_xlim(0.5, 1.0)

    for bar, val in zip(bars, yr10_vals):
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9)

    # Right: Trajectories
    ax = axes[1]
    for strat in strategies:
        res = results[strat]
        t = res["time"]
        color = colors_map.get(strat, "#999")
        ls = "--" if strat == "baseline" else "-"
        lw = 2.5 if strat in ("holistic", "baseline") else 1.2
        ax.plot(t, res["R_effective"], color=color, linestyle=ls,
                linewidth=lw, label=strat.replace("_", " ").title())

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Effective Resilience")
    ax.set_title("Strategy Trajectories")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_monte_carlo_distributions(mc_result: Dict, save_path: str = None):
    """Fig. 10: MC output distributions at years 5, 10, 15, 20."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    years = [5, 10, 15, 20]
    t = mc_result["time"]

    for ax, yr in zip(axes.flat, years):
        idx = np.argmin(np.abs(t - yr))
        data = mc_result["R_system_all"][:, idx]

        ax.hist(data, bins=40, density=True, alpha=0.7,
                color=COLORS["R_system"], edgecolor="white")
        ax.axvline(np.median(data), color="red", linestyle="--",
                   linewidth=1.5, label=f"Median: {np.median(data):.3f}")
        ax.axvline(np.percentile(data, 10), color="orange",
                   linestyle=":", label=f"80% CI: [{np.percentile(data, 10):.3f}, "
                   f"{np.percentile(data, 90):.3f}]")
        ax.axvline(np.percentile(data, 90), color="orange", linestyle=":")

        ax.set_xlabel("System Resilience")
        ax.set_ylabel("Density")
        ax.set_title(f"Year {yr} (CV={np.std(data)/np.mean(data)*100:.1f}%)")
        ax.legend(fontsize=8)

    plt.suptitle("Monte Carlo Output Distributions", fontsize=14, y=1.02)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_sensitivity_tornado(sobol_results: Dict, save_path: str = None):
    """Fig. 7: Sobol indices tornado chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    rankings = sobol_results["rankings"][:8]  # Top 8
    names = [r["parameter"] for r in rankings]
    S1 = [r["S1"] for r in rankings]
    ST = [r["ST"] for r in rankings]

    y = np.arange(len(names))
    height = 0.35

    bars1 = ax.barh(y - height / 2, S1, height, color=COLORS["R_system"],
                    alpha=0.8, label="First-order ($S_i$)")
    bars2 = ax.barh(y + height / 2, ST, height, color=COLORS["threat"],
                    alpha=0.8, label="Total-order ($S_{Ti}$)")

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Sobol Index")
    ax.set_title(f"Parameter Sensitivity (Year {sobol_results['eval_year']:.0f})")
    ax.legend()

    # Add elasticity annotations
    for i, r in enumerate(rankings):
        ax.text(max(r["ST"], r["S1"]) + 0.01, i,
                f"ε={r['elasticity']:+.2f}", va="center", fontsize=9)

    ax.invert_yaxis()
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_copula_analysis(sweep: Dict, save_path: str = None):
    """Copula correlation sweep plot."""
    fig, ax = plt.subplots(figsize=(8, 5))

    rhos = [r["rho"] for r in sweep["results"]]
    R_cop = [r["R_copula"] for r in sweep["results"]]
    R_ind = sweep["results"][0]["R_independent"]

    ax.plot(rhos, R_cop, "o-", color=COLORS["R_system"], linewidth=2,
            markersize=8, label="Copula-adjusted $R_{system}$")
    ax.axhline(R_ind, color="gray", linestyle="--", alpha=0.7,
               label=f"Independence baseline ({R_ind:.3f})")

    # Annotate key points
    for r in sweep["results"]:
        if r["rho"] in [0.3, 0.4, 0.6]:
            ax.annotate(f"{r['overestimation_pct']:.1f}% overest.",
                        xy=(r["rho"], r["R_copula"]),
                        xytext=(r["rho"] + 0.05, r["R_copula"] - 0.03),
                        fontsize=9, arrowprops=dict(arrowstyle="->"))

    ax.set_xlabel("Common-cause correlation (ρ)")
    ax.set_ylabel("System Resilience")
    ax.set_title(f"Copula Extension Impact (Year {sweep['eval_year']:.0f})")
    ax.legend()
    ax.set_xlim(-0.05, 0.65)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_feedback_loop_dominance(result: Dict, save_path: str = None):
    """Fig. 3: Feedback loop dominance over mission lifecycle."""
    fig, ax = plt.subplots(figsize=(10, 5))
    t = result["time"]

    # Approximate loop strengths from simulation data
    R_sys = result["R_system"]
    R_eff = result["R_effective"]
    states = result["states"]

    # B1: Threat Learning (prep growth rate)
    dprep = np.gradient(states[:, 0], t)
    B1 = np.abs(dprep) / np.maximum(states[:, 0], 0.01)

    # B2: Core Resilience (resist + restore growth)
    dresist = np.gradient(states[:, 1], t)
    B2 = np.abs(dresist) / np.maximum(states[:, 1], 0.01)

    # R1: Adaptation Enhancement (adaptation * other growth)
    R1 = states[:, 3] * np.abs(np.gradient(R_sys, t))

    # R2: Adversary Co-evolution (threat growth)
    dthreat = np.gradient(states[:, 5], t)
    R2 = np.abs(dthreat) * states[:, 5]

    # Normalize
    total = B1 + B2 + R1 + R2 + 1e-10
    B1_n, B2_n, R1_n, R2_n = B1 / total, B2 / total, R1 / total, R2 / total

    ax.stackplot(t, B1_n, B2_n, R1_n, R2_n,
                 labels=["B1: Threat Learning", "B2: Core Resilience",
                         "R1: Adaptation Enhancement", "R2: Adversary Co-evolution"],
                 colors=[COLORS["prep"], COLORS["resist"],
                         COLORS["adapt"], COLORS["threat"]],
                 alpha=0.7)

    ax.axvline(3, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(8, color="gray", linestyle=":", alpha=0.5)
    ax.text(1.5, 0.95, "Foundation", ha="center", fontsize=9)
    ax.text(5.5, 0.95, "Acceleration", ha="center", fontsize=9)
    ax.text(14, 0.95, "Maturation", ha="center", fontsize=9)

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Relative Loop Strength")
    ax.set_title("Feedback Loop Dominance Over Mission Lifecycle")
    ax.legend(loc="center right", fontsize=9)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_posterior_distributions(delphi_results: Dict, save_path: str = None):
    """Fig. 4: Posterior distributions for key parameters."""
    key_params = ["k_prep", "k_resist", "theta", "gamma_threat",
                  "xi_resist", "gamma"]

    available = [p for p in key_params if p in delphi_results]
    if not available:
        return None

    n_params = len(available)
    cols = min(3, n_params)
    rows = (n_params + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))
    if n_params == 1:
        axes = [axes]
    else:
        axes = axes.flat

    for ax, param_name in zip(axes, available):
        info = delphi_results[param_name]
        samples = info["aggregation"]["samples"]
        ci = info["aggregation"]["ci_80"]
        median = info["aggregation"]["posterior_median"]

        ax.hist(samples, bins=40, density=True, alpha=0.7,
                color=COLORS["R_system"], edgecolor="white")
        ax.axvline(median, color="red", linewidth=1.5,
                   label=f"Median: {median:.3f}")
        ax.axvspan(ci[0], ci[1], alpha=0.15, color="orange",
                   label=f"80% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
        ax.set_title(f"${param_name}$")
        ax.legend(fontsize=7)

    # Hide unused axes
    for ax in axes[n_params:]:
        ax.set_visible(False)

    plt.suptitle("Posterior Distributions (Bayesian Aggregation)", fontsize=13)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def plot_validation_residuals(cv_results: Dict, save_path: str = None):
    """Fig. 5: Residual analysis."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    obs = cv_results["observed"]
    pred = cv_results["predicted"]
    resid = cv_results["residuals"]

    # (a) Predicted vs observed
    ax = axes[0]
    ax.scatter(obs, pred, alpha=0.6, s=30, color=COLORS["R_system"])
    lims = [min(obs.min(), pred.min()) - 0.05, max(obs.max(), pred.max()) + 0.05]
    ax.plot(lims, lims, "k--", alpha=0.5, label="Perfect fit")
    ax.set_xlabel("Observed Severity")
    ax.set_ylabel("Predicted Severity")
    ax.set_title(f"Predicted vs Observed (r={cv_results['correlation']:.2f})")
    ax.legend()

    # (b) Residual distribution
    ax = axes[1]
    ax.hist(resid, bins=20, density=True, alpha=0.7,
            color=COLORS["restore"], edgecolor="white")
    x_norm = np.linspace(resid.min(), resid.max(), 100)
    from scipy.stats import norm
    ax.plot(x_norm, norm.pdf(x_norm, resid.mean(), resid.std()),
            "r-", linewidth=1.5)
    ax.set_xlabel("Residual")
    ax.set_ylabel("Density")
    ax.set_title("Residual Distribution")

    # (c) Residuals vs fitted
    ax = axes[2]
    ax.scatter(pred, resid, alpha=0.6, s=30, color=COLORS["adapt"])
    ax.axhline(0, color="gray", linestyle="--")
    ax.set_xlabel("Fitted Values")
    ax.set_ylabel("Residuals")
    ax.set_title("Residuals vs Fitted")

    plt.suptitle(f"Validation: RMSE={cv_results['rmse']:.3f}, "
                 f"MAPE={cv_results['mape']:.1f}%", fontsize=12)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
    return fig


def generate_all_figures(output_dir: str = "output"):
    """Generate all figures (called from run_all.py)."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nAll figures will be saved to: {output_dir}/")
    return output_dir
