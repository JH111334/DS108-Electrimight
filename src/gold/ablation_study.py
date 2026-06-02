"""Run ablation studies for forecasting and proxy anomaly labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.utils.class_weight import compute_sample_weight

from src.utils import GOLD_DIR, PROJECT_ROOT


LABEL_COLUMNS = [
    "anomaly_idling",
    "anomaly_idling_score",
    "anomaly_leakage",
    "anomaly_leakage_score",
    "anomaly_overload",
    "anomaly_overload_score",
    "anomaly_any",
    "anomaly_max_score",
    "anomaly_explanation",
]

BASE_ELECTRIC_COLUMNS = [
    "Lagging_Current_Reactive.Power_kVarh",
    "Leading_Current_Reactive_Power_kVarh",
    "Lagging_Current_Power_Factor",
    "Leading_Current_Power_Factor",
]

CONTEXT_COLUMNS = [
    "NSM",
    "WeekStatus",
    "Day_of_week",
    "Load_Type",
]

WEATHER_COLUMNS = [
    "temperature_2m",
    "precipitation",
    "relative_humidity_2m",
    "windspeed_10m",
    "temp_rolling_24h",
    "temp_diff_24h",
    "heat_index",
    "is_extreme_hot",
    "is_extreme_cold",
    "humidity_x_temp",
    "windspeed_rolling_6h",
]

TIME_COLUMNS = [
    "Usage_kWh_lag_1",
    "Usage_kWh_lag_2",
    "Usage_kWh_lag_4",
    "Usage_kWh_lag_96",
    "Usage_kWh_rmean_24",
    "Usage_kWh_rstd_24",
    "Usage_kWh_rskew_24",
    "Usage_kWh_rmean_48",
    "Usage_kWh_rstd_48",
    "Usage_kWh_rskew_48",
    "Usage_kWh_rmean_96",
    "Usage_kWh_rstd_96",
    "Usage_kWh_rskew_96",
    "NSM_sin",
    "NSM_cos",
]

WAVELET_COLUMNS = [
    "Usage_kWh_cA_mean",
    "Usage_kWh_cA_std",
    "Usage_kWh_cA_energy",
    "Usage_kWh_cA_max_abs",
    "Usage_kWh_cD3_mean",
    "Usage_kWh_cD3_std",
    "Usage_kWh_cD3_energy",
    "Usage_kWh_cD3_max_abs",
    "Usage_kWh_cD2_mean",
    "Usage_kWh_cD2_std",
    "Usage_kWh_cD2_energy",
    "Usage_kWh_cD2_max_abs",
    "Usage_kWh_cD1_mean",
    "Usage_kWh_cD1_std",
    "Usage_kWh_cD1_energy",
    "Usage_kWh_cD1_max_abs",
]

PHYSICAL_COLUMNS = [
    "Apparent_Power_S",
    "Apparent_Power_S_Net",
    "Reactive_Power_Q_Net",
    "Reactive_Power_Q_Total",
    "Phase_Angle_Phi",
    "Phase_Angle_Lagging_Phi",
    "Phase_Angle_Leading_Phi",
]

RULE_DEFINING_COLUMNS = [
    "Usage_kWh",
    "Lagging_Current_Reactive.Power_kVarh",
    "Leading_Current_Reactive_Power_kVarh",
    "Lagging_Current_Power_Factor",
    "Leading_Current_Power_Factor",
    "NSM",
    "WeekStatus",
    "Load_Type",
    "Usage_kWh_rmean_24",
    "Usage_kWh_rmean_48",
    "Usage_kWh_rmean_96",
    "Apparent_Power_S",
    "Apparent_Power_S_Net",
    "Reactive_Power_Q_Net",
    "Reactive_Power_Q_Total",
    "Phase_Angle_Phi",
    "Phase_Angle_Lagging_Phi",
    "Phase_Angle_Leading_Phi",
]


def _existing(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [col for col in columns if col in df.columns]


def _temporal_split(df: pd.DataFrame, train_frac: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(df) * train_frac)
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def _preprocessor(df: pd.DataFrame, columns: list[str]) -> ColumnTransformer:
    numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
    categorical_cols = [col for col in columns if col not in numeric_cols]
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_cols),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )


def _safe_classification_metrics(y_true: pd.Series, prob: np.ndarray) -> dict[str, float]:
    pred = prob >= 0.5
    metrics = {
        "pr_auc": average_precision_score(y_true, prob),
        "f1": f1_score(y_true, pred, zero_division=0),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
    }
    if y_true.nunique() == 2:
        metrics["roc_auc"] = roc_auc_score(y_true, prob)
    else:
        metrics["roc_auc"] = float("nan")
    return {key: float(value) for key, value in metrics.items()}


def _feature_configs(df: pd.DataFrame, target: str, rule_free: bool = False) -> dict[str, list[str]]:
    raw = _existing(df, BASE_ELECTRIC_COLUMNS + CONTEXT_COLUMNS)
    if target == "Usage_kWh":
        raw = [col for col in raw if col != "Usage_kWh"]
    else:
        raw = _existing(df, ["Usage_kWh"] + BASE_ELECTRIC_COLUMNS + CONTEXT_COLUMNS)

    configs = {
        "A0_raw_context": raw,
        "A1_time": raw + _existing(df, TIME_COLUMNS),
        "A2_time_weather": raw + _existing(df, TIME_COLUMNS + WEATHER_COLUMNS),
        "A3_time_weather_wavelet": raw + _existing(df, TIME_COLUMNS + WEATHER_COLUMNS + WAVELET_COLUMNS),
        "A4_all_engineered": raw
        + _existing(df, TIME_COLUMNS + WEATHER_COLUMNS + WAVELET_COLUMNS + PHYSICAL_COLUMNS),
    }

    if rule_free:
        forbidden = set(_existing(df, RULE_DEFINING_COLUMNS + LABEL_COLUMNS))
        configs = {
            name: [col for col in columns if col not in forbidden]
            for name, columns in configs.items()
        }
    return configs


def run_forecasting(df: pd.DataFrame) -> list[dict[str, Any]]:
    horizon = 4  # 1 hour ahead for 15-minute records.
    work_df = df.copy()
    work_df["Usage_kWh_t_plus_1h"] = work_df["Usage_kWh"].shift(-horizon)
    work_df = work_df.iloc[:-horizon].copy()
    train_df, test_df = _temporal_split(work_df)
    results = []
    for name, columns in _feature_configs(df, target="Usage_kWh").items():
        if "Usage_kWh" not in columns:
            columns = ["Usage_kWh"] + columns
        model = Pipeline(
            steps=[
                ("preprocess", _preprocessor(train_df, columns)),
                ("model", HistGradientBoostingRegressor(random_state=42)),
            ]
        )
        target_col = "Usage_kWh_t_plus_1h"
        train_valid = train_df[columns + [target_col]].dropna(subset=[target_col])
        test_valid = test_df[columns + [target_col]].dropna(subset=[target_col])
        model.fit(train_valid[columns], train_valid[target_col])
        pred = model.predict(test_valid[columns])
        rmse = float(np.sqrt(mean_squared_error(test_valid[target_col], pred)))
        results.append(
            {
                "task": "forecast_usage_t_plus_1h",
                "track": "full",
                "config": name,
                "n_train": int(len(train_valid)),
                "n_test": int(len(test_valid)),
                "n_features": int(len(columns)),
                "mae": float(mean_absolute_error(test_valid[target_col], pred)),
                "rmse": float(rmse),
                "r2": float(r2_score(test_valid[target_col], pred)),
            }
        )
    return results


def _classification_cv_rows(
    df: pd.DataFrame,
    columns: list[str],
    config: str,
    track: str,
    n_splits: int = 5,
) -> list[dict[str, Any]]:
    rows = []
    splitter = TimeSeriesSplit(n_splits=n_splits)
    for fold, (train_idx, test_idx) in enumerate(splitter.split(df), start=1):
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()
        train_valid = train_df[columns + ["anomaly_any"]].dropna(subset=["anomaly_any"])
        test_valid = test_df[columns + ["anomaly_any"]].dropna(subset=["anomaly_any"])
        y_train = train_valid["anomaly_any"].astype(bool)
        y_test = test_valid["anomaly_any"].astype(bool)
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            continue
        model = Pipeline(
            steps=[
                ("preprocess", _preprocessor(train_valid, columns)),
                ("model", HistGradientBoostingClassifier(random_state=42)),
            ]
        )
        sample_weight = compute_sample_weight("balanced", y_train)
        model.fit(train_valid[columns], y_train, model__sample_weight=sample_weight)
        prob = model.predict_proba(test_valid[columns])[:, 1]
        row = {
            "task": "classify_proxy_anomaly_any_cv",
            "track": track,
            "config": config,
            "fold": int(fold),
            "n_train": int(len(train_valid)),
            "n_test": int(len(test_valid)),
            "train_positive_rate": float(y_train.mean()),
            "test_positive_rate": float(y_test.mean()),
            "n_features": int(len(columns)),
        }
        row.update(_safe_classification_metrics(y_test, prob))
        rows.append(row)
    return rows


def run_proxy_classification(
    df: pd.DataFrame,
    synthetic_path: Path | None = None,
) -> list[dict[str, Any]]:
    train_df, test_df = _temporal_split(df)
    results: list[dict[str, Any]] = []

    for track, rule_free in [("full", False), ("rule_free", True)]:
        configs = _feature_configs(df, target="anomaly_any", rule_free=rule_free)
        for name, columns in configs.items():
            if not columns:
                continue
            model = Pipeline(
                steps=[
                    ("preprocess", _preprocessor(train_df, columns)),
                    ("model", HistGradientBoostingClassifier(random_state=42)),
                ]
            )
            train_valid = train_df[columns + ["anomaly_any"]].dropna(subset=["anomaly_any"])
            test_valid = test_df[columns + ["anomaly_any"]].dropna(subset=["anomaly_any"])
            y_train = train_valid["anomaly_any"].astype(bool)
            y_test = test_valid["anomaly_any"].astype(bool)
            sample_weight = compute_sample_weight("balanced", y_train)
            model.fit(train_valid[columns], y_train, model__sample_weight=sample_weight)
            prob = model.predict_proba(test_valid[columns])[:, 1]
            row = {
                "task": "classify_proxy_anomaly_any",
                "track": track,
                "config": name,
                "n_train": int(len(train_valid)),
                "n_test": int(len(test_valid)),
                "train_positive_rate": float(y_train.mean()),
                "test_positive_rate": float(y_test.mean()),
                "n_features": int(len(columns)),
            }
            row.update(_safe_classification_metrics(y_test, prob))
            results.append(row)
            results.extend(_classification_cv_rows(df, columns, name, track))

        if track == "full" and synthetic_path and synthetic_path.exists():
            numeric_columns = [
                col for col in configs["A4_all_engineered"]
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
            ]
            if numeric_columns:
                synthetic_df = pd.read_csv(synthetic_path)
                synthetic_features = synthetic_df[_existing(synthetic_df, numeric_columns)].copy()
                missing_cols = [col for col in numeric_columns if col not in synthetic_features.columns]
                for col in missing_cols:
                    synthetic_features[col] = np.nan
                synthetic_features = synthetic_features[numeric_columns]
                synthetic_features["anomaly_any"] = True
                augmented_train = pd.concat(
                    [train_df[numeric_columns + ["anomaly_any"]], synthetic_features],
                    ignore_index=True,
                )
                model = Pipeline(
                    steps=[
                        ("preprocess", _preprocessor(augmented_train, numeric_columns)),
                        ("model", HistGradientBoostingClassifier(random_state=42)),
                    ]
                )
                y_train = augmented_train["anomaly_any"].astype(bool)
                y_test = test_df["anomaly_any"].astype(bool)
                sample_weight = compute_sample_weight("balanced", y_train)
                model.fit(augmented_train[numeric_columns], y_train, model__sample_weight=sample_weight)
                prob = model.predict_proba(test_df[numeric_columns])[:, 1]
                row = {
                    "task": "classify_proxy_anomaly_any",
                    "track": "full",
                    "config": "A5_all_engineered_fcgan",
                    "n_train": int(len(augmented_train)),
                    "n_test": int(len(test_df)),
                    "train_positive_rate": float(y_train.mean()),
                    "test_positive_rate": float(y_test.mean()),
                    "n_features": int(len(numeric_columns)),
                }
                row.update(_safe_classification_metrics(y_test, prob))
                results.append(row)
    return results


def _write_bar_chart(
    results: pd.DataFrame,
    task: str,
    metric: str,
    output_path: Path,
    title: str,
) -> None:
    subset = results[results["task"] == task].copy()
    if subset.empty:
        return
    subset = (
        subset.groupby(["track", "config"], as_index=False)[metric]
        .mean()
        .sort_values(metric, ascending=(metric == "rmse"))
    )
    label = subset["track"] + ":" + subset["config"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(label, subset[metric])
    ax.set_title(title)
    ax.set_ylabel(metric)
    ax.tick_params(axis="x", rotation=35, labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def run_ablation(
    input_path: Path,
    synthetic_path: Path,
    output_dir: Path,
    figures_dir: Path,
) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)

    rows = run_forecasting(df)
    rows.extend(run_proxy_classification(df, synthetic_path=synthetic_path))
    results = pd.DataFrame(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "ablation_results.csv"
    summary_path = output_dir / "ablation_summary.json"
    results.to_csv(results_path, index=False, encoding="utf-8")

    summary = {
        "input_path": str(input_path),
        "synthetic_path": str(synthetic_path),
        "n_rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "forecast_best_by_rmse": results[results["task"] == "forecast_usage_t_plus_1h"]
        .sort_values("rmse")
        .head(1)
        .to_dict(orient="records"),
        "proxy_best_by_pr_auc": results[results["task"] == "classify_proxy_anomaly_any_cv"]
        .groupby(["track", "config"], as_index=False)
        .mean(numeric_only=True)
        .sort_values("pr_auc", ascending=False)
        .head(1)
        .to_dict(orient="records"),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    _write_bar_chart(
        results,
        task="forecast_usage_t_plus_1h",
        metric="rmse",
        output_path=figures_dir / "fig09_ablation_forecast_rmse.png",
        title="Forecasting Ablation: RMSE by Feature Group",
    )
    _write_bar_chart(
        results,
        task="classify_proxy_anomaly_any_cv",
        metric="pr_auc",
        output_path=figures_dir / "fig10_ablation_proxy_pr_auc.png",
        title="Proxy Anomaly Ablation CV: PR-AUC by Feature Group",
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DS108 ablation studies")
    parser.add_argument("--input", type=Path, default=GOLD_DIR / "steel_final.csv")
    parser.add_argument("--synthetic", type=Path, default=GOLD_DIR / "steel_synthetic_gan.csv")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "reports")
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=PROJECT_ROOT / "references" / "report-guides" / "figures",
    )
    args = parser.parse_args()
    results = run_ablation(args.input, args.synthetic, args.output_dir, args.figures_dir)
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
