-- ===========================================================
-- WP2 T2.4 - DBRepo view definitions
-- Frost Day Prediction in Vienna
-- ===========================================================

USE frost_day_vienna;  

DROP VIEW IF EXISTS vw_ml_daily_features;
DROP VIEW IF EXISTS vw_ml_complete_cases;
DROP VIEW IF EXISTS vw_ml_balanced_training_sample;
DROP VIEW IF EXISTS vw_monthly_frost_summary;
 
CREATE VIEW vw_ml_daily_features AS
SELECT
    s.station_code,
    s.name AS station_name,
    s.latitude,
    s.longitude,
    s.altitude_m,
    o.obs_date,
    YEAR(o.obs_date) AS obs_year,
    MONTH(o.obs_date) AS obs_month,
    DAYOFYEAR(o.obs_date) AS obs_day_of_year,
    o.temp_mean_c,
    o.temp_max_c,
    o.temp_min_c,
    o.precipitation_mm,
    o.sunshine_h,
    o.humidity_pct,
    o.visibility_m,
    CASE WHEN o.temp_min_c < 0 THEN 1 ELSE 0 END AS is_frost_day
FROM daily_observation AS o
INNER JOIN station AS s
    ON s.station_id = o.station_id;

CREATE VIEW vw_ml_complete_cases AS
SELECT
    station_code,
    obs_date,
    obs_year,
    obs_month,
    obs_day_of_year,
    temp_mean_c,
    temp_max_c,
    temp_min_c,
    precipitation_mm,
    sunshine_h,
    humidity_pct,
    visibility_m,
    is_frost_day
FROM vw_ml_daily_features
WHERE temp_mean_c IS NOT NULL
  AND temp_max_c IS NOT NULL
  AND temp_min_c IS NOT NULL
  AND precipitation_mm IS NOT NULL
  AND sunshine_h IS NOT NULL
  AND humidity_pct IS NOT NULL
  AND visibility_m IS NOT NULL;

CREATE VIEW vw_ml_balanced_training_sample AS
WITH labelled_rows AS (
    SELECT
        cc.*,
        ROW_NUMBER() OVER (
            PARTITION BY cc.is_frost_day
            ORDER BY cc.obs_date, cc.station_code
        ) AS class_row_number
    FROM vw_ml_complete_cases AS cc
),
class_counts AS (
    SELECT is_frost_day, COUNT(*) AS class_count
    FROM vw_ml_complete_cases
    GROUP BY is_frost_day
),
sample_size AS (
    SELECT MIN(class_count) AS rows_per_class
    FROM class_counts
)
SELECT
    station_code,
    obs_date,
    obs_year,
    obs_month,
    obs_day_of_year,
    temp_mean_c,
    temp_max_c,
    temp_min_c,
    precipitation_mm,
    sunshine_h,
    humidity_pct,
    visibility_m,
    is_frost_day
FROM labelled_rows
CROSS JOIN sample_size
WHERE class_row_number <= rows_per_class;

CREATE VIEW vw_monthly_frost_summary AS
SELECT
    station_code,
    obs_year,
    obs_month,
    COUNT(*) AS observation_days,
    SUM(is_frost_day) AS frost_days,
    ROUND(AVG(temp_min_c), 2) AS avg_min_temp_c,
    ROUND(SUM(precipitation_mm), 2) AS precipitation_total_mm
FROM vw_ml_complete_cases
GROUP BY station_code, obs_year, obs_month;
