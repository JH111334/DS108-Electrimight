# DS108-Electrimight: Complete Feature Catalog — `data/gold/steel_final.csv`

**Dataset shape:** 35,040 rows × 64 columns  
**Time range:** 2018-01-01 00:00 → 2018-12-31 23:45 (15-minute frequency)  
**Location:** POSCO Gwangyang Steel Plant, South Korea

---

## 1. Raw / Electrical (Bronze) — 11 features

Directly loaded from `Steel_industry_data.csv` after cleaning (duplicate removal, linear interpolation, Power-Factor scaling %→[0,1]).

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes (from data) |
|---|------|-------------|------------------------|------|------|---------------------------|
| 1 | **date** | Timestamp of the observation | Parsed from raw CSV with `dayfirst=True` | datetime | — | 2018-01-01 00:00:00 → 2018-12-31 23:45:00 (unique, 35,040 records) |
| 2 | **Usage_kWh** | Active power consumed (P) | Raw sensor measurement | float | kWh | 0.00 → 157.18; mean=27.39, std=33.44 |
| 3 | **Lagging_Current_Reactive.Power_kVarh** | Reactive power (lagging, inductive load Q) | Raw sensor measurement | float | kVarh | 0.00 → 96.91; mean=13.04, std=16.31 |
| 4 | **Leading_Current_Reactive_Power_kVarh** | Reactive power (leading, capacitive load) | Raw sensor measurement | float | kVarh | 0.00 → 27.76; mean=3.87, std=7.42 |
| 5 | **CO2(tCO2)** | CO₂ emissions associated with the observation | Raw sensor / calculated emission factor | float | tCO₂ | 0.00 → 0.07; mean=0.0115, std=0.016 |
| 6 | **Lagging_Current_Power_Factor** | Power factor (lagging / inductive) | Scaled from 0–100 % → 0–1 during cleaning; clipped to [0,1] | float | unitless | 0.00 → 1.00; mean=0.806, std=0.189 |
| 7 | **Leading_Current_Power_Factor** | Power factor (leading / capacitive) | Same scaling & clipping as lagging PF | float | unitless | 0.00 → 1.00; mean=0.844, std=0.305 |
| 8 | **NSM** | Number of Seconds from Midnight | Derived from timestamp: seconds elapsed since 00:00 | int | seconds | 0 → 85,500 (in 900 s steps); mean=42,750 |
| 9 | **WeekStatus** | Weekday vs Weekend classification | Derived from date | object / categorical | — | Weekday: 25,056 (71.5 %); Weekend: 9,984 (28.5 %) |
| 10 | **Day_of_week** | Day name | Derived from date | object / categorical | — | Monday: 5,088; Tue–Sat: 4,992 each; Sunday: 4,992 |
| 11 | **Load_Type** | Operational load classification | Raw categorical label | object / categorical | — | Light_Load: 18,072 (51.6 %); Medium_Load: 9,696 (27.7 %); Maximum_Load: 7,272 (20.8 %) |

---

## 2. Weather (Open-Meteo) — 4 features

Fetched from Open-Meteo Archive API for coordinates (34.975°N, 127.589°E) — Gwangyang, Korea. Hourly data resampled to 15 min via linear interpolation + edge extrapolation.

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 12 | **temperature_2m** | Air temperature at 2 m above ground | Open-Meteo `temperature_2m` | float | °C | −10.6 → 35.7; mean=13.85, std=10.01 |
| 13 | **precipitation** | Precipitation rate | Open-Meteo `precipitation` | float | mm | 0.0 → 44.0; mean=0.196, std=1.045 |
| 14 | **relative_humidity_2m** | Relative humidity at 2 m | Open-Meteo `relative_humidity_2m` | float | % | 6.0 → 100.0; mean=70.67, std=19.86 |
| 15 | **windspeed_10m** | Wind speed at 10 m above ground | Open-Meteo `windspeed_10m` | float | km/h | 0.0 → 42.2; mean=10.46, std=5.92 |

---

## 3. Weather-Derived — 7 features

Engineered in `src/bronze/weather_loader.py` after resampling.

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 16 | **temp_rolling_24h** | Smoothed temperature over past 24 h | `temperature_2m`.rolling(window=96, min_periods=1).mean() | float | °C | −8.07 → 30.94; mean=13.85, std=9.55 |
| 17 | **temp_diff_24h** | Temperature change vs same time yesterday | `temperature_2m`.diff(96), forward-filled, NaN→0 | float | °C | −12.0 → 9.2; mean≈0.0, std=2.68 |
| 18 | **heat_index** | Apparent temperature (feels-like) | Rothfusz formula (NOAA): converts T(°C)→°F, computes HI, converts back. If T<26.7°C or RH<40 %, returns T. | float | °C | −10.6 → 44.63; mean=14.29, std=10.78 |
| 19 | **is_extreme_hot** | Flag for extreme heat (>95th percentile) | `(temperature_2m > p95).astype(int)` where p95 is year-level 95th percentile | int (bool) | — | 0 or 1; True rate ≈ 5.0 % |
| 20 | **is_extreme_cold** | Flag for extreme cold (<5th percentile) | `(temperature_2m < p05).astype(int)` | int (bool) | — | 0 or 1; True rate ≈ 4.9 % |
| 21 | **humidity_x_temp** | Heat–humidity interaction (proxy for cooling load) | `relative_humidity_2m × temperature_2m` | float | %·°C | −535.5 → 2,686.4; mean=1,047.9, std=803.0 |
| 22 | **windspeed_rolling_6h** | Smoothed wind speed over past 6 h | `windspeed_10m`.rolling(window=24, min_periods=1).mean() | float | km/h | 0.92 → 38.87; mean=10.46, std=5.54 |

---

## 4. Time-Domain (Lag + Rolling + Trig) — 15 features

Engineered in `src/silver/time_features.py`.

### Lag Features
| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 23 | **Usage_kWh_lag_1** | Active power 15 min ago | `Usage_kWh`.shift(1) | float | kWh | 0.0 → 157.18; mean=27.39; count=35,039 (1 NaN) |
| 24 | **Usage_kWh_lag_2** | Active power 30 min ago | `Usage_kWh`.shift(2) | float | kWh | 0.0 → 157.18; count=35,038 (2 NaN) |
| 25 | **Usage_kWh_lag_4** | Active power 1 h ago | `Usage_kWh`.shift(4) | float | kWh | 0.0 → 157.18; count=35,036 (4 NaN) |
| 26 | **Usage_kWh_lag_96** | Active power 24 h ago | `Usage_kWh`.shift(96) | float | kWh | 0.0 → 157.18; count=34,944 (96 NaN) |

### Rolling Window Statistics
Window sizes (in 15-min steps): **24** = 6 h, **48** = 12 h, **96** = 24 h.

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 27 | **Usage_kWh_rmean_24** | Rolling mean (6 h) | `Usage_kWh`.rolling(24, min_periods=1).mean() | float | kWh | 2.59 → 114.45; mean=27.39, std=25.72 |
| 28 | **Usage_kWh_rstd_24** | Rolling std (6 h) | `Usage_kWh`.rolling(24, min_periods=1).std() | float | kWh | 0.026 → 62.88; mean=16.00, std=14.87 |
| 29 | **Usage_kWh_rskew_24** | Rolling skewness (6 h) | `Usage_kWh`.rolling(24, min_periods=1).skew() | float | — | −4.71 → 4.90; mean=0.693, std=1.390 |
| 30 | **Usage_kWh_rmean_48** | Rolling mean (12 h) | `Usage_kWh`.rolling(48, min_periods=1).mean() | float | kWh | 2.65 → 104.59; mean=27.39, std=21.03 |
| 31 | **Usage_kWh_rstd_48** | Rolling std (12 h) | `Usage_kWh`.rolling(48, min_periods=1).std() | float | kWh | 0.127 → 57.25; mean=22.05, std=14.29 |
| 32 | **Usage_kWh_rskew_48** | Rolling skewness (12 h) | `Usage_kWh`.rolling(48, min_periods=1).skew() | float | — | −4.32 → 6.92; mean=0.934, std=1.329 |
| 33 | **Usage_kWh_rmean_96** | Rolling mean (24 h) | `Usage_kWh`.rolling(96, min_periods=1).mean() | float | kWh | 2.69 → 83.06; mean=27.39, std=14.90 |
| 34 | **Usage_kWh_rstd_96** | Rolling std (24 h) | `Usage_kWh`.rolling(96, min_periods=1).std() | float | kWh | 0.170 → 55.26; mean=26.86, std=13.58 |
| 35 | **Usage_kWh_rskew_96** | Rolling skewness (24 h) | `Usage_kWh`.rolling(96, min_periods=1).skew() | float | — | −0.75 → 9.78; mean=0.946, std=1.111 |

### Trigonometric Temporal Encoding
| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 36 | **NSM_sin** | Sine encoding of NSM (daily cycle) | `sin(2π × NSM / 86400)` | float | — | −1.0 → 1.0; mean≈0 (circular) |
| 37 | **NSM_cos** | Cosine encoding of NSM (daily cycle) | `cos(2π × NSM / 86400)` | float | — | −1.0 → 1.0; mean≈0 (circular) |

> **Why:** NSM jumps from 86,400 back to 0 at midnight. The sin/cos pair removes this artificial discontinuity so the model sees 23:59 and 00:01 as 2 min apart.

---

## 5. Frequency-Domain (DWT Wavelet) — 16 features

Engineered in `src/silver/wavelet_features.py` using **rolling-window DWT** (Discrete Wavelet Transform).

- **Wavelet:** Daubechies-4 (`db4`)
- **Decomposition level:** 3
- **Rolling window:** 64 steps (16 h)
- **Prefix:** `Usage_kWh`

For each window of 64 samples, `pywt.wavedec` produces:
- `cA` — Approximation coefficients (macro trend)
- `cD3` — Detail level 3 (low-frequency oscillations)
- `cD2` — Detail level 2 (mid-frequency)
- `cD1` — Detail level 1 (high-frequency anomalies)

Four statistics are extracted per coefficient band:
- `_mean` — average energy level
- `_std` — volatility of the band
- `_energy` — `Σ(coeff²)` (total signal energy)
- `_max_abs` — peak absolute amplitude

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 38 | **Usage_kWh_cA_mean** | Mean of approximation coeffs | `np.mean(cA)` over rolling-64 window | float | kWh-equiv | 7.44 → 296.64; mean=77.58, std=49.31; count=34,977 (63 NaN) |
| 39 | **Usage_kWh_cA_std** | Std of approximation coeffs | `np.std(cA)` | float | kWh-equiv | 0.09 → 164.91; mean=63.15, std=36.24 |
| 40 | **Usage_kWh_cA_energy** | Energy of approximation coeffs | `np.sum(cA²)` | float | kWh² | 776 → 1,341,844; mean=192,525, std=179,179 |
| 41 | **Usage_kWh_cA_max_abs** | Max absolute approximation coeff | `np.max(\|cA\|)` | float | kWh-equiv | 7.88 → 454.20; mean=186.83, std=100.76 |
| 42 | **Usage_kWh_cD3_mean** | Mean of detail-3 coeffs | `np.mean(cD3)` | float | kWh-equiv | −17.42 → 18.71; mean≈0, std=3.58 |
| 43 | **Usage_kWh_cD3_std** | Std of detail-3 coeffs | `np.std(cD3)` | float | kWh-equiv | 0.05 → 73.82; mean=19.72, std=13.48 |
| 44 | **Usage_kWh_cD3_energy** | Energy of detail-3 coeffs | `np.sum(cD3²)` | float | kWh² | 0.03 → 76,334; mean=8,170, std=9,229 |
| 45 | **Usage_kWh_cD3_max_abs** | Max absolute detail-3 coeff | `np.max(\|cD3\|)` | float | kWh-equiv | 0.12 → 220.27; mean=49.87, std=35.34 |
| 46 | **Usage_kWh_cD2_mean** | Mean of detail-2 coeffs | `np.mean(cD2)` | float | kWh-equiv | −11.98 → 10.89; mean≈0, std=1.79 |
| 47 | **Usage_kWh_cD2_std** | Std of detail-2 coeffs | `np.std(cD2)` | float | kWh-equiv | 0.07 → 46.52; mean=11.51, std=7.99 |
| 48 | **Usage_kWh_cD2_energy** | Energy of detail-2 coeffs | `np.sum(cD2²)` | float | kWh² | 0.12 → 45,458; mean=4,191, std=4,931 |
| 49 | **Usage_kWh_cD2_max_abs** | Max absolute detail-2 coeff | `np.max(\|cD2\|)` | float | kWh-equiv | 0.15 → 133.39; mean=31.69, std=22.24 |
| 50 | **Usage_kWh_cD1_mean** | Mean of detail-1 coeffs | `np.mean(cD1)` | float | kWh-equiv | −6.75 → 7.00; mean≈0, std=1.02 |
| 51 | **Usage_kWh_cD1_std** | Std of detail-1 coeffs | `np.std(cD1)` | float | kWh-equiv | 0.07 → 24.51; mean=6.59, std=4.76 |
| 52 | **Usage_kWh_cD1_energy** | Energy of detail-1 coeffs | `np.sum(cD1²)` | float | kWh² | 0.19 → 21,109; mean=2,349, std=2,845 |
| 53 | **Usage_kWh_cD1_max_abs** | Max absolute detail-1 coeff | `np.max(\|cD1\|)` | float | kWh-equiv | 0.23 → 71.62; mean=21.06, std=14.71 |

> **Physical meaning:** `cD1` captures the highest-frequency transients (sudden load spikes / anomalies). A surge in `cD1_energy` or `cD1_max_abs` flags a potential electrical fault that smooth rolling statistics might miss.

---

## 6. Physical-Domain — 2 features

Engineered in `src/silver/physical_features.py` from the power-triangle relationships.

| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 54 | **Apparent_Power_S** | Apparent power (magnitude of power triangle) | `S = √(P² + Q²)` where `P = Usage_kWh`, `Q = Lagging_Current_Reactive.Power_kVarh` | float | kVA (here kWh-equivalent) | 0.0 → 175.35; mean=31.04, std=36.62 |
| 55 | **Phase_Angle_Phi** | Phase angle between voltage and current | `φ = arccos(PF)` where `PF = Lagging_Current_Power_Factor` clipped to [0,1] | float | radians | 0.0 → π/2 (1.571); mean=0.520, std=0.383 |

> **Physical insight:** When `P` is flat but `Q` spikes (e.g., rotor jam), `S` inflates — a cable-overload warning. `Phase_Angle_Phi` provides a linear-scale view of power-factor degradation that is sharper than raw PF for ML models.

---

## 7. Anomaly Labels — 9 features

Engineered in `src/silver/anomaly_labels.py`. Labels are rule-based with confidence scores ∈ [0,1].

### Boolean Flags
| # | Name | Description | Rule / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|---------------------|------|------|---------------|
| 56 | **anomaly_idling** | Idling / energy-waste anomaly | `Light_Load` AND (`night` OR `weekend`) AND (`Usage_kWh > median`) AND (`PF < 0.50`) | bool | — | True: 10 (0.03 %); False: 35,030 |
| 57 | **anomaly_leakage** | Gradual energy leakage / concept drift | `rolling_mean(Usage_kWh, 672)` > baseline + 5 %, where baseline = mean of first 4 weeks | bool | — | True: 2,336 (6.67 %); False: 32,704 |
| 58 | **anomaly_overload** | Local overload / extreme point anomaly | `Usage_kWh > 99.5th percentile` AND (`Q > 99.5th percentile` OR `PF < 0.70`) | bool | — | True: 48 (0.14 %); False: 34,992 |
| 59 | **anomaly_any** | Union of all three anomalies | `idling OR leakage OR overload` | bool | — | True: 2,388 (6.82 %); False: 32,652 |

### Confidence Scores
| # | Name | Description | Formula | Type | Unit | Range / Notes |
|---|------|-------------|---------|------|------|---------------|
| 60 | **anomaly_idling_score** | Confidence for idling | `0.3·I(Light) + 0.3·I(off-hours) + 0.2·I(Usage>med) + 0.2·I(PF<0.50)` | float | — | 0.0 → 1.0; mean=0.438, std=0.220 |
| 61 | **anomaly_leakage_score** | Confidence for leakage | Tiered: >20 %→1.0; >10 %→0.7; >5 %→0.4; else 0.0 | float | — | 0.0 → 1.0; mean=0.042, std=0.166 |
| 62 | **anomaly_overload_score** | Confidence for overload | `0.5·I(Usage extreme) + 0.25·I(Q extreme) + 0.25·I(PF<0.70)` | float | — | 0.0 → 0.75; mean=0.080, std=0.121 |
| 63 | **anomaly_max_score** | Maximum of the three scores | `max(idling_score, leakage_score, overload_score)` | float | — | 0.0 → 1.0; mean=0.454, std=0.225 |

### Explanation
| # | Name | Description | Formula / How Computed | Type | Unit | Range / Notes |
|---|------|-------------|------------------------|------|------|---------------|
| 64 | **anomaly_explanation** | Human-readable reason for the top anomaly | Picks the label with highest score; generates text via `explain_idling`, `explain_leakage`, or `explain_overload`. If max score < 0.1 → "No significant anomaly detected". | object / str | — | Most common: "Idling detected: usage above median" (10,493 rows); "Idling detected: light load condition; nighttime off-hours; usage above median" (5,298 rows); leakage explanations appear for high leakage-score rows. |

---

## Quick Reference: Feature Count by Category

| Category | Count |
|----------|-------|
| 1. Raw / Electrical | 11 |
| 2. Weather (Open-Meteo) | 4 |
| 3. Weather-Derived | 7 |
| 4. Time-Domain (lag + rolling + trig) | 15 |
| 5. Frequency-Domain (DWT) | 16 |
| 6. Physical-Domain | 2 |
| 7. Anomaly Labels | 9 |
| **Total** | **64** |

---

## Engineering Pipeline Order

1. **Bronze** — `data_loader.py` loads & cleans raw steel data.
2. **Weather** — `weather_loader.py` fetches Open-Meteo, resamples 1 h → 15 min, engineers 7 derived features, left-joins on `date`.
3. **Time** — `time_features.py` adds lags (1,2,4,96), rolling stats (24,48,96), and NSM sin/cos.
4. **Wavelet** — `wavelet_features.py` computes rolling DWT (`db4`, level 3, window 64) → 16 statistical features.
5. **Physical** — `physical_features.py` computes `Apparent_Power_S` and `Phase_Angle_Phi`.
6. **Anomaly** — `anomaly_labels.py` applies rule-based detectors with confidence scoring.
7. **Gold** — `pipeline.py` saves final output to `data/gold/steel_final.csv`.
