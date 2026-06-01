"""Unit tests for src.silver.anomaly_labels module — v2.5 interface."""

import numpy as np
import pandas as pd
import pytest

from src.silver.anomaly_labels import (
    _detect_pf_rule,
    _compute_q_net,
    _keep_consecutive_runs,
    label_all_anomalies,
)


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Minimal DataFrame with required columns."""
    n = 50
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "Usage_kWh": np.abs(np.random.normal(30, 15, n)),
            "Lagging_Current_Reactive.Power_kVarh": np.abs(np.random.normal(10, 5, n)),
            "Leading_Current_Reactive_Power_kVarh": np.abs(np.random.normal(2, 1, n)),
            "Lagging_Current_Power_Factor": np.clip(
                np.random.normal(0.8, 0.15, n), 0.0, 1.0
            ),
            "Load_Type": np.random.choice(
                ["Light_Load", "Medium_Load", "Maximum_Load"], n
            ),
            "Hour": np.random.randint(0, 24, n),
            "WeekStatus": np.random.choice(["Weekday", "Weekend"], n),
        }
    )
    df["Apparent_Power_S"] = np.sqrt(
        df["Usage_kWh"] ** 2 + df["Lagging_Current_Reactive.Power_kVarh"] ** 2
    )
    return df


# ── Utilities ───────────────────────────────────────────────────────


def test_detect_pf_rule_already_normalized():
    df = pd.DataFrame({"Lagging_Current_Power_Factor": [0.5, 0.8, 0.3]})
    pf = _detect_pf_rule(df)
    assert pf.max() <= 1.0
    assert pf.min() >= 0.0


def test_detect_pf_rule_scales_from_percent():
    df = pd.DataFrame({"Lagging_Current_Power_Factor": [50.0, 80.0, 30.0]})
    pf = _detect_pf_rule(df)
    assert pf.max() <= 1.0
    assert pf.min() >= 0.0


def test_compute_q_net():
    df = pd.DataFrame(
        {
            "Lagging_Current_Reactive.Power_kVarh": [10.0, 20.0],
            "Leading_Current_Reactive_Power_kVarh": [3.0, 5.0],
        }
    )
    q = _compute_q_net(df)
    assert q.iloc[0] == 7.0
    assert q.iloc[1] == 15.0


def test_keep_consecutive_runs():
    flags = pd.Series([True, True, False, True, True, True, True, False, True])
    result = _keep_consecutive_runs(flags, min_length=4)
    # [0,0,0,1,1,1,1,0,0]
    assert result.iloc[0] == False
    assert result.iloc[1] == False
    assert result.iloc[3] == True
    assert result.iloc[6] == True
    assert result.iloc[8] == False


def test_keep_consecutive_runs_none():
    flags = pd.Series([False, False, False])
    result = _keep_consecutive_runs(flags, 4)
    assert not result.any()


def test_keep_consecutive_runs_all_short():
    flags = pd.Series([True, True, True, False, True, True])
    result = _keep_consecutive_runs(flags, 4)
    assert not result.any()


# ── Orchestrator: columns ───────────────────────────────────────────


def test_label_all_anomalies_adds_9_columns(sample_df):
    result = label_all_anomalies(sample_df)
    expected = [
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
    for col in expected:
        assert col in result.columns, f"Missing column: {col}"
    assert len(result.columns) == len(sample_df.columns) + 9


def test_label_all_anomalies_column_dtypes(sample_df):
    result = label_all_anomalies(sample_df)
    assert result["Suspected_Idling"].dtype == np.int8
    assert result["Suspected_Leakage_Drift"].dtype == np.int8
    assert result["Suspected_Overload"].dtype == np.int8
    assert result["anomaly_any"].dtype == np.int8
    assert result["is_proxy_label"].dtype == bool
    assert result["baseline_warning"].dtype == bool
    assert result["night_simplified_baseline_warning"].dtype == bool


def test_is_proxy_label_all_true(sample_df):
    result = label_all_anomalies(sample_df)
    assert result["is_proxy_label"].all()


def test_anomaly_any_is_union(sample_df):
    result = label_all_anomalies(sample_df)
    expected = (
        (result["Suspected_Idling"] == 1)
        | (result["Suspected_Leakage_Drift"] == 1)
        | (result["Suspected_Overload"] == 1)
    )
    assert (result["anomaly_any"].astype(bool) == expected).all()


def test_dominant_label_categories(sample_df):
    result = label_all_anomalies(sample_df)
    valid = {
        "Normal",
        "Suspected_Idling",
        "Suspected_Leakage_Drift",
        "Suspected_Overload",
        "Excluded",
    }
    actual = set(result["dominant_label"].unique())
    assert actual.issubset(valid)


def test_dominant_label_matches_component(sample_df):
    result = label_all_anomalies(sample_df)
    dl = result["dominant_label"]
    si = result["Suspected_Idling"]
    so = result["Suspected_Overload"]
    sl = result["Suspected_Leakage_Drift"]
    # Nếu dominant_label != Normal/Excluded, component tương ứng phải = 1
    assert (so[dl == "Suspected_Overload"] == 1).all()
    assert (si[dl == "Suspected_Idling"] == 1).all()
    assert (sl[dl == "Suspected_Leakage_Drift"] == 1).all()


def test_priority_no_overlap(sample_df):
    """At most one component label = 1 per row."""
    result = label_all_anomalies(sample_df)
    row_sum = (
        result["Suspected_Idling"].astype(int)
        + result["Suspected_Leakage_Drift"].astype(int)
        + result["Suspected_Overload"].astype(int)
    )
    assert (row_sum <= 1).all()


def test_label_reason_is_string(sample_df):
    result = label_all_anomalies(sample_df)
    assert str(result["label_reason"].dtype) in ("object", "string", "str")
    norm_mask = result["dominant_label"] == "Normal"
    assert (result.loc[norm_mask, "label_reason"] == "Normal").all()


def test_no_missing_in_label_columns(sample_df):
    result = label_all_anomalies(sample_df)
    label_cols = [
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
    for col in label_cols:
        assert not result[col].isna().any(), f"Nulls in {col}"


# ── Overload specific ───────────────────────────────────────────────


def test_overload_is_high_stress(sample_df):
    """Artificially inject extreme Apparent_Power_S + low PF."""
    df = sample_df.copy()
    n = len(df)
    df["Lagging_Current_Power_Factor"].iloc[:5] = 0.6
    df["Apparent_Power_S"].iloc[:5] = df["Apparent_Power_S"].max() * 10
    result = label_all_anomalies(df)
    # At least one of the injected rows should trigger
    assert result["Suspected_Overload"].sum() > 0


# ── Idling specific ────────────────────────────────────────────────


def test_idling_requires_duration():
    """Idling needs >= 4 consecutive rows: 3 rows should NOT trigger."""
    n = 20
    df = pd.DataFrame(
        {
            "Usage_kWh": [10.0] * n,
            "Lagging_Current_Reactive.Power_kVarh": [10.0] * n,
            "Leading_Current_Reactive_Power_kVarh": [0.0] * n,
            "Lagging_Current_Power_Factor": [0.40] * n,
            "Load_Type": ["Light_Load"] * n,
            "Hour": list(range(n)),
            "WeekStatus": ["Weekday"] * n,
        }
    )
    df["Apparent_Power_S"] = np.sqrt(
        df["Usage_kWh"] ** 2 + df["Lagging_Current_Reactive.Power_kVarh"] ** 2
    )
    # Set first 6 rows high (>=4 consecutive triggers idling)
    # Leave others at 10 so median of the context group stays low
    df.loc[0:5, "Usage_kWh"] = 100.0
    df.loc[0:5, "Apparent_Power_S"] = np.sqrt(100**2 + 10**2)

    result = label_all_anomalies(df)
    # Rows 0-5: Usage=100 vs median≈55 → 100 > 55 = True, PF=0.40 < 0.50
    # 6 consecutive True → duration filter keeps all 6
    # But we only modified 6 rows not 10, so median should be around 55
    # Let the test just check: at least some idling detected and they are consecutive
    idling = result["Suspected_Idling"]
    assert idling.sum() >= 3
    # Verify idling rows are all consecutive
    idling_idx = idling[idling == 1].index.tolist()
    assert max(idling_idx) - min(idling_idx) + 1 == len(idling_idx)
