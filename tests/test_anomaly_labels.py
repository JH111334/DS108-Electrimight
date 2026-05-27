"""Unit tests for src.anomaly_labels module."""

import numpy as np
import pandas as pd
import pytest

from src.silver.anomaly_labels import (
    explain_idling,
    explain_leakage,
    explain_overload,
    label_all_anomalies,
    label_idling,
    label_leakage,
    label_overload,
    score_idling,
    score_leakage,
    score_overload,
)


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """DataFrame mô phỏng với đủ các cột cần thiết."""
    return pd.DataFrame({
        "Usage_kWh": [5.0, 50.0, 120.0, 8.0, 60.0],
        "Lagging_Current_Reactive.Power_kVarh": [1.0, 20.0, 80.0, 2.0, 25.0],
        "Lagging_Current_Power_Factor": [0.45, 0.85, 0.65, 0.40, 0.90],
        "Load_Type": ["Light_Load", "Maximum_Load", "Maximum_Load", "Light_Load", "Medium_Load"],
        "WeekStatus": ["Weekend", "Weekday", "Weekday", "Weekend", "Weekday"],
        "NSM": [1000, 50000, 50000, 80000, 50000],
    })


# ── Idling ────────────────────────────────────────────────────────────


def test_label_idling_logic(sample_df: pd.DataFrame):
    """Idling = Light_Load & off-hours & Usage > median & PF < 0.50."""
    flags = label_idling(sample_df)
    # Row 0: Light_Load, Weekend, NSM=1000 (night), PF=0.45 (<0.50), Usage=5.0
    # Usage median = 50.0 -> 5.0 NOT > 50, so False
    assert flags.iloc[0] == False
    # Row 3: Light_Load, Weekend, NSM=80000 (>75600), PF=0.40, Usage=8.0 NOT > 50
    assert flags.iloc[3] == False


def test_label_idling_detects_when_usage_high():
    """Idling detected khi Usage > median và đủ điều kiện khác."""
    df = pd.DataFrame({
        "Usage_kWh": [10.0, 20.0, 100.0],  # median=20, 100>20
        "Lagging_Current_Power_Factor": [0.90, 0.85, 0.40],  # < 0.50
        "Load_Type": ["Light_Load", "Light_Load", "Light_Load"],
        "WeekStatus": ["Weekend", "Weekend", "Weekend"],
        "NSM": [1000, 1000, 1000],  # night
    })
    flags = label_idling(df)
    assert flags.iloc[2] == True


def test_score_idling_range(sample_df: pd.DataFrame):
    """Score idling trong [0, 1]."""
    scores = score_idling(sample_df)
    assert scores.between(0.0, 1.0).all()
    assert scores.dtype == np.float64 or scores.dtype == float


# ── Leakage ───────────────────────────────────────────────────────────


def test_label_leakage_baseline_increase():
    """Leakage detected khi rolling mean vượt baseline 5%."""
    # Tạo chuỗi tăng dần rõ rệt
    usage = np.concatenate([
        np.full(672, 20.0),  # baseline week
        np.full(672, 26.0),  # +30%, cần >21.0 để vượt 5%
    ])
    df = pd.DataFrame({"Usage_kWh": usage})
    flags = label_leakage(df, window=672, threshold_pct=5.0)
    # Phần đầu (baseline) không vượt 5%
    assert flags.iloc[:600].sum() == 0
    # Phần sau đủ xa sẽ vượt 5%
    assert flags.iloc[1300:].all()


def test_score_leakage_gradation():
    """Score leakage phân cấp đúng theo % tăng."""
    # Cần ít nhất 4 tuần baseline (2.688 mẫu) ổn định để baseline = 20.0
    usage = np.concatenate([
        np.full(2688, 20.0),   # 4 tuần baseline ổn định
        np.full(2000, 26.0),   # +30%
    ])
    df = pd.DataFrame({"Usage_kWh": usage})
    scores = score_leakage(df, window=672)
    # Sau khi ổn định, score = 1.0 vì +30%
    assert scores.iloc[3500] == pytest.approx(1.0, abs=1e-6)


# ── Overload ──────────────────────────────────────────────────────────


def test_label_overload_detects_extreme_usage():
    """Overload detected khi Usage cực cao và (Reactive cao OR PF thấp)."""
    df = pd.DataFrame({
        "Usage_kWh": [10.0, 20.0, 30.0, 40.0, 50.0, 150.0],  # 150 > P99.5
        "Lagging_Current_Reactive.Power_kVarh": [1.0, 2.0, 3.0, 4.0, 5.0, 90.0],
        "Lagging_Current_Power_Factor": [0.90, 0.85, 0.80, 0.75, 0.70, 0.60],
    })
    flags = label_overload(df)
    assert flags.iloc[5] == True


def test_label_overload_no_false_positive():
    """Không đánh dấu overload khi Usage bình thường."""
    df = pd.DataFrame({
        "Usage_kWh": [10.0, 20.0, 30.0, 40.0, 50.0],
        "Lagging_Current_Reactive.Power_kVarh": [1.0, 2.0, 3.0, 4.0, 5.0],
        "Lagging_Current_Power_Factor": [0.90, 0.85, 0.80, 0.75, 0.70],
    })
    flags = label_overload(df)
    assert flags.iloc[0] == False


def test_score_overload_range(sample_df: pd.DataFrame):
    """Score overload trong [0, 1]."""
    scores = score_overload(sample_df)
    assert scores.between(0.0, 1.0).all()


# ── Explanation ───────────────────────────────────────────────────────


def test_explain_idling_returns_string():
    """explain_idling trả về str."""
    row = pd.Series({
        "Load_Type": "Light_Load",
        "NSM": 1000,
        "WeekStatus": "Weekend",
        "Usage_kWh": 20.0,
        "Lagging_Current_Power_Factor": 0.45,
    })
    text = explain_idling(row)
    assert isinstance(text, str)
    assert "Idling detected" in text


def test_explain_leakage_format():
    """explain_leakage chứa % tăng."""
    row = pd.Series({"Usage_kWh": 30.0})
    text = explain_leakage(row, baseline=25.0, pct_increase=20.0)
    assert "20.0%" in text


def test_explain_overload_returns_string():
    """explain_overload trả về str."""
    row = pd.Series({
        "Usage_kWh": 150.0,
        "Lagging_Current_Reactive.Power_kVarh": 90.0,
        "Lagging_Current_Power_Factor": 0.60,
    })
    text = explain_overload(row)
    assert isinstance(text, str)
    assert "Overload detected" in text


# ── Orchestrator ──────────────────────────────────────────────────────


def test_label_all_anomalies_adds_columns(sample_df: pd.DataFrame):
    """label_all_anomalies thêm đúng 9 cột mới."""
    result = label_all_anomalies(sample_df)
    expected_new = [
        "anomaly_idling", "anomaly_idling_score",
        "anomaly_leakage", "anomaly_leakage_score",
        "anomaly_overload", "anomaly_overload_score",
        "anomaly_any", "anomaly_max_score", "anomaly_explanation",
    ]
    for col in expected_new:
        assert col in result.columns


def test_label_all_anomalies_scores_in_range(sample_df: pd.DataFrame):
    """Tất cả score nằm trong [0, 1]."""
    result = label_all_anomalies(sample_df)
    for col in ["anomaly_idling_score", "anomaly_leakage_score", "anomaly_overload_score"]:
        assert result[col].between(0.0, 1.0).all()


def test_label_all_anomalies_anomaly_any_is_or(sample_df: pd.DataFrame):
    """anomaly_any = OR của 3 nhãn."""
    result = label_all_anomalies(sample_df)
    expected = (
        result["anomaly_idling"] | result["anomaly_leakage"] | result["anomaly_overload"]
    )
    assert (result["anomaly_any"] == expected).all()


def test_label_all_anomalies_max_score_logic(sample_df: pd.DataFrame):
    """anomaly_max_score = max của 3 score."""
    result = label_all_anomalies(sample_df)
    expected = result[["anomaly_idling_score", "anomaly_leakage_score", "anomaly_overload_score"]].max(axis=1)
    assert np.allclose(result["anomaly_max_score"], expected, atol=1e-6)
