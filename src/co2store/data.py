from __future__ import annotations

import numpy as np
import pandas as pd

NUMERIC = [
    "FIELD_EXTENT_MEAN",
    "GROSS_THICK_MEAN",
    "VERT_NET_GROSS_MEAN",
    "POROSITY_MEAN",
    "CO2_DENSIT",
    "DEPTH_MEAN",
    "TEMP_C_MEAN",
    "PRESSURE_MEAN",
    "PERM_MEAN",
]


def load_units(path: str) -> pd.DataFrame:
    """CO2StoP 'Hydrocarbon_Storage_Units.csv': storage units with a positive mean capacity estimate (Mt).

    The database codes missing values as 0; for the parameters below a 0 is therefore treated as missing.
    """
    d = pd.read_csv(path, low_memory=False)
    d["country"] = d.STORAGE_UNIT_ID.astype(str).str[:2]
    d = d[d.EST_STORECAP_MEAN > 0].copy()
    for c in NUMERIC + ["STORE_EFF_FACT_USER", "STORE_EFF_FACT_DB"]:
        d[c] = d[c].where(d[c] > 0)
    d["eff_pct"] = d.STORE_EFF_FACT_USER.fillna(d.STORE_EFF_FACT_DB)
    d["log_cap"] = np.log10(d.EST_STORECAP_MEAN)
    return d.reset_index(drop=True)


def volumetric_mt(d: pd.DataFrame, net_gross_default: float = 1.0) -> pd.Series:
    """Volumetric capacity in Mt: area[km2] x thickness[m] x net/gross x porosity x CO2 density[kg/m3] x efficiency[%]."""
    ng = d.VERT_NET_GROSS_MEAN.fillna(net_gross_default)
    kg = (
        d.FIELD_EXTENT_MEAN
        * 1e6
        * d.GROSS_THICK_MEAN
        * ng
        * d.POROSITY_MEAN
        * d.CO2_DENSIT
        * d.eff_pct
        / 100.0
    )
    return kg / 1e9
