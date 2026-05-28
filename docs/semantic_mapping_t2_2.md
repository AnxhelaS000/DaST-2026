# T2.2 Semantic Mapping

## Ontologies used

We use the Climate and Forecast Standard Names ontology for meteorological attributes because the dataset consists of climate and weather measurements, including air temperature, precipitation, humidity, sunshine duration and wind speed. CF Standard Names are widely used for unambiguous description of geophysical and meteorological variables, and the NERC Vocabulary Server provides persistent URIs for these concepts.

For structural observation metadata such as observation time and station/platform, we use SOSA/SSN because it is a W3C/OGC ontology for sensors, observations, observed properties and platforms.

## Semantic mapping table

| DBRepo table | DBRepo column | Meaning | Semantic concept / URI | Ontology |
|---|---|---|---|---|
| `station` | `station_id` | unique numeric station identifier | `http://www.w3.org/ns/sosa/Platform` | SOSA/SSN |
| `station` | `station_code` | alphanumeric station code assigned by GeoSphere Austria | `http://www.w3.org/ns/sosa/Platform` | SOSA/SSN |
| `station` | `name` | human-readable station name | `http://www.w3.org/ns/sosa/Platform` | SOSA/SSN |
| `station` | `latitude` | station latitude | `http://www.w3.org/2003/01/geo/wgs84_pos#lat` | WGS84 Geo |
| `station` | `longitude` | station longitude | `http://www.w3.org/2003/01/geo/wgs84_pos#long` | WGS84 Geo |
| `station` | `altitude_m` | station altitude above sea level | `http://www.w3.org/2003/01/geo/wgs84_pos#alt` | WGS84 Geo |
| `daily_observation` | `station_id` | foreign key referencing the station | `http://www.w3.org/ns/sosa/hasFeatureOfInterest` | SOSA/SSN |
| `daily_observation` | `obs_date` | date of the daily observation | `http://www.w3.org/ns/sosa/resultTime` | SOSA/SSN |
| `daily_observation` | `temp_mean_c` | daily mean air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `daily_observation` | `temp_max_c` | daily maximum air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `daily_observation` | `temp_min_c` | daily minimum air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `daily_observation` | `precipitation_mm` | daily precipitation amount | `http://vocab.nerc.ac.uk/standard_name/precipitation_amount/` | CF Standard Names |
| `daily_observation` | `sunshine_h` | sunshine duration | `http://vocab.nerc.ac.uk/standard_name/duration_of_sunshine/` | CF Standard Names |
| `daily_observation` | `humidity_pct` | mean relative humidity | `http://vocab.nerc.ac.uk/standard_name/relative_humidity/` | CF Standard Names |
| `daily_observation` | `visibility_m` | horizontal visibility distance | `http://vocab.nerc.ac.uk/standard_name/visibility_in_air/` | CF Standard Names |
## DBRepo metadata integration

These semantic mappings are intended to be added to the DBRepo column metadata via the DBRepo REST API after the database schema and table identifiers from T2.1 are available. Each dataset attribute will be annotated with its corresponding ontology URI so that the attributes are findable and interoperable according to the FAIR requirements.
