#!/usr/bin/env python3
"""
run_all.py — Complete analysis pipeline for the Tripartite Space Cybersecurity
Resilience Model.

Reproduces all key results, tables, and figures from the paper.
Usage: python run_all.py
"""

import sys
import os
import time
import numpy as np

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calibration.parameters import ParameterSet, WEIGHT_SCENARIOS
from calibration.delphi import run_full_delphi_aggregation
from calibration.validation import (
    cross_validate, temporal_split_validation, posterior_predictive_check,
    reconstruction_criterion
)
from analysis.constraint_scenarios import run_constraint_scenarios
from analysis.prior_perturbation import run_adverse_shift
from data.incidents import get_dataset
from models.system import SpaceResilienceModel, run_baseline
from models.adversary import red_queen_equilibrium, red_queen_erosion_pct
from models.composition import (
    supply_chain_leverage, verify_composition_properties, system_resilience
)
from analysis.simulation import monte_carlo_simulation, robustness_check
from analysis.strategies import (
    run_strategy_comparison, print_strategy_table,
    compute_super_additivity, ahp_weight_sensitivity
)
from analysis.sensitivity import run_sobol_analysis, print_sobol_table
from analysis.copula import copula_sweep, copula_strategy_impact, print_copula_results
from analysis.case_studies import (
    viasat_case_study, starlink_case_study, print_case_study
)
from visualization.plots import (
    plot_baseline_trajectory, plot_adversary_dynamics,
    plot_strategy_comparison, plot_monte_carlo_distributions,
    plot_sensitivity_tornado, plot_copula_analysis,
    plot_feedback_loop_dominance, plot_posterior_distributions,
    plot_validation_residuals,
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def separator(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rng = np.random.default_rng(42)

    # ── 0. Run Tests ──────────────────────────────────────────────────────
    separator("0. MODEL TESTS & PROPERTY VERIFICATION")
    from tests.test_model import run_all_tests
    all_pass = run_all_tests()
    if not all_pass:
        print("WARNING: Some tests failed. Continuing anyway.\n")

    # ── 1. Baseline Simulation ────────────────────────────────────────────
    separator("1. BASELINE SIMULATION (Table V, Fig. 5)")
    params = ParameterSet()
    model = SpaceResilienceModel(params)
    baseline = model.simulate(T=20.0, dt=0.25)

    print("\nBaseline Resilience Trajectory (Table V):")
    print(f"{'Year':>6} {'R_system':>10} {'R_effective':>12} {'Growth':>10}")
    print("-" * 42)
    for yr in [0, 3, 5, 8, 10, 15, 20]:
        idx = np.argmin(np.abs(baseline["time"] - yr))
        R_s = baseline["R_system"][idx]
        R_e = baseline["R_effective"][idx]
        if yr == 0:
            print(f"{yr:>6} {R_s:>10.3f} {R_e:>12.3f} {'--':>10}")
        else:
            prev_idx = np.argmin(np.abs(baseline["time"] - max(0, yr - 1)))
            growth = (R_s - baseline["R_system"][prev_idx]) / max(baseline["R_system"][prev_idx], 0.01) * 100
            print(f"{yr:>6} {R_s:>10.3f} {R_e:>12.3f} {growth:>+9.1f}%")

    plot_baseline_trajectory(baseline, os.path.join(OUTPUT_DIR, "baseline_trajectory.png"))
    plot_feedback_loop_dominance(baseline, os.path.join(OUTPUT_DIR, "feedback_loop_dominance.png"))
    print(f"\n  → Saved: baseline_trajectory.png, feedback_loop_dominance.png")

    # ── 2. Theorem Verification ───────────────────────────────────────────
    separator("2. THEOREM & PROPERTY VERIFICATION")

    # Theorem 1
    R_eff = np.array([0.4, 0.5, 0.35, 0.3])
    props = verify_composition_properties(R_eff)
    print("\nTheorem 1 Properties:")
    for prop, val in props.items():
        print(f"  {prop:<20}: {'✓' if val else '✗'}")

    # Lemma 1: Supply chain leverage
    R_raw = np.array([0.5, 0.6, 0.4, 0.3])
    xi = params.get_xi()
    L = supply_chain_leverage(R_raw, xi, 0.5)
    print(f"\nLemma 1: Supply chain leverage L = {L:.3f} (expected ~1.47)")

    # Theorem 2: Red Queen equilibrium
    rq = red_queen_equilibrium(
        theta=0.12, phi=0.25, I_bar=1.0,
        delta_threat=0.08, gamma_threat=0.35, S_threat_min=0.10
    )
    print(f"\nTheorem 2: Red Queen Equilibrium")
    print(f"  S*_threat     = {rq['S_threat_star']:.4f}")
    print(f"  R*_system     = {rq['R_system_star']:.4f}")
    print(f"  R*_effective  = {rq['R_eff_star']:.4f}")
    print(f"  Contraction   = {rq['contraction_factor']:.4f} < 1: {rq['is_contractive']}")
    print(f"  Eigenvalue    = {rq['eigenvalue']:.4f} < 0: {rq['is_stable']}")

    # Super-additivity
    sa = compute_super_additivity(params)
    print(f"\nSuper-Additivity Check:")
    print(f"  Sum of individual gains: {sa['sum_individual']:.4f}")
    print(f"  Joint gain:              {sa['joint_gain']:.4f}")
    print(f"  Super-additive:          {sa['super_additive']} "
          f"(ratio: {sa['ratio']:.2f})")

    # ── 3. Adversary Dynamics ─────────────────────────────────────────────
    separator("3. ADVERSARY DYNAMICS & RED QUEEN EFFECT (Fig. 8-9)")
    plot_adversary_dynamics(baseline, os.path.join(OUTPUT_DIR, "adversary_dynamics.png"))
    print(f"\n  → Saved: adversary_dynamics.png")

    # Erosion analysis
    for yr in [10, 15, 20]:
        idx = np.argmin(np.abs(baseline["time"] - yr))
        erosion = red_queen_erosion_pct(
            baseline["R_system"][idx], baseline["states"][idx, 5],
            params.gamma_threat, params.S_threat_min
        )
        print(f"  Year {yr}: Erosion = {erosion:.1f}%")

    # ── 4. Strategy Comparison ────────────────────────────────────────────
    separator("4. STRATEGY COMPARISON (Table VI)")
    strat_results = run_strategy_comparison(T=20.0, params=params)
    print_strategy_table(strat_results)
    plot_strategy_comparison(strat_results,
                            os.path.join(OUTPUT_DIR, "strategy_comparison.png"))
    print(f"\n  → Saved: strategy_comparison.png")

    # ── 5. Monte Carlo Simulation ─────────────────────────────────────────
    separator("5. MONTE CARLO SIMULATION (Fig. 10)")
    n_mc = 500  # Use 10000 for paper-quality; 500 for speed
    print(f"  Running {n_mc} MC iterations (use 10000 for paper quality)...")
    mc = monte_carlo_simulation(n_iterations=n_mc, T=20.0, rng=rng, verbose=True)

    print(f"\nMC Statistics at Year 10:")
    yr10_idx = np.argmin(np.abs(mc["time"] - 10))
    R_yr10 = mc["R_system_all"][:, yr10_idx]
    print(f"  Mean:   {np.mean(R_yr10):.3f}")
    print(f"  Median: {np.median(R_yr10):.3f}")
    print(f"  Std:    {np.std(R_yr10):.3f}")
    print(f"  80% CI: [{np.percentile(R_yr10, 10):.3f}, {np.percentile(R_yr10, 90):.3f}]")
    print(f"  CV:     {np.std(R_yr10)/np.mean(R_yr10)*100:.1f}%")

    # Robustness
    rob = robustness_check(mc)
    print(f"\nRobustness (Table VIII):")
    for k, v in rob.items():
        print(f"  {k:<35}: {v:.1f}%")

    plot_monte_carlo_distributions(mc, os.path.join(OUTPUT_DIR, "monte_carlo_distributions.png"))
    print(f"\n  → Saved: monte_carlo_distributions.png")

    # ── 6. Sobol Sensitivity Analysis ─────────────────────────────────────
    separator("6. SOBOL SENSITIVITY ANALYSIS (Table VII, Fig. 7)")
    n_sobol = 128  # Use 512+ for paper quality
    print(f"  Running Sobol with N={n_sobol} base samples...")
    sobol_results = run_sobol_analysis(n_samples=n_sobol, eval_year=10.0,
                                       full=True, verbose=True)
    print_sobol_table(sobol_results)
    plot_sensitivity_tornado(sobol_results,
                            os.path.join(OUTPUT_DIR, "sensitivity_tornado.png"))
    print(f"\n  → Saved: sensitivity_tornado.png")

    # ── 7. Copula Analysis ────────────────────────────────────────────────
    separator("7. COPULA CORRELATED FAILURE ANALYSIS")
    sweep = copula_sweep(n_samples=5000, rng=rng)
    print_copula_results(sweep)

    impact = copula_strategy_impact(rho=0.4, n_samples=5000, rng=rng)
    print(f"\nHolistic still best at ρ=0.4: {impact['holistic_still_best']}")

    plot_copula_analysis(sweep, os.path.join(OUTPUT_DIR, "copula_analysis.png"))
    print(f"\n  → Saved: copula_analysis.png")

    # ── 8. Expert Elicitation ─────────────────────────────────────────────
    separator("8. BAYESIAN DELPHI AGGREGATION (Fig. 4)")
    print("  Running Bayesian aggregation for all 17 parameters...")
    delphi = run_full_delphi_aggregation(rng=rng)

    print(f"\n{'Parameter':<15} {'Posterior Mean':>15} {'80% CI':>25} {'R-hat':>8}")
    print("-" * 68)
    for sym, info in list(delphi.items())[:8]:
        agg = info["aggregation"]
        ci = agg["ci_80"]
        print(f"{sym:<15} {agg['posterior_mean']:>15.4f} "
              f"[{ci[0]:.4f}, {ci[1]:.4f}]{' ':>5} {agg['R_hat']:>7.3f}")

    plot_posterior_distributions(delphi,
                                os.path.join(OUTPUT_DIR, "posterior_distributions.png"))
    print(f"\n  → Saved: posterior_distributions.png")

    # ── 9. Validation ─────────────────────────────────────────────────────
    separator("9. MODEL VALIDATION")

    d = get_dataset()
    cv = cross_validate(n_folds=10, rng=rng, params=params)
    print(f"\nComparative Performance, 10-fold CV on the disclosed coded corpus")
    print(f"(n={cv['n_incidents']}; Appendix H.3 catalog + S.4 implication matrix)")
    print("-" * 66)
    print(f"{'Model':<22}{'RMSE':>8}{'r':>8}{'MAPE':>9}")
    print("-" * 66)
    for m, label in [("naive_mean", "Naive mean"), ("fair", "Static risk (FAIR)"),
                     ("resilience_triangle", "Resilience triangle"),
                     ("linear_additive", "Linear additive"),
                     ("independent", "Indep. dimensions"),
                     ("proposed", "Proposed (full)")]:
        x = cv[m]
        print(f"{label:<22}{x['rmse']:>8.3f}{x['correlation']:>8.2f}{x['mape']:>8.1f}%")
    print("-" * 66)
    print("  Note: disclosed-subset metrics differ from the paper's full-corpus")
    print("  values (0.42 / 0.78): 7 member-confidential incidents are withheld")
    print("  and the S.3 anchored coding is deterministic on this subset.")

    rc = reconstruction_criterion(params=params)
    print(f"\nPre-registered criterion (Appendix S.2, r>=0.6 & MAPE<=20%): "
          f"r={rc['r']:.2f}, MAPE={rc['mape']:.1f}% -> "
          f"{'MET' if rc['meets_criterion'] else 'NOT MET'}")

    tsv = temporal_split_validation(params=params)
    print(f"\nTemporal Split (train 2007-2017, test 2018-2022):")
    print(f"  Calibration: RMSE={tsv['calibration']['rmse']:.3f}, "
          f"r={tsv['calibration']['correlation']:.3f} (n={tsv['n_train']})")
    print(f"  Validation:  RMSE={tsv['validation']['rmse']:.3f}, "
          f"r={tsv['validation']['correlation']:.3f} (n={tsv['n_test']})")

    ppc = posterior_predictive_check(n_sims=1000, rng=rng)
    print(f"\nPosterior Predictive p-value: {ppc['p_value']:.3f}")

    plot_validation_residuals(cv["proposed"],
                              os.path.join(OUTPUT_DIR, "residual_analysis.png"))
    print(f"\n  → Saved: residual_analysis.png")

    # ── 10. Case Studies ──────────────────────────────────────────────────
    separator("10. CASE STUDIES")

    viasat = viasat_case_study(params)
    print_case_study(viasat, "2022 Viasat KA-SAT Disruption")

    starlink = starlink_case_study(params)
    print_case_study(starlink, "2022 Starlink RF Interference")

    from analysis.case_studies import ahp_posture_index
    print(f"\nAHP-weighted posture indices (main-text operational comparison):")
    print(f"  Viasat KA-SAT : {ahp_posture_index(viasat['posture'], params):.3f}  (paper ~0.27)")
    print(f"  Starlink      : {ahp_posture_index(starlink['posture'], params):.3f}  (paper ~0.48)")

    # ── 11. AHP Weight Sensitivity ────────────────────────────────────────
    separator("11. AHP WEIGHT SENSITIVITY")
    ahp = ahp_weight_sensitivity(T=20.0, params=params)
    print(f"\n{'Scenario':<25} {'R_sys (yr10)':>12} {'R_eff (yr10)':>12}")
    print("-" * 52)
    for name, res in ahp.items():
        print(f"{name:<25} {res['R_system_yr10']:>12.3f} {res['R_effective_yr10']:>12.3f}")

    # ── 12. Operational-Constraint Scenarios (C1-C3) ──────────────────────
    separator("12. OPERATIONAL-CONSTRAINT SCENARIOS (C1-C3, Appendix P)")

    cs = run_constraint_scenarios(params)
    print(f"\nReference holistic advantage (yr 10): "
          f"{cs['reference']['holistic_advantage_yr10']:.1f}%")
    print(f"C1 budget simplex w/ premiums:        "
          f"{cs['C1_budget']['holistic_advantage_yr10']:.1f}%  "
          f"(paper: 11.6% -> 9.4%)")
    c2 = cs["C2_adversary_cap"]
    print(f"C2 tight cap (A_max=0.85): erosion(20) = {c2['erosion_yr20_pct']:.1f}% "
          f"(bounded <24%: {c2['erosion_bounded_below_24pct']})")
    print(f"   Red Queen tax multiplier yr 20: capped {c2['tax_multiplier_yr20_capped']:.2f}x "
          f"vs unbounded {c2['tax_multiplier_yr20_unbounded']:.2f}x")
    c3 = cs["C3_replacement"]
    print(f"C3 replacement (T_cyc=5): resilience {c3['resilience_gain_pct']:+.1f}%, "
          f"cost {c3['cost_increase_pct']:+.1f}%  (paper: +4% / +22%)")

    # ── 13. Prior-Perturbation Robustness (Appendix Q.1) ──────────────────
    separator("13. PRIOR-PERTURBATION ROBUSTNESS (Appendix Q.1)")

    pp = run_adverse_shift(params)
    for label in ["baseline", "adverse_joint_shift"]:
        r_ = pp[label]
        print(f"\n{label}:")
        print(f"  Holistic advantage (yr10): {r_['holistic_advantage_yr10']:.1f}%")
        print(f"  Red Queen erosion (yr10):  {r_['red_queen_erosion_yr10']:.1f}%")
        print(f"  Supply-chain leverage L:   {r_['supply_chain_leverage']:.2f}")
    surv = pp["conclusions_survive"]
    print(f"\nPolicy conclusions survive adverse shift "
          f"(theta=0.15, eta=0.38, gamma=0.98):")
    print(f"  Holistic advantage > 0: {surv['holistic_still_positive']}")
    print(f"  Leverage L > 1:         {surv['leverage_still_gt_1']}")
    print(f"  Erosion > 10%:          {surv['erosion_still_gt_10pct']}")

    # ── 14. Extreme-Condition Tests (Appendix B.1 / I.3) ──────────────────
    separator("14. EXTREME-CONDITION TESTS (TC01-TC08)")
    from tests.test_extreme_conditions import run_all_tc
    run_all_tc()

    # ── Summary ───────────────────────────────────────────────────────────
    separator("SUMMARY OF KEY FINDINGS")
    elapsed = time.time() - t0

    idx10 = np.argmin(np.abs(baseline["time"] - 10))
    idx15 = np.argmin(np.abs(baseline["time"] - 15))

    holistic_adv_10 = (strat_results["holistic"]["metrics"]["yr10_R_eff"] -
                       strat_results["baseline"]["metrics"]["yr10_R_eff"]) / \
                      strat_results["baseline"]["metrics"]["yr10_R_eff"] * 100
    holistic_adv_15 = (strat_results["holistic"]["metrics"]["yr15_R_eff"] -
                       strat_results["baseline"]["metrics"]["yr15_R_eff"]) / \
                      strat_results["baseline"]["metrics"]["yr15_R_eff"] * 100

    print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │ Finding                        │ Result                 │
  ├─────────────────────────────────────────────────────────┤
  │ Growth pattern                 │ Logistic (3 phases)    │
  │ Holistic advantage (yr 10)     │ +{holistic_adv_10:.1f}%               │
  │ Holistic advantage (yr 15)     │ +{holistic_adv_15:.1f}%               │
  │ Supply chain leverage          │ {L:.2f}×                │
  │ Red Queen erosion (yr 10)      │ {red_queen_erosion_pct(baseline["R_system"][idx10], baseline["states"][idx10, 5], params.gamma_threat, params.S_threat_min):.1f}%              │
  │ Red Queen erosion (yr 20)      │ {red_queen_erosion_pct(baseline["R_system"][-1], baseline["states"][-1, 5], params.gamma_threat, params.S_threat_min):.1f}%              │
  │ Super-additivity               │ {'Confirmed' if sa['super_additive'] else 'Not confirmed':<22} │
  │ MC logistic pattern            │ {rob.get('logistic_growth', 0):.0f}% of runs           │
  └─────────────────────────────────────────────────────────┘

  Output directory: {OUTPUT_DIR}
  Total runtime:    {elapsed:.1f} seconds
  Figures generated: {len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')])}
""")

    print("Done! All analyses complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
