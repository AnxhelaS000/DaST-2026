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

## Licences
_To be completed._

## Contributors
| Name           | Role | ORCID                |
|----------------|------|----------------------|
| Sophie Konecny | A | 0009-0006-5745-5729  |
| Vivek Sharma   | B | 0009-0006-4879-6388  |
| Anxhela        | C | 0009-0008-9371-0488                |
| Nayma         | D | _TBD_                |

## Zenodo DOI
_To be added after first Zenodo release._
