# DaST-2026
# Frost Day Prediction in Vienna

## Abstract
This repository contains a fully documented, open-science machine learning experiment
that predicts frost days in Vienna using historical meteorological data from the
GeoSphere Austria Data Hub (Messstationen Tagesdaten v2, station Vienna Hohe Warte,
2000–2023). A frost day is defined as any day where the minimum temperature drops
below 0°C. The experiment trains a Random Forest Classifier on daily weather features
including mean temperature, minimum temperature, maximum temperature, precipitation,
sunshine hours, humidity, and visibility, producing a binary frost/no-frost prediction. The pipeline follows the
CRISP-DM methodology, implemented in Python 3.11 using scikit-learn, pandas, and
NumPy. Input data is openly available under a CC0 licence. All outputs — including
the trained model (.joblib), evaluation figures (PNG), and metrics (CSV) — are
publicly archived with persistent identifiers following FAIR principles.

## File Organisation

### Folder Structure
| Folder | Contents |
|--------|----------|
| `data/` | Input datasets used in the experiment |
| `src/` | All scripts and notebooks |
| `outputs/` | Generated figures, model artefacts, predictions |
| `docs/` | Documentation files (model card, validation outputs, etc.) |

### File-Naming Convention

**Input datasets:**
`data_<source>_<description>_<version>.<ext>`
Example: `data_geosphere-austria_frost-days_v1.csv`

**Output files (figures and model artefacts):**
`fig_<description>_<date>.<ext>`
Example: `fig_confusion-matrix_2026-05-04.png`

`model_<algorithm>_<version>.<ext>`
Example: `model_random-forest_v1.joblib`

**Scripts:**
`<step-number>_<description>.py` or `.ipynb`
Example: `01_data-loading.ipynb`, `02_preprocessing.py`

**Configuration files:**
`config_<description>.<ext>`
Example: `config_hyperparameters.json`

## Requirements and Installation
_To be completed._

## Reproduction Instructions
_To be completed._

## Inputs and Outputs

### Inputs
| Name | Source | Licence |
|------|--------|---------|
| Messstationen Tagesdaten v2 | [GeoSphere Austria Data Hub](https://data.hub.geosphere.at) | CC0 |

### Outputs
| Name | Type | Description |
|------|------|-------------|
| `model_random-forest_v1.joblib` | Model artefact | Trained Random Forest Classifier |
| `fig_confusion-matrix_*.png` | Figure | Confusion matrix on test set |
| `fig_roc-curve_*.png` | Figure | ROC-AUC curve |
| `fig_feature-importance_*.png` | Figure | Feature importance chart |

## WP2: DBRepo Views and API Data Loading

### T2.4 View Definitions
The intended SQL view definitions for my part are in `docs/views.sql`. The goal
is to keep the database tables normalised, but still have query-ready data for
the machine-learning code.

| View | Purpose |
|------|---------|
| `vw_ml_daily_features` | Intended SQL view: joins station metadata with daily observations and derives `obs_year`, `obs_month`, `obs_day_of_year`, and `is_frost_day`. |
| `vw_ml_complete_cases` | Intended SQL view: keeps only rows where all ML input columns are present. |
| `vw_ml_balanced_training_sample` | Intended SQL view: deterministic class-balanced sample with equal frost and non-frost rows. |
| `vw_monthly_frost_summary` | Intended SQL view: monthly aggregate with observation count, frost-day count, average minimum temperature, and total precipitation. |

DBRepo object identifiers used in the notebooks and scripts:

| Object | DBRepo UUID | Implemented in DBRepo | Defined in `docs/views.sql` | Equivalent logic in Python loader |
|--------|-------------|-----------------------|------------------------------|-----------------------------|
| Database `frost_day_prediction_in_vienna` | `a16a980a-3489-492b-adcf-74c70a07248b` | Yes | n/a | n/a |
| Table `station` | `9c57f7ff-99b6-454b-8d51-cff340ecf934` | Yes | n/a | n/a |
| Table `daily_observation` | `21e39deb-1db9-4d34-bc04-45fa5cef72a0` | Yes | n/a | n/a |
| View `vw_ml_daily_features` | `59cafa7d-0267-4c6a-a94d-6bf4670badf7` | Yes. DBRepo exposes the physical observation columns. Derived columns (obs_month, obs_day_of_year, is_frost_day) are added by the Python loader. | Yes. The SQL adds station metadata, date parts, and `is_frost_day`. | Yes. `02_load-data-from-dbrepo.py` derives `obs_month`, `obs_day_of_year`, and `is_frost_day`. |
| View `vw_ml_complete_cases` | `f868d4e8-5505-4ec8-9a9b-c2de34e2c545` | Yes. DBRepo exposes the physical observation columns. Complete-case filtering is applied by the Python loader. | Yes. The SQL filters out incomplete model rows. | Yes. The loader drops rows with missing model inputs. |
| View `vw_ml_balanced_training_sample` | _Not created_ | No. The DBRepo builder/client did not provide the required CTE/window-function support. | Yes. The SQL uses `ROW_NUMBER()` and class counts. | No. Training code should use the complete-case loader unless this SQL view is created manually. |
| View `vw_monthly_frost_summary` | `5cb817ff-670d-4142-a1d8-c43cce6997bf` | No. DBRepo does not support GROUP BY aggregation in the view builder. The full SQL definition is in docs/views.sql and is the authoritative specification. | Yes. The SQL groups by station, year, and month and computes aggregate columns. | Not needed for model loading; it is a reporting/quality-check view. |

Some SQL features used in `docs/views.sql`, especially computed columns,
aggregates, and the balanced-sample CTE, are not reproduced by the current
DBRepo web/client view builder. For that reason the SQL file documents the
intended views, while the Python loader derives the small computed columns and
applies the complete-case filtering after reading the DBRepo view.


### T2.6 DBRepo REST API Loading
The DBRepo data loader is `src/02_load-data-from-dbrepo.py`. It replaces local
CSV loading in the experiment. After downloading the DBRepo view, it adds
`obs_month`, `obs_day_of_year`, and `is_frost_day`.

`is_frost_day` is calculated from `temp_min_c < 0`. I kept `temp_min_c` out of
the final feature matrix because otherwise the model could learn the label
directly from the threshold instead of using the other weather variables.

Required environment variables:

| Variable | Description |
|----------|-------------|
| `DBREPO_ENDPOINT` | DBRepo base URL, e.g. `https://test.dbrepo.tuwien.ac.at`. |
| `DBREPO_USERNAME` | DBRepo username. |
| `DBREPO_PASSWORD` | DBRepo password. |
| `DATABASE_ID` | DBRepo database UUID. |
| `DBREPO_FEATURE_VIEW_ID` | DBRepo UUID for the ML feature view. |

Endpoints used:

| Endpoint | Purpose |
|----------|---------|
| `GET {DBREPO_ENDPOINT}/api/v1/database/{DATABASE_ID}` | Read database metadata in the view-creation notebook. |
| `GET {DBREPO_ENDPOINT}/api/v1/database/{DATABASE_ID}/view/{DBREPO_FEATURE_VIEW_ID}/data?page={page}&size={size}` | Load paginated view data for the experiment. |
| `GET {DBREPO_ENDPOINT}/api/v1/database/{DATABASE_ID}/view/{view_id}/data?page=0&size=5` | Preview/verify created views in `src/03_create-dbrepo-views.ipynb`. |

The script authenticates with HTTP Basic Authentication using
the DBRepo username and password from `.env`.

The loader checks the main things that can go wrong: connection problems,
timeouts, bad HTTP status codes, invalid JSON, missing columns, and empty
results. It also loops over result pages instead of assuming that the first
page contains the full dataset.

Current DBRepo API smoke test:

```text
Loaded 5071 rows from DBRepo.
Frost days: 815 / 5071
```

The required T2.6 equality check can be run once the original local CSV is
available:

```powershell
python src\02_load-data-from-dbrepo.py path\to\original_local_file.csv
```

The original local CSV was not retained in this repository; it has already been
uploaded to DBRepo. Therefore, the practical verification was run by comparing
the DBRepo feature view against the DBRepo base observation table after applying
the same transformations:

```powershell
python src\02_load-data-from-dbrepo.py --dbrepo-table-check
```

The printed output of this check must be copied into the final report. At the
time of writing this README, the repository contains the helper function but
does not contain the final report text.

Verification output:

```text
row_match: True
numeric_match: True
label_match: True
identical: True
source_table_rows: 5071
feature_view_rows: 5071
```

## Licences
_To be completed._

## Contributors
| Name           | Role | ORCID                |
|----------------|------|----------------------|
| Sophie Konecny | A | 0009-0006-5745-5729  |
| Vivek Sharma   | B | 0009-0006-4879-6388  |
| Anxhela Sulmina| C | 0009-0008-9371-0488  |
| Nayma Alam     | D | 0009-0003-4731-9553  |


## RO-Crate

The experiment is described as a Research Object Crate (RO-Crate 1.1) in
[`ro-crate-metadata.json`](ro-crate-metadata.json) at the repository root.
The file lists all entities — input datasets (with source URLs/DOIs), code,
trained model and output figures (with TUWRD DOIs), authors (with ORCIDs),
and licences — together with the relationships between them.

Validation was run with `roc-validator` v0.9.0 against the `ro-crate-1.1`
profile. Results (38/38 REQUIRED checks passed, 0 issues) are stored under
[`docs/validation/`](docs/validation/).

## Zenodo DOI
<<<<<<< HEAD
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20457340.svg)](https://doi.org/10.5281/zenodo.20457340)
=======
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20457341.svg)](https://doi.org/10.5281/zenodo.20457341)
 

>>>>>>> e22e9e46eebe50c36297007f09c7f1a534a6054d

