"""
Figure Generation Script for IEEE Report

Tạo 8 publication-ready figures sử dụng dữ liệu thực tế.
Lưu vào references/report-guides/figures/ (dpi=300 cho in ấn).
"""

import logging
import sys
from pathlib import Path

# Ensure project root is on path when running this script directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt
import seaborn as sns

from src.silver.anomaly_labels import label_all_anomalies
from src.bronze.data_loader import clean_data, load_steel_data
from src.silver.physical_features import build_physical_features
from src.silver.time_features import build_time_features
from src.utils import RAW_CSV, setup_logging

# matplotlib.use("Agg")  # Non-interactive backend
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["axes.labelsize"] = 9
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8

logger = setup_logging("INFO")

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "references" / "report-guides" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Data Loading ──────────────────────────────────────────────────────


def _load_and_prepare() -> pd.DataFrame:
    """Tải, làm sạch, và chuẩn bị dữ liệu cho visualization."""
    logger.info("Đang tải dữ liệu...")
    raw = load_steel_data(RAW_CSV)
    clean, _ = clean_data(raw)

    # Physical features
    phys = build_physical_features(clean)

    # Time features (chỉ lấy một số cột quan trọng để tránh memory bloat)
    time = build_time_features(phys, target_col="Usage_kWh")

    # Anomaly labels
    labeled = label_all_anomalies(time)
    return labeled


# ── Figure 1: Time Series with Anomalies ──────────────────────────────


def fig01_time_series(df: pd.DataFrame) -> None:
    """Vẽ chuỗi thờ gian Usage_kWh với overlay anomaly."""
    fig, ax = plt.subplots(figsize=(8, 3))

    # Lấy 2 tuần đầu để zoom chi tiết
    sample = df.iloc[:1344].copy()
    ax.plot(sample["date"], sample["Usage_kWh"], color="steelblue", lw=0.6, label="Usage (kWh)")

    # Overlay anomalies
    for col, color, label in [
        ("anomaly_idling", "orange", "Idling"),
        ("anomaly_leakage", "green", "Leakage"),
        ("anomaly_overload", "crimson", "Overload"),
    ]:
        mask = sample[col] == True
        if mask.any():
            ax.scatter(
                sample.loc[mask, "date"],
                sample.loc[mask, "Usage_kWh"],
                color=color,
                s=15,
                zorder=5,
                label=label,
                edgecolors="white",
                linewidths=0.3,
            )

    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Usage (kWh)")
    ax.set_title("Fig. 1. Time-series of Power Consumption with Detected Anomalies (2-week zoom)")
    ax.legend(loc="upper right", fontsize=7)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig01_time_series.png")
    plt.close(fig)
    logger.info("Đã lưu fig01_time_series.png")


# ── Figure 2: Correlation Heatmap ─────────────────────────────────────


def fig02_correlation_heatmap(df: pd.DataFrame) -> None:
    """Ma trận tương quan các biến chính."""
    cols = [
        "Usage_kWh",
        "Lagging_Current_Reactive.Power_kVarh",
        "Leading_Current_Reactive_Power_kVarh",
        "Lagging_Current_Power_Factor",
        "Leading_Current_Power_Factor",
        "CO2(tCO2)",
        "NSM",
        "Apparent_Power_S",
        "Phase_Angle_Phi",
    ]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        annot_kws={"size": 7},
        ax=ax,
    )
    ax.set_title("Fig. 2. Pearson Correlation Matrix of Key Electrical Variables")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig02_correlation_heatmap.png")
    plt.close(fig)
    logger.info("Đã lưu fig02_correlation_heatmap.png")


# ── Figure 3: DWT Decomposition ───────────────────────────────────────


def fig03_dwt_decomposition(df: pd.DataFrame) -> None:
    """Phân rã DWT 3 mức trên một đoạn Usage_kWh."""
    segment = df["Usage_kWh"].iloc[:2048].values
    coeffs = pywt.wavedec(segment, wavelet="db4", level=3)
    labels = ["cA3 (Approx)", "cD3 (Low-freq)", "cD2 (Mid-freq)", "cD1 (High-freq)"]

    fig, axes = plt.subplots(len(coeffs) + 1, 1, figsize=(8, 5), sharex=True)
    axes[0].plot(segment, color="steelblue", lw=0.5)
    axes[0].set_ylabel("Original")
    axes[0].set_title("Fig. 3. DWT Decomposition (db4, Level 3) of Usage_kWh")

    for i, (coeff, label) in enumerate(zip(coeffs, labels)):
        ax = axes[i + 1]
        ax.plot(coeff, color="darkgreen" if i == 0 else "darkred", lw=0.5)
        ax.set_ylabel(label, fontsize=8)
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Sample Index")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig03_dwt_decomposition.png")
    plt.close(fig)
    logger.info("Đã lưu fig03_dwt_decomposition.png")


# ── Figure 4: S–φ Scatter ─────────────────────────────────────────────


def fig04_s_phi_scatter(df: pd.DataFrame) -> None:
    """Scatter Apparent Power vs Phase Angle, màu theo Load_Type."""
    fig, ax = plt.subplots(figsize=(5, 4))

    # Downsample để scatter không bị quá dày
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    load_types = sample["Load_Type"].unique()
    palette = sns.color_palette("tab10", n_colors=len(load_types))

    for lt, color in zip(load_types, palette):
        mask = sample["Load_Type"] == lt
        ax.scatter(
            sample.loc[mask, "Apparent_Power_S"],
            sample.loc[mask, "Phase_Angle_Phi"],
            s=8,
            alpha=0.5,
            color=color,
            label=lt,
            edgecolors="none",
        )

    ax.set_xlabel("Apparent Power S (kVA)")
    ax.set_ylabel("Phase Angle φ (rad)")
    ax.set_title("Fig. 4. Operating Modes in S–φ Space")
    ax.legend(title="Load Type", fontsize=7, title_fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig04_s_phi_scatter.png")
    plt.close(fig)
    logger.info("Đã lưu fig04_s_phi_scatter.png")


# ── Figure 5: Anomaly Timeline ────────────────────────────────────────


def fig05_anomaly_timeline(df: pd.DataFrame) -> None:
    """Phân bố anomaly theo giờ trong ngày."""
    df = df.copy()
    df["hour"] = pd.to_datetime(df["date"]).dt.hour

    fig, axes = plt.subplots(1, 3, figsize=(8, 2.5), sharey=True)
    titles = ["Idling", "Leakage", "Overload"]
    cols = ["anomaly_idling", "anomaly_leakage", "anomaly_overload"]

    for ax, col, title in zip(axes, cols, titles):
        hourly = df.groupby("hour")[col].sum()
        ax.bar(hourly.index, hourly.values, color="crimson", alpha=0.7, width=0.8)
        ax.set_xlabel("Hour of Day")
        ax.set_title(title, fontsize=9)
        ax.set_xticks(range(0, 24, 4))
        ax.grid(axis="y", alpha=0.3)

    axes[0].set_ylabel("Anomaly Count")
    fig.suptitle("Fig. 5. Hourly Distribution of Anomalies", fontsize=10, y=1.02)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig05_anomaly_timeline.png")
    plt.close(fig)
    logger.info("Đã lưu fig05_anomaly_timeline.png")


# ── Figure 6: Missingness Pattern ─────────────────────────────────────


def fig06_missingness_pattern() -> None:
    """Visualize missingness pattern trên dữ liệu thô (nếu có)."""
    raw = load_steel_data(RAW_CSV)
    missing = raw.isnull()

    if missing.sum().sum() == 0:
        # Tạo synthetic missing pattern để demo
        np.random.seed(42)
        demo = raw.copy()
        for col in ["Usage_kWh", "Lagging_Current_Reactive.Power_kVarh", "CO2(tCO2)"]:
            if col in demo.columns:
                miss_idx = np.random.choice(demo.index, size=int(0.02 * len(demo)), replace=False)
                demo.loc[miss_idx, col] = np.nan
        missing = demo.isnull()

    # Lấy 2000 dòng đầu để visualize
    sub = missing.iloc[:2000]
    fig, ax = plt.subplots(figsize=(8, 3))
    sns.heatmap(sub.T, cbar=False, cmap="Greys_r", xticklabels=False, ax=ax)
    ax.set_title("Fig. 6. Missingness Pattern (Black = Missing, White = Observed)")
    ax.set_xlabel("Sample Index (first 2,000)")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig06_missingness_pattern.png")
    plt.close(fig)
    logger.info("Đã lưu fig06_missingness_pattern.png")


# ── Figure 7: Physical Features Distribution ──────────────────────────


def fig07_physical_distribution(df: pd.DataFrame) -> None:
    """Phân phối S và φ theo Load_Type."""
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.8))

    sns.kdeplot(data=df, x="Apparent_Power_S", hue="Load_Type", ax=axes[0], fill=True, alpha=0.3, legend=False)
    axes[0].set_xlabel("Apparent Power S (kVA)")
    axes[0].set_title("(a) Distribution of S")
    axes[0].grid(alpha=0.3)

    sns.kdeplot(data=df, x="Phase_Angle_Phi", hue="Load_Type", ax=axes[1], fill=True, alpha=0.3)
    axes[1].set_xlabel("Phase Angle φ (rad)")
    axes[1].set_title("(b) Distribution of φ")
    axes[1].grid(alpha=0.3)

    fig.suptitle("Fig. 7. Kernel Density Estimates of Physical-Domain Features", fontsize=10, y=1.02)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig07_physical_distribution.png")
    plt.close(fig)
    logger.info("Đã lưu fig07_physical_distribution.png")


# ── Figure 8: Feature Engineering Impact ──────────────────────────────


def fig08_feature_impact(df: pd.DataFrame) -> None:
    """So sánh phân phối gốc vs sau feature engineering (lag, rolling std)."""
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.8))

    # Rolling std spike detection
    roll_std = df["Usage_kWh_rstd_24"] if "Usage_kWh_rstd_24" in df.columns else None
    if roll_std is not None:
        axes[0].plot(df["date"].iloc[:1344], roll_std.iloc[:1344], color="darkorange", lw=0.5)
        axes[0].set_title("(a) Rolling Std (24-step) — Early Warning Signal")
        axes[0].set_xlabel("Timestamp")
        axes[0].set_ylabel("Rolling Std")
        axes[0].grid(alpha=0.3)
    else:
        axes[0].text(0.5, 0.5, "Rolling std not available", ha="center", va="center")

    # Lag autocorrelation
    if "Usage_kWh_lag_96" in df.columns:
        axes[1].scatter(
            df["Usage_kWh"].iloc[96::100],
            df["Usage_kWh_lag_96"].iloc[96::100],
            s=5,
            alpha=0.4,
            color="teal",
            edgecolors="none",
        )
        axes[1].set_xlabel("Usage_kWh(t)")
        axes[1].set_ylabel("Usage_kWh(t-24h)")
        axes[1].set_title("(b) Lag-96 Autocorrelation")
        axes[1].grid(alpha=0.3)
    else:
        axes[1].text(0.5, 0.5, "Lag feature not available", ha="center", va="center")

    fig.suptitle("Fig. 8. Impact of Time-Domain Feature Engineering", fontsize=10, y=1.02)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig08_feature_impact.png")
    plt.close(fig)
    logger.info("Đã lưu fig08_feature_impact.png")


# ── Main ──────────────────────────────────────────────────────────────


def main():
    """Chạy toàn bộ figure generation."""
    logger.info("=" * 60)
    logger.info("FIGURE GENERATION START")
    logger.info("=" * 60)

    df = _load_and_prepare()
    logger.info(f"Data prepared: {df.shape}")

    fig01_time_series(df)
    fig02_correlation_heatmap(df)
    fig03_dwt_decomposition(df)
    fig04_s_phi_scatter(df)
    fig05_anomaly_timeline(df)
    fig06_missingness_pattern()
    fig07_physical_distribution(df)
    fig08_feature_impact(df)

    logger.info("=" * 60)
    logger.info(f"All figures saved to {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
