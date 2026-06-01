# Data Codebook — Steel Industry Energy Consumption Dataset

> **Dataset:** UCI Steel Industry Energy Consumption (2018)
> **Observations:** 35,040 | **Interval:** 15 minutes | **Period:** 2018-01-01 to 2018-12-31
> **Weather source:** Open-Meteo API, Gwangyang, Korea (34.975°N, 127.589°E, timezone: Asia/Seoul)

---

## Table A-I: Raw Features

| Variable Name | Type | Unit | Min | Max | Description |
|---|---|---|---|---|---|
| `date` | datetime | — | 2018-01-01 00:00 | 2018-12-31 23:45 | Timestamp at 15-min intervals; no gaps or duplicates |
| `Usage_kWh` | float | kWh | 0.00 | 157.18 | Active energy consumption per interval; right-skewed (mean=27.39, median=4.57) |
| `Lagging_Current_Reactive_Power_kVarh` | float | kVarh | 0.00 | 96.91 | Lagging reactive power; 20.53% zero values; positively correlated with `Usage_kWh` |
| `Leading_Current_Reactive_Power_kVarh` | float | kVarh | 0.00 | 27.76 | Leading reactive power; 67.38% zero values; negatively correlated with `Usage_kWh` (r = −0.325) |
| `CO2(tCO2)` | float | tCO₂ | 0.00 | 0.07 | CO₂ emission equivalent; 59.90% zero values; near-perfect correlation with `Usage_kWh` — likely a derived proxy, not an independent sensor signal |
| `Lagging_Current_Power_Factor` | float | % | 0.00 | 100.00 | Lagging power factor reported by meter; mean=80.58%, median=87.96% |
| `Leading_Current_Power_Factor` | float | % | 0.00 | 100.00 | Leading power factor reported by meter; median=100%, indicating predominantly resistive/corrected load |
| `NSM` | int | s | 0 | 85500 | Seconds from midnight; encodes intra-day position at 15-min resolution (00:00 → 23:45) |
| `WeekStatus` | categorical | — | — | — | Day type: Weekday (71.51%, n=25,056) / Weekend (28.49%, n=9,984) |
| `Day_of_week` | categorical | — | — | — | Day of week; Sunday lowest mean (7.55 kWh), Thursday highest (35.11 kWh) |
| `Load_Type` | categorical | — | — | — | Light\_Load (51.58%) / Medium\_Load (27.67%) / Maximum\_Load (20.75%) |

> **Note:** Zero values in reactive power variables are retained as valid operational states, not treated as missing values.

---

## Table A-II: Engineered Features

### A. Physical Derivatives

| Feature Name | Formula / Logic | Unit | Description |
|---|---|---|---|
| `Apparent_Power_S` | √(P² + Q_net²), where Q_net is computed internally from lagging and leading reactive energy | proxy | Relative apparent load index; combines active and net reactive energy per 15-min interval. Unit is interval-relative, not instantaneous kVA. Referred to as *apparent-load proxy* in the paper to avoid implying instantaneous power measurement; the column name `Apparent_Power_S` is retained in the dataset |
| `Phase_Angle_Phi` | Phase angle derived from active/reactive relationship or normalized power factor, depending on implementation | rad | Relative phase angle proxy used to describe active–reactive load relationship |

> **Note:** Columns such as `Q_net`, `Power_Factor_Volatility`, `Reactive_Power_Ratio`, `PF_derived_abs`, and `PF_signed` may be computed internally for rule evaluation but are not persistent columns in the current Gold table unless explicitly materialized. The labeling rules use `PF_rule = Lagging_Current_Power_Factor / 100` (derived from the raw meter column), not a persisted `PF_abs` column. `Apparent_Power_S` is the persistent column name used throughout the dataset and all labeling rules.
>
> **Note:** Some intermediate quantities used by labeling functions may be computed in memory and not persisted as dataframe columns. The codebook lists only persistent columns unless explicitly stated otherwise.

### B. Time-Domain Statistical Features

| Feature Name | Formula / Logic | Unit | Description |
|---|---|---|---|
| `Usage_kWh_lag_1` | `Usage_kWh`.shift(1) | kWh | 1-step lag, corresponding to 15 minutes prior |
| `Usage_kWh_lag_2` | `Usage_kWh`.shift(2) | kWh | 2-step lag, corresponding to 30 minutes prior |
| `Usage_kWh_lag_4` | `Usage_kWh`.shift(4) | kWh | 4-step lag, corresponding to 1 hour prior |
| `Usage_kWh_lag_96` | `Usage_kWh`.shift(96) | kWh | 96-step lag, corresponding to the same time on the previous day |

### C. Frequency-Domain Features (DWT — Daubechies-4, 3-level decomposition)

| Feature Name Pattern | Formula / Logic | Unit | Description |
|---|---|---|---|
| `Usage_kWh_cA_mean` | Mean of DWT approximation coefficients | — | Average low-frequency trend component within a 64-sample causal window |
| `Usage_kWh_cA_std` | Standard deviation of DWT approximation coefficients | — | Variability of low-frequency trend component |
| `Usage_kWh_cA_energy` | Energy of DWT approximation coefficients | — | Magnitude of low-frequency trend component |
| `Usage_kWh_cA_max_abs` | Maximum absolute value of DWT approximation coefficients | — | Peak magnitude of low-frequency trend component |
| `Usage_kWh_cD1_mean`, `Usage_kWh_cD2_mean`, `Usage_kWh_cD3_mean` | Mean of DWT detail coefficients by level | — | Average detail component at each decomposition level |
| `Usage_kWh_cD1_std`, `Usage_kWh_cD2_std`, `Usage_kWh_cD3_std` | Standard deviation of DWT detail coefficients by level | — | Variability of detail components |
| `Usage_kWh_cD1_energy`, `Usage_kWh_cD2_energy`, `Usage_kWh_cD3_energy` | Energy of DWT detail coefficients by level | — | Magnitude of transient/frequency components |
| `Usage_kWh_cD1_max_abs`, `Usage_kWh_cD2_max_abs`, `Usage_kWh_cD3_max_abs` | Maximum absolute value of DWT detail coefficients by level | — | Peak detail magnitude at each decomposition level |

> **Note:** Wavelet features are named using the target column as prefix. For `target_col="Usage_kWh"`, generated columns follow the pattern `Usage_kWh_cA_*` and `Usage_kWh_cD[1-3]_*`. No engineered wavelet column contains the literal substring `dwt`.
>
> **Note:** DWT features are computed on causal 64-sample sliding windows: `W_t = {x(t−63), …, x(t)}`. Each output scalar is assigned to the most recent timestamp `t` in the window, preserving temporal causality.

### D. Cyclic Time Encoding

| Feature Name | Formula / Logic | Unit | Description |
|---|---|---|---|
| `Hour` | timestamp.hour | int | Hour of day ∈ [0, 23] |
| `Month` | timestamp.month | int | Month ∈ [1, 12] |
| `Time_Sine` | sin(2π · NSM / 86400) | — | Cyclic sine encoding of intra-day position |
| `Time_Cosine` | cos(2π · NSM / 86400) | — | Cyclic cosine encoding of intra-day position |
| `Is_Weekend` | 1 if Weekend, else 0 | binary | Weekday mean=33.63 kWh vs weekend mean=11.73 kWh |

### E. Weather-Derived Features

> Resampled from hourly to 15-min via forward-fill before merge. The 3 final timestamps at 2018-12-31 23:15–23:45 were filled via forward-fill from the 23:00 observation.

| Feature Name | Formula / Logic | Unit | Description |
|---|---|---|---|
| `temperature_2m` | Raw from API | °C | Ambient temperature; range [−10.6, 35.7], mean=13.85°C |
| `relative_humidity_2m` | Raw from API | % | Relative humidity; mean=70.67% |
| `precipitation` | Raw from API | mm | Rainfall; highly right-skewed — 85% of hours have zero precipitation |
| `windspeed_10m` | Raw from API | km/h | Wind speed at 10 m; mean=10.46 km/h |
| `THI` | T − 0.55 · (1 − RH/100) · (T − 14.5) | — | Temperature-Humidity Index; weak global correlation with `Usage_kWh` (r=0.038), stronger in nighttime and Light\_Load subsets |
| `Thermal_Lag_3h` | `temperature_2m`.shift(12) | °C | Temperature lagged by 3 hours (12 records) |
| `Thermal_Lag_6h` | `temperature_2m`.shift(24) | °C | Temperature lagged by 6 hours; r=−0.306 with `Usage_kWh` in Medium\_Load group |
| `temp_rolling_24h` | Rolling mean of `temperature_2m`, window=96 | °C | 24-hour trailing mean temperature after weather resampling |
| `windspeed_rolling_6h` | Rolling mean of `windspeed_10m`, window=24 | km/h | 6-hour trailing mean wind speed after weather resampling |

---

## Table A-III: Weak Label Codebook

> **Important:** All labels are rule-based weak/proxy labels, not validated ground-truth fault annotations. They should not be interpreted as confirmed operational failures. Synthetic samples generated from minority labels via GAN augmentation are used for class-balance evaluation only and do not constitute evidence of real fault events.

| Label | Rule Condition | Safe Interpretation | Observed % |
|---|---|---|---|
| `Suspected_Idling` | `Load_Type` = `Light_Load` **AND** `Usage_kWh` > Median(`Usage_kWh` \| `Light_Load`, `Hour`, `WeekStatus`) **AND** (`Lagging_Current_Power_Factor` / 100) < 0.50 **AND** duration ≥ 4 consecutive rows | Idle-waste behavior: non-negligible consumption with poor power factor under Light\_Load conditions. Not confirmed machine shutdown. | 0.582% |
| `Suspected_Overload` | `Apparent_Power_S` > P99.5(`Apparent_Power_S` \| `Load_Type`, `Hour`, `WeekStatus`) **AND** (`Lagging_Current_Power_Factor` / 100) < 0.70 | High-stress proxy signal: point anomaly allowed, no minimum duration. Precision over recall by design. Not verified asset-level overload. | 0.009% |
| `Suspected_Leakage_Drift` | `Usage_kWh` > 1 **AND** 28-day rolling mean of `Apparent_Power_S` increases ≥ 5% relative to `Load_Type` baseline **AND** at least one of: (i) (`Lagging_Current_Power_Factor` / 100) < 0.50, (ii) internal PF volatility > P95 by `Load_Type`, (iii) internal reactive ratio outside [P5, P95] by `Load_Type` **AND** duration ≥ 4 consecutive rows | Energy inefficiency drift signal. Not physical leakage, insulation failure, or confirmed equipment fault. | 9.829% |
| `anomaly_any` | Union of all three labels above; conflicts resolved by priority: Overload > Idling > Leakage\_Drift > Normal | Binary proxy anomaly flag for offline analysis, audit, and weak-supervision experiments. | 10.420% |

> **Threshold notation:** Context-relative thresholds (Median, P99.5) are computed within operational context groups defined by `Load_Type`, `Hour`, and `WeekStatus` — not as global cutoffs across the full dataset.
>
> **PF source:** Proxy rules use `PF_rule = Lagging_Current_Power_Factor / 100` (raw meter-reported value normalized to [0, 1]). `PF_derived_abs`, `PF_signed`, `Reactive_Power_Ratio`, and `Power_Factor_Volatility` are internal/diagnostic quantities unless explicitly materialized. No persistent `PF_meter_abs` or `PF_abs` column exists in the processed dataframe.
>
> **Observed percentages:** Reflect final pipeline output (35,040 × 64) as of v2.5 implementation. Idling 204 (0.582%), Leakage 3,444 (9.829%), Overload 3 (0.009%), anomaly_any 3,651 (10.420%).

---

## Table A-IV: Labeling Output Columns

> **Note:** These columns expand the processed dataframe from 55 to 64 columns, confirmed by the final v2.5 pipeline output.

| # | Column Name | Dtype | Description |
|---|---|---|---|
| 1 | `Suspected_Idling` | int8 | Idle-waste behavior flag: 1 = non-negligible consumption with `PF_rule` < 0.50 under Light\_Load sustained ≥ 1 hour. Not confirmed machine shutdown. |
| 2 | `Suspected_Leakage_Drift` | int8 | Energy inefficiency drift flag: 1 = rising `Apparent_Power_S` trend (28-day ≥ 5%) with poor PF/reactive conditions sustained ≥ 1 hour. Not physical leakage or insulation failure. |
| 3 | `Suspected_Overload` | int8 | High-stress proxy signal flag: 1 = `Apparent_Power_S` > P99.5 AND `PF_rule` < 0.70. Point anomaly (no minimum duration). Precision over recall by design. Not confirmed equipment fault. |
| 4 | `anomaly_any` | int8 | Binary proxy anomaly flag: union of Idling, Leakage\_Drift, and Overload. For offline analysis, audit, and weak-supervision experiments. |
| 5 | `dominant_label` | str | Winning label per priority: Overload > Idling > Leakage\_Drift > Normal. `"Excluded"` for hard-filtered rows. |
| 6 | `label_reason` | str | Machine-parseable string listing the conditions that triggered the label (e.g., `"PF<0.70;S>P99.5"`). If not materialized as a persistent column, the pipeline must capture trigger conditions in audit logs or validation reports. |
| 7 | `is_proxy_label` | bool | Dataset-level flag: always `True` for all rows, including `Normal`. This is a permanent reminder that **all label fields** (`Suspected_Idling`, `Suspected_Leakage_Drift`, `Suspected_Overload`, `anomaly_any`, `dominant_label`) originate from rule-based proxy labeling, not ground truth. |
| 8 | `baseline_warning` | bool | `True` if the context baseline computation fell back due to small group size (n < 10) or zero standard deviation. |
| 9 | `night_simplified_baseline_warning` | bool | `True` if `baseline_level = 3` (simplified fallback) AND `Hour ∈ {0–5}`. Labels remain assigned but warrant downstream caution. |

> **Confidence score:** `confidence_score` is **not materialized** in the current Gold table and remains an optional/future extension per LABELING_GUIDELINE_v2.5.md Section 9. Do not list it as a current persistent column.

> **Internal vs Persistent:** Columns such as `confidence_score`, `confidence_band`, `baseline_level`, `pf_clipped`, and intermediate point-level flags (`anomaly_idling_point`, etc.) may be computed during pipeline execution but are **not persistent Gold table columns** unless explicitly materialized.
>
> **`baseline_level` may be computed internally** to produce `baseline_warning` and `night_simplified_baseline_warning`; it does not have to be materialized as a persistent column if the warning flags are persisted.
>
> **`baseline_warning=True`** is an audit flag, not a data error or exclusion flag. It indicates that the context baseline computation used a simplified fallback group (e.g., n<10 or zero variance). Rows with `baseline_warning=True` are still labeled normally; downstream analysts can filter on this flag for sensitivity analysis.

---

## Terminology Notes

The following terms are used consistently across the codebook, labeling guideline, and paper:

| Term | Meaning / Constraint |
|---|---|
| **weak/proxy labels** | Rule-based labels — not ground truth, not SCADA-confirmed. |
| **apparent-load proxy** | `Apparent_Power_S` is an interval-relative index, not instantaneous kVA. |
| **energy inefficiency drift** | What `Suspected_Leakage_Drift` measures — not physical leakage. |
| **idle-waste behavior** | What `Suspected_Idling` measures — not machine shutdown. |
| **high-stress proxy signal** | What `Suspected_Overload` measures — not confirmed equipment fault. |
| **not ground truth** | Applied to all labels in this codebook. |
| **not SCADA-confirmed** | No supervisory control data available to validate labels. |
| **not physical leakage** | `Suspected_Leakage_Drift` is statistical, not insulation failure. |
| **not insulation failure** | Requires megohmmeter measurement; out of scope. |
| **not confirmed equipment fault** | No maintenance logs or asset-level thresholds available. |
