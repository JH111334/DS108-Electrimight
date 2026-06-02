# Proxy Labeling Guideline v2.5

**Project:** DS108 Electrimight  
**Updated:** 2026-06-01  
**Scope:** Offline analytics, feature engineering, weak supervision benchmark, and report interpretation.

## Status

This guideline is the root-level reference for the current repository. It refines the v2.5 design from `origin/overhaul/damned`, but keeps the schema aligned with the current working pipeline and `data/gold/steel_final.csv`.

The remote v2.5 design is better as a long-term labeling design because it introduces context-aware baselines, priority resolution, event-level thinking, warning flags, and clearer safe/unsafe uses. It is **not safe to replace the current project documents blindly** until the pipeline, tests, codebook, report tables, and downstream artifacts are migrated together.

## Current Gold Output

The current Gold table has 64 columns. The persistent label columns are:

| Column | Meaning |
|---|---|
| `anomaly_idling` | Proxy idling / idle-waste flag. |
| `anomaly_idling_score` | Idling confidence score in [0, 1]. |
| `anomaly_leakage` | Proxy leakage / energy inefficiency drift flag. |
| `anomaly_leakage_score` | Leakage confidence score in [0, 1]. |
| `anomaly_overload` | Proxy local overload flag. |
| `anomaly_overload_score` | Overload confidence score in [0, 1]. |
| `anomaly_any` | OR union of idling, leakage, and overload. |
| `anomaly_max_score` | Maximum of the three confidence scores. |
| `anomaly_explanation` | Human-readable explanation for the strongest proxy signal. |

The current table does **not** materialize `Suspected_Idling`, `Suspected_Leakage_Drift`, `Suspected_Overload`, `dominant_label`, `label_reason`, `baseline_warning`, or `night_simplified_baseline_warning`.

## Safe Uses

- Post-hoc analysis of proxy anomaly distribution by time, weather, and load context.
- Ablation study for feature construction.
- Weak-supervision benchmark design.
- Dataset documentation, codebook, datasheet, and reproducibility checks.
- Baseline warning for maintenance prioritization in low-instrumentation settings.

## Unsafe Uses

- Do not interpret proxy labels as SCADA-confirmed or maintenance-confirmed faults.
- Do not use `anomaly_any` or score columns as same-timestamp input features for forecasting `Usage_kWh`.
- Do not use these labels for real-time trip, relay, or SCADA decisions.
- Do not claim insulation leakage, confirmed overload, or machine shutdown without asset-level validation.

## Label Definitions

### Idling / Idle-Waste Proxy

**Current rule:** all conditions are true:

- `Load_Type == "Light_Load"`
- off-hours: `NSM < 21600` or `NSM > 75600` or `WeekStatus == "Weekend"`
- `Usage_kWh > median(Usage_kWh)`
- `Lagging_Current_Power_Factor < 0.50`

**Interpretation:** non-negligible consumption under light/off-hour context with poor power factor. This is an idle-waste proxy, not confirmed machine shutdown.

**Current score:**

```text
0.3*I(Light_Load)
+ 0.3*I(off_hours)
+ 0.2*I(Usage_kWh > median)
+ 0.2*I(PF_lag < 0.50)
```

### Leakage / Energy Inefficiency Drift Proxy

**Current rule:**

- rolling mean of `Usage_kWh` over 672 rows exceeds the first four-week baseline by more than 5%.

**Interpretation:** long-run energy inefficiency drift relative to a baseline. It is not physical insulation leakage.

**Current score:**

| Increase over baseline | Score |
|---:|---:|
| > 20% | 1.0 |
| > 10% and <= 20% | 0.7 |
| > 5% and <= 10% | 0.4 |
| <= 5% | 0.0 |

### Local Overload Proxy

**Current rule:**

- `Usage_kWh > P99.5(Usage_kWh)`
- and either `Lagging_Current_Reactive.Power_kVarh > P99.5(Q_lag)` or `Lagging_Current_Power_Factor < 0.70`

**Interpretation:** high-stress proxy signal. It is not confirmed equipment overload because rated capacities and asset-level current/temperature are unavailable.

**Current score:**

```text
0.5*I(Usage_kWh > P99.5)
+ 0.25*I(Q_lag > P99.5)
+ 0.25*I(PF_lag < 0.70)
```

## Validation Requirements

Every run that changes labeling logic should report:

- counts and percentages for `anomaly_idling`, `anomaly_leakage`, `anomaly_overload`, and `anomaly_any`;
- overlap between component labels;
- `anomaly_any` rate by `Load_Type`;
- mutual information or another association metric between `Load_Type` and `anomaly_any`;
- top `anomaly_explanation` values;
- evidence that labels are not used as features in same-timestamp forecasting;
- whether any pipeline schema change requires updating `CODEBOOK.csv`, report tables, datasheet, and tests.

## Migration Target

The v2.5 design can be migrated later, but only as a coordinated change. The target improvements are:

- context-aware baselines using `Load_Type`, hour, and `WeekStatus`;
- duration filtering for idling and leakage drift;
- priority resolution: Overload > Idling > Leakage > Normal;
- persistent fields such as `dominant_label`, `label_reason`, `is_proxy_label`, and baseline warning flags;
- event-level aggregation for consecutive anomaly runs;
- rule-free ablation as a required validation track.

Migration is not a documentation-only change. It requires updating `src/silver/anomaly_labels.py`, tests, `data/gold/steel_final.csv`, report tables, Streamlit UI, and downstream notebooks/artifacts.
