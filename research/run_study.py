"""CO2StoP (EU CO2 Storage Potential project, open data): volumetric consistency and conformal capacity screening.

usage: python research/run_study.py <Hydrocarbon_Storage_Units.csv>
Data: storage units of the CO2StoP database (JRC / Zenodo 15837736) with a positive mean capacity estimate (226 units, 22 countries);
units with area, thickness, porosity and CO2 density all given: used below. The capacities are ESTIMATES made by the project partners,
not measurements of what can be injected.
(1) Is the reported capacity reproducible from the reported parameters (volumetric formula)?
(2) Screening model for log10 capacity from geology without the efficiency factor; 90 % conformal intervals; random vs leave-one-country-out.
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from co2store.data import load_units, volumetric_mt
from co2store.models import conformal_margin, design

warnings.filterwarnings("ignore")
ALPHA = 0.1
MIN_UNITS = 5


def models():
    return {
        "ridge_logs": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(1.0)),
        "boosting": HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.05, max_depth=3, random_state=0
        ),
    }


def main(path: str):
    d = load_units(path)
    d = d.dropna(
        subset=["FIELD_EXTENT_MEAN", "GROSS_THICK_MEAN", "POROSITY_MEAN", "CO2_DENSIT"]
    ).reset_index(drop=True)
    out = {
        "note": "CO2StoP storage units (estimates by project partners); log10 of capacity in Mt; alpha=0.1",
        "n_units": len(d),
        "n_countries": int(d.country.nunique()),
        "log10_capacity_sd": float(d.log_cap.std()),
    }
    # (1) volumetric reproducibility
    v = volumetric_mt(d)
    ok = v.notna() & (v > 0)
    ratio = (d.EST_STORECAP_MEAN[ok] / v[ok]).to_numpy()
    out["volumetric"] = {
        "n": int(ok.sum()),
        "median_ratio_reported_over_calc": float(np.median(ratio)),
        "share_within_10pct": float(np.mean(np.abs(ratio - 1) <= 0.10)),
        "share_within_factor_2": float(np.mean((ratio > 0.5) & (ratio < 2.0))),
        "log10_ratio_sd": float(np.std(np.log10(ratio))),
    }
    ratio_by_method = {}
    for m, g in d[ok].groupby("CAP_EST_METHOD"):
        rr = (g.EST_STORECAP_MEAN / v[ok][g.index]).to_numpy()
        if len(rr) >= 5:
            ratio_by_method[m] = {
                "n": len(rr),
                "median_ratio": float(np.median(rr)),
                "share_within_10pct": float(np.mean(np.abs(rr - 1) <= 0.10)),
            }
    out["volumetric_by_method"] = ratio_by_method
    # (2) screening model
    X, y, g = design(d), d.log_cap.to_numpy(), d.country.to_numpy()
    big = {c for c in np.unique(g) if (g == c).sum() >= MIN_UNITS}
    out["screening"] = {}
    for name, mk in models().items():
        res = {}
        # random 5-fold with a calibration part (30 % of training fold)
        cov, wid, err = [], [], []
        for seed in range(10):
            for tr, te in KFold(5, shuffle=True, random_state=seed).split(X):
                rng = np.random.default_rng(seed)
                perm = rng.permutation(tr)
                cal, fit = perm[: int(0.3 * len(perm))], perm[int(0.3 * len(perm)) :]
                m = mk.fit(X.iloc[fit], y[fit])
                q = conformal_margin(y[cal] - m.predict(X.iloc[cal]), ALPHA)
                e = y[te] - m.predict(X.iloc[te])
                cov.append(np.mean(np.abs(e) <= q))
                wid.append(2 * q)
                err.append(np.mean(np.abs(e)))
        res["random"] = {
            "coverage": float(np.mean(cov)),
            "mean_width_decades": float(np.mean(wid)),
            "mae_decades": float(np.mean(err)),
        }
        # leave-one-country-out
        covs, wids, errs, per = [], [], [], {}
        for c in sorted(big):
            te = np.where(g == c)[0]
            tr = np.where(g != c)[0]
            cs, ws, es = [], [], []
            for seed in range(10):
                perm = np.random.default_rng(seed).permutation(tr)
                cal, fit = perm[: int(0.3 * len(perm))], perm[int(0.3 * len(perm)) :]
                m = mk.fit(X.iloc[fit], y[fit])
                q = conformal_margin(y[cal] - m.predict(X.iloc[cal]), ALPHA)
                e = y[te] - m.predict(X.iloc[te])
                cs.append(np.mean(np.abs(e) <= q))
                ws.append(2 * q)
                es.append(np.mean(np.abs(e)))
            per[c] = {
                "n": len(te),
                "coverage": float(np.mean(cs)),
                "mae_decades": float(np.mean(es)),
            }
            covs += [per[c]["coverage"]] * len(te)
            wids.append(np.mean(ws))
            errs += [per[c]["mae_decades"]] * len(te)
        res["leave_country_out"] = {
            "coverage_unit_weighted": float(np.mean(covs)),
            "mean_width_decades": float(np.mean(wids)),
            "mae_decades": float(np.mean(errs)),
            "per_country": per,
            "countries_below_0.75": [c for c, v_ in per.items() if v_["coverage"] < 0.75],
        }
        out["screening"][name] = res
        print(
            name,
            {
                k: {
                    a: (round(b, 3) if isinstance(b, float) else b)
                    for a, b in v_.items()
                    if a != "per_country"
                }
                for k, v_ in res.items()
            },
        )
    Path(__file__).with_name("results.json").write_text(json.dumps(out, indent=1))
    print(out["n_units"], out["n_countries"], out["volumetric"], out["log10_capacity_sd"])


if __name__ == "__main__":
    main(sys.argv[1])
