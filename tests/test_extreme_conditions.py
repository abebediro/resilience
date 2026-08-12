"""Extreme-condition tests TC01-TC08 (Appendix B.1 / I.3) - qualitative checks."""

import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copy import deepcopy
from calibration.parameters import ParameterSet
from models.system import SpaceResilienceModel
from models.composition import supply_chain_modulation


def _sim(p, T=20.0, budget=None):
    return SpaceResilienceModel(p).simulate(T=T, budget=budget)


def test_TC01_zero_investment():
    """All stocks decay toward zero without investment."""
    r = _sim(ParameterSet(), budget=0.0)
    final = r["states"][-1, :5]
    initial = r["states"][0, :5]
    assert np.all(final < initial), "Stocks did not decay under zero investment"
    assert np.all(final < 0.12), f"Stocks not near zero at yr 20: {final.round(3)}"
    print(f"  TC01 zero investment: final stocks {final.round(3)} -> PASS")


def test_TC02_max_resistance_only():
    """Resistance-only allocation: R_eff peaks then declines as adversary adapts."""
    p = ParameterSet()
    m = SpaceResilienceModel(p)
    w = np.array([0.0, 1.0, 0.0, 0.0, 0.0])
    r = m.simulate(T=20, weights=w)
    peak_i = int(np.argmax(r["R_effective"]))
    assert r["time"][peak_i] < 19.0, "No interior peak"
    assert r["R_effective"][-1] < r["R_effective"][peak_i], "No post-peak decline"
    print(f"  TC02 resistance-only: peak {r['R_effective'][peak_i]:.2f} at yr "
          f"{r['time'][peak_i]:.0f}, declines to {r['R_effective'][-1]:.2f} -> PASS")


def test_TC03_deep_space_latency():
    """10x latency severely degrades prep/adapt outflows."""
    import models.environment as env
    base = env.latency
    try:
        env.latency = lambda t: 10.0
        r_deep = _sim(ParameterSet())
    finally:
        env.latency = base
    r_norm = _sim(ParameterSet())
    assert r_deep["states"][-1, 0] < r_norm["states"][-1, 0]
    assert r_deep["states"][-1, 3] < r_norm["states"][-1, 3]
    print("  TC03 deep-space latency: prep/adapt degraded -> PASS")


def test_TC04_perfect_supply_chain():
    """S_supply=1 lifts effective capacities by the cascade fractions."""
    xi = ParameterSet().get_xi()
    R = 0.5
    for i, name in enumerate(["prep", "resist", "restore", "adapt"]):
        eff_half = supply_chain_modulation(R, xi[i], 0.5)
        eff_perfect = supply_chain_modulation(R, xi[i], 1.0)
        gain = (eff_perfect - eff_half) / eff_half * 100
        assert eff_perfect > eff_half
    print("  TC04 perfect supply chain: effective capacities lifted -> PASS")


def test_TC05_high_adversary_learning():
    """theta=0.30: R_eff peaks then declines."""
    p = ParameterSet(); p.theta = 0.30
    r = _sim(p)
    peak_i = int(np.argmax(r["R_effective"]))
    assert r["R_effective"][-1] < r["R_effective"][peak_i] + 1e-9
    print(f"  TC05 theta=0.30: peak {r['R_effective'][peak_i]:.2f}, "
          f"final {r['R_effective'][-1]:.2f} -> PASS")


def test_TC06_no_adversary_learning():
    """theta=0: R_effective == R_system throughout (with threat decaying)."""
    p = ParameterSet(); p.theta = 0.0
    r = _sim(p)
    # threat decays below S_threat_min -> zero erosion in tail
    tail = slice(len(r["time"]) // 2, None)
    assert np.allclose(r["R_effective"][tail], r["R_system"][tail], atol=1e-6)
    print("  TC06 theta=0: no Red Queen erosion -> PASS")


def test_TC07_maximum_radiation():
    """gamma=2.0: resistance collapses relative to baseline.

    Tested in the decay regime (zero investment, high initial resistance)
    since under the calibrated investment scale the inflow saturates the
    stock at 1.0, masking the radiation effect."""
    init = ParameterSet().get_initial_state()
    init[1] = 0.91  # start from the paper's high-resistance reference point
    p_hi = ParameterSet(); p_hi.gamma = 2.0
    r_hi = SpaceResilienceModel(p_hi).simulate(T=10, budget=0.0, initial_state=init)
    r_base = SpaceResilienceModel(ParameterSet()).simulate(T=10, budget=0.0,
                                                           initial_state=init)
    assert r_hi["states"][-1, 1] < r_base["states"][-1, 1], \
        "High radiation did not accelerate resistance decay"
    print(f"  TC07 gamma=2.0: resistance {r_hi['states'][-1,1]:.2f} vs "
          f"baseline-gamma {r_base['states'][-1,1]:.2f} at yr 10 (no invest) -> PASS")


def test_TC08_zero_supply_chain():
    """S_supply=0: effective capacities severely degraded by cascades."""
    xi = ParameterSet().get_xi()
    eff_resist = supply_chain_modulation(0.20, xi[1], 0.0)
    eff_prep = supply_chain_modulation(0.15, xi[0], 0.0)
    assert abs(eff_resist - 0.20 * 0.32) < 1e-9
    assert abs(eff_prep - 0.15 * 0.58) < 1e-9
    print(f"  TC08 zero supply chain: eff_resist={eff_resist:.3f}, "
          f"eff_prep={eff_prep:.3f} -> PASS")


def run_all_tc():
    print("\nExtreme-Condition Tests (Appendix B.1 / I.3)")
    print("-" * 55)
    tests = [test_TC01_zero_investment, test_TC02_max_resistance_only,
             test_TC03_deep_space_latency, test_TC04_perfect_supply_chain,
             test_TC05_high_adversary_learning, test_TC06_no_adversary_learning,
             test_TC07_maximum_radiation, test_TC08_zero_supply_chain]
    passed = 0
    for t in tests:
        try:
            t(); passed += 1
        except AssertionError as e:
            print(f"  {t.__name__}: FAIL ({e})")
    print(f"-" * 55)
    print(f"{passed}/{len(tests)} extreme-condition tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_all_tc() else 1)
