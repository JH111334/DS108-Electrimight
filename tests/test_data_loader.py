"""Unit tests for src.data_loader module."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.bronze.data_loader import clean_data, inspect_data, load_steel_data


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    """Tạo DataFrame thô mô phỏng cấu trúc Steel Industry."""
    dates = pd.date_range("2018-01-01", periods=10, freq="15min")
    return pd.DataFrame({
        "date": dates,
        "Usage_kWh": [10.0, 12.0, np.nan, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4],
        "CO2(tCO2)": [0.01, 0.012, 0.014, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045],
        "Lagging_Current_Power_Factor": [85.0, 88.0, 90.0, 92.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0],
        "Leading_Current_Power_Factor": [95.0, 96.0, 97.0, 98.0, 99.0, 99.5, 99.8, 99.9, 100.0, 100.0],
        "NSM": [0, 900, 1800, 2700, 3600, 4500, 5400, 6300, 7200, 8100],
        "WeekStatus": ["Weekday"] * 10,
        "Day_of_week": ["Monday"] * 10,
        "Load_Type": ["Light_Load"] * 5 + ["Maximum_Load"] * 5,
    })


# ── load_steel_data ───────────────────────────────────────────────────


def test_load_steel_data_file_not_found():
    """Raise FileNotFoundError khi tệp không tồn tại."""
    with pytest.raises(FileNotFoundError):
        load_steel_data(Path("non_existent_file.csv"))


def test_load_steel_data_returns_dataframe(tmp_path: Path):
    """Trả về DataFrame với cột date dạng datetime."""
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({
        "date": ["01/01/2018 00:00", "01/01/2018 00:15"],
        "Usage_kWh": [10.0, 12.0],
    })
    df.to_csv(csv_path, index=False)

    loaded = load_steel_data(csv_path)
    assert isinstance(loaded, pd.DataFrame)
    assert pd.api.types.is_datetime64_any_dtype(loaded["date"])


# ── inspect_data ──────────────────────────────────────────────────────


def test_inspect_data_keys(sample_raw_df: pd.DataFrame):
    """Report chứa đủ các khóa cơ bản."""
    report = inspect_data(sample_raw_df)
    assert "shape" in report
    assert "dtypes" in report
    assert "missing_count" in report
    assert "missing_pct" in report
    assert "duplicates" in report
    assert report["shape"] == sample_raw_df.shape


def test_inspect_data_missing_values(sample_raw_df: pd.DataFrame):
    """Phát hiện đúng số lượng missing."""
    report = inspect_data(sample_raw_df)
    assert report["missing_count"]["Usage_kWh"] == 1
    assert report["duplicates"] == 0


# ── clean_data ────────────────────────────────────────────────────────


def test_clean_data_removes_duplicates():
    """Loại bỏ bản ghi trùng lặp."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["01/01/2018 00:00", "01/01/2018 00:00", "01/01/2018 00:15"], dayfirst=True),
        "Usage_kWh": [10.0, 10.0, 12.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0, 2.0, 3.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5, 0.5, 0.6],
        "CO2(tCO2)": [0.01, 0.01, 0.012],
        "Lagging_Current_Power_Factor": [85.0, 85.0, 88.0],
        "Leading_Current_Power_Factor": [95.0, 95.0, 96.0],
        "NSM": [0, 0, 900],
    })
    cleaned, report = clean_data(df)
    assert report["duplicates_removed"] == 1
    assert len(cleaned) == 2


def test_clean_data_imputes_missing():
    """Nội suy giá trị thiếu."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["01/01/2018 00:00", "01/01/2018 00:15", "01/01/2018 00:30"], dayfirst=True),
        "Usage_kWh": [10.0, np.nan, 14.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0, 3.0, 4.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5, 0.6, 0.7],
        "CO2(tCO2)": [0.01, 0.012, 0.014],
        "Lagging_Current_Power_Factor": [85.0, 88.0, 90.0],
        "Leading_Current_Power_Factor": [95.0, 96.0, 97.0],
        "NSM": [0, 900, 1800],
    })
    cleaned, report = clean_data(df)
    assert report["missing_imputed"] > 0
    assert cleaned["Usage_kWh"].isnull().sum() == 0
    # Giá trị nội suy tuyến tính nằm giữa 10 và 14
    assert cleaned.loc[1, "Usage_kWh"] == pytest.approx(12.0, rel=1e-3)


def test_clean_data_scales_power_factor():
    """Scale Power Factor từ % về [0, 1]."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["01/01/2018 00:00"], dayfirst=True),
        "Usage_kWh": [10.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5],
        "CO2(tCO2)": [0.01],
        "Lagging_Current_Power_Factor": [85.0],
        "Leading_Current_Power_Factor": [95.0],
        "NSM": [0],
    })
    cleaned, report = clean_data(df)
    assert report["pf_columns_scaled"] == 2
    assert cleaned["Lagging_Current_Power_Factor"].iloc[0] == pytest.approx(0.85)
    assert cleaned["Leading_Current_Power_Factor"].iloc[0] == pytest.approx(0.95)


def test_clean_data_clips_invalid_pf():
    """Clip PF về [0, 1] nếu vượt ngưỡng sau scale."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["01/01/2018 00:00", "01/01/2018 00:15"], dayfirst=True),
        "Usage_kWh": [10.0, 12.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0, 3.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5, 0.6],
        "CO2(tCO2)": [0.01, 0.012],
        "Lagging_Current_Power_Factor": [105.0, -5.0],  # Vượt [0,100]
        "Leading_Current_Power_Factor": [100.0, 0.0],
        "NSM": [0, 900],
    })
    cleaned, report = clean_data(df)
    assert cleaned["Lagging_Current_Power_Factor"].max() <= 1.0
    assert cleaned["Lagging_Current_Power_Factor"].min() >= 0.0


def test_clean_data_corrects_negative_usage():
    """Sửa Usage_kWh âm về 0."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["01/01/2018 00:00"], dayfirst=True),
        "Usage_kWh": [-5.0],
        "Lagging_Current_Reactive.Power_kVarh": [2.0],
        "Leading_Current_Reactive_Power_kVarh": [0.5],
        "CO2(tCO2)": [0.01],
        "Lagging_Current_Power_Factor": [85.0],
        "Leading_Current_Power_Factor": [95.0],
        "NSM": [0],
    })
    cleaned, report = clean_data(df)
    assert report["negative_usage_corrected"] == 1
    assert cleaned["Usage_kWh"].iloc[0] == 0.0


def test_clean_data_sorts_by_date():
    """Sắp xếp tăng dần theo date."""
    df = pd.DataFrame({
        "date": pd.to_datetime(["02/01/2018 00:00", "01/01/2018 00:00"], dayfirst=True),
        "Usage_kWh": [12.0, 10.0],
        "Lagging_Current_Reactive.Power_kVarh": [3.0, 2.0],
        "Leading_Current_Reactive_Power_kVarh": [0.6, 0.5],
        "CO2(tCO2)": [0.012, 0.01],
        "Lagging_Current_Power_Factor": [88.0, 85.0],
        "Leading_Current_Power_Factor": [96.0, 95.0],
        "NSM": [0, 0],
    })
    cleaned, _ = clean_data(df)
    assert cleaned["date"].is_monotonic_increasing


def test_clean_data_report_final_shape(sample_raw_df: pd.DataFrame):
    """Report chứa final_shape."""
    cleaned, report = clean_data(sample_raw_df)
    assert "final_shape" in report
    assert report["final_shape"] == cleaned.shape
