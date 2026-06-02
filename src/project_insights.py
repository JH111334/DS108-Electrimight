"""Report the strongest DS108 Electrimight project insights in one run."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import GOLD_DIR, PIPELINE_METADATA_DIR, PROJECT_ROOT


DEFAULT_GOLD_PATH = GOLD_DIR / "steel_final.csv"
DEFAULT_ABLATION_PATH = PIPELINE_METADATA_DIR / "ablation_results.csv"
DEFAULT_PIPELINE_STATS_PATH = PIPELINE_METADATA_DIR / "pipeline_stats.json"
DEFAULT_GAN_STATS_PATH = PIPELINE_METADATA_DIR / "gan_stats.json"
DEFAULT_OUTPUT_PATH = PIPELINE_METADATA_DIR / "project_insights.md"


CONFIG_LABELS = {
    "A0_raw_context": "RAW + CONTEXT",
    "A1_time": "RAW + TIME",
    "A2_time_weather": "RAW + TIME + WEATHER",
    "A3_time_weather_wavelet": "RAW + TIME + WEATHER + WAVELET",
    "A4_all_engineered": "ALL ENGINEERED",
    "A5_all_engineered_fcgan": "ALL ENGINEERED + FC-GAN",
}


@dataclass(frozen=True)
class InsightSummary:
    """Store the key metrics shown to instructors."""

    n_rows: int
    n_columns: int
    anomaly_count: int
    anomaly_rate_pct: float
    best_forecast_config: str
    best_forecast_rmse: float
    raw_forecast_rmse: float
    best_proxy_config: str
    best_proxy_pr_auc: float
    rule_free_best_pr_auc: float | None
    gan_mean_error_pct: float | None
    gan_std_error_pct: float | None
    gan_correlation_mae: float | None


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file with explicit UTF-8 decoding."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _require_file(path: Path, purpose: str) -> None:
    """Raise a clear error when an expected artifact is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {purpose}: {path}. Run the pipeline/ablation step first."
        )


def _dataset_shape(gold_path: Path) -> tuple[int, int]:
    """Return the final dataset shape without loading unnecessary metadata."""
    df = pd.read_csv(gold_path)
    return int(df.shape[0]), int(df.shape[1])


def _anomaly_stats(gold_path: Path, pipeline_stats: dict[str, Any]) -> tuple[int, float]:
    """Return anomaly count and rate from stats, falling back to the dataset."""
    if "n_any_anomaly" in pipeline_stats and "any_anomaly_pct" in pipeline_stats:
        return int(pipeline_stats["n_any_anomaly"]), float(pipeline_stats["any_anomaly_pct"])

    df = pd.read_csv(gold_path, usecols=["anomaly_any"])
    anomaly_count = int(df["anomaly_any"].astype(bool).sum())
    anomaly_rate_pct = float(anomaly_count / len(df) * 100)
    return anomaly_count, anomaly_rate_pct


def _forecast_table(ablation: pd.DataFrame) -> pd.DataFrame:
    """Extract one-hour-ahead forecasting RMSE rows."""
    table = ablation[ablation["task"] == "forecast_usage_t_plus_1h"].copy()
    if table.empty:
        raise ValueError("No forecast_usage_t_plus_1h rows found in ablation results.")
    return table.sort_values("rmse", ascending=True)


def _proxy_cv_table(ablation: pd.DataFrame, track: str) -> pd.DataFrame:
    """Aggregate proxy anomaly CV metrics by feature configuration."""
    rows = ablation[
        (ablation["task"] == "classify_proxy_anomaly_any_cv")
        & (ablation["track"] == track)
    ].copy()
    if rows.empty:
        return rows
    grouped = rows.groupby("config", as_index=False).mean(numeric_only=True)
    return grouped.sort_values("pr_auc", ascending=False)


def build_summary(
    gold_path: Path,
    ablation_path: Path,
    pipeline_stats_path: Path,
    gan_stats_path: Path,
) -> InsightSummary:
    """Build the project insight summary from existing artifacts."""
    _require_file(gold_path, "gold dataset")
    _require_file(ablation_path, "ablation results")

    pipeline_stats = _read_json(pipeline_stats_path)
    gan_stats = _read_json(gan_stats_path)
    ablation = pd.read_csv(ablation_path)

    n_rows, n_columns = _dataset_shape(gold_path)
    anomaly_count, anomaly_rate_pct = _anomaly_stats(gold_path, pipeline_stats)

    forecast = _forecast_table(ablation)
    best_forecast = forecast.iloc[0]
    raw_forecast = forecast[forecast["config"] == "A0_raw_context"]
    if raw_forecast.empty:
        raise ValueError("A0_raw_context forecast row is missing.")

    proxy_full = _proxy_cv_table(ablation, track="full")
    if proxy_full.empty:
        raise ValueError("No full-track proxy anomaly CV rows found.")
    best_proxy = proxy_full.iloc[0]

    proxy_rule_free = _proxy_cv_table(ablation, track="rule_free")
    rule_free_best = None if proxy_rule_free.empty else float(proxy_rule_free.iloc[0]["pr_auc"])

    return InsightSummary(
        n_rows=n_rows,
        n_columns=n_columns,
        anomaly_count=anomaly_count,
        anomaly_rate_pct=anomaly_rate_pct,
        best_forecast_config=str(best_forecast["config"]),
        best_forecast_rmse=float(best_forecast["rmse"]),
        raw_forecast_rmse=float(raw_forecast.iloc[0]["rmse"]),
        best_proxy_config=str(best_proxy["config"]),
        best_proxy_pr_auc=float(best_proxy["pr_auc"]),
        rule_free_best_pr_auc=rule_free_best,
        gan_mean_error_pct=_optional_float(gan_stats, "mean_error_pct"),
        gan_std_error_pct=_optional_float(gan_stats, "std_error_pct"),
        gan_correlation_mae=_optional_float(gan_stats, "correlation_mae"),
    )


def _optional_float(values: dict[str, Any], key: str) -> float | None:
    """Return a float value when present, otherwise None."""
    if key not in values:
        return None
    return float(values[key])


def _label(config: str) -> str:
    """Return a readable feature configuration label."""
    return CONFIG_LABELS.get(config, config)


def _format_optional(value: float | None, digits: int = 4) -> str:
    """Format optional numeric values for console and Markdown output."""
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def load_comparison_tables(
    ablation_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load sorted comparison tables for all ablation configurations."""
    _require_file(ablation_path, "ablation results")
    ablation = pd.read_csv(ablation_path)
    forecast = _forecast_table(ablation)
    proxy_full = _proxy_cv_table(ablation, track="full")
    proxy_rule_free = _proxy_cv_table(ablation, track="rule_free")
    return forecast, proxy_full, proxy_rule_free


def _console_forecast_table(table: pd.DataFrame) -> str:
    """Format all forecasting configs for ASCII-safe console output."""
    rows = table[["config", "n_features", "rmse", "mae", "r2"]].copy()
    rows["config"] = rows["config"].map(_label)
    return rows.to_string(
        index=False,
        formatters={
            "rmse": "{:.4f}".format,
            "mae": "{:.4f}".format,
            "r2": "{:.4f}".format,
        },
    )


def _console_proxy_table(table: pd.DataFrame) -> str:
    """Format all proxy-label configs for ASCII-safe console output."""
    if table.empty:
        return "No rows found."
    rows = table[["config", "n_features", "pr_auc", "f1", "precision", "recall"]].copy()
    rows["config"] = rows["config"].map(_label)
    return rows.to_string(
        index=False,
        formatters={
            "pr_auc": "{:.4f}".format,
            "f1": "{:.4f}".format,
            "precision": "{:.4f}".format,
            "recall": "{:.4f}".format,
        },
    )


def _markdown_forecast_table(table: pd.DataFrame) -> str:
    """Format the forecasting comparison table as Markdown."""
    rows = ["| Rank | Config | RMSE | MAE | R2 |", "|---:|---|---:|---:|---:|"]
    for rank, row in enumerate(table.itertuples(index=False), start=1):
        rows.append(
            f"| {rank} | {_label(row.config)} | {row.rmse:.4f} | "
            f"{row.mae:.4f} | {row.r2:.4f} |"
        )
    return "\n".join(rows)


def _markdown_proxy_table(table: pd.DataFrame) -> str:
    """Format the proxy-label comparison table as Markdown."""
    if table.empty:
        return "Khong co dong ket qua."
    rows = ["| Rank | Config | PR-AUC | F1 | Precision | Recall |", "|---:|---|---:|---:|---:|---:|"]
    for rank, row in enumerate(table.itertuples(index=False), start=1):
        rows.append(
            f"| {rank} | {_label(row.config)} | {row.pr_auc:.4f} | "
            f"{row.f1:.4f} | {row.precision:.4f} | {row.recall:.4f} |"
        )
    return "\n".join(rows)


def print_console(
    summary: InsightSummary,
    forecast_table: pd.DataFrame,
    proxy_full_table: pd.DataFrame,
    proxy_rule_free_table: pd.DataFrame,
) -> None:
    """Print ASCII-safe insights for Windows PowerShell."""
    rmse_gain = summary.raw_forecast_rmse - summary.best_forecast_rmse
    print("\nDS108 ELECTRIMIGHT - ONE-RUN PROJECT INSIGHTS")
    print("=" * 58)
    print(f"Final gold dataset     : {summary.n_rows:,} rows x {summary.n_columns} columns")
    print(
        "Proxy anomaly labels   : "
        f"{summary.anomaly_count:,} rows ({summary.anomaly_rate_pct:.3f}%)"
    )
    print("-" * 58)
    print("FORECASTING INSIGHT: Usage_kWh(t+1h)")
    print(f"Best config            : {_label(summary.best_forecast_config)}")
    print(f"Best RMSE              : {summary.best_forecast_rmse:.4f}")
    print(f"Raw/context RMSE       : {summary.raw_forecast_rmse:.4f}")
    print(f"RMSE improvement       : {rmse_gain:.4f} lower than raw/context")
    print("-" * 58)
    print("PROXY ANOMALY INSIGHT: anomaly_any")
    print(f"Best full-track config : {_label(summary.best_proxy_config)}")
    print(f"Best CV PR-AUC         : {summary.best_proxy_pr_auc:.4f}")
    print(f"Best rule-free PR-AUC  : {_format_optional(summary.rule_free_best_pr_auc)}")
    print("-" * 58)
    print("ALL FORECASTING CONFIGS SORTED BY RMSE (LOWER IS BETTER)")
    print(_console_forecast_table(forecast_table))
    print("-" * 58)
    print("ALL FULL-TRACK PROXY CONFIGS SORTED BY CV PR-AUC (HIGHER IS BETTER)")
    print(_console_proxy_table(proxy_full_table))
    print("-" * 58)
    print("ALL RULE-FREE PROXY CONFIGS SORTED BY CV PR-AUC")
    print(_console_proxy_table(proxy_rule_free_table))
    print("-" * 58)
    print("GAN VALIDATION SNAPSHOT")
    print(f"Mean error pct         : {_format_optional(summary.gan_mean_error_pct, 2)}%")
    print(f"Std error pct          : {_format_optional(summary.gan_std_error_pct, 2)}%")
    print(f"Correlation MAE        : {_format_optional(summary.gan_correlation_mae, 3)}")
    print("=" * 58)
    print("Takeaway 1: RAW + TIME gives the lowest forecasting RMSE.")
    print("Takeaway 2: RAW + TIME + WEATHER gives the highest proxy-label PR-AUC.")
    print("Takeaway 3: Rule-free PR-AUC is low, so proxy labels still need domain rules.")


def write_markdown(
    summary: InsightSummary,
    output_path: Path,
    forecast_table: pd.DataFrame,
    proxy_full_table: pd.DataFrame,
    proxy_rule_free_table: pd.DataFrame,
) -> None:
    """Write a Vietnamese UTF-8 Markdown insight report."""
    rmse_gain = summary.raw_forecast_rmse - summary.best_forecast_rmse
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# Project Insights - DS108 Electrimight

File này tóm tắt các số liệu quan trọng nhất để giảng viên có thể chạy một lần và xem ngay giá trị của project.

## Dataset thành phẩm

- Gold dataset: **{summary.n_rows:,} dòng x {summary.n_columns} cột**.
- Proxy anomaly labels: **{summary.anomaly_count:,} dòng**, tương đương **{summary.anomaly_rate_pct:.3f}%**.

## Insight 1 - Forecasting

- Target: `Usage_kWh(t+1h)`.
- Config tốt nhất theo RMSE: **{_label(summary.best_forecast_config)}**.
- RMSE tốt nhất: **{summary.best_forecast_rmse:.4f}**.
- RMSE raw/context: **{summary.raw_forecast_rmse:.4f}**.
- Mức giảm RMSE: **{rmse_gain:.4f}**.

Kết luận: **RAW + TIME cho RMSE thấp nhất** trong ablation forecasting. Điều này hợp lý vì tiêu thụ điện công nghiệp phụ thuộc mạnh vào lịch sử gần và chu kỳ thời gian.

### Bảng chứng minh RMSE

{_markdown_forecast_table(forecast_table)}

## Insight 2 - Proxy anomaly labels

- Target: `anomaly_any`.
- Config full-track tốt nhất theo cross-validation PR-AUC: **{_label(summary.best_proxy_config)}**.
- PR-AUC tốt nhất: **{summary.best_proxy_pr_auc:.4f}**.
- PR-AUC tốt nhất ở rule-free track: **{_format_optional(summary.rule_free_best_pr_auc)}**.

Kết luận: **RAW + TIME + WEATHER cho PR-AUC cao nhất với proxy labels**. Weather có giá trị như contextual enrichment, nhưng rule-free PR-AUC thấp cho thấy nhãn proxy vẫn cần domain rules và không nên overclaim là phát hiện lỗi thật độc lập.

### Bảng chứng minh PR-AUC full-track

{_markdown_proxy_table(proxy_full_table)}

### Bảng rule-free để làm rõ giới hạn

{_markdown_proxy_table(proxy_rule_free_table)}

## Insight 3 - GAN validation

- Mean error: **{_format_optional(summary.gan_mean_error_pct, 2)}%**.
- Std error: **{_format_optional(summary.gan_std_error_pct, 2)}%**.
- Correlation MAE: **{_format_optional(summary.gan_correlation_mae, 3)}**.

Kết luận: GAN hiện tại phù hợp để trình bày như baseline augmentation cho lớp anomaly proxy. Mean/std khá gần, nhưng correlation còn lệch nên chưa nên claim là mô hình sinh chuỗi thời gian tốt nhất.

## Câu chốt để trình bày

Electrimight tạo ra một dataset công nghiệp có thể kiểm thử từ meter logs thô: **RAW + TIME giúp dự báo điện tốt nhất**, còn **RAW + TIME + WEATHER giúp dự đoán proxy anomaly tốt nhất**. Kết quả này cũng chỉ ra giới hạn quan trọng: proxy labels hữu ích cho benchmark offline, nhưng cần SCADA/maintenance labels để xác nhận lỗi thật.
"""
    output_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Print and write the key DS108 Electrimight project insights."
    )
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD_PATH)
    parser.add_argument("--ablation", type=Path, default=DEFAULT_ABLATION_PATH)
    parser.add_argument("--pipeline-stats", type=Path, default=DEFAULT_PIPELINE_STATS_PATH)
    parser.add_argument("--gan-stats", type=Path, default=DEFAULT_GAN_STATS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> None:
    """Run the one-command insight report."""
    args = parse_args()
    summary = build_summary(
        gold_path=args.gold,
        ablation_path=args.ablation,
        pipeline_stats_path=args.pipeline_stats,
        gan_stats_path=args.gan_stats,
    )
    forecast, proxy_full, proxy_rule_free = load_comparison_tables(args.ablation)
    print_console(summary, forecast, proxy_full, proxy_rule_free)
    write_markdown(summary, args.output, forecast, proxy_full, proxy_rule_free)
    print(f"\nUTF-8 Markdown report written to: {args.output}")


if __name__ == "__main__":
    main()
