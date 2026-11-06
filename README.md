# articles-CO2Store

Uncertainty-aware screening of CO2 storage capacity for saline-aquifer storage units, on the open CO2StoP database
(EU CO2 Storage Potential project; JRC / Zenodo 15837736). The capacities in the database are **estimates by project partners**, not
measurements of injectivity or containment. TRL 4 (public real data, laboratory validation only).

```
pip install -e ".[dev]" && python -m pytest
# data: https://zenodo.org/records/15837736 (co2jrc_openformats.zip -> CO2Stop_DataInterrogationSystem/Hydrocarbon_Storage_Units.csv; not committed)
python research/run_study.py <Hydrocarbon_Storage_Units.csv>
```
