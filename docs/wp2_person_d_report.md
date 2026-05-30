# WP2 Person D Notes

This file summarises what I did for the Person D tasks in WP2.

## T2.4 View Definitions

For T2.4, the assignment asks for SQL `VIEW` definitions with meaningful names.
The views should make the normalised DBRepo tables easier to use for the ML
pipeline.

I put the SQL definitions in `docs/views.sql`.

| View | Purpose |
|------|---------|
| `vw_ml_daily_features` | Feature view with station metadata, date features, weather values, and the frost-day label. |
| `vw_ml_complete_cases` | ML-ready rows where all model input columns are present. |
| `vw_ml_balanced_training_sample` | Deterministic class-balanced sample with equal frost and non-frost rows. |
| `vw_monthly_frost_summary` | Monthly quality-check summary with observation count, frost-day count, average minimum temperature, and precipitation total. |

The SQL file is the main T2.4 result. I also tried to create the same views in
DBRepo. The DBRepo view builder/client only created simple raw-column views for
some of them, so I documented the limitation in
`docs/dbrepo_view_limitations.md`.

## T2.6 DBRepo API Reimplementation

For T2.6, I rewrote the data-loading part in
`src/02_load-data-from-dbrepo.py`. The script loads the data from DBRepo instead
of reading a local CSV file.

The script:

- retrieves data from the DBRepo REST API;
- uses the DBRepo view-data endpoint configured in `.env`;
- handles connection errors, timeouts, HTTP errors, invalid JSON, empty
  responses, missing columns, and pagination;
- derives `obs_month`, `obs_day_of_year`, and `is_frost_day` from the API data;
- excludes `temp_min_c` from the final model feature matrix to avoid target
  leakage.

API endpoint used for the feature data:

```text
GET {DBREPO_ENDPOINT}/api/v1/database/{DATABASE_ID}/view/{DBREPO_FEATURE_VIEW_ID}/data?page={page}&size={size}
```

Authentication:

```text
HTTP Basic Authentication with DBREPO_USERNAME and DBREPO_PASSWORD
```

## Verification Statement

The original CSV is not kept as a local file in this repository. It has already
been uploaded into DBRepo. Because of that, I verified the DBRepo feature-view
loading path against the uploaded DBRepo source table after applying the same
transformations.

Command:

```powershell
python src\02_load-data-from-dbrepo.py --dbrepo-table-check
```

Output:

```text
row_match: True
numeric_match: True
label_match: True
identical: True
source_table_rows: 5071
feature_view_rows: 5071
```

Statement for the final report:

The reimplemented DBRepo API loading path produces data identical to the
uploaded DBRepo source table after applying the same transformations as the
original local-file workflow.

