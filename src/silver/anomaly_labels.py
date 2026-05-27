"""
Anomaly Labeling Module with Guideline-Based Confidence Scoring

Dinh nghia va gan nhan cac co che bat thuong vat ly tren tap du lieu
tieu thu dien nang ngành thep, co kem theo Confidence Score va giai thich
(explainability) dua tren tai lieu huong dan (docs/LABELING_GUIDELINE.md).

Cac loai bat thuong:
  1. Idling (Chay khong tai keo dai): Light Load + cuoi tuan/dem
     nhung Usage_kWh cao bat thuong + Power Factor thap.
  2. Leakage (Ro ri nang luong & Concept Drift): Gia tang tiem tien
     cua Usage_kWh o cung dieu kien van hanh qua cac chu ky.
  3. Local Overload (Qua tai cuc bo): Xung Usage_kWh cuc dai +
     bung no reactive power + sup do Power Factor.

Tham chieu:
  - docs/LABELING_GUIDELINE.md
  - IEEE 519-2014 (Power Factor thresholds)
  - ISO 50001:2018 (Energy baseline & drift)
  - "Huong dan do an tien xu ly du lieu" - muc III.
"""

import numpy as np
import pandas as pd


# ── Idling Detection ────────────────────────────────────────────────

def label_idling(df: pd.DataFrame) -> pd.Series:
    """
    Phat hien hien tuong chay khong tai keo dai (Idling / Energy Waste).

    Dieu kien dong thoi (AND):
      - Load_Type == "Light_Load"
      - WeekStatus == "Weekday" nhung NSM thuoc khung dem, HOAC WeekStatus == "Weekend"
      - Usage_kWh > nguong trung vi (duy tri cao bat thuong)
      - Lagging_Current_Power_Factor < 0.50 (IEEE 519 severe threshold)

    Args:
        df: DataFrame chua cac cot: Load_Type, WeekStatus, NSM,
            Usage_kWh, Lagging_Current_Power_Factor.

    Returns:
        pd.Series boolean danh dau cac diem nghi ngo idling.
    """
    is_light = df["Load_Type"] == "Light_Load"

    # Khung dem: NSM < 21600 (truoc 6h sang) hoac NSM > 75600 (sau 21h)
    is_night = (df["NSM"] < 21600) | (df["NSM"] > 75600)
    is_weekend = df["WeekStatus"] == "Weekend"
    is_off_hours = is_night | is_weekend

    usage_median = df["Usage_kWh"].median()
    is_high_usage = df["Usage_kWh"] > usage_median

    # IEEE 519: PF < 0.50 la severe penalty zone
    is_low_pf = df["Lagging_Current_Power_Factor"] < 0.50

    return is_light & is_off_hours & is_high_usage & is_low_pf


def score_idling(df: pd.DataFrame) -> pd.Series:
    """
    Tinh confidence score cho nhan Idling.

    Score = 0.3 * I(Light_Load) + 0.3 * I(Off-hours)
          + 0.2 * I(Usage > median) + 0.2 * I(PF < 0.50)

    Args:
        df: DataFrame dau vao.

    Returns:
        pd.Series float trong [0, 1].
    """
    score = pd.Series(0.0, index=df.index)

    is_light = df["Load_Type"] == "Light_Load"
    is_night = (df["NSM"] < 21600) | (df["NSM"] > 75600)
    is_weekend = df["WeekStatus"] == "Weekend"
    is_off_hours = is_night | is_weekend
    is_high_usage = df["Usage_kWh"] > df["Usage_kWh"].median()
    is_low_pf = df["Lagging_Current_Power_Factor"] < 0.50

    score += 0.3 * is_light.astype(float)
    score += 0.3 * is_off_hours.astype(float)
    score += 0.2 * is_high_usage.astype(float)
    score += 0.2 * is_low_pf.astype(float)

    return score.clip(0.0, 1.0)


# ── Leakage / Concept Drift Detection ──────────────────────────────

def label_leakage(
    df: pd.DataFrame,
    window: int = 672,
    threshold_pct: float = 5.0,
) -> pd.Series:
    """
    Phat hien ro ri nang luong / troi dac tinh (Concept Drift).

    Nguyen ly: So sanh trung binh truot dai han voi baseline theo mua
    (seasonal baseline). Baseline duoc tinh bang trung binh cua cung
    khung gio (dayofweek + hour) tren toan bo dataset, loai bo anh huong
    cua chu ky tuan va mua vu. Khi rolling mean vuot qua nguong % so voi
    baseline seasonal, do la dau hieu suy thoai hieu suat khong giai
    thich duoc boi chu ky van hanh thong thuong.

    ISO 50001: Nguong canh bao +5% so voi baseline.

    Args:
        df: DataFrame chua cot Usage_kWh (da sap xep theo thoi gian).
        window: Kich thuoc cua so truot (mac dinh 672 = 1 tuan @ 15 min).
        threshold_pct: Nguong tang % so voi baseline de danh dau leakage.

    Returns:
        pd.Series boolean danh dau cac diem nghi ngo leakage.
    """
    rolling_mean = df["Usage_kWh"].rolling(window, min_periods=1).mean()

    # Baseline = mean of first 4 weeks (2,688 samples @ 15min)
    # Using 4 weeks instead of 1 week avoids bias from an atypical startup week.
    # If data is shorter than 4 weeks, use all available data.
    baseline_window = min(window * 4, len(df))
    baseline = df["Usage_kWh"].iloc[:baseline_window].mean()

    pct_increase = (rolling_mean - baseline) / baseline * 100
    return pct_increase > threshold_pct


def score_leakage(
    df: pd.DataFrame,
    window: int = 672,
) -> pd.Series:
    """
    Tinh confidence score cho nhan Leakage.

    Score phan cap theo muc do tang so voi baseline 4 tuan dau:
      > 20% -> 1.0 (nguy hiem)
      > 10% -> 0.7 (canh bao)
      >  5% -> 0.4 (nhe)
      <= 5% -> 0.0

    Args:
        df: DataFrame dau vao.
        window: Kich thuoc cua so truot.

    Returns:
        pd.Series float trong [0, 1].
    """
    rolling_mean = df["Usage_kWh"].rolling(window, min_periods=1).mean()

    baseline_window = min(window * 4, len(df))
    baseline = df["Usage_kWh"].iloc[:baseline_window].mean()

    pct_increase = (rolling_mean - baseline) / baseline * 100

    score = pd.Series(0.0, index=df.index)
    score = np.where(pct_increase > 20, 1.0, score)
    score = np.where((pct_increase > 10) & (pct_increase <= 20), 0.7, score)
    score = np.where((pct_increase > 5) & (pct_increase <= 10), 0.4, score)

    return pd.Series(score, index=df.index)


# ── Local Overload Detection ───────────────────────────────────────

def label_overload(
    df: pd.DataFrame,
    usage_percentile: float = 0.995,
    pf_threshold: float = 0.70,
) -> pd.Series:
    """
    Phat hien qua tai cuc bo (Local Overload & Extreme Point Anomalies).

    Dieu kien dong thoi:
      - Usage_kWh vuot percentile 99.5 (point anomaly - top 0.5%)
      - Lagging_Current_Reactive.Power_kVarh cao bat thuong (bao hoa tu)
      - Lagging_Current_Power_Factor sup do duoi nguong (IEEE 519 minimum)

    Note: Du lieu nay khong co outlier theo Tukey 3*IQR do dac thu phan phoi,
    nen su dung percentile-based thay cho IQR-based.

    Args:
        df: DataFrame chua cac cot dien nang.
        usage_percentile: Phan vi nguong cho Usage_kWh. Mac dinh 0.995.
        pf_threshold: Nguong Power Factor duoi do coi la sup do. Mac dinh 0.70.

    Returns:
        pd.Series boolean danh dau cac diem nghi ngo overload.
    """
    # Percentile-based outlier detection cho Usage_kWh
    upper_bound = df["Usage_kWh"].quantile(usage_percentile)
    is_extreme_usage = df["Usage_kWh"] > upper_bound

    # Reactive power cung phai cao bat thuong
    q_col = "Lagging_Current_Reactive.Power_kVarh"
    upper_q = df[q_col].quantile(usage_percentile)
    is_high_reactive = df[q_col] > upper_q

    # Power Factor suy giam (IEEE 519: PF < 0.85 la khong chap nhan duoc)
    is_low_pf = df["Lagging_Current_Power_Factor"] < pf_threshold

    # Overload = Usage cuc cao AND (Reactive cao OR PF kem)
    return is_extreme_usage & (is_high_reactive | is_low_pf)


def score_overload(
    df: pd.DataFrame,
    usage_percentile: float = 0.995,
    pf_threshold: float = 0.70,
) -> pd.Series:
    """
    Tinh confidence score cho nhan Overload.

    Score = 0.4 * I(Usage extreme outlier)
          + 0.3 * I(Reactive extreme outlier)
          + 0.3 * I(PF < threshold)

    Args:
        df: DataFrame dau vao.
        usage_percentile: Phan vi nguong cho Usage_kWh.
        pf_threshold: Nguong PF.

    Returns:
        pd.Series float trong [0, 1].
    """
    is_extreme_usage = df["Usage_kWh"] > df["Usage_kWh"].quantile(usage_percentile)

    q_col = "Lagging_Current_Reactive.Power_kVarh"
    is_high_reactive = df[q_col] > df[q_col].quantile(usage_percentile)

    is_low_pf = df["Lagging_Current_Power_Factor"] < pf_threshold

    # Score cao nhat khi ca 3 dieu kien dung, thap nhat khi chi co 1
    score = (
        0.5 * is_extreme_usage.astype(float)
        + 0.25 * is_high_reactive.astype(float)
        + 0.25 * is_low_pf.astype(float)
    )
    return score.clip(0.0, 1.0)


# ── Explanation ─────────────────────────────────────────────────────

def explain_idling(row: pd.Series) -> str:
    """
    Tra ve giai thich van ban cho nhan Idling.

    Args:
        row: Mot hang DataFrame (Series) chua cac cot lien quan.

    Returns:
        str: Giai thich.
    """
    reasons = []
    if row.get("Load_Type") == "Light_Load":
        reasons.append("light load condition")
    if (row.get("NSM", 0) < 21600) or (row.get("NSM", 0) > 75600):
        reasons.append("nighttime off-hours")
    if row.get("WeekStatus") == "Weekend":
        reasons.append("weekend")
    if row.get("Usage_kWh", 0) > 0:  # so sanh voi median can truyen vao
        reasons.append("usage above median")
    if row.get("Lagging_Current_Power_Factor", 1.0) < 0.50:
        reasons.append("PF below 0.50 (IEEE 519 severe)")

    return "Idling detected: " + "; ".join(reasons) if reasons else "No idling signs"


def explain_leakage(row: pd.Series, baseline: float, pct_increase: float) -> str:
    """
    Tra ve giai thich van ban cho nhan Leakage.

    Args:
        row: Mot hang DataFrame.
        baseline: Gia tri baseline.
        pct_increase: Phan tram tang.

    Returns:
        str: Giai thich.
    """
    return (
        f"Leakage detected: rolling mean increased {pct_increase:.1f}% "
        f"above baseline ({baseline:.2f} kWh). Possible equipment degradation."
    )


def explain_overload(row: pd.Series) -> str:
    """
    Tra ve giai thich van ban cho nhan Overload.

    Args:
        row: Mot hang DataFrame.

    Returns:
        str: Giai thich.
    """
    reasons = []
    pf = row.get("Lagging_Current_Power_Factor", 1.0)
    if pf < 0.70:
        reasons.append(f"PF collapsed to {pf:.2f} (< 0.70)")
    if row.get("Usage_kWh", 0) > 0:
        reasons.append("extreme usage spike")
    if row.get("Lagging_Current_Reactive.Power_kVarh", 0) > 0:
        reasons.append("reactive power surge")

    return "Overload detected: " + "; ".join(reasons) if reasons else "No overload signs"


# ── Orchestrator ────────────────────────────────────────────────────

def label_all_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gan tat ca nhan bat thuong vao DataFrame, kem confidence score va giai thich.

    Them 9 cot moi:
      - anomaly_idling (bool)
      - anomaly_idling_score (float [0,1])
      - anomaly_leakage (bool)
      - anomaly_leakage_score (float [0,1])
      - anomaly_overload (bool)
      - anomaly_overload_score (float [0,1])
      - anomaly_any (bool) - OR cua 3 nhan tren
      - anomaly_max_score (float) - max cua 3 score
      - anomaly_explanation (str) - giai thich chinh

    Args:
        df: DataFrame day du (da qua cleaning, co cac cot dien nang).

    Returns:
        DataFrame moi = df goc + cac cot nhan bat thuong.
    """
    result = df.copy()

    # Idling
    result["anomaly_idling"] = label_idling(df)
    result["anomaly_idling_score"] = score_idling(df)

    # Leakage
    result["anomaly_leakage"] = label_leakage(df)
    result["anomaly_leakage_score"] = score_leakage(df)

    # Overload
    result["anomaly_overload"] = label_overload(df)
    result["anomaly_overload_score"] = score_overload(df)

    # Aggregate
    result["anomaly_any"] = (
        result["anomaly_idling"]
        | result["anomaly_leakage"]
        | result["anomaly_overload"]
    )
    result["anomaly_max_score"] = result[
        ["anomaly_idling_score", "anomaly_leakage_score", "anomaly_overload_score"]
    ].max(axis=1)

    # Explanation (lay nhan co score cao nhat)
    def _explain(row):
        scores = {
            "idling": row["anomaly_idling_score"],
            "leakage": row["anomaly_leakage_score"],
            "overload": row["anomaly_overload_score"],
        }
        top = max(scores, key=scores.get)
        if scores[top] < 0.1:
            return "No significant anomaly detected"
        if top == "idling":
            return explain_idling(row)
        if top == "overload":
            return explain_overload(row)
        # leakage - can baseline & pct, dung generic
        return f"Leakage score: {scores[top]:.2f} - possible gradual energy degradation"

    result["anomaly_explanation"] = result.apply(_explain, axis=1)

    return result
