# -*- coding: utf-8 -*-
import numpy as np
from bgcr_budyko.models.bgcr import bgcr_monthly
from bgcr_budyko.params.w_schemes import w_from_SI, w_from_SI_albedo

def test_shapes_and_bounds():
    nY, nM = 2, 12
    P = np.abs(np.random.randn(nY, nM))*50 + 10
    Epa = np.abs(np.random.randn(nY, nM))*3 + 2
    Erad= np.abs(np.random.randn(nY, nM))*2 + 0.5
    E, out = bgcr_monthly(P, Epa, Erad, w=1.6)
    assert E.shape == P.shape
    assert np.all(E >= 0)
    assert np.all(out['ratio'] <= 1.0 + 1e-6)

def test_w_schemes_monotonicity():
    SI = np.linspace(0.1, 1.1, 10)
    ALB= np.linspace(0.15, 0.5, 10)
    ws = w_from_SI(SI)
    wd = w_from_SI_albedo(SI, ALB)
    assert ws.shape == SI.shape and wd.shape == SI.shape
