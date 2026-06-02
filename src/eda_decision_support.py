"""Generate EDA evidence for preprocessing and feature decisions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_METADATA = ROOT / "metadata" / "pipeline"
PATHS = {
    "raw": ROOT / "data" / "bronze" / "Steel_industry_data.csv",
    "weather": ROOT / "data" / "bronze" / "weather_gwangyang_2018.csv",
    "gold": ROOT / "data" / "gold" / "steel_final.csv",
    "gan": PIPELINE_METADATA / "gan_stats.json",
    "pipeline": PIPELINE_METADATA / "pipeline_stats.json",
    "ablation": PIPELINE_METADATA / "ablation_summary.json",
    "out_json": PIPELINE_METADATA / "eda_decision_support.json",
    "out_md": PIPELINE_METADATA / "eda_decision_support.md",
}


def read_json(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON file or return an empty mapping."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_csv(path: Path, parse_date: bool = False) -> pd.DataFrame:
    """Read a UTF-8 CSV file with optional day-first date parsing."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    df = pd.read_csv(path, encoding="utf-8")
    if parse_date and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df.sort_values("date")
    return df


def median_step_minutes(series: pd.Series) -> float:
    """Return the median timestamp step in minutes."""
    timestamps = pd.to_datetime(series, dayfirst=True, errors="coerce").dropna().sort_values()
    if len(timestamps) < 2:
        return 0.0
    return float(timestamps.diff().dropna().dt.total_seconds().median() / 60)


def smoothness_stats(weather: pd.DataFrame) -> dict[str, float]:
    """Summarize hourly weather smoothness from first differences."""
    numeric_cols = [
        col
        for col in ["temperature_2m", "relative_humidity_2m", "precipitation", "windspeed_10m"]
        if col in weather.columns
    ]
    stats: dict[str, float] = {}
    for col in numeric_cols:
        diff = weather[col].astype(float).diff().abs().dropna()
        stats[f"{col}_median_abs_hourly_change"] = float(diff.median())
        stats[f"{col}_p95_abs_hourly_change"] = float(diff.quantile(0.95))
    return stats


def time_cycle_stats(gold: pd.DataFrame) -> dict[str, float]:
    """Measure how strongly average load varies by hour."""
    if not {"NSM", "Usage_kWh"}.issubset(gold.columns):
        return {}
    hourly = gold.assign(hour=(gold["NSM"] / 3600).round(2)).groupby("hour")["Usage_kWh"].mean()
    return {
        "hourly_usage_mean_min": float(hourly.min()),
        "hourly_usage_mean_max": float(hourly.max()),
        "hourly_usage_mean_range": float(hourly.max() - hourly.min()),
    }


def physical_zero_stats(gold: pd.DataFrame) -> dict[str, float]:
    """Summarize zero-heavy reactive power and low power-factor behavior."""
    stats: dict[str, float] = {}
    if "Leading_Current_Reactive_Power_kVarh" in gold.columns:
        leading = gold["Leading_Current_Reactive_Power_kVarh"].astype(float)
        stats["leading_reactive_zero_pct"] = float(leading.eq(0).mean() * 100)
    if "Lagging_Current_Reactive.Power_kVarh" in gold.columns:
        lagging = gold["Lagging_Current_Reactive.Power_kVarh"].astype(float)
        stats["lagging_reactive_zero_pct"] = float(lagging.eq(0).mean() * 100)
    if "Lagging_Current_Power_Factor" in gold.columns:
        pf = gold["Lagging_Current_Power_Factor"].astype(float)
        stats["lagging_pf_below_050_pct"] = float(pf.lt(0.50).mean() * 100)
    return stats


def build_decisions() -> dict[str, Any]:
    """Build EDA-backed decision records from project artifacts."""
    raw = read_csv(PATHS["raw"])
    weather = read_csv(PATHS["weather"], parse_date=True)
    gold = read_csv(PATHS["gold"], parse_date=True)
    pipeline = read_json(PATHS["pipeline"])
    gan = read_json(PATHS["gan"])
    ablation = read_json(PATHS["ablation"])

    raw_step = median_step_minutes(raw["date"])
    weather_time_col = "date" if "date" in weather.columns else "time"
    weather_step = median_step_minutes(weather[weather_time_col])
    smoothness = smoothness_stats(weather)
    time_stats = time_cycle_stats(gold)
    physical_stats = physical_zero_stats(gold)

    final_shape = pipeline.get("final_shape", list(gold.shape))
    anomaly_pct = float(pipeline.get("any_anomaly_pct", 0.0))
    anomaly_count = int(pipeline.get("n_any_anomaly", 0))
    forecast_best = ablation.get("forecast_best_by_rmse", [{}])[0]
    proxy_best = ablation.get("proxy_best_by_pr_auc", [{}])[0]

    return {
        "metrics": {
            "raw_rows": int(len(raw)),
            "raw_cols": int(raw.shape[1]),
            "raw_step_minutes": raw_step,
            "weather_rows": int(len(weather)),
            "weather_step_minutes": weather_step,
            "gold_rows": int(gold.shape[0]),
            "gold_cols": int(gold.shape[1]),
            "pipeline_final_shape": final_shape,
            "anomaly_any_count": anomaly_count,
            "anomaly_any_pct": anomaly_pct,
            **smoothness,
            **time_stats,
            **physical_stats,
            "gan_mean_error_pct": float(gan.get("mean_error_pct", 0.0)),
            "gan_std_error_pct": float(gan.get("std_error_pct", 0.0)),
            "gan_correlation_mae": float(gan.get("correlation_mae", 0.0)),
        },
        "decisions": [
            {
                "decision": "Resample weather hourly xuống 15 phút trước khi merge.",
                "eda_evidence": (
                    f"Dữ liệu điện có bước thời gian {raw_step:.0f} phút với {len(raw):,} dòng; "
                    f"weather có bước thời gian {weather_step:.0f} phút với {len(weather):,} dòng."
                ),
                "effect": "Đưa hai nguồn về cùng timestamp grid, giữ nguyên 35.040 dòng điện và tránh lệch hàng khi merge.",
            },
            {
                "decision": "Chọn linear interpolation cho weather.",
                "eda_evidence": (
                    "Các biến weather thay đổi tương đối trơn theo giờ; ví dụ median absolute hourly change "
                    f"temperature={smoothness.get('temperature_2m_median_abs_hourly_change', 0.0):.2f}, "
                    f"humidity={smoothness.get('relative_humidity_2m_median_abs_hourly_change', 0.0):.2f}."
                ),
                "effect": "Tạo giá trị 15 phút dễ kiểm toán, không dùng back-fill tương lai và không cần spline/MICE cho dữ liệu ngoại sinh đã đầy đủ.",
            },
            {
                "decision": "Tạo lag, rolling và sin/cos time features.",
                "eda_evidence": (
                    "Usage_kWh trung bình theo giờ biến thiên rõ; khoảng dao động hourly mean "
                    f"là {time_stats.get('hourly_usage_mean_range', 0.0):.2f} kWh."
                ),
                "effect": (
                    f"Ablation xác nhận RAW + TIME có RMSE thấp nhất "
                    f"({float(forecast_best.get('rmse', 0.0)):.4f}) cho forecasting 1 giờ."
                ),
            },
            {
                "decision": "Giữ zero reactive power như tín hiệu vật lý, không coi là missing thường.",
                "eda_evidence": (
                    f"Leading reactive zero chiếm {physical_stats.get('leading_reactive_zero_pct', 0.0):.2f}% "
                    f"và lagging PF < 0.50 chiếm {physical_stats.get('lagging_pf_below_050_pct', 0.0):.2f}%."
                ),
                "effect": "Các giá trị này hỗ trợ diễn giải tải cảm/kháng và tạo physical features/proxy rules có thể kiểm toán.",
            },
            {
                "decision": "Thử GAN augmentation cho lớp anomaly proxy.",
                "eda_evidence": f"anomaly_any có {anomaly_count:,} mẫu, chiếm {anomaly_pct:.3f}% toàn bộ dataset.",
                "effect": "GAN được dùng như baseline cân bằng lớp minority, không dùng làm bằng chứng lỗi thật.",
            },
            {
                "decision": "Giới hạn claim của GAN ở mức baseline augmentation.",
                "eda_evidence": (
                    f"GAN mean error={float(gan.get('mean_error_pct', 0.0)):.2f}%, "
                    f"std error={float(gan.get('std_error_pct', 0.0)):.2f}%, "
                    f"correlation MAE={float(gan.get('correlation_mae', 0.0)):.3f}."
                ),
                "effect": "Mean/std khá gần nhưng correlation còn lệch, nên không overclaim synthetic data thay thế dữ liệu thật.",
            },
            {
                "decision": "Bổ sung weather cho proxy risk prediction.",
                "eda_evidence": (
                    "Weather là ngữ cảnh ngoại sinh sau resampling; ablation full track cho thấy "
                    f"{proxy_best.get('config', 'A2_time_weather')} đạt PR-AUC "
                    f"{float(proxy_best.get('pr_auc', 0.0)):.4f}."
                ),
                "effect": "Weather nên được trình bày là contextual enrichment cho proxy labels, không phải nguyên nhân chắc chắn của lỗi.",
            },
        ],
    }


def write_outputs(result: dict[str, Any]) -> None:
    """Write JSON and Markdown reports for EDA-driven decisions."""
    PATHS["out_json"].parent.mkdir(parents=True, exist_ok=True)
    with PATHS["out_json"].open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    lines = [
        "# EDA-driven Design Decisions",
        "",
        "File này nối trực tiếp quan sát EDA với các quyết định tiền xử lý, feature engineering và GAN trong project.",
        "",
        "## Bảng quyết định",
        "",
        "| Quyết định | Bằng chứng EDA | Tác dụng |",
        "| --- | --- | --- |",
    ]
    for item in result["decisions"]:
        lines.append(f"| {item['decision']} | {item['eda_evidence']} | {item['effect']} |")
    lines.append("")
    lines.append("## Metrics nguồn")
    lines.append("")
    for key, value in result["metrics"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    PATHS["out_md"].write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Generate EDA decision-support artifacts."""
    result = build_decisions()
    write_outputs(result)
    print(f"Wrote {PATHS['out_md'].relative_to(ROOT)}")
    print(f"Wrote {PATHS['out_json'].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
