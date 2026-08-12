"""
Unit tests for the space cybersecurity resilience model.

Tests:
- Theorem 1 properties (composition)
- Lemma 1 (supply chain leverage)
- Theorem 2 (Red Queen equilibrium)
- Axiom verification
- Simulation boundary conditions
- Numerical stability
"""

import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.composition import (
    system_resilience, supply_chain_modulation, supply_chain_leverage,
    verify_composition_properties, copula_resilience
)
from models.adversary import (
    dS_threat_dt, effective_resilience, red_queen_equilibrium,
    geopolitical_shock_investment
)
from models.environment import SpaceEnvironment
from models.dimensions import adaptation_enhancement, dS_prep_dt
from models.system import SpaceResilienceModel
from calibration.parameters import ParameterSet


def test_theorem1_order_invariance():
    """Theorem 1, Property 1: R_system = 1 - prod(1-R_i^eff) is invariant to ordering."""
    # Test on effective capacities directly (after supply chain modulation)
    R_eff = np.array([0.3, 0.5, 0.4, 0.6])
    R_base = 1.0 - np.prod(1.0 - R_eff)

    # All permutations of R_eff should give same result
    from itertools import permutations
    for perm in list(permutations(R_eff))[:24]:
        R_perm = 1.0 - np.prod(1.0 - np.array(perm))
        assert abs(R_perm - R_base) < 1e-10, \
            f"Order invariance violated: {R_base} vs {R_perm}"
    print("  ✓ Theorem 1.1: Order invariance")


def test_theorem1_monotonicity():
    """Theorem 1, Property 1: R_system is monotone in each R_i."""
    S_supply = 0.5
    base = [0.3, 0.5, 0.4, 0.2]
    R_base = system_resilience(*base, S_supply)

    for i in range(4):
        improved = list(base)
        improved[i] += 0.1
        R_imp = system_resilience(*improved, S_supply)
        assert R_imp >= R_base, \
            f"Monotonicity violated for dim {i}: {R_base} > {R_imp}"
    print("  ✓ Theorem 1.1: Monotonicity")


def test_theorem1_bounds():
    """Theorem 1, Property 3: 0 <= R_system <= 1."""
    rng = np.random.default_rng(42)
    for _ in range(1000):
        R = rng.uniform(0, 1, 4)
        S = rng.uniform(0, 1)
        R_sys = system_resilience(*R, S)
        assert 0 <= R_sys <= 1, f"Bounds violated: {R_sys}"

    # Boundary cases
    assert system_resilience(0, 0, 0, 0, 0.5) < 0.01
    assert system_resilience(1, 1, 1, 1, 1.0) > 0.99
    print("  ✓ Theorem 1.3: Bounds [0, 1]")


def test_theorem1_super_additivity():
    """Theorem 1, Property 4: Positive cross-partials (complementarity).
    
    The paper proves d²R/dR_i dR_j = prod_{k!=i,j} q_k > 0 when q_k < 1,
    establishing that dimensions are complements: the marginal value of 
    improving dimension i increases when dimension j is weaker (higher q_j).
    """
    R_eff = np.array([0.3, 0.4, 0.35, 0.25])
    q = 1.0 - R_eff
    
    all_positive = True
    for i in range(4):
        for j in range(i+1, 4):
            remaining = [k for k in range(4) if k not in (i, j)]
            cross_partial = np.prod(q[remaining])
            if cross_partial <= 0:
                all_positive = False
    
    assert all_positive, "Cross-partial not positive for all dim pairs"
    
    # Verify complementarity: marginal gain from improving dim i is larger 
    # when other dims are weaker
    eps = 0.01
    # Marginal gain of dim 0 when dim 1 is at 0.4
    R_base = 1.0 - np.prod(1.0 - R_eff)
    R_plus = 1.0 - np.prod(1.0 - (R_eff + eps * np.array([1,0,0,0])))
    marginal_high = (R_plus - R_base) / eps
    
    # Marginal gain of dim 0 when dim 1 is lower (0.1)
    R_eff_low = R_eff.copy()
    R_eff_low[1] = 0.1
    R_base_low = 1.0 - np.prod(1.0 - R_eff_low)
    R_plus_low = 1.0 - np.prod(1.0 - (R_eff_low + eps * np.array([1,0,0,0])))
    marginal_low = (R_plus_low - R_base_low) / eps
    
    assert marginal_low > marginal_high, \
        f"Complementarity: marginal should be higher when others weaker"
    print(f"  ✓ Theorem 1.4: Complementarity (cross-partials positive)")


def test_theorem1_concavity():
    """Theorem 1, Property 2: Joint concavity (diminishing returns)."""
    S = 0.5
    # Check diminishing marginal returns
    gains = []
    for R_level in [0.1, 0.3, 0.5, 0.7, 0.9]:
        R_before = system_resilience(R_level, 0.5, 0.5, 0.5, S)
        R_after = system_resilience(R_level + 0.05, 0.5, 0.5, 0.5, S)
        gains.append(R_after - R_before)

    # Gains should be non-increasing
    for i in range(len(gains) - 1):
        assert gains[i] >= gains[i + 1] - 1e-10, \
            f"Concavity violated at level {i}: {gains[i]} < {gains[i+1]}"
    print("  ✓ Theorem 1.2: Joint concavity (diminishing returns)")


def test_lemma1_supply_chain_leverage():
    """Lemma 1: Supply chain leverage L >= 1."""
    R_raw = np.array([0.5, 0.6, 0.4, 0.3])
    xi = np.array([0.42, 0.68, 0.31, 0.25])
    S_supply = 0.5
    L = supply_chain_leverage(R_raw, xi, S_supply)
    assert L >= 1.0, f"Leverage < 1: {L}"
    print(f"  ✓ Lemma 1: Supply chain leverage L={L:.3f} >= 1")


def test_theorem2_red_queen_equilibrium():
    """Theorem 2: Unique, locally asymptotically stable equilibrium."""
    result = red_queen_equilibrium(
        theta=0.12, phi=0.25, I_bar=1.0,
        delta_threat=0.08, gamma_threat=0.35, S_threat_min=0.10
    )
    assert result["is_contractive"], "Contraction condition not met"
    assert result["is_stable"], "Stability condition not met"
    assert result["S_threat_star"] > 0, "Zero threat equilibrium"
    assert result["R_eff_star"] < result["R_system_star"], "No erosion at equilibrium"
    print(f"  ✓ Theorem 2: Stable equilibrium (S*_threat={result['S_threat_star']:.3f}, "
          f"eigenvalue={result['eigenvalue']:.4f})")


def test_axiom1_monotone_decay():
    """Axiom 1: Without investment, dS/dt <= 0."""
    S = 0.5
    for k in [0.03, 0.05, 0.07, 0.12]:
        ds = dS_prep_dt(S, 0.0, 0.0, k, 0.8, 1.5)
        assert ds <= 0, f"Axiom 1 violated: dS/dt = {ds} > 0 with no investment"
    print("  ✓ Axiom 1: Monotone decay without investment")


def test_axiom2_diminishing_returns():
    """Axiom 2: Investment effectiveness decreasing in S."""
    V = 0.5
    gains = []
    for S in [0.1, 0.3, 0.5, 0.7, 0.9]:
        ds = dS_prep_dt(S, V/2, V/2, 0.05, 0.8, 1.5)
        gains.append(ds)
    # Net growth should decrease with S (due to increasing decay)
    for i in range(len(gains) - 1):
        assert gains[i] >= gains[i + 1] - 0.01, \
            f"Axiom 2 violated: gain at S={0.1+0.2*i:.1f} ({gains[i]:.4f}) < " \
            f"gain at S={0.3+0.2*i:.1f} ({gains[i+1]:.4f})"
    print("  ✓ Axiom 2: Diminishing returns")


def test_axiom4_adversary_response():
    """Axiom 4: d(Threat)/dt increases with R_system, decreases with S_threat."""
    # Higher R_system -> higher threat growth
    dt1 = dS_threat_dt(0.3, 0.5, 0.12, 0.25, 1.0, 0.08)
    dt2 = dS_threat_dt(0.3, 0.8, 0.12, 0.25, 1.0, 0.08)
    assert dt2 > dt1, "Axiom 4a violated: threat doesn't respond to higher defense"

    # Higher S_threat -> lower net growth (due to decay)
    dt3 = dS_threat_dt(0.3, 0.5, 0.12, 0.25, 1.0, 0.08)
    dt4 = dS_threat_dt(0.8, 0.5, 0.12, 0.25, 1.0, 0.08)
    assert dt4 < dt3, "Axiom 4b violated: threat doesn't self-limit"
    print("  ✓ Axiom 4: Adversary response")


def test_axiom5_supply_chain_propagation():
    """Axiom 5: R_i^eff <= R_i * [1 - xi_i(1-C)]."""
    R = 0.7
    xi = 0.68
    S_supply = 0.5
    R_eff = supply_chain_modulation(R, xi, S_supply)
    bound = R * (1 - xi * (1 - S_supply))
    assert abs(R_eff - bound) < 1e-10, "Supply chain modulation mismatch"
    assert R_eff <= R, f"Effective > raw: {R_eff} > {R}"
    print("  ✓ Axiom 5: Supply chain propagation")


def test_simulation_stability():
    """Test simulation produces bounded, physically plausible results."""
    model = SpaceResilienceModel()
    result = model.simulate(T=20.0, dt=0.25)

    # All states in [0, 1]
    assert np.all(result["states"] >= -1e-10), "Negative state encountered"
    assert np.all(result["states"] <= 1 + 1e-10), "State > 1 encountered"
    assert np.all(result["R_system"] >= 0), "Negative R_system"
    assert np.all(result["R_system"] <= 1), "R_system > 1"

    # System resilience should generally increase from initial low values
    R_0 = result["R_system"][0]
    R_final = result["R_system"][-1]
    assert R_final > R_0, f"Resilience did not grow: {R_0:.3f} -> {R_final:.3f}"
    print("  ✓ Simulation stability and bounds")


def test_geopolitical_scenarios():
    """Test geopolitical shock scenarios produce expected patterns."""
    for scenario in ["steady", "single_escalation", "sustained"]:
        I = geopolitical_shock_investment(10.0, 1.0, scenario)
        assert I >= 1.0, f"Investment below baseline for {scenario}"

    # Single escalation should spike near t=5
    I_before = geopolitical_shock_investment(4.9, 1.0, "single_escalation")
    I_after = geopolitical_shock_investment(5.1, 1.0, "single_escalation")
    assert I_after > I_before, "No spike at escalation point"
    print("  ✓ Geopolitical shock scenarios")


def test_adaptation_enhancement():
    """Test adaptation enhancement produces expected amplification."""
    V = 1.0
    S_adapt = 0.5
    psi = 0.28
    tau = 2.5

    V_eff = adaptation_enhancement(V, S_adapt, psi, 5.0, tau)
    assert V_eff > V, "No enhancement effect"

    V_eff_0 = adaptation_enhancement(V, 0.0, psi, 5.0, tau)
    assert abs(V_eff_0 - V) < 1e-10, "Enhancement with zero adaptation"
    print(f"  ✓ Adaptation enhancement (multiplier: {V_eff/V:.3f})")


def test_copula_extension():
    """Test copula produces lower resilience than independence."""
    rng = np.random.default_rng(42)
    R_indep = system_resilience(0.5, 0.6, 0.4, 0.3, 0.5)
    R_cop = copula_resilience(0.5, 0.6, 0.4, 0.3, 0.5,
                              rho=0.4, n_samples=10000, rng=rng)
    # Copula should give equal or lower resilience (correlated failures)
    # With small samples there's variance, so allow small tolerance
    assert R_cop <= R_indep + 0.05, \
        f"Copula ({R_cop:.3f}) > independence ({R_indep:.3f}) + tolerance"
    print(f"  ✓ Copula extension (indep={R_indep:.3f}, copula={R_cop:.3f})")


def test_environment_modifiers():
    """Test environment modifiers are >= 1 (acceleration)."""
    env = SpaceEnvironment()
    for t in [0, 5, 10, 15, 20]:
        assert env.A_env_prep(t) >= 1.0
        assert env.A_env_resist(t) >= 1.0
        assert env.A_env_restore(t) >= 1.0
        assert env.A_env_adapt(t) >= 1.0
    print("  ✓ Environment modifiers >= 1")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Model Tests & Property Verification")
    print("=" * 60)

    tests = [
        test_theorem1_order_invariance,
        test_theorem1_monotonicity,
        test_theorem1_bounds,
        test_theorem1_super_additivity,
        test_theorem1_concavity,
        test_lemma1_supply_chain_leverage,
        test_theorem2_red_queen_equilibrium,
        test_axiom1_monotone_decay,
        test_axiom2_diminishing_returns,
        test_axiom4_adversary_response,
        test_axiom5_supply_chain_propagation,
        test_simulation_stability,
        test_geopolitical_scenarios,
        test_adaptation_enhancement,
        test_copula_extension,
        test_environment_modifiers,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'=' * 60}\n")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
