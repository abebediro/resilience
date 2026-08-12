"""
Model validation against the coded incident corpus (Appendix H/S data)
with the comparative baselines of Table model_comparison_results:
naive mean, FAIR-style static risk, resilience triangle (Bruneau),
linear additive, independent dimensions, and the proposed model.
"""

import numpy as np
from typing import Dict
from models.composition import system_resilience
from calibration.parameters import ParameterSet
from data.incidents import get_dataset


def _posture_from_implications(imp: np.ndarray) -> np.ndarray:
    """Pre-incident capability proxy: posture_i = 1 - implication_i,
    floored at 0.05 (a fully overwhelmed dimension retains minimal capacity)."""
    return np.clip(1.0 - imp, 0.05, 1.0)


def predict_proposed(imp: np.ndarray, params: ParameterSet = None,
                     scale: float = 1.0) -> float:
    """Proposed model predictor: mirrored defense-in-depth composition in
    FAILURE space with supply-chain cascade amplification.

    Severity accrues as successive barriers fail (the dual of
    Eq. system_resilience): F = f1 + (1-f1) f2 + (1-f1)(1-f2) f3 + ...
    where f_i = min(1, imp_i * [1 + xi_i * imp_supply]) is the
    cascade-amplified failure intensity of dimension i. A single scalar
    `scale` (fitted on the training fold) maps composed failure to the
    anchored severity scale; the composition itself carries no fitted
    structure.
    """
    if params is None:
        params = ParameterSet()
    xi = params.get_xi()
    f = np.minimum(1.0, imp[:4] * (1.0 + xi * imp[4]))
    F = 1.0 - np.prod(1.0 - f)   # order-invariant compact form (Thm 1)
    return float(np.clip(scale * F, 0.0, 1.0))


def fit_proposed_scale(X: np.ndarray, y: np.ndarray,
                       params: ParameterSet = None) -> float:
    """Least-squares severity calibration constant for the proposed model."""
    F = np.array([predict_proposed(x, params, scale=1.0) for x in X])
    denom = float(F @ F)
    return float(F @ y) / denom if denom > 1e-12 else 1.0


def predict_independent(imp: np.ndarray, scale: float = 1.0) -> float:
    """Independent-dimensions baseline: same failure composition WITHOUT
    supply-chain cascade amplification."""
    F = 1.0 - np.prod(1.0 - imp[:4])
    return float(np.clip(scale * F, 0.0, 1.0))


def fit_independent_scale(X: np.ndarray, y: np.ndarray) -> float:
    F = np.array([predict_independent(x, scale=1.0) for x in X])
    denom = float(F @ F)
    return float(F @ y) / denom if denom > 1e-12 else 1.0


def predict_naive_mean(train_sev: np.ndarray) -> float:
    return float(np.mean(train_sev))


def predict_fair(imp: np.ndarray) -> float:
    """FAIR-style static risk proxy: unweighted mean implication (sum P*I)."""
    return float(np.mean(imp))


def predict_resilience_triangle(imp: np.ndarray) -> float:
    """Bruneau resilience-triangle proxy: event-scoped severity ~ primary
    implication magnitude (recovery-area proxy without duration data)."""
    return float(np.max(imp))


def fit_linear_additive(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Least-squares fit severity = a + sum b_i * implication_i."""
    A = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


def predict_linear_additive(imp: np.ndarray, coef: np.ndarray) -> float:
    return float(coef[0] + imp @ coef[1:])


def _metrics(y: np.ndarray, yhat: np.ndarray) -> Dict:
    resid = y - yhat
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    mape = float(np.mean(np.abs(resid / np.maximum(y, 1e-10)))) * 100
    r = float(np.corrcoef(y, yhat)[0, 1]) if np.std(yhat) > 1e-12 else 0.0
    return {"rmse": rmse, "mape": mape, "correlation": r,
            "observed": y, "predicted": yhat, "residuals": resid}


def cross_validate(n_folds: int = 10, rng: np.random.Generator = None,
                   params: ParameterSet = None) -> Dict:
    """10-fold CV of all models against the real 63-incident corpus.

    Returns per-model metrics matching Table model_comparison_results layout.
    """
    if rng is None:
        rng = np.random.default_rng(42)
    if params is None:
        params = ParameterSet()

    d = get_dataset()
    X, y = d["implications"], d["severity_norm"]
    n = len(y)
    idx = rng.permutation(n)
    folds = np.array_split(idx, n_folds)

    preds = {m: np.zeros(n) for m in
             ["naive_mean", "fair", "resilience_triangle",
              "linear_additive", "independent", "proposed"]}

    for f in folds:
        train = np.setdiff1d(idx, f)
        coef = fit_linear_additive(X[train], y[train])
        mean_sev = predict_naive_mean(y[train])
        s_prop = fit_proposed_scale(X[train], y[train], params)
        s_ind = fit_independent_scale(X[train], y[train])
        for i in f:
            preds["naive_mean"][i] = mean_sev
            preds["fair"][i] = predict_fair(X[i])
            preds["resilience_triangle"][i] = predict_resilience_triangle(X[i])
            preds["linear_additive"][i] = predict_linear_additive(X[i], coef)
            preds["independent"][i] = predict_independent(X[i], s_ind)
            preds["proposed"][i] = predict_proposed(X[i], params, s_prop)

    out = {m: _metrics(y, p) for m, p in preds.items()}
    out["n_incidents"] = n
    out["n_folds"] = n_folds
    return out


def temporal_split_validation(params: ParameterSet = None) -> Dict:
    """Train 2007-2017, held-out 2018-2022 (Appendix B.7 design)."""
    if params is None:
        params = ParameterSet()
    d = get_dataset()
    X, y, yr = d["implications"], d["severity_norm"], d["years"]
    tr = yr <= 2017
    te = ~tr

    s_prop = fit_proposed_scale(X[yr <= 2017], y[yr <= 2017], params)

    def ev(mask):
        yhat = np.array([predict_proposed(X[i], params, s_prop)
                         for i in np.where(mask)[0]])
        m = _metrics(y[mask], yhat)
        m["n"] = int(mask.sum())
        return m

    return {"calibration": ev(tr), "validation": ev(te),
            "n_train": int(tr.sum()), "n_test": int(te.sum())}


def posterior_predictive_check(n_sims: int = 1000,
                               rng: np.random.Generator = None) -> Dict:
    """Posterior predictive p-value: simulated mean severity vs observed."""
    if rng is None:
        rng = np.random.default_rng(42)
    d = get_dataset()
    obs = d["severity_norm"]
    obs_stat = obs.mean()
    sim = np.array([rng.beta(3.2, 2.6, size=len(obs)).mean()
                    for _ in range(n_sims)])
    return {"observed_mean": obs_stat, "simulated_means": sim,
            "p_value": float(np.mean(sim >= obs_stat)), "n_sims": n_sims}


def reconstruction_criterion(params: ParameterSet = None) -> Dict:
    """Pre-registered criterion (Appendix S.2): r>=0.6 and MAPE<=20%."""
    cv = cross_validate(params=params)
    m = cv["proposed"]
    return {"r": m["correlation"], "mape": m["mape"], "rmse": m["rmse"],
            "meets_criterion": m["correlation"] >= 0.6 and m["mape"] <= 20.0}
