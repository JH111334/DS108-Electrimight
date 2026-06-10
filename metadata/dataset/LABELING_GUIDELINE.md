# Proxy Anomaly Labeling Methodology

This document explains the labeling methodology used in DS108-Electrimight. The
labels are designed for offline benchmarking and report analysis. They are
**proxy labels**, not maintenance-confirmed equipment-fault labels.

## Scope

The current implementation labels three types of industrial electricity-consumption
patterns:

- idling or energy-waste behavior;
- leakage/concept drift in sustained usage;
- local overload-risk behavior.

The default dataset is the UCI Steel Industry Energy Consumption dataset. The
schema contract in `src/schema.py` allows extension to other industrial meter
datasets when timestamp and active energy/power columns are available. Reactive
power, power factor, load type, and weather fields improve interpretability but
must be mapped carefully if the dataset changes.

## Labeling Principles

The label design follows four principles:

1. **Explainability:** every positive label must have a readable reason.
2. **Physical plausibility:** thresholds are tied to electrical behavior,
   operating context, or robust statistics.
3. **No target leakage:** label columns are annotations and evaluation targets,
   not ordinary predictive features.
4. **Conservative reporting:** proxy labels indicate suspicious patterns, not
   verified plant failures.

Each label receives a confidence score between 0 and 1. The score records how
many supporting conditions are present and how strong the evidence is.

## Label 1: Idling

Idling represents electricity consumption during low-production or off-hours
conditions with poor power-factor evidence. In a steel plant, this may correspond
to equipment remaining energized while producing limited useful output.

Current rule structure:

| Evidence | Interpretation |
|---|---|
| Light-load status or low-load proxy | operating state is compatible with idling |
| Off-hours or weekend timestamp | production demand is expected to be lower |
| Usage above median | consumption is still materially present |
| Effective power factor below 0.50 | severe power-factor degradation evidence |

The implemented logic requires the relevant conditions to align before assigning
`anomaly_idling`. The current gold dataset contains **10 idling proxy rows**.

## Label 2: Leakage / Concept Drift

Leakage or concept drift represents a sustained increase in energy consumption
relative to an early-period baseline. This label is intended to capture gradual
degradation patterns such as equipment aging, thermal losses, sensor drift, or
process changes.

Current rule structure:

| Evidence | Interpretation |
|---|---|
| rolling mean over 672 observations | one week of 15-minute data |
| baseline from the early stable period | reference consumption level |
| increase above 5% | weak signal of drift or leakage-like behavior |
| larger increases | higher confidence tiers |

The current gold dataset contains **2,336 leakage/concept-drift proxy rows**.
This is the dominant proxy anomaly class.

## Label 3: Local Overload

Local overload represents extreme active usage accompanied by reactive-power or
power-factor stress. The label is meant to identify short periods where the
electrical load appears unusually demanding.

Current rule structure:

| Evidence | Interpretation |
|---|---|
| `Usage_kWh` above the 99.5th percentile | robust extreme-usage evidence |
| reactive magnitude above a high percentile | electrical stress evidence |
| effective power factor below 0.70 | degraded power quality evidence |

The current gold dataset contains **48 overload proxy rows**.

## Aggregate Label

`anomaly_any` is the union of all three proxy labels. Current distribution:

| Metric | Value |
|---|---:|
| Total rows | 35,040 |
| `anomaly_any=True` | 2,388 |
| Rate | 6.815% |

This rate is suitable for imbalanced-learning experiments, but it should be
presented as a proxy-label rate rather than a verified fault rate.

## Confidence Scores

The confidence scores are deterministic and auditable:

- `anomaly_idling_score` combines load status, off-hours context, usage level,
  and power-factor evidence;
- `anomaly_leakage_score` increases with the percentage rise above baseline;
- `anomaly_overload_score` combines extreme usage, reactive stress, and
  low-power-factor evidence;
- `anomaly_max_score` records the strongest available proxy evidence.

The explanation column selects the most relevant label family and stores a short
human-readable reason for the assigned proxy.

## Validation

Label changes should be accompanied by:

```powershell
python -m pytest tests/test_anomaly_labels.py
python -m src.data_assertions
python -m src.leakage_audit
```

The latest project validation reports **52 pytest tests passed** and all dataset
assertions passed.

## Reporting Guidance

Use the following language in reports:

> The anomaly columns are physics-informed proxy labels. They provide an
> explainable benchmark for offline evaluation, but they are not ground-truth
> SCADA fault records.

Avoid stating that the project has detected real equipment failures unless
maintenance logs or expert inspections are later added.
