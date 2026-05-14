-- ============================================================
-- Frost Day Prediction in Vienna
-- Relational schema in Third Normal Form (3NF)
-- Source data: GeoSphere Austria – Messstationen Tagesdaten v2
--              Station: Wien-Hohe Warte | Period: 2000–2023
--              License: CC0
-- ============================================================

CREATE SCHEMA IF NOT EXISTS frost_day_vienna
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE frost_day_vienna;

DROP TABLE IF EXISTS daily_observation;
DROP TABLE IF EXISTS station;

-- Table 1: station
-- Holds one row per weather station.
-- Normalises all station-level attributes out of the observation
-- table, eliminating repetition across thousands of daily rows.
CREATE TABLE IF NOT EXISTS station (
    station_id    INT          NOT NULL AUTO_INCREMENT,
    station_code  VARCHAR(20)  NOT NULL COMMENT 'GeoSphere Austria station identifier',
    name          VARCHAR(100) NOT NULL COMMENT 'Human-readable station name',
    latitude      DECIMAL(8,5)          COMMENT 'WGS84 latitude in decimal degrees',
    longitude     DECIMAL(8,5)          COMMENT 'WGS84 longitude in decimal degrees',
    altitude_m    INT                   COMMENT 'Station altitude above sea level [m]',
    PRIMARY KEY (station_id),
    UNIQUE KEY uq_station_code (station_code)
) ENGINE=InnoDB
  COMMENT='Weather station metadata (GeoSphere Austria)';


-- Table 2: daily_observation
-- Holds one row per (station, calendar date).
-- Every attribute is a direct measurement or aggregate for that
-- specific station-date combination – no non-key attribute
-- determines another, satisfying 3NF.
CREATE TABLE IF NOT EXISTS daily_observation (
    station_id       INT          NOT NULL  COMMENT 'FK → station.station_id',
    obs_date         DATE         NOT NULL  COMMENT 'Observation date (UTC+1)',
    temp_mean_c      DECIMAL(5,2)           COMMENT 'tl_mittel  – daily mean air temperature [°C]',
    temp_max_c       DECIMAL(5,2)           COMMENT 'tlmax      – daily maximum air temperature [°C]',
    temp_min_c       DECIMAL(5,2)           COMMENT 'tlmin      – daily minimum air temperature [°C]',
    precipitation_mm DECIMAL(6,2)           COMMENT 'rr         – daily precipitation sum [mm]',
    sunshine_h       DECIMAL(5,2)           COMMENT 'so_h       – daily sunshine duration [h]',
    humidity_pct     DECIMAL(5,2)           COMMENT 'rf_mittel  – daily mean relative humidity [%]',
    visibility_m     DECIMAL(8,1)           COMMENT 'vv_mittel  – daily mean horizontal visibility [m]',
    PRIMARY KEY (station_id, obs_date),
    CONSTRAINT fk_obs_station
        FOREIGN KEY (station_id) REFERENCES station (station_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
  COMMENT='Daily meteorological observations (GeoSphere Austria, CC0)';
