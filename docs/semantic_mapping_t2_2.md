# T2.2 Semantic Mapping

## Ontologies used

We use the Climate and Forecast Standard Names ontology for meteorological attributes because the dataset consists of climate and weather measurements, including air temperature, precipitation, humidity, sunshine duration and wind speed. CF Standard Names are widely used for unambiguous description of geophysical and meteorological variables, and the NERC Vocabulary Server provides persistent URIs for these concepts.

For structural observation metadata such as observation time and station/platform, we use SOSA/SSN because it is a W3C/OGC ontology for sensors, observations, observed properties and platforms.

## Semantic mapping table

| CSV column | Meaning | Semantic concept / URI | Ontology |
|---|---|---|---|
| `time` | observation date/time | `http://www.w3.org/ns/sosa/resultTime` | SOSA/SSN |
| `station` | weather station identifier | `http://www.w3.org/ns/sosa/Platform` | SOSA/SSN |
| `tl_mittel` | daily mean air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `tlmax` | daily maximum air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `tlmin` | daily minimum air temperature | `http://vocab.nerc.ac.uk/standard_name/air_temperature/` | CF Standard Names |
| `rr` | daily precipitation amount | `http://vocab.nerc.ac.uk/standard_name/precipitation_amount/` | CF Standard Names |
| `so_h` | sunshine duration / sunshine hours | `http://vocab.nerc.ac.uk/standard_name/duration_of_sunshine/` | CF Standard Names |
| `rf_mittel` | mean relative humidity | `http://vocab.nerc.ac.uk/standard_name/relative_humidity/` | CF Standard Names |
| `vv_mittel` | mean wind speed | `http://vocab.nerc.ac.uk/standard_name/wind_speed/` | CF Standard Names |
## DBRepo metadata integration

These semantic mappings are intended to be added to the DBRepo column metadata via the DBRepo REST API after the database schema and table identifiers from T2.1 are available. Each dataset attribute will be annotated with its corresponding ontology URI so that the attributes are findable and interoperable according to the FAIR requirements.
