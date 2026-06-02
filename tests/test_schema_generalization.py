"""Tests for generic industrial meter schema support."""

import pandas as pd

from src.bronze.data_loader import clean_data
from src.schema import ACTIVE_POWER_COL, LAGGING_REACTIVE_COL, LEADING_PF_COL
from src.silver.physical_features import build_physical_features


def test_clean_data_accepts_common_meter_aliases() -> None:
    """Generic meter aliases are canonicalized to Electrimight columns."""
    raw = pd.DataFrame(
        {
            "timestamp": ["01/01/2018 00:00", "01/01/2018 00:15"],
            "active_energy_kwh": [10.0, 12.0],
            "Q_lagging": [2.0, 3.0],
            "Q_leading": [0.5, 0.25],
            "PF_lag": [85.0, 90.0],
            "PF_lead": [95.0, 97.0],
        }
    )

    cleaned, report = clean_data(raw)

    assert ACTIVE_POWER_COL in cleaned.columns
    assert LAGGING_REACTIVE_COL in cleaned.columns
    assert LEADING_PF_COL in cleaned.columns
    assert "NSM" in cleaned.columns
    assert "WeekStatus" in cleaned.columns
    assert report["pf_columns_scaled"] == 2
    assert cleaned[LEADING_PF_COL].iloc[0] == 0.95


def test_physical_features_use_lagging_and_leading_reactive_power() -> None:
    """Physical features include net and total reactive-power signals."""
    df = pd.DataFrame(
        {
            "Usage_kWh": [10.0],
            "Lagging_Current_Reactive.Power_kVarh": [4.0],
            "Leading_Current_Reactive_Power_kVarh": [1.5],
            "Lagging_Current_Power_Factor": [0.8],
            "Leading_Current_Power_Factor": [0.9],
        }
    )

    result = build_physical_features(df)

    assert result["Reactive_Power_Q_Net"].iloc[0] == 2.5
    assert result["Reactive_Power_Q_Total"].iloc[0] == 5.5
    assert "Apparent_Power_S_Net" in result.columns
    assert "Phase_Angle_Leading_Phi" in result.columns
