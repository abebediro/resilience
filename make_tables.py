"""Generate LaTeX result tables from live model output (IEEE booktabs style)."""
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
np.random.seed(42)

from calibration.parameters import ParameterSet, PARAMETER_TABLE
from calibration.validation import (cross_validate, temporal_split_validation,
                                    reconstruction_criterion)
from models.system import SpaceResilienceModel
from models.composition import supply_chain_leverage
from analysis.strategies import run_strategy_comparison
from analysis.sensitivity import run_sobol_analysis
from analysis.constraint_scenarios import run_constraint_scenarios
from analysis.prior_perturbation import run_adverse_shift
from analysis.case_studies import viasat_case_study, starlink_case_study, ahp_posture_index

params = ParameterSet()
rng = np.random.default_rng(42)
OUT = []
def w(s): OUT.append(s)

def header(caption, label, cols, colspec):
    w(r"\begin{table}[!t]")
    w(r"\centering")
    w(rf"\caption{{{caption}}}")
    w(rf"\label{{{label}}}")
    w(r"\scriptsize")
    w(r"\renewcommand{\arraystretch}{1.15}")
    w(rf"\begin{{tabular}}{{{colspec}}}")
    w(r"\toprule")
    w(" & ".join(cols) + r" \\")
    w(r"\midrule")

def footer():
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w("")

# ---------- Table 1: Baseline trajectory ----------
m = SpaceResilienceModel(params)
r = m.simulate(T=20, dt=0.25)
def at(t):
    i = np.argmin(np.abs(r["time"]-t)); return i
w(r"% ===== Table: Baseline Resilience Trajectory (live model output) =====")
header("Baseline Resilience Trajectory (Model-Conditional)", "tab:baseline_live",
       [r"\textbf{Year}", r"\textbf{$R_{sys}$}", r"\textbf{$R_{eff}$}",
        r"\textbf{Threat}", r"\textbf{Erosion}"], "ccccc")
prev = None
for t in [0,3,5,8,10,15,20]:
    i = at(t); rs=r["R_system"][i]; re=r["R_effective"][i]; th=r["states"][i,5]
    ero = (rs-re)/rs*100 if rs>0 else 0
    w(f"{t} & {rs:.3f} & {re:.3f} & {th:.3f} & {ero:.1f}\\% \\\\")
footer()

# ---------- Table 2: Comparative validation ----------
cv = cross_validate(n_folds=10, rng=np.random.default_rng(42), params=params)
w(r"% ===== Table: Comparative Performance on disclosed corpus (live) =====")
header("Comparative Performance Against Baseline Models (10-fold CV, disclosed $n=63$)",
       "tab:validation_live",
       [r"\textbf{Model}", r"\textbf{RMSE}", r"\textbf{$r$}", r"\textbf{MAPE}"],
       "lccc")
labels = [("naive_mean","Naive mean"),("fair","Static risk (FAIR)"),
          ("resilience_triangle","Resilience triangle"),
          ("linear_additive","Linear additive"),
          ("independent","Independent dimensions"),
          ("proposed",r"\textbf{Proposed (full)}")]
for k,lab in labels:
    x=cv[k]
    bold = k=="proposed"
    rmse=f"\\textbf{{{x['rmse']:.3f}}}" if bold else f"{x['rmse']:.3f}"
    rr=f"\\textbf{{{x['correlation']:.2f}}}" if bold else f"{x['correlation']:.2f}"
    mp=f"\\textbf{{{x['mape']:.1f}\\%}}" if bold else f"{x['mape']:.1f}\\%"
    w(f"{lab} & {rmse} & {rr} & {mp} \\\\")
footer()

# ---------- Table 3: Strategy comparison ----------
strat = run_strategy_comparison(T=20, params=params)
w(r"% ===== Table: Strategy performance (live) =====")
header("Strategy Performance at Year 10 (Model-Conditional)", "tab:strategy_live",
       [r"\textbf{Strategy}", r"\textbf{$R_{sys}$ (yr10)}",
        r"\textbf{$R_{eff}$ (yr10)}", r"\textbf{$\Delta$ vs base}"], "lccc")
base_eff = strat["baseline"]["metrics"]["yr10_R_eff"]
order = ["baseline","preparedness","resistance","restoration","adaptation","supply_chain","holistic"]
for s in order:
    if s not in strat: continue
    mt = strat[s]["metrics"]
    delta = (mt["yr10_R_eff"]-base_eff)/base_eff*100
    name = s.replace("_"," ").title()
    dstr = "--" if s=="baseline" else f"{delta:+.1f}\\%"
    bold = s=="holistic"
    if bold:
        w(f"\\textbf{{{name}}} & \\textbf{{{mt['yr10_R_sys']:.3f}}} & "
          f"\\textbf{{{mt['yr10_R_eff']:.3f}}} & \\textbf{{{dstr}}} \\\\")
    else:
        w(f"{name} & {mt['yr10_R_sys']:.3f} & {mt['yr10_R_eff']:.3f} & {dstr} \\\\")
footer()

# ---------- Table 4: Sobol sensitivity ----------
sob = run_sobol_analysis(n_samples=512)
w(r"% ===== Table: Sobol sensitivity indices (live) =====")
header("Parameter Sensitivity (Sobol Indices, Year 10)", "tab:sobol_live",
       [r"\textbf{\#}", r"\textbf{Parameter}", r"\textbf{$S_i$}",
        r"\textbf{$S_{Ti}$}"], "clcc")
rows = sob["rankings"]
for row in rows[:8]:
    nm = row["parameter"].replace("_","\\_")
    w(f"{row['rank']} & ${nm}$ & {row['S1']:.3f} & {row['ST']:.3f} \\\\")
footer()

# ---------- Table 5: Constraint scenarios C1-C3 ----------
cs = run_constraint_scenarios(params)
w(r"% ===== Table: Operational constraint scenarios (live) =====")
header("Operational-Constraint Scenario Effects (C1--C3)", "tab:constraints_live",
       [r"\textbf{Constraint}", r"\textbf{Metric}", r"\textbf{Value}"], "llc")
c2=cs["C2_adversary_cap"]; c3=cs["C3_replacement"]
w(f"Reference & Holistic advantage (yr10) & {cs['reference']['holistic_advantage_yr10']:.1f}\\% \\\\")
w(f"C1 budget & Holistic advantage (yr10) & {cs['C1_budget']['holistic_advantage_yr10']:.1f}\\% \\\\")
w(f"C2 cap (0.85) & Erosion (yr20) & {c2['erosion_yr20_pct']:.1f}\\% \\\\")
w(f"C2 cap (0.85) & Tax mult.\\ yr20 (capped) & {c2['tax_multiplier_yr20_capped']:.2f}$\\times$ \\\\")
w(f"C2 uncapped & Tax mult.\\ yr20 & {c2['tax_multiplier_yr20_unbounded']:.2f}$\\times$ \\\\")
w(f"C3 ($T_{{cyc}}{{=}}5$) & Mean resilience gain & {c3['resilience_gain_pct']:+.1f}\\% \\\\")
w(f"C3 ($T_{{cyc}}{{=}}5$) & Cumulative cost & {c3['cost_increase_pct']:+.1f}\\% \\\\")
footer()

# ---------- Table 6: Prior perturbation ----------
pp = run_adverse_shift(params)
w(r"% ===== Table: Prior-perturbation robustness (live) =====")
header("Year-10 Policy Conclusions under Adverse Prior Perturbation",
       "tab:perturbation_live",
       [r"\textbf{Conclusion}", r"\textbf{Baseline}", r"\textbf{Adverse Shift}"], "lcc")
b=pp["baseline"]; a=pp["adverse_joint_shift"]
w(f"Holistic advantage & {b['holistic_advantage_yr10']:.1f}\\% & {a['holistic_advantage_yr10']:.1f}\\% \\\\")
w(f"Supply-chain leverage $L$ & {b['supply_chain_leverage']:.2f} & {a['supply_chain_leverage']:.2f} \\\\")
w(f"Red Queen erosion & {b['red_queen_erosion_yr10']:.1f}\\% & {a['red_queen_erosion_yr10']:.1f}\\% \\\\")
footer()

# ---------- Table 7: Case studies ----------
v=viasat_case_study(params); s=starlink_case_study(params)
w(r"% ===== Table: Case-study posture indices (live) =====")
header("Retrodictive Case-Study Posture Indices", "tab:cases_live",
       [r"\textbf{Case}", r"\textbf{AHP Posture}", r"\textbf{Observed Outcome}"], "lcp{3.4cm}")
w(f"Viasat KA-SAT (2022) & {ahp_posture_index(v['posture'],params):.3f} & "
  r"Catastrophic; $\approx$45-day physical recovery \\")
w(f"Starlink (2022) & {ahp_posture_index(s['posture'],params):.3f} & "
  r"Localized; days-scale disruption \\")
footer()

# ---------- Table 8: Calibrated parameters ----------
w(r"% ===== Table: Calibrated parameter set (Table V) =====")
w(r"\begin{table}[!t]")
w(r"\centering")
w(r"\caption{Calibrated Parameter Set with Uncertainty and Identifiability Class}")
w(r"\label{tab:params_live}")
w(r"\scriptsize")
w(r"\renewcommand{\arraystretch}{1.1}")
w(r"\begin{tabular}{llccl}")
w(r"\toprule")
w(r"\textbf{Parameter} & \textbf{Sym.} & \textbf{Value} & \textbf{80\% CI} & \textbf{Class} \\")
w(r"\midrule")
for p in PARAMETER_TABLE:
    sym = p.symbol.replace("_","\\_")
    w(f"{p.name} & ${sym}$ & {p.value:g} & [{p.ci_80[0]:g}, {p.ci_80[1]:g}] & {p.ident_class} \\\\")
w(r"\bottomrule")
w(r"\end{tabular}")
w(r"\end{table}")
w("")

open("output_pdf/result_tables.tex","w").write("\n".join(OUT))
print("Wrote", len(OUT), "lines to result_tables.tex")
print("\n--- Preview (first 40 lines) ---")
print("\n".join(OUT[:40]))
