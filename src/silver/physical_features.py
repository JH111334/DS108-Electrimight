"""Build electrical-domain features from generic industrial meter signals."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.schema import (
    ACTIVE_POWER_COL,
    LAGGING_PF_COL,
    LAGGING_REACTIVE_COL,
    LEADING_PF_COL,
    LEADING_REACTIVE_COL,
)


def _zero_series(df: pd.DataFrame) -> pd.Series:
    """Create a zero-valued series aligned with the input DataFrame."""
    return pd.Series(0.0, index=df.index)


def _series_or_zero(df: pd.DataFrame, column: str) -> pd.Series:
    """Return a numeric source column or zeros when the column is absent."""
    if column not in df.columns:
        return _zero_series(df)
    return pd.to_numeric(df[column], errors="coerce").fillna(0.0)


def compute_apparent_power(df: pd.DataFrame) -> pd.Series:
    """Compute legacy apparent power from active power and lagging Q."""
    p = pd.to_numeric(df[ACTIVE_POWER_COL], errors="coerce").fillna(0.0)
    q_lag = _series_or_zero(df, LAGGING_REACTIVE_COL)
    apparent = np.sqrt(p**2 + q_lag**2)
    apparent.name = "Apparent_Power_S"
    return apparent


def compute_reactive_net(df: pd.DataFrame) -> pd.Series:
    """Compute net reactive power as lagging Q minus leading Q."""
    q_net = _series_or_zero(df, LAGGING_REACTIVE_COL) - _series_or_zero(
        df, LEADING_REACTIVE_COL
    )
    q_net.name = "Reactive_Power_Q_Net"
    return q_net


def compute_reactive_total(df: pd.DataFrame) -> pd.Series:
    """Compute total reactive magnitude from lagging and leading components."""
    q_total = _series_or_zero(df, LAGGING_REACTIVE_COL).abs() + _series_or_zero(
        df, LEADING_REACTIVE_COL
    ).abs()
    q_total.name = "Reactive_Power_Q_Total"
    return q_total


def compute_net_apparent_power(df: pd.DataFrame) -> pd.Series:
    """Compute apparent power using active power and net reactive power."""
    p = pd.to_numeric(df[ACTIVE_POWER_COL], errors="coerce").fillna(0.0)
    q_net = compute_reactive_net(df)
    apparent = np.sqrt(p**2 + q_net**2)
    apparent.name = "Apparent_Power_S_Net"
    return apparent


def _phase_angle_from_pf(df: pd.DataFrame, column: str, output_name: str) -> pd.Series:
    """Convert a power-factor column to phase angle in radians."""
    if column not in df.columns:
        phi = pd.Series(np.nan, index=df.index)
    else:
        pf = pd.to_numeric(df[column], errors="coerce").clip(0, 1)
        phi = np.arccos(pf)
    phi.name = output_name
    return phi


def compute_phase_angle(df: pd.DataFrame) -> pd.Series:
    """Compute the legacy lagging phase angle for backward compatibility."""
    phi = _phase_angle_from_pf(df, LAGGING_PF_COL, "Phase_Angle_Phi")
    return phi


def build_physical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Append physical electrical features without requiring a steel-only schema."""
    result = df.copy()
    result["Reactive_Power_Q_Net"] = compute_reactive_net(df)
    result["Reactive_Power_Q_Total"] = compute_reactive_total(df)
    result["Apparent_Power_S"] = compute_apparent_power(df)
    result["Apparent_Power_S_Net"] = compute_net_apparent_power(df)
    result["Phase_Angle_Phi"] = compute_phase_angle(df)
    result["Phase_Angle_Lagging_Phi"] = result["Phase_Angle_Phi"]
    result["Phase_Angle_Leading_Phi"] = _phase_angle_from_pf(
        df, LEADING_PF_COL, "Phase_Angle_Leading_Phi"
    )
    return result
