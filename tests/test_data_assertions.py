"""Unit tests for src.data_assertions module."""

import numpy as np
import pandas as pd
import pytest

from src.data_assertions import (
    DataAssertionError,
    assert_anomaly_rate_below,
    assert_correlation_preserved,
    assert_feature_count,
    assert_no_duplicate_timestamps,
    assert_no_negative_usage,
    assert_no_nulls,
    assert_nsm_consistency,
    assert_pf_in_range,
    assert_physical_consistency,
    assert_temporal_sorted,
    run_pipeline_assertions,
)


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def valid_df() -> pd.DataFrame:
    """DataFrame hợp lệ đầy đủ các cột cần thiết."""
    return pd.DataFrame({
        "date": pd.date_range("2018-01-01", periods=5, freq="15min"),
        "Usage_kWh": [10.0, 12.0, 15.0, 18.0, 20.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0, 3.0, 4.0, 5.0, 6.0],
        "Lagging_Current_Power_Factor": [0.85, 0.88, 0.90, 0.92, 0.95],
        "Leading_Current_Power_Factor": [0.95, 0.96, 0.97, 0.98, 0.99],
        "NSM": [0, 900, 1800, 2700, 3600],
        "Apparent_Power_S": [np.sqrt(10**2 + 2**2), np.sqrt(12**2 + 3**2),
                             np.sqrt(15**2 + 4**2), np.sqrt(18**2 + 5**2),
                             np.sqrt(20**2 + 6**2)],
        "anomaly_idling": [False, False, False, False, False],
        "anomaly_leakage": [False, False, False, False, False],
        "anomaly_overload": [False, False, False, False, False],
    })


# ── Physical Constraints ──────────────────────────────────────────────


def test_assert_no_negative_usage_pass(valid_df: pd.DataFrame):
    """Không raise khi Usage_kWh không âm."""
    assert_no_negative_usage(valid_df, strict=True)


def test_assert_no_negative_usage_fail():
    """Raise DataAssertionError khi có Usage_kWh âm."""
    df = pd.DataFrame({"Usage_kWh": [10.0, -1.0]})
    with pytest.raises(DataAssertionError):
        assert_no_negative_usage(df, strict=True)


def test_assert_pf_in_range_pass(valid_df: pd.DataFrame):
    """Không raise khi PF trong [0, 1]."""
    assert_pf_in_range(valid_df, strict=True)


def test_assert_pf_in_range_fail():
    """Raise DataAssertionError khi PF ngoài [0, 1]."""
    df = pd.DataFrame({
        "Lagging_Current_Power_Factor": [0.5, 1.2],
        "Leading_Current_Power_Factor": [0.9, 0.95],
    })
    with pytest.raises(DataAssertionError):
        assert_pf_in_range(df, strict=True)


def test_assert_physical_consistency_pass(valid_df: pd.DataFrame):
    """Không raise khi S² ≈ P² + Q²."""
    assert_physical_consistency(valid_df, tolerance=1e-3, strict=True)


def test_assert_physical_consistency_fail():
    """Raise DataAssertionError khi sai lệch vượt tolerance."""
    df = pd.DataFrame({
        "Usage_kWh": [10.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0],
        "Apparent_Power_S": [50.0],  # Sai lệch lớn
    })
    with pytest.raises(DataAssertionError):
        assert_physical_consistency(df, tolerance=1e-3, strict=True)


# ── Temporal Constraints ──────────────────────────────────────────────


def test_assert_temporal_sorted_pass(valid_df: pd.DataFrame):
    """Không raise khi date tăng dần."""
    assert_temporal_sorted(valid_df, strict=True)


def test_assert_temporal_sorted_fail():
    """Raise DataAssertionError khi date không tăng dần."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["2018-01-02", "2018-01-01"]),
    })
    with pytest.raises(DataAssertionError):
        assert_temporal_sorted(df, strict=True)


def test_assert_no_duplicate_timestamps_pass(valid_df: pd.DataFrame):
    """Không raise khi không có timestamp trùng."""
    assert_no_duplicate_timestamps(valid_df, strict=True)


def test_assert_no_duplicate_timestamps_fail():
    """Raise DataAssertionError khi có timestamp trùng."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["2018-01-01", "2018-01-01"]),
    })
    with pytest.raises(DataAssertionError):
        assert_no_duplicate_timestamps(df, strict=True)


def test_assert_nsm_consistency_pass(valid_df: pd.DataFrame):
    """Không raise khi NSM khớp timestamp."""
    assert_nsm_consistency(valid_df, strict=True)


def test_assert_nsm_consistency_fail():
    """Raise DataAssertionError khi NSM không khớp."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["2018-01-01 00:15"]),
        "NSM": [0],  # Sai, phải là 900
    })
    with pytest.raises(DataAssertionError):
        assert_nsm_consistency(df, strict=True)


# ── Completeness ──────────────────────────────────────────────────────


def test_assert_no_nulls_pass(valid_df: pd.DataFrame):
    """Không raise khi không có null."""
    assert_no_nulls(valid_df, strict=True)


def test_assert_no_nulls_fail():
    """Raise DataAssertionError khi có null."""
    df = pd.DataFrame({"A": [1.0, np.nan]})
    with pytest.raises(DataAssertionError):
        assert_no_nulls(df, strict=True)


def test_assert_no_nulls_excludes_cols():
    """Cho phép null trong exclude_cols."""
    df = pd.DataFrame({"A": [1.0, np.nan], "B": [1, 2]})
    assert_no_nulls(df, exclude_cols=["A"], strict=True)


# ── Anomaly Constraints ───────────────────────────────────────────────


def test_assert_anomaly_rate_below_pass(valid_df: pd.DataFrame):
    """Không raise khi tỷ lệ anomaly < threshold."""
    assert_anomaly_rate_below(valid_df, threshold=0.10, strict=True)


def test_assert_anomaly_rate_below_fail():
    """Raise DataAssertionError khi tỷ lệ vượt ngưỡng."""
    df = pd.DataFrame({
        "anomaly_idling": [True] * 15 + [False] * 5,  # 30%
    })
    with pytest.raises(DataAssertionError):
        assert_anomaly_rate_below(df, threshold=0.10, strict=True)


# ── Feature Engineering Constraints ───────────────────────────────────


def test_assert_feature_count_pass(valid_df: pd.DataFrame):
    """Không raise khi số cột >= min_features."""
    assert_feature_count(valid_df, min_features=5, strict=True)


def test_assert_feature_count_fail():
    """Raise DataAssertionError khi số cột ít hơn min."""
    df = pd.DataFrame({"A": [1, 2]})
    with pytest.raises(DataAssertionError):
        assert_feature_count(df, min_features=5, strict=True)


def test_assert_correlation_preserved_pass():
    """Không raise khi synthetic gần real."""
    real = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [2, 4, 6, 8, 10]})
    syn = pd.DataFrame({"A": [1.1, 2.1, 2.9, 4.2, 5.1], "B": [2.2, 3.9, 6.1, 7.8, 10.2]})
    assert_correlation_preserved(real, syn, threshold=0.90, strict=True)


def test_assert_correlation_preserved_fail():
    """Raise DataAssertionError khi tương quan sai lệch nhiều."""
    real = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [2, 4, 6, 8, 10]})
    # Synthetic: A và B độc lập hoàn toàn -> correlation structure khác biệt
    np.random.seed(7)
    syn = pd.DataFrame({
        "A": np.random.normal(3, 1, 200),
        "B": np.random.normal(6, 2, 200),
    })
    with pytest.raises(DataAssertionError):
        assert_correlation_preserved(real, syn, threshold=0.90, strict=True)


# ── Orchestrator ──────────────────────────────────────────────────────


def test_run_pipeline_assertions_post_cleaning(valid_df: pd.DataFrame):
    """Tất cả assertions PASS ở giai đoạn post_cleaning."""
    results = run_pipeline_assertions(valid_df, stage="post_cleaning", strict=False)
    assert all(v == "PASS" for v in results.values())


def test_run_pipeline_assertions_post_labeling(valid_df: pd.DataFrame):
    """Tất cả assertions PASS ở giai đoạn post_labeling."""
    results = run_pipeline_assertions(valid_df, stage="post_labeling", strict=False)
    assert all(v == "PASS" for v in results.values())
