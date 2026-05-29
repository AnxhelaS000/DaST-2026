# DBRepo View Creation Limitations

This note explains why the full SQL views from `docs/views.sql` are not all
available as native DBRepo views.

The SQL definitions need features that the DBRepo web/client view builder did
not accept during this exercise:

| Intended view | Required SQL feature | DBRepo result |
|---------------|----------------------|---------------|
| `vw_ml_daily_features` | Join plus computed columns such as `YEAR(obs_date)` and `is_frost_day` | DBRepo created only a simple raw-column view. A temporary join test failed in the Python client. |
| `vw_ml_complete_cases` | `IS NOT NULL` filters across all model input columns | A temporary complete-case filter view failed with `failed to save in search service`. |
| `vw_ml_balanced_training_sample` | CTE plus `ROW_NUMBER() OVER (PARTITION BY ...)` | Not supported by the DBRepo view builder/client. |
| `vw_monthly_frost_summary` | `GROUP BY` aggregation with counts, sums, and averages | DBRepo created only a simple raw-column view. |

I also tested raw SQL creation through the REST endpoint with a temporary view
payload. DBRepo returned:

```text
POST /api/v1/database/<database_id>/view -> 400
Failed to read request
``` 

For that reason, `docs/views.sql` is kept as the SQL definition for T2.4. The
Python loader in `src/02_load-data-from-dbrepo.py` implements the equivalent
model-loading logic needed for T2.6.

