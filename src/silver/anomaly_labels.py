"""Create auditable proxy anomaly labels for industrial electricity datasets."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.schema import (
    ACTIVE_POWER_COL,
    LAGGING_PF_COL,
    LAGGING_REACTIVE_COL,
    LEADING_PF_COL,
    LEADING_REACTIVE_COL,
    LOAD_TYPE_COL,
    NSM_COL,
    WEEK_STATUS_COL,
)


def _false_series(index: pd.Index) -> pd.Series:
    """Return an aligned false series."""
    return pd.Series(False, index=index)


def _off_hours(df: pd.DataFrame) -> pd.Series:
    """Infer off-hours from timestamp-derived context."""
    if NSM_COL in df.columns:
        is_night = (df[NSM_COL] < 21600) | (df[NSM_COL] > 75600)
    else:
        is_night = _false_series(df.index)

    if WEEK_STATUS_COL in df.columns:
        is_weekend = df[WEEK_STATUS_COL].astype(str).eq("Weekend")
    else:
        is_weekend = _false_series(df.index)

    return is_night | is_weekend


def _light_load_condition(df: pd.DataFrame) -> pd.Series:
    """Use Load_Type when available, otherwise derive a low-load proxy."""
    if LOAD_TYPE_COL in df.columns:
        return df[LOAD_TYPE_COL].astype(str).eq("Light_Load")
    threshold = df[ACTIVE_POWER_COL].quantile(0.33)
    return df[ACTIVE_POWER_COL] <= threshold


def _effective_power_factor(df: pd.DataFrame) -> pd.Series:
    """Return the most reliable PF signal for rule thresholds."""
    if LAGGING_PF_COL in df.columns:
        return pd.to_numeric(df[LAGGING_PF_COL], errors="coerce").fillna(1.0)
    if LEADING_PF_COL in df.columns:
        return pd.to_numeric(df[LEADING_PF_COL], errors="coerce").fillna(1.0)
    return pd.Series(1.0, index=df.index)


def _reactive_magnitude(df: pd.DataFrame) -> pd.Series:
    """Return the strongest available reactive-power magnitude."""
    candidates = [
        col
        for col in [
            LAGGING_REACTIVE_COL,
            LEADING_REACTIVE_COL,
            "Reactive_Power_Q_Total",
            "Reactive_Power_Q_Net",
        ]
        if col in df.columns
    ]
    if not candidates:
        return pd.Series(0.0, index=df.index)
    values = df[candidates].apply(pd.to_numeric, errors="coerce").abs()
    return values.max(axis=1).fillna(0.0)


def label_idling(df: pd.DataFrame) -> pd.Series:
    """Detect sustained high usage during light/off-hour operating context."""
    is_light = _light_load_condition(df)
    is_off_hours = _off_hours(df)
    is_high_usage = df[ACTIVE_POWER_COL] > df[ACTIVE_POWER_COL].median()
    is_low_pf = _effective_power_factor(df) < 0.50
    return is_light & is_off_hours & is_high_usage & is_low_pf


def score_idling(df: pd.DataFrame) -> pd.Series:
    """Score idling proxy evidence in the range [0, 1]."""
    score = pd.Series(0.0, index=df.index)
    score += 0.3 * _light_load_condition(df).astype(float)
    score += 0.3 * _off_hours(df).astype(float)
    score += 0.2 * (df[ACTIVE_POWER_COL] > df[ACTIVE_POWER_COL].median()).astype(float)
    score += 0.2 * (_effective_power_factor(df) < 0.50).astype(float)
    return score.clip(0.0, 1.0)


def label_leakage(
    df: pd.DataFrame,
    window: int = 672,
    threshold_pct: float = 5.0,
) -> pd.Series:
    """Detect gradual usage drift above a rolling energy baseline."""
    rolling_mean = df[ACTIVE_POWER_COL].rolling(window, min_periods=1).mean()
    baseline_window = min(window * 4, len(df))
    baseline = df[ACTIVE_POWER_COL].iloc[:baseline_window].mean()
    pct_increase = (rolling_mean - baseline) / baseline * 100
    return pct_increase > threshold_pct


def score_leakage(df: pd.DataFrame, window: int = 672) -> pd.Series:
    """Score leakage proxy evidence from baseline percentage increase."""
    rolling_mean = df[ACTIVE_POWER_COL].rolling(window, min_periods=1).mean()
    baseline_window = min(window * 4, len(df))
    baseline = df[ACTIVE_POWER_COL].iloc[:baseline_window].mean()
    pct_increase = (rolling_mean - baseline) / baseline * 100

    score = pd.Series(0.0, index=df.index)
    score = np.where(pct_increase > 20, 1.0, score)
    score = np.where((pct_increase > 10) & (pct_increase <= 20), 0.7, score)
    score = np.where((pct_increase > 5) & (pct_increase <= 10), 0.4, score)
    return pd.Series(score, index=df.index)


def label_overload(
    df: pd.DataFrame,
    usage_percentile: float = 0.995,
    pf_threshold: float = 0.70,
) -> pd.Series:
    """Detect local overload proxies from usage spikes and reactive/PF stress."""
    is_extreme_usage = df[ACTIVE_POWER_COL] > df[ACTIVE_POWER_COL].quantile(
        usage_percentile
    )
    reactive = _reactive_magnitude(df)
    is_high_reactive = reactive > reactive.quantile(usage_percentile)
    is_low_pf = _effective_power_factor(df) < pf_threshold
    return is_extreme_usage & (is_high_reactive | is_low_pf)


def score_overload(
    df: pd.DataFrame,
    usage_percentile: float = 0.995,
    pf_threshold: float = 0.70,
) -> pd.Series:
    """Score overload proxy evidence in the range [0, 1]."""
    is_extreme_usage = df[ACTIVE_POWER_COL] > df[ACTIVE_POWER_COL].quantile(
        usage_percentile
    )
    reactive = _reactive_magnitude(df)
    is_high_reactive = reactive > reactive.quantile(usage_percentile)
    is_low_pf = _effective_power_factor(df) < pf_threshold
    score = (
        0.5 * is_extreme_usage.astype(float)
        + 0.25 * is_high_reactive.astype(float)
        + 0.25 * is_low_pf.astype(float)
    )
    return score.clip(0.0, 1.0)


def explain_idling(row: pd.Series) -> str:
    """Return a readable explanation for idling proxy evidence."""
    reasons: list[str] = []
    if row.get(LOAD_TYPE_COL) == "Light_Load":
        reasons.append("light load condition")
    if (row.get(NSM_COL, 0) < 21600) or (row.get(NSM_COL, 0) > 75600):
        reasons.append("nighttime off-hours")
    if row.get(WEEK_STATUS_COL) == "Weekend":
        reasons.append("weekend")
    if row.get(ACTIVE_POWER_COL, 0) > 0:
        reasons.append("usage above median")
    pf = row.get(LAGGING_PF_COL, row.get(LEADING_PF_COL, 1.0))
    if pf < 0.50:
        reasons.append("PF below 0.50 (IEEE 519 severe)")
    return "Idling detected: " + "; ".join(reasons) if reasons else "No idling signs"


def explain_leakage(row: pd.Series, baseline: float, pct_increase: float) -> str:
    """Return a readable explanation for leakage proxy evidence."""
    return (
        f"Leakage detected: rolling mean increased {pct_increase:.1f}% "
        f"above baseline ({baseline:.2f} kWh). Possible equipment degradation."
    )


def explain_overload(row: pd.Series) -> str:
    """Return a readable explanation for overload proxy evidence."""
    reasons: list[str] = []
    pf = row.get(LAGGING_PF_COL, row.get(LEADING_PF_COL, 1.0))
    if pf < 0.70:
        reasons.append(f"PF collapsed to {pf:.2f} (< 0.70)")
    if row.get(ACTIVE_POWER_COL, 0) > 0:
        reasons.append("extreme usage spike")
    if max(
        row.get(LAGGING_REACTIVE_COL, 0),
        row.get(LEADING_REACTIVE_COL, 0),
        row.get("Reactive_Power_Q_Total", 0),
    ) > 0:
        reasons.append("reactive power surge")
    return "Overload detected: " + "; ".join(reasons) if reasons else "No overload signs"


def label_all_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Append proxy anomaly labels, scores, and explanations."""
    result = df.copy()
    result["anomaly_idling"] = label_idling(df)
    result["anomaly_idling_score"] = score_idling(df)
    result["anomaly_leakage"] = label_leakage(df)
    result["anomaly_leakage_score"] = score_leakage(df)
    result["anomaly_overload"] = label_overload(df)
    result["anomaly_overload_score"] = score_overload(df)
    result["anomaly_any"] = (
        result["anomaly_idling"]
        | result["anomaly_leakage"]
        | result["anomaly_overload"]
    )
    score_cols = [
        "anomaly_idling_score",
        "anomaly_leakage_score",
        "anomaly_overload_score",
    ]
    result["anomaly_max_score"] = result[score_cols].max(axis=1)

    def _explain(row: pd.Series) -> str:
        scores = {
            "idling": row["anomaly_idling_score"],
            "leakage": row["anomaly_leakage_score"],
            "overload": row["anomaly_overload_score"],
        }
        top = max(scores, key=scores.get)
        if scores[top] < 0.1:
            return "No significant anomaly detected"
        if top == "idling":
            return explain_idling(row)
        if top == "overload":
            return explain_overload(row)
        return f"Leakage score: {scores[top]:.2f} - possible gradual energy degradation"

    result["anomaly_explanation"] = result.apply(_explain, axis=1)
    return result
