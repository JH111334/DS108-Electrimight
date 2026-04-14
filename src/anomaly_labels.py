"""
Anomaly Labeling Module

Định nghĩa và gán nhãn các cơ chế bất thường vật lý trên tập dữ liệu
tiêu thụ điện năng ngành thép (Outlines §III):

  1. Idling (Chạy không tải kéo dài): Light Load + cuối tuần/đêm
     nhưng Usage_kWh cao bất thường + Power Factor thấp.
  2. Leakage (Rò rỉ năng lượng & Concept Drift): Gia tăng tiệm tiến
     của Usage_kWh ở cùng điều kiện vận hành qua các chu kỳ.
  3. Local Overload (Quá tải cục bộ): Xung Usage_kWh cực đại +
     bùng nổ reactive power + sụp đổ Power Factor.

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục III.
"""

import numpy as np
import pandas as pd


# ── Idling Detection ────────────────────────────────────────────────

def label_idling(df: pd.DataFrame) -> pd.Series:
    """
    Phát hiện hiện tượng chạy không tải kéo dài (Idling / Energy Waste).

    Điều kiện đồng thời:
      - Load_Type == "Light_Load"
      - WeekStatus == "Weekday" nhưng NSM thuộc khung đêm, HOẶC WeekStatus == "Weekend"
      - Usage_kWh > ngưỡng trung vị (duy trì cao bất thường)
      - Lagging_Current_Power_Factor < 0.5 (hiệu suất điện cực kém)

    Args:
        df: DataFrame chứa các cột: Load_Type, WeekStatus, NSM,
            Usage_kWh, Lagging_Current_Power_Factor.

    Returns:
        pd.Series boolean đánh dấu các điểm nghi ngờ idling.
    """
    is_light = df["Load_Type"] == "Light_Load"

    # Khung đêm: NSM < 21600 (trước 6h sáng) hoặc NSM > 75600 (sau 21h)
    is_night = (df["NSM"] < 21600) | (df["NSM"] > 75600)
    is_weekend = df["WeekStatus"] == "Weekend"
    is_off_hours = is_night | is_weekend

    usage_median = df["Usage_kWh"].median()
    is_high_usage = df["Usage_kWh"] > usage_median

    is_low_pf = df["Lagging_Current_Power_Factor"] < 0.5

    return is_light & is_off_hours & is_high_usage & is_low_pf


# ── Leakage / Concept Drift Detection ──────────────────────────────

def label_leakage(
    df: pd.DataFrame,
    window: int = 672,
    threshold_pct: float = 5.0,
) -> pd.Series:
    """
    Phát hiện rò rỉ năng lượng / trôi dạt khái niệm (Concept Drift).

    Nguyên lý: So sánh trung bình trượt dài hạn với trung bình tổng thể.
    Khi đường trung bình trượt vượt quá ngưỡng % so với mức cơ sở ban đầu
    (tuần đầu tiên), đó là dấu hiệu suy thoái hiệu suất tiệm tiến.

    Args:
        df: DataFrame chứa cột Usage_kWh (đã sắp xếp theo thời gian).
        window: Kích thước cửa sổ trượt (mặc định 672 = 1 tuần @ 15 min).
        threshold_pct: Ngưỡng tăng % so với baseline để đánh dấu leakage.

    Returns:
        pd.Series boolean đánh dấu các điểm nghi ngờ leakage.
    """
    rolling_mean = df["Usage_kWh"].rolling(window, min_periods=1).mean()

    # Baseline = trung bình tuần đầu tiên
    baseline = df["Usage_kWh"].iloc[:window].mean()

    pct_increase = (rolling_mean - baseline) / baseline * 100
    return pct_increase > threshold_pct


# ── Local Overload Detection ───────────────────────────────────────

def label_overload(
    df: pd.DataFrame,
    usage_multiplier: float = 3.0,
    pf_threshold: float = 0.7,
) -> pd.Series:
    """
    Phát hiện quá tải cục bộ (Local Overload & Extreme Point Anomalies).

    Điều kiện đồng thời:
      - Usage_kWh vượt IQR × multiplier (point anomaly)
      - Lagging_Current_Reactive.Power_kVarh cao bất thường (bão hòa từ)
      - Lagging_Current_Power_Factor sụp đổ dưới ngưỡng

    Args:
        df: DataFrame chứa các cột điện năng.
        usage_multiplier: Hệ số nhân IQR cho Usage_kWh. Mặc định 3.0.
        pf_threshold: Ngưỡng Power Factor dưới đó coi là sụp đổ.

    Returns:
        pd.Series boolean đánh dấu các điểm nghi ngờ overload.
    """
    # IQR-based outlier detection cho Usage_kWh
    Q1 = df["Usage_kWh"].quantile(0.25)
    Q3 = df["Usage_kWh"].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + usage_multiplier * IQR
    is_extreme_usage = df["Usage_kWh"] > upper_bound

    # Reactive power cũng phải cao bất thường
    q_col = "Lagging_Current_Reactive.Power_kVarh"
    Q1_q = df[q_col].quantile(0.25)
    Q3_q = df[q_col].quantile(0.75)
    IQR_q = Q3_q - Q1_q
    is_high_reactive = df[q_col] > (Q3_q + usage_multiplier * IQR_q)

    # Power Factor sụp đổ
    is_low_pf = df["Lagging_Current_Power_Factor"] < pf_threshold

    return is_extreme_usage & is_high_reactive & is_low_pf


# ── Orchestrator ────────────────────────────────────────────────────

def label_all_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gán tất cả nhãn bất thường vào DataFrame.

    Thêm 3 cột boolean:
      - anomaly_idling
      - anomaly_leakage
      - anomaly_overload

    Args:
        df: DataFrame đầy đủ (đã qua cleaning, có các cột điện năng).

    Returns:
        DataFrame mới = df gốc + 3 cột nhãn bất thường.
    """
    result = df.copy()
    result["anomaly_idling"] = label_idling(df)
    result["anomaly_leakage"] = label_leakage(df)
    result["anomaly_overload"] = label_overload(df)
    return result
