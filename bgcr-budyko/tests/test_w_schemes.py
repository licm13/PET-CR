import numpy as np
from bgcr_budyko.params.w_schemes import w_from_SI, w_from_SI_albedo

def test_w_from_SI_basic():
    SI = np.linspace(0.0, 1.0, 10)
    w = w_from_SI(SI)
    assert w.shape == SI.shape
    assert (w > 0).all()
    assert np.isfinite(w).all()

def test_w_from_SI_albedo_basic():
    SI = np.linspace(0.0, 1.0, 10)
    ALB = np.linspace(0.1, 0.4, 10)
    w = w_from_SI_albedo(SI, ALB)
    assert w.shape == SI.shape
    assert (w > 0).all()
    assert np.isfinite(w).all()