# Software Requirements Specification – CO2Store

- SR-1 `data.load_units`: CO2StoP storage units with a positive mean capacity estimate; 0 is the database code for a missing value and is treated as missing; country = first two letters of the unit id; efficiency = user estimate, else database value (percent).
- SR-2 `data.volumetric_mt`: area[km2] x thickness[m] x net/gross (1 if missing) x porosity x CO2 density[kg/m3] x efficiency / 100, in Mt (a unit test fixes the unit conversion).
- SR-3 `models.design`: log10 of area, thickness, porosity and density plus net/gross, depth, temperature, pressure (missing allowed); `conformal_margin`: split-conformal absolute-residual margin.
- SR-4 `research/run_study.py`: ridge (median imputation) and gradient boosting; random 5-fold CV x 10 with a 30 % calibration part of each training fold; leave-one-country-out for countries with at least 5 units (calibration on a random 30 % of the other countries' units, 10 repeats); alpha 0.1.
- SR-5 Two unit tests.
