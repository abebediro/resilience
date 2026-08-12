# A Tripartite Model for Space Cybersecurity Resilience

A. Diro, A. An, A. Tullu (RMIT University, 2026)

Single source repository for the paper *"A Tripartite Model for Space
Cybersecurity Resilience."* It combines the **working Python
implementation** (system-dynamics model, calibration, analysis,
figures) with the **archival research data and extended documentation**
that the page-limited journal supplement references but does not
reproduce.

**Citation:** [paper DOI, once assigned]
**Data DOI:** [Zenodo/OSF DOI, once minted]

## The model

A tripartite resilience model combining:
1. **Resilience engineering** — five-dimensional stock-flow dynamics
2. **Complex adaptive systems** — adversary–defender co-evolution (Red Queen)
3. **Mission assurance** — environment-modulated degradation and supply-chain cascades

## Repository layout

```
.                              # working implementation (run from here)
├── models/                    # stock-flow dimensions, composition (Eq. 1),
│                              #   adversary (Red Queen), environment, integrated system
├── calibration/              # calibrated parameters (Table V), Bayesian Delphi
│                              #   aggregation, cross-validation
├── analysis/                 # Monte Carlo, Sobol sensitivity, strategy comparison,
│                              #   copula (correlated failure), Viasat/Starlink case studies,
│                              #   constraint scenarios, prior-perturbation robustness
├── data/                     # 63 disclosed incidents + implication matrix embedded for the model
├── visualization/            # all paper figures
├── tests/                    # unit + property + extreme-condition tests
├── run_all.py                # full analysis pipeline (figures + tables)
├── run_all_pdf.py            # pipeline with PDF result document
├── make_tables.py            # result tables
├── output/  output_pdf/      # generated figures, tables, and result document
│
└── supplementary/            # archival data & documentation (appendix material)
    ├── delphi/               # consent form, Round-1 questionnaire, expert panel,
    │                         #   per-expert raw responses, convergence, final params, AHP, Bayesian model   
    ├── incidents/            # 63 disclosed incidents (catalog + coding matrix), coding
    │                         #   manual, source verification, summary stats, attribution        
    ├── extended_analysis/    # full sensitivity tables, Viasat case study, limitations, cost
    │                         #   functions, cross-background, epistemic provenance, operational
    │                         #   constraints, deployment pathway, extended derivations  
    ├── reference/            # nomenclature, glossary                                       
    ├── validation/           # model validation & selection diagnostics                    
    ├── vensim/               # Vensim system-dynamics equation listing                     
    └── appendix_reference_code_notes/   # notes on the appendix reference transcription (see below)
```

The **core proofs** (Theorem 1, Theorem 2, Corollary 1, Lemma 1) and the
identifiability analysis are included in the  Supplementary Material, not here — see the manuscript.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full analysis pipeline (all figures + tables)
python run_all.py

# With PDF result document
python run_all_pdf.py

# Specific analyses
python -m analysis.simulation      # Monte Carlo
python -m analysis.sensitivity     # Sobol sensitivity
python -m analysis.strategies      # strategy comparison
python -m analysis.case_studies    # Viasat & Starlink

# Tests
python -m pytest tests/
```

## Key results

- **Logistic resilience growth** across three phases (foundation → acceleration → maturation)
- **Holistic strategy superiority**: ~16.3% over specialized strategies at year 15
- **Supply-chain leverage**: 1.47× cross-dimensional returns
- **Red Queen erosion**: 18–21% effective resilience loss without countermeasures

## Reproduction notes (paper v2: Diro, An & Tullu)

- Initial conditions / AHP weights follow Appendix A.10 / A.11.
- Reference dynamics (phase-based investment, efficiency curves,
  time-varying environment) follow Appendix I (Vensim) / K (Python).
- Operational constraints C1–C3 (Appendix P) are implemented: budget-premium
  simplex, finite-adversary logistic cap (default on, `A_max=0.975`), and
  satellite replacement cycles.
- Real incident data: the 63 disclosed incidents (Appendix H.3) and the
  anchored implication matrix (Appendix S.4) are embedded in `data/incidents.py`;
  their raw catalog and coding manual are in `supplementary/incidents/`.
  Disclosed-subset validation metrics (RMSE 0.064, r 0.93, MAPE 10%) differ
  from the paper's full-corpus values (0.42 / 0.78) because 7 member-confidential
  incidents are withheld.
- Calibration: a single global `investment_scale` (=0.20) plus the C2 cap
  reconciles the headline main-text targets (R_sys(10)≈0.91, Red Queen erosion
  ≈16–20%). This resolves the face-value mismatch between the printed
  Appendix I/K listing and the published trajectory table — see
  `supplementary/appendix_reference_code_notes/`.
- Case-study figures R_system≈0.27 (Viasat) / ≈0.48 (Starlink) are the
  AHP-weighted posture indices, reproduced in `analysis/case_studies.py`.

## A note on the two code paths

The maintained implementation is the package at the repository root; run it.
The appendix also printed a compact *reference transcription* of the model;
its known discrepancies (and why the maintained code differs) are documented
in `supplementary/appendix_reference_code_notes/KNOWN_ISSUES.md`. The
transcription itself is not carried here to avoid two divergent copies of the
same model — the paper's appendix and the notes preserve its provenance.


## License

Data and documentation: CC-BY 4.0. Code: MIT. See `LICENSE`. Confirm before
publishing — these are the suggested defaults, not a venue requirement.

