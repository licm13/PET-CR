import numpy as np
import pandas as pd

from bgcr_budyko.models.bgcr import bgcr_monthly

def test_bgcr_monthly_shape_and_range():
    # Create synthetic monthly inputs (12 months)
    n = 12
    P = np.linspace(10, 100, n)      # precipitation
    Epa = np.linspace(50, 120, n)    # potential evap (energy-limited)
    Erad = np.linspace(30, 90, n)    # radiative evaporative demand

    E, out = bgcr_monthly(P, Epa, Erad, w=1.6)

    # Basic assertions
    assert len(E) == n
    assert np.isfinite(E).all()
    # Physical bound: evaporation should be between 0 and Epa
    assert (E >= 0).all()
    assert (E <= Epa + 1e-8).all()