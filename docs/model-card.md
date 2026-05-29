# Model Card: Random Forest Classifier for Frost Day Prediction in Vienna

> Cross-references:
> - RO-Crate: [`ro-crate-metadata.json`](../ro-crate-metadata.json) <!-- TODO: add once T3.1 is complete -->
> - FAIR4ML metadata: [`metadata/fair4ml.json`](../metadata/fair4ml.json) <!-- TODO: add once T3.3 is complete -->

---

## Model Description

This model is a **Random Forest Classifier** trained to predict whether a given calendar day in Vienna is a *frost day* — defined as any day on which the minimum air temperature drops below 0 °C. It is a binary classification model that outputs a label of `1` (frost day) or `0` (no frost day) for each daily observation. The model is implemented using scikit-learn <!-- TODO: add version, e.g. 1.4.2 --> in Python 3.11 and serialised as `outputs/model_random-forest_v1.joblib`.

The classifier was built as part of the *Frost Day Prediction in Vienna* experiment following the CRISP-DM methodology. It takes seven daily meteorological features as input: mean temperature, minimum temperature, maximum temperature, precipitation, sunshine hours, relative humidity, and horizontal visibility. These features were selected based on their physical relevance to frost formation and their availability in the GeoSphere Austria Messstationen Tagesdaten v2 dataset.

<!-- TODO: Fill in final hyperparameters after training, e.g.:
Key hyperparameters: n_estimators=XXX, max_depth=XXX, min_samples_split=XXX, class_weight='balanced', random_state=42.
-->

| Attribute | Value |
|-----------|-------|
| Model type | Random Forest Classifier |
| Framework | scikit-learn <!-- TODO: version --> |
| Language | Python 3.11 |
| Task | Binary classification (frost day / no-frost day) |
| Output | `0` = no frost, `1` = frost day |
| Artefact | `outputs/model_random-forest_v1.joblib` |

---

## Intended Use

This model is intended for **educational and research purposes** as a demonstration of reproducible machine learning on publicly available meteorological data. It can be used to explore the relationship between daily weather variables and frost occurrence in Vienna, and to study the suitability of Random Forests for binary meteorological classification tasks. The model is appropriate for use within the academic context of the TU Wien Data Stewardship course.

The primary use case is retrospective analysis: given a set of daily observations for Vienna Hohe Warte station, the model produces a frost-day binary label. It may serve as a baseline for more sophisticated seasonal or climate-aware prediction approaches. Results are best interpreted alongside domain knowledge about Viennese winter climatology.

The model is **not** intended for operational weather forecasting or any decision-making where incorrect predictions could have safety, financial, or policy consequences. It was trained on a single station (Wien-Hohe Warte) and should only be applied to data from that station or meteorologically comparable urban Alpine sites.

---

## Out-of-Scope Uses

This model must **not** be used as an operational frost-warning system for agricultural, infrastructure, or emergency-management purposes. It has not been validated for real-time forecasting scenarios, nor does it incorporate forecast data or NWP model output. Applying it to stations outside Vienna, or to data from periods beyond the training window (2000–2023), may produce unreliable results without additional validation.

The model is not suitable for use with different spatial resolutions (e.g., gridded reanalysis data) without retraining, as it was trained on point observations from a single station. It should not be used to draw conclusions about climate change trends, as it does not model temporal drift and was not designed as a climatological trend tool. Any commercial application is outside the scope of the model's design and licence.

---

## Training Data

The model was trained on the **GeoSphere Austria Messstationen Tagesdaten v2** dataset, specifically daily observations from the **Wien-Hohe Warte** meteorological station (station code: `5904`) covering the period **2000–2023** (8 766 daily records). The dataset is published under the **CC0 1.0** licence and is freely available from the GeoSphere Austria Data Hub.

The data were ingested into a MariaDB database via the TU Wien DBRepo infrastructure and are citable via the persistent identifier **DOI: [10.82556/cxve-c208](https://doi.org/10.82556/cxve-c208)**. The original source record is available at <https://data.hub.geosphere.at/dataset/klima-v2-1d>. A frost-day label was derived at query time using the rule `temp_min_c < 0`, which is the standard WMO definition of a frost day; this derived column was not stored in the database to preserve 3NF.

<!-- TODO: Add train/test split details after pipeline is run, e.g.:
The dataset was split into a training set (years 2000–2019, ~80%) and a held-out test set (years 2020–2023, ~20%) with no data leakage. Class imbalance (approx. X% frost days) was addressed by [method, e.g. class_weight='balanced'].
-->

| Attribute | Value |
|-----------|-------|
| Source | GeoSphere Austria Messstationen Tagesdaten v2 |
| Station | Wien-Hohe Warte |
| Period | 2000–2023 |
| Records | 8 766 daily observations |
| Licence | CC0 1.0 |
| DOI (DBRepo) | [10.82556/cxve-c208](https://doi.org/10.82556/cxve-c208) |
| Original source | <https://data.hub.geosphere.at/dataset/klima-v2-1d> |

### Input Features

| Feature | Column | Unit | Description |
|---------|--------|------|-------------|
| Mean temperature | `temp_mean_c` | °C | Daily mean air temperature |
| Minimum temperature | `temp_min_c` | °C | Daily minimum air temperature |
| Maximum temperature | `temp_max_c` | °C | Daily maximum air temperature |
| Precipitation | `precipitation_mm` | mm | Daily precipitation sum |
| Sunshine duration | `sunshine_h` | h | Daily sunshine hours |
| Relative humidity | `humidity_pct` | % | Daily mean relative humidity |
| Visibility | `visibility_m` | m | Daily mean horizontal visibility |

### Target Variable

| Label | Value | Definition |
|-------|-------|------------|
| Frost day | `1` | `temp_min_c < 0 °C` |
| No frost day | `0` | `temp_min_c ≥ 0 °C` |

---

## Evaluation Results

<!-- TODO: Replace all placeholder values below with actual results after running the pipeline.
     Run the evaluation script and insert the numbers from outputs/metrics_*.csv. -->

The model was evaluated on the held-out test set (<!-- TODO: years/period -->). All metrics below are computed on the test set only; no test data were used during training or hyperparameter tuning.

| Metric | Value |
|--------|-------|
| Accuracy | <!-- TODO: e.g. 0.93 --> |
| Precision (frost class) | <!-- TODO: e.g. 0.88 --> |
| Recall (frost class) | <!-- TODO: e.g. 0.85 --> |
| F1-score (frost class) | <!-- TODO: e.g. 0.86 --> |
| ROC-AUC | <!-- TODO: e.g. 0.97 --> |
| Support (test set, total) | <!-- TODO: e.g. 1 461 --> |

<!-- TODO: Add confusion matrix values:
|  | Predicted No Frost | Predicted Frost |
|--|-------------------|-----------------|
| Actual No Frost | TN = XXX | FP = XXX |
| Actual Frost    | FN = XXX | TP = XXX |
-->

Evaluation figures are stored in `outputs/`:
- `fig_confusion-matrix_*.png` — confusion matrix on the test set
- `fig_roc-curve_*.png` — ROC-AUC curve
- `fig_feature-importance_*.png` — feature importance (mean decrease in impurity)

---

## Limitations

The model is trained on data from a single weather station (Wien-Hohe Warte) and therefore captures local microclimatic conditions specific to that site; results are not guaranteed to generalise to other locations, even within Vienna. Missing values in the original dataset were handled by <!-- TODO: specify imputation method, e.g. forward-fill / mean imputation --> and the model does not explicitly represent uncertainty from missing observations. The Random Forest model does not capture temporal dependencies between consecutive days, which may limit its performance during prolonged cold spells or unusual synoptic situations.

The training data cover 2000–2023 and reflect the climatic conditions of that period; as the climate shifts, the historical statistical relationships between features and frost occurrence may weaken. The model was not designed to handle distributional shift and should be periodically retrained as new data become available. Class imbalance between frost and non-frost days (frost days are a minority class in the Vienna climate) means that raw accuracy may be misleading; users should inspect precision and recall separately.

---

## Ethical Considerations

The training data are anonymised daily aggregates from a governmental weather monitoring network and contain no personal information; there are no privacy risks associated with the dataset or the model. The model's predictions are deterministic given fixed inputs and a fixed random seed, supporting reproducibility and auditability. Because the model is intended solely for educational use, no marginalised or vulnerable groups are affected by its outputs.

Users should be aware that weather-driven models can embed historical climatological biases if the underlying monitoring infrastructure has changed over the training period (e.g., station relocations, sensor upgrades). The model was not reviewed for fairness across demographic groups because its target variable is a physical quantity, not a social one. The CC0 licence of the training data and the MIT licence of the code are compatible, and no proprietary data or models were used in training.

---

## Licence

The trained model artefact (`outputs/model_random-forest_v1.joblib`) and all associated evaluation outputs are released under the **MIT Licence**. The underlying training data (GeoSphere Austria Messstationen Tagesdaten v2) remain under the **CC0 1.0** licence as provided by GeoSphere Austria. The source code used to train and evaluate the model is also released under the **MIT Licence**; see [`LICENSE`](../LICENSE) in the repository root.

<!-- TODO: Create a LICENSE file in the repo root with the MIT licence text if not already present. -->
<!-- TODO: Add TUWRD DOI for the model artefact deposit once registered. -->

| Artefact | Licence |
|----------|---------|
| Training data | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Source code | [MIT](https://opensource.org/licenses/MIT) |
| Trained model artefact | [MIT](https://opensource.org/licenses/MIT) |
| Evaluation outputs (figures, metrics) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

---

## Contributors

| Name | Role | ORCID |
|------|------|-------|
| Sophie Konecny | A    | [0009-0006-5745-5729](https://orcid.org/0009-0006-5745-5729) |
| Vivek Sharma | B    | [0009-0006-4879-6388](https://orcid.org/0009-0006-4879-6388) |
| Anxhela Sulmina | D    | [0009-0008-9371-0488](https://orcid.org/0009-0008-9371-0488) |
| Nayma Alam | C    | <!-- TODO: ORCID --> |

---

*This model card follows the format proposed by [Mitchell et al. (2019)](https://doi.org/10.1145/3287560.3287596).*
