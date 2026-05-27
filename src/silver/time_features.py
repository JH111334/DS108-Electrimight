"""
Time-Domain Feature Engineering Module

Kỹ thuật biến đổi miền thời gian (Outlines §IV.1):
  - Lag Features: Quán tính tiêu thụ điện qua các độ trễ 15m, 30m, 1h, 24h
  - Rolling Statistics: Trung bình trượt, độ lệch chuẩn trượt, độ xiên trượt
  - Trigonometric Encoding: Mã hóa sin/cos cho biến NSM (chu kỳ ngày)

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục 1 (Time-Domain).
"""

import numpy as np
import pandas as pd


# ── Lag Features ────────────────────────────────────────────────────

def create_lag_features(
    df: pd.DataFrame,
    col: str = "Usage_kWh",
    lags: list = None,
) -> pd.DataFrame:
    """
    Tạo các biến trễ (lag variables) cho một cột chuỗi thời gian.

    Dữ liệu có tần suất 15 phút, nên:
      - lag 1  = 15 phút trước
      - lag 2  = 30 phút trước
      - lag 4  = 1 giờ trước
      - lag 96 = 24 giờ trước

    Sự bất đồng bộ giữa t và t-k khi không đổi Load_Type
    là tín hiệu chỉ điểm cho sự cố khởi động thiết bị lỗi.

    Args:
        df: DataFrame đầu vào (đã sắp xếp theo thời gian).
        col: Tên cột cần tạo lag.
        lags: Danh sách các bước trễ. Mặc định [1, 2, 4, 96].

    Returns:
        DataFrame chứa các cột lag mới.
    """
    if lags is None:
        lags = [1, 2, 4, 96]

    lag_df = pd.DataFrame(index=df.index)
    for lag in lags:
        lag_df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return lag_df


# ── Rolling Window Statistics ───────────────────────────────────────

def create_rolling_features(
    df: pd.DataFrame,
    col: str = "Usage_kWh",
    windows: list = None,
) -> pd.DataFrame:
    """
    Tính toán thống kê cửa sổ trượt (rolling window statistics).

    Cửa sổ mặc định (tính theo số bước 15 phút):
      - 24 bước = 6 giờ
      - 48 bước = 12 giờ
      - 96 bước = 24 giờ

    Đặc trưng: Rolling Mean, Rolling Std, Rolling Skewness.
    Độ lệch chuẩn trượt tăng vọt là dấu hiệu trước sự cố quá tải.

    Args:
        df: DataFrame đầu vào (đã sắp xếp theo thời gian).
        col: Tên cột cần tính rolling.
        windows: Danh sách kích thước cửa sổ. Mặc định [24, 48, 96].

    Returns:
        DataFrame chứa các cột rolling mới.
    """
    if windows is None:
        windows = [24, 48, 96]

    roll_df = pd.DataFrame(index=df.index)
    for w in windows:
        roll_df[f"{col}_rmean_{w}"] = df[col].rolling(w, min_periods=1).mean()
        roll_df[f"{col}_rstd_{w}"] = df[col].rolling(w, min_periods=1).std()
        roll_df[f"{col}_rskew_{w}"] = df[col].rolling(w, min_periods=1).skew()
    return roll_df


# ── Trigonometric Temporal Encoding ─────────────────────────────────

def encode_nsm_cyclical(df: pd.DataFrame, col: str = "NSM") -> pd.DataFrame:
    """
    Mã hóa chu kỳ lượng giác cho biến NSM (Number of Seconds from Midnight).

    NSM chạy từ 0 → 86400, tạo ra sự gián đoạn giả tại nửa đêm.
    Ánh xạ sang hệ tọa độ tròn:
        NSM_sin = sin(2π × NSM / 86400)
        NSM_cos = cos(2π × NSM / 86400)

    Đảm bảo mô hình hiểu rằng 23:59 và 00:01 chỉ cách nhau 2 phút.

    Args:
        df: DataFrame chứa cột NSM.
        col: Tên cột NSM. Mặc định "NSM".

    Returns:
        DataFrame chứa 2 cột: NSM_sin, NSM_cos.
    """
    cyc_df = pd.DataFrame(index=df.index)
    seconds_in_day = 86400
    cyc_df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / seconds_in_day)
    cyc_df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / seconds_in_day)
    return cyc_df


# ── Orchestrator ────────────────────────────────────────────────────

def build_time_features(
    df: pd.DataFrame,
    target_col: str = "Usage_kWh",
) -> pd.DataFrame:
    """
    Tổng hợp tất cả đặc trưng miền thời gian vào DataFrame gốc.

    Gọi tuần tự: lag → rolling → trig encoding, rồi nối (concat) kết quả.

    Args:
        df: DataFrame đầu vào (đã sắp xếp theo thời gian).
        target_col: Cột mục tiêu cho lag & rolling. Mặc định "Usage_kWh".

    Returns:
        DataFrame mới = df gốc + tất cả đặc trưng thời gian.
    """
    parts = [df]

    parts.append(create_lag_features(df, col=target_col))
    parts.append(create_rolling_features(df, col=target_col))

    if "NSM" in df.columns:
        parts.append(encode_nsm_cyclical(df))

    return pd.concat(parts, axis=1)
