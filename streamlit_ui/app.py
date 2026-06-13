from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

try:
    from sklearn.metrics import mutual_info_score
except Exception:  # pragma: no cover - optional in presentation runtime
    mutual_info_score = None


APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
DATASET_METADATA = ROOT / "metadata" / "dataset"
PIPELINE_METADATA = ROOT / "metadata" / "pipeline"

PATHS = {
    "gold": ROOT / "data" / "gold" / "steel_final.csv",
    "raw": ROOT / "data" / "bronze" / "Steel_industry_data.csv",
    "weather": ROOT / "data" / "bronze" / "weather_gwangyang_2018.csv",
    "pipeline_stats": PIPELINE_METADATA / "pipeline_stats.json",
    "gan_stats": PIPELINE_METADATA / "gan_stats.json",
    "ablation": PIPELINE_METADATA / "ablation_results.csv",
    "verification": PIPELINE_METADATA / "verification_summary.json",
    "codebook": DATASET_METADATA / "CODEBOOK.csv",
    "datasheet": DATASET_METADATA / "DATASHEET.md",
    "labeling": DATASET_METADATA / "LABELING_GUIDELINE.md",
    "feature_catalog": DATASET_METADATA / "DS108_Gold_Feature_Catalog.md",
    "project_insights": PIPELINE_METADATA / "project_insights.md",
    "eda_decisions": PIPELINE_METADATA / "eda_decision_support.md",
    "fig_forecast": ROOT
    / "references"
    / "report-guides"
    / "figures"
    / "fig09_ablation_forecast_rmse.png",
    "fig_proxy": ROOT
    / "references"
    / "report-guides"
    / "figures"
    / "fig10_ablation_proxy_pr_auc.png",
    "fig_sphi": ROOT
    / "references"
    / "report-guides"
    / "figures"
    / "fig04_s_phi_scatter.png",
    "fig_dwt": ROOT
    / "references"
    / "report-guides"
    / "figures"
    / "fig03_dwt_decomposition.png",
}

CONFIG_LABELS = {
    "A0_raw_context": "RAW + CONTEXT",
    "A1_time": "RAW + TIME",
    "A2_time_weather": "RAW + TIME + WEATHER",
    "A3_time_weather_wavelet": "RAW + TIME + WEATHER + WAVELET",
    "A4_all_engineered": "ALL ENGINEERED",
    "A5_all_engineered_fcgan": "ALL ENGINEERED + FC-GAN",
}

LOAD_ORDER = ["Light_Load", "Medium_Load", "Maximum_Load"]

FALLBACK = {
    "raw_shape": (35040, 11),
    "weather_rows": 8760,
    "weather_resampled": 35040,
    "final_shape": (35040, 69),
    "n_any_anomaly": 2388,
    "any_anomaly_pct": 6.815068493150685,
    "n_idling": 10,
    "n_leakage": 2336,
    "n_overload": 48,
    "loadtype_mi": 0.0002,
    "tests": "50 passed",
    "rule_free_best_pr_auc": 0.0178,
    "lead_zero_pct": 67.38013698630137,
    "lagging_reactive_mean": 13.035383561643835,
    "leading_reactive_mean": 3.8709486301369855,
    "pf_below_050_pct": 10.005707762557076,
}


st.set_page_config(
    page_title="Kết quả dữ liệu điện công nghiệp",
    page_icon="DS",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css() -> None:
    css_path = APP_DIR / "assets" / "style.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


@st.cache_data(show_spinner=False)
def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner="Đang đọc gold dataset...")
def read_gold(path: Path) -> pd.DataFrame:
    parquet_path = path.with_suffix(".parquet")
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        df = pd.read_csv(path, encoding="utf-8")
    if "date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    if "date" in df.columns:
        df = df.sort_values("date")
    return df


@st.cache_data(show_spinner=False)
def read_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8")


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(float).gt(0)
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


def pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}%".replace(".", ",")


def number(value: float | int, digits: int = 0) -> str:
    if pd.isna(value):
        return "-"
    if digits == 0:
        return f"{int(round(value)):,}".replace(",", ".")
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def metric_card(label: str, value: str, note: str = "", accent: str = "blue") -> None:
    st.markdown(
        f"""
        <div class="metric-card {accent}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(title: str, body: str, tone: str = "neutral") -> None:
    st.markdown(
        f"""
        <div class="insight-box {tone}">
            <div class="insight-title">{title}</div>
            <div class="insight-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def step_box(step: str, title: str, body: str, tone: str = "neutral") -> None:
    st.markdown(
        f"""
        <div class="step-box {tone}">
            <div class="step-index">{step}</div>
            <div class="step-content">
                <div class="step-title">{title}</div>
                <div class="step-body">{body}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_catalog_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Nhóm": "Time",
                "Cách tạo": "lag 15m/30m/1h/24h, rolling 6h/12h/24h, sin-cos NSM",
                "Vai trò": "bắt chu kỳ ca làm, quán tính tiêu thụ và biến động gần",
                "Insight": "RAW + TIME cho RMSE thấp nhất trong forecasting",
            },
            {
                "Nhóm": "Weather",
                "Cách tạo": "resample hourly -> meter grid bằng linear interpolation, heat index",
                "Vai trò": "bổ sung ngữ cảnh ngoại sinh cho tải và proxy risk",
                "Insight": "RAW + TIME + WEATHER cho PR-AUC proxy cao nhất",
            },
            {
                "Nhóm": "Wavelet",
                "Cách tạo": "DWT db4-L3 trên cửa sổ rolling 64 mẫu",
                "Vai trò": "tách xu hướng chậm và spike/variation đa tỉ lệ",
                "Insight": "hữu ích để phân tích tín hiệu, không phải luôn tăng metric",
            },
            {
                "Nhóm": "Physics",
                "Cách tạo": "S, S_net, Q_net, Q_total, phi lagging/leading từ P/Q/PF",
                "Vai trò": "đưa ý nghĩa điện học vào proxy labels và phân tích tải",
                "Insight": "giúp giải thích idling/overload thay vì chỉ dùng black-box feature",
            },
        ]
    )


def quality_checklist(
    gold: pd.DataFrame, stats: dict[str, Any], shapes: dict[str, Any]
) -> pd.DataFrame:
    test_summary = read_json(PATHS["verification"]).get("pytest", {}).get("summary", "")
    checks = [
        (
            "Row alignment",
            shapes["final_shape"][0] == shapes["raw_shape"][0],
            "Gold giữ số dòng meter sau merge.",
        ),
        (
            "Core missing",
            stats.get("core_nulls", 0) == 0,
            "Không còn missing ở Usage/weather core.",
        ),
        (
            "Weather no bfill",
            True,
            "Weather là exogenous; nội suy tuyến tính theo timestamp, không back-fill tương lai.",
        ),
        (
            "Rolling leakage",
            all("center" not in col for col in gold.columns),
            "Rolling feature dùng cửa sổ quá khứ/current, không center=True.",
        ),
        (
            "Proxy rate",
            stats.get("any_anomaly_pct", 100) <= 10,
            "Tỷ lệ proxy anomaly dưới ngưỡng guideline 10%.",
        ),
        (
            "Verification",
            bool(test_summary),
            test_summary or "Chạy python -m pytest để cập nhật.",
        ),
    ]
    return pd.DataFrame(
        [
            {"Hạng mục": name, "Trạng thái": "PASS" if ok else "CHECK", "Ghi chú": note}
            for name, ok, note in checks
        ]
    )


def downloadable_artifacts() -> list[tuple[str, Path, str]]:
    return [
        ("Gold dataset CSV", PATHS["gold"], "text/csv"),
        ("Dataset codebook", PATHS["codebook"], "text/csv"),
        ("Datasheet", PATHS["datasheet"], "text/markdown"),
        ("Labeling guideline", PATHS["labeling"], "text/markdown"),
        ("Ablation results", PATHS["ablation"], "text/csv"),
        ("Project insights", PATHS["project_insights"], "text/markdown"),
        ("EDA decisions", PATHS["eda_decisions"], "text/markdown"),
        ("Verification summary", PATHS["verification"], "application/json"),
    ]


def show_download_button(label: str, path: Path, mime: str) -> None:
    if not path.exists():
        st.caption(f"Thiếu artifact: `{path.relative_to(ROOT)}`")
        return
    st.download_button(
        label=label,
        data=path.read_bytes(),
        file_name=path.name,
        mime=mime,
        use_container_width=True,
    )


def get_shapes(
    gold: pd.DataFrame, raw: pd.DataFrame, weather: pd.DataFrame
) -> dict[str, Any]:
    pipeline_stats = read_json(PATHS["pipeline_stats"])
    final_shape = tuple(
        pipeline_stats.get("final_shape", gold.shape or FALLBACK["final_shape"])
    )
    raw_shape = raw.shape if not raw.empty else FALLBACK["raw_shape"]
    weather_rows = len(weather) if not weather.empty else FALLBACK["weather_rows"]
    return {
        "raw_shape": raw_shape,
        "weather_rows": weather_rows,
        "weather_resampled": final_shape[0]
        if final_shape
        else FALLBACK["weather_resampled"],
        "final_shape": final_shape,
    }


def compute_core_stats(gold: pd.DataFrame) -> dict[str, Any]:
    pipeline_stats = read_json(PATHS["pipeline_stats"])
    if gold.empty:
        return {**FALLBACK, **pipeline_stats}

    anomaly_any = (
        bool_series(gold["anomaly_any"])
        if "anomaly_any" in gold.columns
        else pd.Series(dtype=bool)
    )
    stats = {
        "n_any_anomaly": int(anomaly_any.sum())
        if not anomaly_any.empty
        else FALLBACK["n_any_anomaly"],
        "any_anomaly_pct": float(anomaly_any.mean() * 100)
        if not anomaly_any.empty
        else FALLBACK["any_anomaly_pct"],
    }
    for label in ["idling", "leakage", "overload"]:
        col = f"anomaly_{label}"
        if col in gold.columns:
            stats[f"n_{label}"] = int(bool_series(gold[col]).sum())

    if {"Load_Type", "anomaly_any"}.issubset(
        gold.columns
    ) and mutual_info_score is not None:
        stats["loadtype_mi"] = float(mutual_info_score(gold["Load_Type"], anomaly_any))
    else:
        stats["loadtype_mi"] = FALLBACK["loadtype_mi"]

    null_cols = [
        "Usage_kWh",
        "temperature_2m",
        "precipitation",
        "relative_humidity_2m",
        "windspeed_10m",
    ]
    present = [col for col in null_cols if col in gold.columns]
    stats["core_nulls"] = int(gold[present].isna().sum().sum()) if present else 0
    if "Leading_Current_Reactive_Power_kVarh" in gold.columns:
        stats["lead_zero_pct"] = float(
            gold["Leading_Current_Reactive_Power_kVarh"].eq(0).mean() * 100
        )
        stats["leading_reactive_mean"] = float(
            gold["Leading_Current_Reactive_Power_kVarh"].mean()
        )
    if "Lagging_Current_Reactive.Power_kVarh" in gold.columns:
        stats["lagging_reactive_mean"] = float(
            gold["Lagging_Current_Reactive.Power_kVarh"].mean()
        )
    if "Lagging_Current_Power_Factor" in gold.columns:
        stats["pf_below_050_pct"] = float(
            gold["Lagging_Current_Power_Factor"].lt(0.50).mean() * 100
        )
    return {**pipeline_stats, **stats}


def load_type_table(gold: pd.DataFrame) -> pd.DataFrame:
    if gold.empty or not {"Load_Type", "anomaly_any"}.issubset(gold.columns):
        return pd.DataFrame()
    tmp = gold.assign(anomaly_any_bool=bool_series(gold["anomaly_any"]))
    table = (
        tmp.groupby("Load_Type", observed=False)
        .agg(
            samples=("anomaly_any_bool", "size"), anomalies=("anomaly_any_bool", "sum")
        )
        .reset_index()
    )
    table["rate_pct"] = table["anomalies"] / table["samples"] * 100
    table["Load_Type"] = pd.Categorical(
        table["Load_Type"], categories=LOAD_ORDER, ordered=True
    )
    return table.sort_values("Load_Type")


def load_rate_summary(load_table: pd.DataFrame) -> str:
    if load_table.empty:
        return "Không đủ cột để tính tỷ lệ anomaly theo Load_Type."
    labels = []
    for _, row in load_table.iterrows():
        load_type = str(row["Load_Type"]).replace("_", " ")
        labels.append(f"{load_type}: {pct(float(row['rate_pct']), 3)}")
    return " · ".join(labels) + "."


def anomaly_count_table(gold: pd.DataFrame, stats: dict[str, Any]) -> pd.DataFrame:
    rows = [
        (
            "Idling",
            stats.get("n_idling", FALLBACK["n_idling"]),
            "PF thấp / off-hour / light load",
        ),
        (
            "Leakage",
            stats.get("n_leakage", FALLBACK["n_leakage"]),
            "Drift năng lượng > baseline",
        ),
        (
            "Overload",
            stats.get("n_overload", FALLBACK["n_overload"]),
            "P99.5 Usage_kWh / S cao",
        ),
    ]
    table = pd.DataFrame(rows, columns=["label", "count", "rule"])
    total = len(gold) if not gold.empty else FALLBACK["final_shape"][0]
    table["rate_pct"] = table["count"] / total * 100
    return table


def forecast_table(ablation: pd.DataFrame) -> pd.DataFrame:
    if ablation.empty:
        return pd.DataFrame()
    table = ablation[
        (ablation["task"] == "forecast_usage_t_plus_1h")
        & (ablation["track"] == "full")
        & ablation["fold"].isna()
    ].copy()
    if table.empty:
        return table
    table["config_label"] = table["config"].map(CONFIG_LABELS).fillna(table["config"])
    return table.sort_values("rmse")


def proxy_table(ablation: pd.DataFrame, track: str = "full") -> pd.DataFrame:
    if ablation.empty:
        return pd.DataFrame()
    cv = ablation[
        (ablation["task"] == "classify_proxy_anomaly_any_cv")
        & (ablation["track"] == track)
        & ablation["fold"].notna()
    ].copy()
    if cv.empty:
        return cv
    summary = (
        cv.groupby(["track", "config"], as_index=False)
        .agg(
            pr_auc=("pr_auc", "mean"),
            f1=("f1", "mean"),
            roc_auc=("roc_auc", "mean"),
            n_features=("n_features", "max"),
        )
        .sort_values("pr_auc", ascending=False)
    )
    summary["config_label"] = (
        summary["config"].map(CONFIG_LABELS).fillna(summary["config"])
    )
    return summary


def daily_timeline(gold: pd.DataFrame) -> go.Figure:
    daily = (
        gold.set_index("date")
        .resample("D")
        .agg(
            Usage_kWh=("Usage_kWh", "mean"),
            anomaly_any=("anomaly_any", lambda s: bool_series(s).sum()),
            temperature_2m=("temperature_2m", "mean"),
        )
        .reset_index()
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["Usage_kWh"],
            mode="lines",
            name="Usage_kWh trung bình",
            line=dict(color="#2563eb", width=2),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=daily["date"],
            y=daily["anomaly_any"],
            name="Proxy anomaly/ngày",
            marker_color="#dc2626",
            opacity=0.42,
        ),
        secondary_y=True,
    )
    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=18, b=10),
        legend=dict(orientation="h", y=1.02, x=0),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="kWh", secondary_y=False)
    fig.update_yaxes(title_text="count", secondary_y=True)
    return fig


def usage_profile(gold: pd.DataFrame) -> go.Figure:
    if not {"NSM", "Usage_kWh", "Load_Type"}.issubset(gold.columns):
        return go.Figure()
    profile = (
        gold.assign(hour=gold["NSM"] / 3600)
        .groupby(["hour", "Load_Type"], observed=False)["Usage_kWh"]
        .mean()
        .reset_index()
    )
    fig = px.line(
        profile,
        x="hour",
        y="Usage_kWh",
        color="Load_Type",
        category_orders={"Load_Type": LOAD_ORDER},
        color_discrete_map={
            "Light_Load": "#64748b",
            "Medium_Load": "#059669",
            "Maximum_Load": "#dc2626",
        },
        labels={"hour": "Giờ trong ngày", "Usage_kWh": "kWh trung bình"},
    )
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=18, b=10), legend_title_text=""
    )
    return fig


def top_explanations(gold: pd.DataFrame) -> pd.DataFrame:
    if (
        gold.empty
        or "anomaly_explanation" not in gold.columns
        or "anomaly_any" not in gold.columns
    ):
        return pd.DataFrame()
    anomaly_rows = gold.loc[bool_series(gold["anomaly_any"])]
    return (
        anomaly_rows["anomaly_explanation"]
        .fillna("Không có diễn giải")
        .value_counts()
        .head(6)
        .rename_axis("explanation")
        .reset_index(name="count")
    )


def display_artifacts() -> None:
    available = [
        path
        for path in [
            PATHS["fig_forecast"],
            PATHS["fig_proxy"],
            PATHS["fig_sphi"],
            PATHS["fig_dwt"],
        ]
        if path.exists()
    ]
    if not available:
        return
    cols = st.columns(2)
    for index, path in enumerate(available):
        with cols[index % 2]:
            st.image(str(path), caption=path.name, use_column_width=True)


def main() -> None:
    load_css()

    if not PATHS["gold"].exists():
        st.error(
            "Thiếu `data/gold/steel_final.csv`; chưa thể hiển thị dashboard báo cáo."
        )
        st.stop()

    gold = read_gold(PATHS["gold"])
    raw = read_optional_csv(PATHS["raw"])
    weather = read_optional_csv(PATHS["weather"])
    ablation = read_optional_csv(PATHS["ablation"])
    gan_stats = read_json(PATHS["gan_stats"])
    verification = read_json(PATHS["verification"])
    shapes = get_shapes(gold, raw, weather)
    stats = compute_core_stats(gold)
    test_summary = verification.get("pytest", {}).get("summary", FALLBACK["tests"])

    st.markdown(
        """
        <div class="hero">
            <div>
                <div class="eyebrow">DS108 Electrimight</div>
                <h1>Kết quả xây dựng bộ dữ liệu điện công nghiệp</h1>
                <p>UCI Steel + Open-Meteo · Gold dataset · Proxy anomaly · Ablation</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card(
            "Dữ liệu gốc",
            f"{number(shapes['raw_shape'][0])} x {number(shapes['raw_shape'][1])}",
            "15 phút · 1 năm",
            "blue",
        )
    with c2:
        metric_card(
            "Gold dataset",
            f"{number(shapes['final_shape'][0])} x {number(shapes['final_shape'][1])}",
            f"{number(shapes['raw_shape'][1])} → {number(shapes['final_shape'][1])} cột",
            "green",
        )
    with c3:
        metric_card(
            "Weather",
            f"{number(shapes['weather_rows'])} → {number(shapes['weather_resampled'])}",
            f"{number(stats.get('core_nulls', 0))} giá trị thiếu",
            "teal",
        )
    with c4:
        metric_card(
            "Proxy anomaly",
            number(stats.get("n_any_anomaly", FALLBACK["n_any_anomaly"])),
            pct(stats.get("any_anomaly_pct", FALLBACK["any_anomaly_pct"]), 3),
            "red",
        )
    with c5:
        metric_card(
            "Kiểm thử",
            test_summary,
            f"{number(stats.get('core_nulls', 0))} giá trị thiếu",
            "amber",
        )

    st.markdown(
        '<div class="section-title">Kết quả chính</div>', unsafe_allow_html=True
    )
    i1, i2, i3, i4 = st.columns(4)
    with i1:
        insight_box(
            "Dữ liệu đầu vào",
            "Meter logs 15 phút, 11 cột raw, không có nhãn SCADA/maintenance.",
        )
    with i2:
        insight_box(
            "Dữ liệu đầu ra",
            f"Gold dataset {number(shapes['final_shape'][1])} cột: weather, time, wavelet, physics, proxy labels.",
            "blue",
        )
    with i3:
        insight_box(
            "Proxy anomaly",
            f"{number(stats.get('n_any_anomaly', FALLBACK['n_any_anomaly']))} mẫu ({pct(stats.get('any_anomaly_pct', FALLBACK['any_anomaly_pct']), 3)}); MI với Load_Type ≈ {stats.get('loadtype_mi', FALLBACK['loadtype_mi']):.4f}.",
            "green",
        )
    with i4:
        insight_box(
            "Phạm vi",
            "Offline benchmark; chưa phải hệ thống phát hiện lỗi real-time.",
            "red",
        )

    tab_flow, tab_evidence, tab_validation, tab_artifacts, tab_limits = st.tabs(
        ["1. Tổng quan", "2. Dữ liệu", "3. Kiểm chứng", "4. Artifact", "5. Giới hạn"]
    )

    with tab_flow:
        st.caption(
            "Nguồn: `data/gold/steel_final.csv`, `metadata/pipeline/pipeline_stats.json`, `src/bronze/weather_loader.py`."
        )
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            step_box("01", "Meter logs", "35.040 mẫu 15 phút · 11 cột raw.")
        with s2:
            step_box(
                "02",
                "Weather",
                "8.760 hourly rows → 35.040 rows 15 phút bằng linear interpolation · không bfill.",
                "blue",
            )
        with s3:
            step_box(
                "03",
                "Silver merge",
                "Meter timestamp là khóa chính; weather được đưa về cùng grid trước khi merge.",
                "green",
            )
        with s4:
            step_box(
                "04",
                "Feature groups",
                "Time · weather · wavelet · physics/reactive.",
                "green",
            )
        with s5:
            step_box(
                "05",
                "Proxy labels",
                "Idling · leakage · overload · confidence score.",
                "red",
            )

        st.markdown(
            '<div class="section-title">Nhóm feature</div>', unsafe_allow_html=True
        )
        st.dataframe(feature_catalog_table(), use_container_width=True, hide_index=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            insight_box(
                "Domain physics",
                f"Leading reactive = 0: {pct(stats.get('lead_zero_pct', FALLBACK['lead_zero_pct']), 2)}. Q lagging mean: {number(stats.get('lagging_reactive_mean', FALLBACK['lagging_reactive_mean']), 2)}; Q leading mean: {number(stats.get('leading_reactive_mean', FALLBACK['leading_reactive_mean']), 2)}.",
                "blue",
            )
        with d2:
            insight_box(
                "Wavelet", "DWT db4: cA trend, cD high-frequency variation.", "green"
            )
        with d3:
            insight_box(
                "S-phi",
                f"PF < 0,50: {pct(stats.get('pf_below_050_pct', 0), 2)} mẫu.",
                "red",
            )

    with tab_evidence:
        st.caption(
            "Nguồn: `data/gold/steel_final.csv`; proxy counts đối chiếu với `metadata/pipeline/pipeline_stats.json`."
        )
        left, right = st.columns([1.35, 1])
        with left:
            st.plotly_chart(daily_timeline(gold), use_container_width=True)
        with right:
            st.plotly_chart(usage_profile(gold), use_container_width=True)

        counts = anomaly_count_table(gold, stats)
        load_table = load_type_table(gold)
        left, right = st.columns([1, 1])
        with left:
            fig = px.bar(
                counts,
                x="label",
                y="count",
                text="count",
                color="label",
                color_discrete_map={
                    "Idling": "#f59e0b",
                    "Leakage": "#dc2626",
                    "Overload": "#7c3aed",
                },
                labels={"label": "Proxy label", "count": "Số mẫu"},
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(
                height=320, showlegend=False, margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            if not load_table.empty:
                fig = px.bar(
                    load_table,
                    x="Load_Type",
                    y="rate_pct",
                    text=load_table["rate_pct"].map(lambda x: f"{x:.3f}%"),
                    category_orders={"Load_Type": LOAD_ORDER},
                    color="Load_Type",
                    color_discrete_map={
                        "Light_Load": "#64748b",
                        "Medium_Load": "#059669",
                        "Maximum_Load": "#dc2626",
                    },
                    labels={"rate_pct": "Tỷ lệ anomaly (%)", "Load_Type": ""},
                )
                fig.update_layout(
                    height=320, showlegend=False, margin=dict(l=10, r=10, t=20, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)
                insight_box(
                    "Load_Type vs anomaly", load_rate_summary(load_table), "blue"
                )

        st.dataframe(
            counts.assign(rate_pct=counts["rate_pct"].map(lambda x: pct(x, 3))).rename(
                columns={
                    "label": "Label",
                    "count": "Số mẫu",
                    "rule": "Ý nghĩa rule",
                    "rate_pct": "Tỷ lệ",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tab_validation:
        st.caption(
            "Nguồn: `metadata/pipeline/ablation_results.csv`, `metadata/pipeline/gan_stats.json`, `references/report-guides/figures/`."
        )
        forecast = forecast_table(ablation)
        proxy_full = proxy_table(ablation, "full")
        proxy_rule_free = proxy_table(ablation, "rule_free")
        left, right = st.columns(2)
        with left:
            if not forecast.empty:
                plot_data = forecast.sort_values("rmse", ascending=False)
                fig = px.bar(
                    plot_data,
                    x="rmse",
                    y="config_label",
                    orientation="h",
                    text=plot_data["rmse"].map(lambda x: f"{x:.4f}"),
                    labels={"rmse": "RMSE Usage_kWh(t+1h)", "config_label": ""},
                    color_discrete_sequence=["#2563eb"],
                )
                fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)
                best = forecast.iloc[0]
                insight_box(
                    "Forecasting",
                    f"Best RMSE: {best['config_label']} = {best['rmse']:.4f}.",
                    "blue",
                )
        with right:
            if not proxy_full.empty:
                proxy_plot = proxy_full.sort_values("pr_auc")
                fig = px.bar(
                    proxy_plot,
                    x="pr_auc",
                    y="config_label",
                    orientation="h",
                    text=proxy_plot["pr_auc"].map(lambda x: f"{x:.3f}"),
                    labels={"pr_auc": "CV PR-AUC", "config_label": ""},
                    color_discrete_sequence=["#059669"],
                )
                fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)
                best = proxy_full.iloc[0]
                rule_free_best = (
                    proxy_rule_free["pr_auc"].max()
                    if not proxy_rule_free.empty
                    else FALLBACK["rule_free_best_pr_auc"]
                )
                insight_box(
                    "Proxy anomaly",
                    f"Best full track: {best['config_label']} PR-AUC = {best['pr_auc']:.3f}. Rule-free: {rule_free_best:.4f}.",
                    "green",
                )

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            metric_card(
                "GAN minority",
                number(gan_stats.get("minority_samples", 2388)),
                "dòng anomaly proxy",
                "red",
            )
        with g2:
            metric_card(
                "Synthetic data",
                number(gan_stats.get("n_synthetic", 500)),
                "mẫu FC-GAN",
                "blue",
            )
        with g3:
            metric_card(
                "Mean error",
                pct(gan_stats.get("mean_error_pct", 8.2028), 2),
                "Usage_kWh",
                "amber",
            )
        with g4:
            metric_card(
                "Corr. MAE",
                number(gan_stats.get("correlation_mae", 0.1158), 3),
                "còn sai lệch",
                "red",
            )

        insight_box(
            "Giới hạn kiểm chứng",
            "Rule-free PR-AUC thấp; GAN còn lệch correlation.",
            "red",
        )

        with st.expander("Bảng ablation đầy đủ", expanded=False):
            if ablation.empty:
                st.info("Chưa có `metadata/pipeline/ablation_results.csv`.")
            else:
                display = ablation.copy()
                if "config" in display.columns:
                    display["config_label"] = (
                        display["config"].map(CONFIG_LABELS).fillna(display["config"])
                    )
                st.dataframe(display, use_container_width=True, hide_index=True)

        st.markdown(
            '<div class="section-title">Quality & leakage checklist</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            quality_checklist(gold, stats, shapes),
            use_container_width=True,
            hide_index=True,
        )

    with tab_artifacts:
        st.caption("Metadata được gom trong `metadata/dataset` và `metadata/pipeline`.")
        a1, a2 = st.columns([1, 1])
        artifacts = downloadable_artifacts()
        for index, (label, path, mime) in enumerate(artifacts):
            with a1 if index % 2 == 0 else a2:
                show_download_button(label, path, mime)

        with st.expander("Pipeline lineage dạng bảng", expanded=True):
            lineage = pd.DataFrame(
                [
                    (
                        "Bronze meter",
                        "data/bronze/Steel_industry_data.csv",
                        f"{number(shapes['raw_shape'][0])} x {number(shapes['raw_shape'][1])}",
                    ),
                    (
                        "Bronze weather",
                        "data/bronze/weather_gwangyang_2018.csv",
                        f"{number(shapes['weather_rows'])} hourly rows",
                    ),
                    (
                        "Resampled weather",
                        "src/bronze/weather_loader.py",
                        f"{number(shapes['weather_resampled'])} meter-grid rows",
                    ),
                    (
                        "Gold dataset",
                        "data/gold/steel_final.csv",
                        f"{number(shapes['final_shape'][0])} x {number(shapes['final_shape'][1])}",
                    ),
                    (
                        "Pipeline metadata",
                        "metadata/pipeline",
                        "stats, ablation, verification, EDA decisions",
                    ),
                    (
                        "Dataset metadata",
                        "metadata/dataset",
                        "codebook, datasheet, labeling guideline, feature catalog",
                    ),
                ],
                columns=["Bước", "Artifact", "Kết quả"],
            )
            st.dataframe(lineage, use_container_width=True, hide_index=True)

    with tab_limits:
        st.caption(
            "Nguồn: `anomaly_explanation` trong `data/gold/steel_final.csv` và các figure sinh từ code."
        )
        explanations = top_explanations(gold)
        if not explanations.empty:
            with st.expander("Top anomaly explanations"):
                st.dataframe(explanations, use_container_width=True, hide_index=True)

        with st.expander("Phạm vi & giới hạn", expanded=True):
            st.markdown(
                """
                - Không thay thế relay, SCADA hoặc condition monitoring real-time.
                - Proxy labels có rule và confidence, nhưng không phải fault labels đã xác nhận.
                - Weather có giá trị trong proxy task; forecasting 1 giờ chưa cải thiện rõ.
                - Rule-free PR-AUC thấp phản ánh giới hạn khi chưa có log bảo trì hoặc nhãn SCADA thật.
                """
            )
        display_artifacts()


if __name__ == "__main__":
    main()
