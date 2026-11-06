# TRL assessment – CO2Store

**Claimed level: TRL 4** (laboratory validation on public open data). Not TRL 5: the target is a partner estimate, 191 units from 17 countries, no independent capacity or injection data.

Data: 191 saline-aquifer storage units with area, thickness, porosity and CO2 density given; 17 countries. log10 capacity (Mt) has a standard deviation of 1.29 decades.

## (1) Is the reported capacity reproducible from the reported parameters?
Volumetric formula with the reported efficiency factor, 184 units: median ratio reported / calculated = 1.00; only 50 % within 10 %, 73 % within a factor 2; standard deviation of log10 ratio 0.62 decades.

| Estimation method (database field) | n | Median ratio | Share within 10 % |
|---|---|---|---|
| From detailed site characterisation study | 14 | 1.00 | 1.00 |
| Geo-techno-economic simulation (Welkenhuysen et al., submitted) | 5 | 72.43 | 0.20 |
| Pore vol and storage eff coefficient | 142 | 1.00 | 0.49 |
| Pore vol and storage eff coefficient limited by trap vol | 18 | 1.01 | 0.39 |

## (2) Screening model (no efficiency factor), 90 % conformal intervals; widths and errors in decades of log10 Mt

| Model | Random CV coverage | Width | MAE | Leave-country-out coverage | Width | MAE | Countries with coverage < 0.75 |
|---|---|---|---|---|---|---|---|
| Ridge on log parameters | 0.919 | 2.14 | 0.49 | 0.869 | 2.11 | 0.51 | HU, IE |
| Gradient boosting | 0.921 | 2.49 | 0.51 | 0.873 | 2.42 | 0.59 | BE, HU, IE |

## Findings and caveats
- The reported capacities are reproducible from the reported parameters only roughly: half of the units are within 10 % of the volumetric result, a quarter differ by more than a factor of two. The database mixes methods (trap-volume limited, compressibility based, detailed studies, simulations) and some parameter values may have been revised after the capacity was computed.
- The model predicts log capacity to about 0.5 decades on average, but the 90 % interval is about **2.1–2.5 decades wide** (a factor of roughly 12 either side of the prediction): at screening level the capacity of a single unit is known only to about an order of magnitude.
- Coverage holds under random splits (0.92) and falls to about 0.87 when a whole country is withheld; Hungary and Ireland (and Belgium for boosting) are below 0.75, which means national assessment practices differ and the guarantee does not transfer to a new country without calibration data from it.
- The boosting model is no better than ridge on logs; with 191 units a physics-shaped log-linear model is sufficient.
- Capacity here is a theoretical storage estimate. Nothing in this study concerns whether CO2 can be injected or contained, and units with missing parameters (many) are excluded.
