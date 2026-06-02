"""Define reusable meter-data schema contracts for Electrimight."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd


DATE_COL = "date"
ACTIVE_POWER_COL = "Usage_kWh"
LAGGING_REACTIVE_COL = "Lagging_Current_Reactive.Power_kVarh"
LEADING_REACTIVE_COL = "Leading_Current_Reactive_Power_kVarh"
LAGGING_PF_COL = "Lagging_Current_Power_Factor"
LEADING_PF_COL = "Leading_Current_Power_Factor"
NSM_COL = "NSM"
WEEK_STATUS_COL = "WeekStatus"
DAY_OF_WEEK_COL = "Day_of_week"
LOAD_TYPE_COL = "Load_Type"


@dataclass(frozen=True)
class MeterSchema:
    """Map source meter columns to the canonical Electrimight schema."""

    date: str = DATE_COL
    active_power: str = ACTIVE_POWER_COL
    lagging_reactive_power: str | None = LAGGING_REACTIVE_COL
    leading_reactive_power: str | None = LEADING_REACTIVE_COL
    lagging_power_factor: str | None = LAGGING_PF_COL
    leading_power_factor: str | None = LEADING_PF_COL
    seconds_from_midnight: str | None = NSM_COL
    week_status: str | None = WEEK_STATUS_COL
    day_of_week: str | None = DAY_OF_WEEK_COL
    load_type: str | None = LOAD_TYPE_COL


DEFAULT_METER_SCHEMA = MeterSchema()


ALIASES: Mapping[str, tuple[str, ...]] = {
    DATE_COL: ("date", "timestamp", "datetime", "time", "Date", "Timestamp"),
    ACTIVE_POWER_COL: (
        "Usage_kWh",
        "active_energy_kwh",
        "active_power_kw",
        "kwh",
        "kw",
        "P",
        "P_kW",
    ),
    LAGGING_REACTIVE_COL: (
        "Lagging_Current_Reactive.Power_kVarh",
        "lagging_reactive_power_kvarh",
        "reactive_power_lagging_kvarh",
        "Q_lagging",
        "Q_lag",
    ),
    LEADING_REACTIVE_COL: (
        "Leading_Current_Reactive_Power_kVarh",
        "leading_reactive_power_kvarh",
        "reactive_power_leading_kvarh",
        "Q_leading",
        "Q_lead",
    ),
    LAGGING_PF_COL: (
        "Lagging_Current_Power_Factor",
        "lagging_power_factor",
        "power_factor_lagging",
        "PF_lagging",
        "PF_lag",
    ),
    LEADING_PF_COL: (
        "Leading_Current_Power_Factor",
        "leading_power_factor",
        "power_factor_leading",
        "PF_leading",
        "PF_lead",
    ),
    NSM_COL: ("NSM", "seconds_from_midnight", "nsm"),
    WEEK_STATUS_COL: ("WeekStatus", "week_status", "is_weekend"),
    DAY_OF_WEEK_COL: ("Day_of_week", "day_of_week", "weekday"),
    LOAD_TYPE_COL: ("Load_Type", "load_type", "operation_mode", "shift_load_type"),
}


def _find_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    """Return the first matching column name from a candidate list."""
    lower_lookup = {column.lower(): column for column in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        matched = lower_lookup.get(candidate.lower())
        if matched is not None:
            return matched
    return None


def infer_meter_schema(df: pd.DataFrame) -> MeterSchema:
    """Infer a canonical meter schema from common industrial column aliases."""
    mapping: dict[str, str | None] = {
        canonical: _find_column(df, aliases) for canonical, aliases in ALIASES.items()
    }
    missing_required = [
        canonical
        for canonical in (DATE_COL, ACTIVE_POWER_COL)
        if mapping.get(canonical) is None
    ]
    if missing_required:
        raise ValueError(
            "Missing required meter columns after alias inference: "
            + ", ".join(missing_required)
        )

    return MeterSchema(
        date=str(mapping[DATE_COL]),
        active_power=str(mapping[ACTIVE_POWER_COL]),
        lagging_reactive_power=mapping[LAGGING_REACTIVE_COL],
        leading_reactive_power=mapping[LEADING_REACTIVE_COL],
        lagging_power_factor=mapping[LAGGING_PF_COL],
        leading_power_factor=mapping[LEADING_PF_COL],
        seconds_from_midnight=mapping[NSM_COL],
        week_status=mapping[WEEK_STATUS_COL],
        day_of_week=mapping[DAY_OF_WEEK_COL],
        load_type=mapping[LOAD_TYPE_COL],
    )


def canonicalize_meter_columns(
    df: pd.DataFrame,
    schema: MeterSchema | None = None,
) -> pd.DataFrame:
    """Rename recognized meter columns and derive generic time context."""
    schema = schema or infer_meter_schema(df)
    rename_map = {
        schema.date: DATE_COL,
        schema.active_power: ACTIVE_POWER_COL,
    }
    optional_pairs = {
        schema.lagging_reactive_power: LAGGING_REACTIVE_COL,
        schema.leading_reactive_power: LEADING_REACTIVE_COL,
        schema.lagging_power_factor: LAGGING_PF_COL,
        schema.leading_power_factor: LEADING_PF_COL,
        schema.seconds_from_midnight: NSM_COL,
        schema.week_status: WEEK_STATUS_COL,
        schema.day_of_week: DAY_OF_WEEK_COL,
        schema.load_type: LOAD_TYPE_COL,
    }
    rename_map.update(
        {
            source: target
            for source, target in optional_pairs.items()
            if source is not None and source != target
        }
    )

    result = df.rename(columns=rename_map).copy()
    result[DATE_COL] = pd.to_datetime(result[DATE_COL], dayfirst=True, errors="coerce")
    if result[DATE_COL].isna().any():
        raise ValueError("Column 'date' contains unparsable timestamps.")

    if NSM_COL not in result.columns:
        ts = result[DATE_COL]
        result[NSM_COL] = ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second

    if WEEK_STATUS_COL not in result.columns:
        result[WEEK_STATUS_COL] = result[DATE_COL].dt.dayofweek.ge(5).map(
            {True: "Weekend", False: "Weekday"}
        )

    if DAY_OF_WEEK_COL not in result.columns:
        result[DAY_OF_WEEK_COL] = result[DATE_COL].dt.day_name()

    return result


def present_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return only columns available in a DataFrame."""
    return [column for column in columns if column in df.columns]
