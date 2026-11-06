from __future__ import annotations

import numpy as np
import pandas as pd

LOG_FEATURES = ["FIELD_EXTENT_MEAN", "GROSS_THICK_MEAN", "POROSITY_MEAN", "CO2_DENSIT"]
OTHER = ["VERT_NET_GROSS_MEAN", "DEPTH_MEAN", "TEMP_C_MEAN", "PRESSURE_MEAN"]


def design(d: pd.DataFrame) -> pd.DataFrame:
    X = pd.DataFrame({f"log_{c}": np.log10(d[c]) for c in LOG_FEATURES})
    for c in OTHER:
        X[c] = d[c]
    return X


def conformal_margin(res: np.ndarray, alpha: float) -> float:
    n = len(res)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    s = np.sort(np.abs(res))
    return float(s[min(k, n) - 1]) if k <= n else float("inf")
