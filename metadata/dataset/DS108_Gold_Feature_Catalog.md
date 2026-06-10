# DS108-Electrimight Gold Feature Catalog

This catalog summarizes the feature groups in `data/gold/steel_final.csv`. The
complete field-level inventory is maintained in `metadata/dataset/CODEBOOK.csv`.

## Dataset Overview

| Item | Value |
|---|---|
| Dataset path | `data/gold/steel_final.csv` |
| Shape | 35,040 rows x 69 columns |
| Frequency | 15 minutes |
| Time range | 2018-01-01 00:00 to 2018-12-31 23:45 |
| Location | POSCO Gwangyang steel plant, South Korea |
| Primary target for forecasting | `Usage_kWh(t+1h)` |
| Proxy anomaly target | `anomaly_any` |

The feature design is intentionally organized by evidence source. This makes the
ablation results interpretable: the project can compare raw context, temporal
history, weather context, wavelet features, physical features, and GAN-augmented
minority-class examples.

## Feature Groups

| Group | Columns | Purpose |
|---|---:|---|
| Raw electrical and calendar variables | 11 | preserve source measurements and operating context |
| Weather variables | 4 | add exogenous environmental context |
| Weather-derived variables | 7 | summarize weather dynamics and interactions |
| Time-domain variables | 15 | capture lagged demand and rolling behavior |
| DWT wavelet variables | 16 | capture transient frequency-domain behavior |
| Physics-informed variables | 7 | represent power-triangle relationships |
| Proxy anomaly variables | 9 | provide auditable weak labels and explanations |
| **Total** | **69** |  |

## 1. Raw Electrical and Calendar Variables

The first group is loaded from the UCI steel dataset and cleaned in the bronze to
silver stage. It includes timestamp, active usage, lagging/leading reactive
power, CO2, power factor, seconds from midnight, weekday/weekend status, weekday
name, and load type.

Important preprocessing decisions:

- `date` is parsed with `dayfirst=True`;
- power-factor columns are converted from percentage scale to `[0, 1]`;
- valid zero reactive-power values are preserved because they reflect operating
  state, not necessarily missingness;
- the raw source layer remains read-only.

## 2. Weather Variables

Weather data comes from Open-Meteo for Gwangyang coordinates. The original
weather frequency is hourly; the pipeline resamples it to the steel dataset's
15-minute grid before merging.

Variables:

- `temperature_2m`
- `precipitation`
- `relative_humidity_2m`
- `windspeed_10m`

Weather is treated as exogenous context. It is not a direct explanation for
equipment faults, but it helps contextualize industrial load variation.

## 3. Weather-Derived Variables

The weather-derived group adds interpretable transformations:

- rolling 24-hour temperature;
- 24-hour temperature difference;
- heat index;
- extreme-hot and extreme-cold flags;
- humidity-temperature interaction;
- rolling 6-hour wind speed.

These features support contextual enrichment in downstream evaluation. The
ablation results show that adding weather improves proxy anomaly classification
under the full-track setting.

## 4. Time-Domain Variables

Time-domain features are created from `Usage_kWh`:

- lags at 15 minutes, 30 minutes, 1 hour, and 24 hours;
- rolling mean, standard deviation, and skewness over 6-hour, 12-hour, and
  24-hour windows;
- sine/cosine encoding of seconds from midnight.

These features are causal: they use past and current information only. They are
the strongest group for the 1-hour-ahead forecasting task, where the best RMSE
comes from the RAW + TIME configuration.

## 5. Frequency-Domain DWT Variables

The pipeline computes rolling discrete wavelet transform features using:

- wavelet: Daubechies-4 (`db4`);
- decomposition level: 3;
- rolling window: 64 observations, equivalent to 16 hours.

For each coefficient band (`cA`, `cD3`, `cD2`, `cD1`), the pipeline extracts:

- mean;
- standard deviation;
- energy;
- maximum absolute value.

The DWT group is intended to capture transients and load oscillations that are
less visible in smoothed rolling statistics.

## 6. Physics-Informed Variables

The physics-informed group derives electrical quantities from active power,
reactive power, and power factor:

- apparent power;
- net reactive power;
- total reactive magnitude;
- apparent power from net reactive power;
- lagging and leading phase-angle features.

These variables help explain electrical stress and power-factor degradation in a
form that is easier to audit than a purely black-box model input.

## 7. Proxy Anomaly Variables

The final group records proxy anomaly labels:

- `anomaly_idling`
- `anomaly_leakage`
- `anomaly_overload`
- `anomaly_any`
- confidence scores for each label type;
- `anomaly_max_score`;
- `anomaly_explanation`.

These labels are rule-based and explainable. They should be used as benchmark
annotations, not as confirmed operational ground truth.

Current label distribution:

| Label | Count | Rate |
|---|---:|---:|
| Idling | 10 | 0.03% |
| Leakage/concept drift | 2,336 | 6.67% |
| Overload | 48 | 0.14% |
| Any proxy anomaly | 2,388 | 6.815% |

## Pipeline Order

1. `src/bronze/data_loader.py` loads and cleans the original steel data.
2. `src/bronze/weather_loader.py` loads, resamples, and merges weather data.
3. `src/silver/time_features.py` creates lag, rolling, and cyclic features.
4. `src/silver/wavelet_features.py` creates DWT wavelet features.
5. `src/silver/physical_features.py` creates electrical-domain features.
6. `src/silver/anomaly_labels.py` creates proxy anomaly labels.
7. `src/gold/pipeline.py` writes the final gold dataset.

## Interpretation for Reporting

The feature catalog supports the main project claim: Electrimight is a
feature-centric preprocessing pipeline. The strongest forecasting improvement
comes from temporal history, while the strongest proxy anomaly classification
result comes from adding weather context under the full-track ablation. The
project should therefore be described as an auditable dataset-building and
preprocessing study, not as a production fault-detection system.
