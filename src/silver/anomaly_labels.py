"""
Anomaly Labeling Module — v2.5 Guideline Implementation

Sinh weak/proxy labels theo docs/LABELING_GUIDELINE_v2.5.md va data_codebook.md.
Output canonical columns: Suspected_Idling, Suspected_Leakage_Drift,
Suspected_Overload, anomaly_any, dominant_label, label_reason,
is_proxy_label, baseline_warning, night_simplified_baseline_warning.

Tham chieu:
  - docs/LABELING_GUIDELINE_v2.5.md
  - IEEE 519-2014 (Power Factor thresholds)
  - ISO 50001:2018 (Energy baseline & drift)
"""

import numpy as np
import pandas as pd


# ── Utilities ───────────────────────────────────────────────────────────────


def _detect_pf_rule(df: pd.DataFrame) -> pd.Series:
    """
    Tra ve PF_rule trong [0, 1]. Robust detect: chia 100 neu max > 1.0.
    """
    pf = df["Lagging_Current_Power_Factor"].astype(float)
    if pf.max() > 1.0:
        return pf / 100.0
    return pf


def _compute_q_net(df: pd.DataFrame) -> pd.Series:
    """Q_net = lagging - leading reactive power."""
    return (
        df["Lagging_Current_Reactive.Power_kVarh"]
        - df["Leading_Current_Reactive_Power_kVarh"]
    )


def _keep_consecutive_runs(flags: pd.Series, min_length: int = 4) -> pd.Series:
    """
    Chỉ giữ lại các run True có độ dài >= min_length.
    """
    if flags.sum() == 0:
        return flags.copy()
    result = pd.Series(False, index=flags.index)
    group_ids = (flags != flags.shift(1)).cumsum()
    for gid, grp in flags[flags].groupby(group_ids):
        if len(grp) >= min_length:
            result.loc[grp.index] = True
    return result


def _compute_context_p99(
    df: pd.DataFrame,
    column: str,
) -> pd.Series:
    """
    Tra ve P99.5 theo ngữ cảnh cho mỗi dòng.
    Context: Load_Type × Hour × WeekStatus → Hour × WeekStatus → Load_Type → global.
    Đồng thời trả về baseline_level va baseline_warning.
    """
    n = len(df)
    p99_series = pd.Series(np.nan, index=df.index, dtype=float)
    baseline_level = pd.Series(0, index=df.index, dtype=np.int8)
    baseline_warning = pd.Series(False, index=df.index)

    # Level 1: Load_Type × Hour × WeekStatus
    groups = df.groupby(["Load_Type", "Hour", "WeekStatus"], sort=False)
    for keys, idx in groups.groups.items():
        vals = df.loc[idx, column]
        if len(vals) >= 10:
            p99_series.loc[idx] = vals.quantile(0.995)
            baseline_level.loc[idx] = 1
        else:
            # Mark for fallback
            p99_series.loc[idx] = np.nan

    # Level 2: Hour × WeekStatus
    still_nan = p99_series.isna()
    if still_nan.any():
        groups2 = df.loc[still_nan].groupby(["Hour", "WeekStatus"], sort=False)
        for keys, idx in groups2.groups.items():
            vals = df.loc[idx, column]
            if len(vals) >= 10:
                p99_series.loc[idx] = vals.quantile(0.995)
                baseline_level.loc[idx] = 2
            else:
                p99_series.loc[idx] = np.nan

    # Level 3: Load_Type
    still_nan = p99_series.isna()
    if still_nan.any():
        groups3 = df.loc[still_nan].groupby("Load_Type", sort=False)
        for keys, idx in groups3.groups.items():
            vals = df.loc[idx, column]
            if len(vals) >= 10:
                p99_series.loc[idx] = vals.quantile(0.995)
                baseline_level.loc[idx] = 3
            else:
                p99_series.loc[idx] = np.nan

    # Level 4: global fallback
    still_nan = p99_series.isna()
    if still_nan.any():
        p99_series.loc[still_nan] = df[column].quantile(0.995)
        baseline_level.loc[still_nan] = 4
        baseline_warning.loc[still_nan] = True

    # baseline_warning if group size < 10 or std == 0
    for (lt, h, ws), idx in groups.groups.items():
        vals = df.loc[idx, column]
        if len(vals) < 10 or vals.std() == 0:
            baseline_warning.loc[idx] = True

    return p99_series, baseline_level, baseline_warning


def _compute_context_median_idling(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Tra ve Median(Usage_kWh | Light_Load × Hour × WeekStatus) cho mỗi dòng.
    Fallback: Light_Load × Hour → Light_Load global.
    """
    light = df[df["Load_Type"] == "Light_Load"].copy()
    if len(light) == 0:
        return pd.Series(np.nan, index=df.index)

    median_series = pd.Series(np.nan, index=df.index, dtype=float)
    baseline_level = pd.Series(0, index=df.index, dtype=np.int8)
    baseline_warning = pd.Series(False, index=df.index)

    # Level 1: Light_Load × Hour × WeekStatus
    groups = light.groupby(["Hour", "WeekStatus"], sort=False)
    for keys, idx in groups.groups.items():
        idx_full = df.index[df.index.isin(idx)]
        vals = light.loc[idx, "Usage_kWh"]
        if len(vals) >= 10:
            median_series.loc[idx_full] = vals.median()
            baseline_level.loc[idx_full] = 1

    # Level 2: Light_Load × Hour
    still_nan = median_series.isna()
    if still_nan.any():
        groups2 = light.groupby("Hour", sort=False)
        for keys, idx in groups2.groups.items():
            idx_full = df.index[df.index.isin(idx)]
            vals = light.loc[idx, "Usage_kWh"]
            if len(vals) >= 10:
                median_series.loc[idx_full] = vals.median()
                baseline_level.loc[idx_full] = 2

    # Level 3: Light_Load global
    still_nan = median_series.isna()
    if still_nan.any():
        median_series.loc[still_nan] = light["Usage_kWh"].median()
        baseline_level.loc[still_nan] = 3
        baseline_warning.loc[still_nan] = True

    # baseline_warning for small/zero-std groups
    for keys, idx in groups.groups.items():
        vals = light.loc[idx, "Usage_kWh"]
        if len(vals) < 10 or vals.std() == 0:
            idx_full = df.index[df.index.isin(idx)]
            baseline_warning.loc[idx_full] = True

    return median_series, baseline_level, baseline_warning


def _compute_rolling_28d_s(df: pd.DataFrame) -> pd.Series:
    """Rolling 28-day mean of Apparent_Power_S. Window = 28*24*4 = 2688."""
    window = 28 * 24 * 4
    return df["Apparent_Power_S"].rolling(window, min_periods=window).mean()


def _compute_pf_volatility(pf_rule: pd.Series, window: int = 4) -> pd.Series:
    """Rolling std of PF_rule. Default window=4 = 1 hour @ 15min."""
    return pf_rule.rolling(window, min_periods=window).std()


def _compute_reactive_power_ratio(df: pd.DataFrame) -> pd.Series:
    """Reactive_Power_Ratio = Q_net / (Usage_kWh + epsilon). Internal only."""
    q_net = _compute_q_net(df)
    eps = 1e-9
    return q_net / (df["Usage_kWh"] + eps)


# ── Point-Level Labeling ────────────────────────────────────────────────────


def _label_overload_point(
    df: pd.DataFrame,
    p99_s: pd.Series,
) -> pd.Series:
    """
    Overload point-level: Apparent_Power_S > context P99.5 AND PF_rule < 0.70.
    """
    pf_rule = _detect_pf_rule(df)
    cond_a = df["Apparent_Power_S"] > p99_s
    cond_b = pf_rule < 0.70
    return cond_a & cond_b


def _label_idling_point(
    df: pd.DataFrame,
    median_s: pd.Series,
) -> pd.Series:
    """
    Idling point-level: Light_Load & Usage_kWh > context median & PF_rule < 0.50.
    """
    pf_rule = _detect_pf_rule(df)
    is_light = df["Load_Type"] == "Light_Load"
    usage_above = df["Usage_kWh"] > median_s
    low_pf = pf_rule < 0.50
    return is_light & usage_above & low_pf


def _label_leakage_point(
    df: pd.DataFrame,
    rolling_28d_s: pd.Series,
) -> pd.Series:
    """Leakage point-level: Usage_kWh>1 & rolling 28d S >=5% & PF/reactive OR."""
    pf_rule = _detect_pf_rule(df)

    # Usage > 1
    usage_ok = df["Usage_kWh"] > 1

    # Rolling 28-day S increase >= 5% per Load_Type
    # Baseline: first 28 days median per Load_Type (avoid future leakage)
    # If first 28 days not available, use per-Load_Type median with comment
    n_28d = 28 * 24 * 4
    baseline_s = pd.Series(np.nan, index=df.index, dtype=float)
    for lt in df["Load_Type"].unique():
        mask_lt = df["Load_Type"] == lt
        s_lt = df.loc[mask_lt, "Apparent_Power_S"]
        if len(s_lt) >= n_28d:
            baseline_s.loc[mask_lt] = s_lt.iloc[:n_28d].median()
        else:
            # Fallback: per-Load_Type median
            baseline_s.loc[mask_lt] = s_lt.median()
    rolling_increase_ok = rolling_28d_s >= (baseline_s * 1.05)

    # PF/reactive OR condition (at least one)
    cond_a = pf_rule < 0.50

    # Internal PF volatility > P95 by Load_Type
    pf_vol = _compute_pf_volatility(pf_rule)
    p95_vol = pf_vol.groupby(df["Load_Type"]).transform("quantile", q=0.95)
    cond_b = pf_vol > p95_vol

    # Internal reactive ratio outside [P5, P95] by Load_Type
    rpr = _compute_reactive_power_ratio(df)
    p5_rpr = rpr.groupby(df["Load_Type"]).transform("quantile", q=0.05)
    p95_rpr = rpr.groupby(df["Load_Type"]).transform("quantile", q=0.95)
    cond_c = (rpr < p5_rpr) | (rpr > p95_rpr)

    pf_or_reactive = cond_a | cond_b | cond_c

    return usage_ok & rolling_increase_ok & pf_or_reactive


# ── label_reason ────────────────────────────────────────────────────────────


def _build_label_reason(
    df: pd.DataFrame,
    overload: pd.Series,
    idling: pd.Series,
    leakage: pd.Series,
    dominant: pd.Series,
    baseline_warning: pd.Series,
    night_warning: pd.Series,
    overlay_map: dict,
) -> pd.Series:
    """Build parseable label_reason strings."""
    reasons = pd.Series("Normal", index=df.index)
    pf_rule = _detect_pf_rule(df)

    # Overload
    ol_mask = dominant == "Suspected_Overload"
    reasons.loc[ol_mask] = "S>P99.5_context;PF_rule<0.70"

    # Idling
    id_mask = dominant == "Suspected_Idling"
    reasons.loc[id_mask] = "Light_Load;Usage>Median_context;PF_rule<0.50;duration>=4"

    # Leakage
    lk_mask = dominant == "Suspected_Leakage_Drift"
    reasons.loc[lk_mask] = (
        "Usage>1;rolling28d_S>=1.05_baseline;PF_or_reactive_condition;duration>=4"
    )

    # Excluded
    ex_mask = dominant == "Excluded"
    reasons.loc[ex_mask] = "Excluded:hard_filter"

    return reasons


# ── Orchestrator ────────────────────────────────────────────────────────────


def label_all_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gán tất cả weak/proxy labels theo guideline v2.5.

    Thêm 9 cột canonical:
      - Suspected_Idling        (int8)
      - Suspected_Leakage_Drift (int8)
      - Suspected_Overload       (int8)
      - anomaly_any             (int8)
      - dominant_label          (str)
      - label_reason            (str)
      - is_proxy_label          (bool, always True)
      - baseline_warning        (bool)
      - night_simplified_baseline_warning (bool)

    Args:
        df: DataFrame đã qua cleaning và feature engineering (cần có
            Apparent_Power_S, Lagging_Current_Power_Factor, Usage_kWh,
            Load_Type, Hour, WeekStatus, Lagging_Current_Reactive.Power_kVarh,
            Leading_Current_Reactive_Power_kVarh).

    Returns:
        DataFrame mới = df gốc + 9 cột label.
    """
    result = df.copy()

    _hour_added = False
    if "Hour" not in result.columns:
        _hour_added = True
        if "NSM" in result.columns:
            result["Hour"] = result["NSM"] // 3600
        elif "date" in result.columns:
            result["Hour"] = pd.to_datetime(result["date"], dayfirst=True).dt.hour
        else:
            raise KeyError("Cannot derive Hour column: NSM and date missing")

    pf_rule = _detect_pf_rule(result)

    # ── Step 1: Compute context baselines ──────────────────────────────────
    p99_s, bl_level_ol, bl_warn_ol = _compute_context_p99(result, "Apparent_Power_S")
    median_idl, bl_level_id, bl_warn_id = _compute_context_median_idling(result)
    rolling_28d = _compute_rolling_28d_s(result)

    # ── Step 2: Compute point-level flags ──────────────────────────────────
    overload_point = _label_overload_point(result, p99_s)
    idling_point = _label_idling_point(result, median_idl)
    leakage_point = _label_leakage_point(result, rolling_28d)

    # ── Step 3: Hard data-quality filters ──────────────────────────────────
    # Zero-power: Usage_kWh==0 && Apparent_Power_S==0
    zero_power = (result["Usage_kWh"] == 0) & (result["Apparent_Power_S"] == 0)
    # Negative power
    negative_power = result["Usage_kWh"] < 0

    excluded = zero_power | negative_power
    # Set point-level flags to False for excluded rows
    overload_point.loc[excluded] = False
    idling_point.loc[excluded] = False
    leakage_point.loc[excluded] = False

    # ── Step 4: Duration post-processing ───────────────────────────────────
    # Overload: point anomaly, no duration requirement
    # Idling: >= 4 consecutive rows
    # Leakage: >= 4 consecutive rows
    idling_duration = _keep_consecutive_runs(idling_point, min_length=4)
    leakage_duration = _keep_consecutive_runs(leakage_point, min_length=4)

    # ── Step 5: Priority resolution ────────────────────────────────────────
    # Overload > Idling > Leakage > Normal
    dominant_label = pd.Series("Normal", index=result.index, dtype=object)
    dominant_label[excluded] = "Excluded"
    dominant_label[leakage_duration] = "Suspected_Leakage_Drift"
    dominant_label[idling_duration] = "Suspected_Idling"
    dominant_label[overload_point] = "Suspected_Overload"

    # Set component flags based on dominant_label (only winning label ON)
    result["Suspected_Overload"] = pd.Series(
        (dominant_label == "Suspected_Overload").astype(np.int8),
        index=result.index,
    )
    result["Suspected_Idling"] = pd.Series(
        (dominant_label == "Suspected_Idling").astype(np.int8),
        index=result.index,
    )
    result["Suspected_Leakage_Drift"] = pd.Series(
        (dominant_label == "Suspected_Leakage_Drift").astype(np.int8),
        index=result.index,
    )

    # ── Step 6: anomaly_any ────────────────────────────────────────────────
    result["anomaly_any"] = pd.Series(
        (
            (result["Suspected_Overload"] == 1)
            | (result["Suspected_Idling"] == 1)
            | (result["Suspected_Leakage_Drift"] == 1)
        ).astype(np.int8),
        index=result.index,
    )

    # ── Step 7: dominant_label ─────────────────────────────────────────────
    result["dominant_label"] = dominant_label

    # ── Step 8: Warning flags ──────────────────────────────────────────────
    # Merge baseline warnings from Overload and Idling contexts
    result["baseline_warning"] = bl_warn_ol | bl_warn_id

    # Night simplified baseline: baseline_level=3 and Hour in 0-5
    night_hours = result["Hour"].between(0, 5)
    night_level3_ol = (bl_level_ol == 3) & night_hours
    night_level3_id = (bl_level_id == 3) & night_hours
    result["night_simplified_baseline_warning"] = night_level3_ol | night_level3_id

    # ── Step 9: label_reason ───────────────────────────────────────────────
    overlap_before = (
        overload_point.astype(int)
        + idling_point.astype(int)
        + leakage_point.astype(int)
    )
    overlay_count = int((overlap_before > 1).sum())
    result["label_reason"] = _build_label_reason(
        result,
        overload_point,
        idling_point,
        leakage_point,
        dominant_label,
        result["baseline_warning"],
        result["night_simplified_baseline_warning"],
        {"overlap_before": overlay_count},
    )

    # ── Step 10: is_proxy_label ────────────────────────────────────────────
    result["is_proxy_label"] = True

    # ── Cleanup: remove temporary Hour column if we added it ────────────────
    if _hour_added:
        result = result.drop(columns=["Hour"])

    # ── Reorder: ensure canonical column order ──────────────────────────────
    label_order = [
        "Suspected_Idling",
        "Suspected_Leakage_Drift",
        "Suspected_Overload",
        "anomaly_any",
        "dominant_label",
        "label_reason",
        "is_proxy_label",
        "baseline_warning",
        "night_simplified_baseline_warning",
    ]
    base_cols = [c for c in result.columns if c not in label_order]
    result = result[base_cols + label_order]

    return result
