# Datasheet for DS108-Electrimight

This datasheet documents the dataset produced by the DS108-Electrimight
preprocessing pipeline. It follows the intent of the "Datasheets for Datasets"
framework while using report-style wording suitable for academic review.

## 1. Motivation

DS108-Electrimight was created to support research and coursework on industrial
electricity-consumption preprocessing. The dataset is designed for two related
tasks:

- short-term electricity consumption forecasting;
- offline proxy anomaly analysis for energy-waste, leakage/concept drift, and
  overload-risk patterns.

The project extends the original UCI Steel Industry Energy Consumption dataset
with exogenous weather data, time-domain features, DWT wavelet features, and
physics-informed electrical features. The final product is a methodological
benchmark, not a commercial plant-monitoring product.

The dataset was prepared by the DS108 student research group at the University
of Information Technology, Vietnam National University Ho Chi Minh City. No
external funding was used.

## 2. Dataset Composition

Each row represents one 15-minute observation from the POSCO Gwangyang steel
plant in South Korea during 2018. The final gold dataset has:

- **35,040 rows**, covering 365 days at 15-minute frequency;
- **69 columns**, combining source measurements, weather context, engineered
  features, and proxy anomaly labels;
- a continuous timestamp range from **2018-01-01 00:00** to
  **2018-12-31 23:45**.

The final dataset contains the following groups of variables:

| Group | Count | Description |
|---|---:|---|
| Raw electrical and calendar variables | 11 | UCI steel measurements and original time/category fields |
| Weather variables | 4 | Open-Meteo historical weather for Gwangyang |
| Weather-derived variables | 7 | rolling temperature, weather deltas, heat index, interaction features |
| Time-domain variables | 15 | lag, rolling, and cyclic time features |
| DWT wavelet variables | 16 | frequency-domain summaries from rolling Daubechies-4 decomposition |
| Physics-informed variables | 7 | apparent power, reactive-power summaries, phase-angle features |
| Proxy anomaly variables | 9 | boolean labels, confidence scores, and explanation text |

The full column-level description is maintained in
`metadata/dataset/CODEBOOK.csv` and
`metadata/dataset/DS108_Gold_Feature_Catalog.md`.

## 3. Source Data

### Steel Industry Energy Consumption

The electrical source data comes from the UCI Machine Learning Repository:

- Dataset: Steel Industry Energy Consumption
- URL: https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption
- Original authors: Sathishkumar V. E., Jangwoo Park, and Yongyun Cho
- Location: POSCO Gwangyang steel plant, South Korea
- Time range: 01/01/2018 to 31/12/2018
- Frequency: 15 minutes

The original date format is `DD/MM/YYYY`; the project parses it with
`dayfirst=True`.

### Weather Data

Weather variables were collected from the Open-Meteo Historical Weather API for
Gwangyang coordinates:

- Latitude: 34.975 N
- Longitude: 127.589 E
- Frequency before merging: hourly
- Variables: temperature, precipitation, relative humidity, and wind speed

Weather data is exogenous. The pipeline resamples hourly observations to
15-minute intervals before merging them with the steel data.

## 4. Preprocessing and Feature Engineering

The data pipeline uses a Bronze-Silver-Gold structure:

| Layer | Path | Description |
|---|---|---|
| Bronze | `data/bronze/` | original steel CSV and downloaded weather CSV |
| Silver | `data/silver/steel_clean.csv` | cleaned electrical data with normalized power factor |
| Gold | `data/gold/steel_final.csv` | final dataset after weather merge, feature engineering, and labels |

Main transformations:

- remove duplicate timestamps and validate timestamp continuity;
- normalize power factor from percentage scale to `[0, 1]`;
- preserve valid zero reactive-power values as physical signals rather than
  treating them as missing data;
- resample hourly weather to 15-minute frequency by linear interpolation;
- create lag and rolling statistics from past observations only;
- encode daily cyclic behavior with sine/cosine features;
- compute DWT wavelet summaries over rolling 64-sample windows;
- derive apparent power, net/total reactive power, and phase-angle features;
- create proxy anomaly labels with confidence scores and explanations.

Algorithmic missing values are expected in early rows of lag and rolling-window
features. These values are a consequence of causal feature construction and are
documented rather than silently imputed.

## 5. Labels and Intended Interpretation

The dataset includes three proxy anomaly labels:

| Label | Interpretation | Evidence basis |
|---|---|---|
| `anomaly_idling` | off-hours light-load consumption with poor power factor | operating schedule, usage level, power factor |
| `anomaly_leakage` | sustained consumption increase over baseline | rolling mean compared with early-period baseline |
| `anomaly_overload` | extreme usage with reactive-power or power-factor stress | robust usage percentile and electrical stress indicators |

The labels are **physics-informed weak/proxy labels**. They support offline
benchmarking and explainable analysis but should not be presented as verified
equipment faults. Real deployment would require maintenance logs, SCADA events,
or expert electrical inspection.

Current generated counts:

| Metric | Value |
|---|---:|
| Idling proxy rows | 10 |
| Leakage/concept-drift proxy rows | 2,336 |
| Overload proxy rows | 48 |
| Any proxy anomaly rows | 2,388 |
| Any proxy anomaly rate | 6.815% |

## 6. Quality and Validation

The latest validation summary reports the following checks as passed:

- temporal ordering;
- duplicate timestamp detection;
- NSM timestamp consistency;
- null checks;
- non-negative usage;
- power-factor range;
- physical consistency;
- anomaly-rate threshold;
- feature-count expectation.

The current test summary is **52 passed**.

The leakage audit confirms that lag and rolling features use past information
only, weather merging does not use future back-fill, and proxy labels are kept as
targets/annotations rather than ordinary predictive features.

## 7. Uses

Appropriate uses:

- short-term industrial load forecasting;
- educational analysis of preprocessing decisions;
- feature-ablation studies;
- offline proxy anomaly benchmarking;
- comparison between raw, temporal, weather, wavelet, physical, and synthetic
  augmentation feature groups.

Uses that require caution:

- operational safety decisions;
- legal or contractual decisions about energy consumption;
- direct SCADA deployment;
- cross-factory generalization without schema mapping and threshold review.

## 8. Distribution

At the time of this repository snapshot, the dataset is distributed with the
project files because the current gold CSV is below GitHub's hard per-file
limit. If future generated artifacts grow substantially, the preferred
distribution plan is:

- GitHub for code, metadata, notebooks, and small reproducibility artifacts;
- Kaggle Datasets for a public data-science download link;
- Zenodo for a citable academic snapshot when a DOI is needed;
- DVC or Git LFS only when versioned large artifacts must remain connected to the
  Git workflow.

Publication steps should be recorded with the final release notes or deployment
notes submitted with the project deliverables.

## 9. Maintenance

The DS108 project group maintains this dataset for academic review. Updates
should be versioned with:

- a clear changelog or release note;
- updated `CODEBOOK.csv` when columns change;
- updated feature catalog when feature definitions change;
- updated labeling methodology when thresholds or label logic change;
- regenerated pipeline summaries and validation outputs.

Older dataset versions should remain traceable through Git tags, Kaggle versions,
or release archives.
