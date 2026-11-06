import numpy as np
import pandas as pd

from co2store.data import volumetric_mt
from co2store.models import conformal_margin, design


def test_volumetric_formula_units():
    d = pd.DataFrame(
        {
            "VERT_NET_GROSS_MEAN": [0.5],
            "FIELD_EXTENT_MEAN": [100.0],
            "GROSS_THICK_MEAN": [100.0],
            "POROSITY_MEAN": [0.2],
            "CO2_DENSIT": [600.0],
            "eff_pct": [10.0],
        }
    )
    # 100 km2 x 100 m x 0.5 x 0.2 = 1e9 m3 of pore space... x 600 kg/m3 x 0.1 = 6e10 kg = 60 Mt
    assert abs(volumetric_mt(d).iloc[0] - 60.0) < 1e-9


def test_design_uses_logs_and_margin_rank():
    d = pd.DataFrame(
        {
            "FIELD_EXTENT_MEAN": [10.0],
            "GROSS_THICK_MEAN": [100.0],
            "POROSITY_MEAN": [0.1],
            "CO2_DENSIT": [1000.0],
            "VERT_NET_GROSS_MEAN": [0.5],
            "DEPTH_MEAN": [1000.0],
            "TEMP_C_MEAN": [40.0],
            "PRESSURE_MEAN": [10.0],
        }
    )
    X = design(d)
    assert X["log_FIELD_EXTENT_MEAN"].iloc[0] == 1.0 and X["log_CO2_DENSIT"].iloc[0] == 3.0
    assert conformal_margin(np.arange(1.0, 100.0), 0.1) == 90.0
