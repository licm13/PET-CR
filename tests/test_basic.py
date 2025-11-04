"""
Basic tests for PET-CR library

These tests verify that the core functions run without errors and produce
reasonable results.

Note: Install the package first with: pip install -e . (from project root)
Or run from project root: python -m tests.test_basic
"""

import numpy as np
import sys

try:
    from petcr import (
        sigmoid_cr,
        polynomial_cr,
        rescaled_power_cr,
        bouchet_cr,
        aa_cr,
        penman_potential_et,
        priestley_taylor_et,
        vapor_pressure_deficit,
        calculate_psychrometric_constant,
        calculate_saturation_vapor_pressure,
        calculate_slope_svp
    )
except ImportError:
    # Fallback for running directly without installation
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from petcr import (
        sigmoid_cr,
        polynomial_cr,
        rescaled_power_cr,
        bouchet_cr,
        aa_cr,
        penman_potential_et,
        priestley_taylor_et,
        vapor_pressure_deficit,
        calculate_psychrometric_constant,
        calculate_saturation_vapor_pressure,
        calculate_slope_svp
    )


def test_physics_functions():
    """Test physics calculation functions."""
    print("Testing physics functions...")
    
    # Test saturation vapor pressure
    es = calculate_saturation_vapor_pressure(20.0)
    assert es > 0, "Saturation vapor pressure should be positive"
    assert 2000 < es < 3000, f"Expected ~2337 Pa, got {es}"
    
    # Test slope of SVP curve
    delta = calculate_slope_svp(20.0)
    assert delta > 0, "Slope should be positive"
    
    # Test psychrometric constant
    gamma = calculate_psychrometric_constant(101325.0)
    assert gamma > 0, "Psychrometric constant should be positive"
    assert 60 < gamma < 70, f"Expected ~66.8 Pa/K, got {gamma}"
    
    # Test VPD
    vpd = vapor_pressure_deficit(20.0, 50.0)
    assert vpd > 0, "VPD should be positive for RH < 100%"
    
    # Test Priestley-Taylor
    et_pt = priestley_taylor_et(500.0, 50.0, 20.0, 101325.0)
    assert et_pt > 0, "PT ET should be positive"
    assert et_pt < 500.0, "PT ET should be less than net radiation"
    
    # Test Penman
    et_p = penman_potential_et(500.0, 50.0, 20.0, 50.0, 2.0, 101325.0)
    assert et_p > 0, "Penman ET should be positive"
    
    print("✓ All physics functions passed")


def test_cr_models():
    """Test CR model functions."""
    print("\nTesting CR models...")
    
    ep = 400.0
    ew = 350.0
    
    # Test Sigmoid
    ea_sigmoid = sigmoid_cr(ep, ew, beta=0.5)
    assert 0 <= ea_sigmoid <= ew, f"Sigmoid Ea should be between 0 and Ew, got {ea_sigmoid}"
    
    # Test Polynomial
    ea_poly = polynomial_cr(ep, ew, b=2.0)
    assert ea_poly >= 0, f"Polynomial Ea should be non-negative, got {ea_poly}"
    
    # Test Rescaled Power
    ea_rescaled = rescaled_power_cr(ep, ew, n=0.5)
    assert 0 <= ea_rescaled <= ew, f"Rescaled Ea should be between 0 and Ew, got {ea_rescaled}"
    
    # Test Bouchet
    ea_bouchet = bouchet_cr(ep, ew)
    assert ea_bouchet >= 0, f"Bouchet Ea should be non-negative, got {ea_bouchet}"
    expected_bouchet = 2 * ew - ep
    assert abs(ea_bouchet - expected_bouchet) < 1e-6, "Bouchet formula incorrect"
    
    # Test A-A
    ea_aa = aa_cr(ep, ew)
    assert 0 <= ea_aa <= ew, f"A-A Ea should be between 0 and Ew, got {ea_aa}"
    
    print("✓ All CR models passed")


def test_array_inputs():
    """Test that functions work with array inputs."""
    print("\nTesting array inputs...")
    
    ep_array = np.array([300.0, 400.0, 500.0])
    ew_array = np.array([350.0, 350.0, 350.0])
    
    # Test Sigmoid with arrays
    ea_array = sigmoid_cr(ep_array, ew_array, beta=0.5)
    assert len(ea_array) == len(ep_array), "Output length should match input length"
    assert np.all(ea_array > 0), "All Ea values should be positive"
    assert np.all(ea_array <= ew_array), "All Ea values should be <= Ew"
    
    # Test physics with arrays
    temps = np.array([10.0, 20.0, 30.0])
    es_array = calculate_saturation_vapor_pressure(temps)
    assert len(es_array) == len(temps), "Output length should match input length"
    assert np.all(es_array > 0), "All es values should be positive"
    
    print("✓ Array input tests passed")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\nTesting edge cases...")
    
    # Test when Ep = Ew
    ep = ew = 350.0
    
    ea_sigmoid = sigmoid_cr(ep, ew, beta=0.5)
    assert abs(ea_sigmoid - ew) < 1.0, "Sigmoid: When Ep=Ew, Ea should ≈ Ew"
    
    ea_rescaled = rescaled_power_cr(ep, ew)
    assert abs(ea_rescaled - ew) < 1.0, "Rescaled: When Ep=Ew, Ea should ≈ Ew"
    
    ea_bouchet = bouchet_cr(ep, ew)
    assert abs(ea_bouchet - ew) < 1e-6, "Bouchet: When Ep=Ew, Ea should = Ew"
    
    # Test A-A model boundary (Ep < Ew vs Ep > Ew)
    ea_aa_wet = aa_cr(300.0, 350.0)
    assert abs(ea_aa_wet - 350.0) < 1e-6, "A-A: When Ep < Ew, Ea should = Ew"
    
    ea_aa_dry = aa_cr(400.0, 350.0)
    assert ea_aa_dry == 300.0, "A-A: When Ep > Ew, should follow Bouchet"
    
    print("✓ Edge case tests passed")


def test_physical_constraints():
    """Test that results satisfy physical constraints."""
    print("\nTesting physical constraints...")
    
    ep_series = np.linspace(200, 600, 20)
    ew = 350.0
    
    for ep in ep_series:
        # Test all models
        ea_sigmoid = sigmoid_cr(ep, ew, beta=0.5)
        ea_poly = polynomial_cr(ep, ew, b=2.0)
        ea_rescaled = rescaled_power_cr(ep, ew, n=0.5)
        ea_bouchet = bouchet_cr(ep, ew)
        ea_aa = aa_cr(ep, ew)
        
        # All Ea should be non-negative
        assert ea_sigmoid >= 0, f"Sigmoid Ea negative at Ep={ep}"
        assert ea_poly >= 0, f"Polynomial Ea negative at Ep={ep}"
        assert ea_rescaled >= 0, f"Rescaled Ea negative at Ep={ep}"
        assert ea_bouchet >= 0, f"Bouchet Ea negative at Ep={ep}"
        assert ea_aa >= 0, f"A-A Ea negative at Ep={ep}"
        
        # Sigmoid and Rescaled should not exceed Ew
        assert ea_sigmoid <= ew + 1e-6, f"Sigmoid Ea exceeds Ew at Ep={ep}"
        assert ea_rescaled <= ew + 1e-6, f"Rescaled Ea exceeds Ew at Ep={ep}"
        assert ea_aa <= ew + 1e-6, f"A-A Ea exceeds Ew at Ep={ep}"
    
    print("✓ Physical constraint tests passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Running PET-CR Library Tests")
    print("=" * 70)
    
    try:
        test_physics_functions()
        test_cr_models()
        test_array_inputs()
        test_edge_cases()
        test_physical_constraints()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
