"""
Weather Data Integration Module

Tải, xử lý và tích hợp dữ liệu thờ tiết Gwangyang (Hàn Quốc) vào bộ dữ liệu
ngành thép. Dữ liệu thờ tiết từ Open-Meteo có tần suất 1 giờ, được nội suy
về 15 phút để khớp với dữ liệu điện năng.

Phân tích time alignment:
- Steel data: 35040 dòng, 15 phút, 2018-01-01 00:00 → 2018-12-31 23:45
- Weather data: 8760 dòng, 1 giờ, 2018-01-01 00:00 → 2018-12-31 23:00
- Weather kết thúc sớm hơn 45 phút → cần extrapolate 3 điểm cuối.
- Không có giờ thiếu trong weather data.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


# ── Load & Parse ────────────────────────────────────────────────────

def load_weather_data(csv_path: Path) -> pd.DataFrame:
    """
    Tải dữ liệu thờ tiết thô từ CSV.

    Args:
        csv_path: Đường dẫn đến CSV thờ tiết (cột 'time' ISO-8601).

    Returns:
        DataFrame với cột 'time' dạng datetime, làm index.
    """
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time").sort_index()
    return df


# ── Resample Hourly → 15-min ────────────────────────────────────────

def resample_weather_to_15min(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuyển dữ liệu thờ tiết từ tần suất 1 giờ → 15 phút.

    Strategy:
      1. Tạo full index 15 phút bao phủ toàn bộ năm 2018.
      2. Reindex và nội suy tuyến tính (linear interpolation).
         - Nội suy tuyến tính phù hợp vì các đại lượng khí tượng biến đổi
           liên tục theo thờ gian.
      3. Extrapolate 3 điểm cuối (sau 23:00 ngày 31/12) bằng limit_direction='both'.
      4. Không để lại NaN nào sau bước này.

    Args:
        df: DataFrame thờ tiết hourly với datetime index.

    Returns:
        DataFrame 15 phút, 35040 dòng (hoặc nhiều hơn nếu kéo dài hơn).
    """
    # Tạo index 15 phút cho toàn bộ 2018
    start = pd.Timestamp("2018-01-01 00:00:00")
    end = pd.Timestamp("2018-12-31 23:45:00")
    full_index = pd.date_range(start=start, end=end, freq="15min")

    df_15 = df.reindex(full_index)

    # Nội suy tuyến tính + extrapolate cho điểm ngoài rìa
    numeric_cols = df_15.select_dtypes(include=[np.number]).columns.tolist()
    df_15[numeric_cols] = df_15[numeric_cols].interpolate(
        method="linear", limit_direction="both"
    )

    # Đảm bảo không còn NaN
    if df_15.isnull().sum().sum() > 0:
        raise ValueError(
            f"Weather resampling còn {df_15.isnull().sum().sum()} NaN sau nội suy."
        )

    return df_15


# ── Derived Weather Features ────────────────────────────────────────

def _heat_index_rothfusz(t_c: float, rh: float) -> float:
    """
    Tính Heat Index (chỉ số nhiệt cảm nhận) theo công thức Rothfusz.

    Công thức gốc NOAA (T độ F, RH %):
    HI = -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH
         - 6.83783e-3*T^2 - 5.481717e-2*RH^2 + 1.22874e-3*T^2*RH
         + 8.5282e-4*T*RH^2 - 1.99e-6*T^2*RH^2

    Điều chỉnh đơn giản: nếu T < 26.7°C hoặc HI < T, trả về T.
    """
    if t_c < 26.7 or rh < 40:
        return t_c

    t_f = t_c * 9 / 5 + 32

    hi_f = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * rh
        - 0.22475541 * t_f * rh
        - 6.83783e-3 * t_f ** 2
        - 5.481717e-2 * rh ** 2
        + 1.22874e-3 * t_f ** 2 * rh
        + 8.5282e-4 * t_f * rh ** 2
        - 1.99e-6 * t_f ** 2 * rh ** 2
    )

    hi_c = (hi_f - 32) * 5 / 9
    return max(hi_c, t_c)


def build_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo các đặc trưng thờ tiết phái sinh.

    Các đặc trưng tạo ra:
      - temp_rolling_24h   : nhiệt độ trung bình 24h (mượt biến động ngày-đêm).
      - temp_diff_24h      : chênh lệch nhiệt so với cùng thờ điểm hôm trước.
      - heat_index         : chỉ số nhiệt cảm nhận Rothfusz (°C).
      - is_extreme_hot     : cờ nhiệt độ > phân vị 95.
      - is_extreme_cold    : cờ nhiệt độ < phân vị 05.
      - humidity_x_temp    : tương tác nhiệt-ẩm (proxy cho tải làm mát).
      - windspeed_rolling_6h: tốc độ gió trung bình 6h.

    Args:
        df: DataFrame 15 phút chứa cột gốc từ Open-Meteo.

    Returns:
        DataFrame mới = gốc + các cột đặc trưng phái sinh.
    """
    result = df.copy()

    # Rolling & diff (96 bước = 24h @ 15min)
    result["temp_rolling_24h"] = (
        result["temperature_2m"].rolling(window=96, min_periods=1).mean()
    )
    result["temp_diff_24h"] = result["temperature_2m"].diff(96)
    # Forward-fill 96 điểm đầu tiên (24h) vì không có dữ liệu trước 2018-01-01
    result["temp_diff_24h"] = result["temp_diff_24h"].ffill()
    # Nếu vẫn còn NaN (trường hợp edge case), fill bằng 0
    result["temp_diff_24h"] = result["temp_diff_24h"].fillna(0)

    # Heat Index (vectorized approximation)
    result["heat_index"] = result.apply(
        lambda row: _heat_index_rothfusz(
            row["temperature_2m"], row["relative_humidity_2m"]
        ),
        axis=1,
    )

    # Extreme temperature flags (based on full-year distribution)
    temp = result["temperature_2m"]
    p95 = temp.quantile(0.95)
    p05 = temp.quantile(0.05)
    result["is_extreme_hot"] = (temp > p95).astype(int)
    result["is_extreme_cold"] = (temp < p05).astype(int)

    # Interaction feature
    result["humidity_x_temp"] = (
        result["relative_humidity_2m"] * result["temperature_2m"]
    )

    # Wind rolling (24 bước = 6h @ 15min)
    result["windspeed_rolling_6h"] = (
        result["windspeed_10m"].rolling(window=24, min_periods=1).mean()
    )

    return result


# ── Merge with Steel Data ───────────────────────────────────────────

def merge_weather_with_steel(
    steel_df: pd.DataFrame,
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Gộp dữ liệu thép với dữ liệu thờ tiết đã xử lý.

    Strategy:
      - Left join trên cột 'date' (thép) và index của weather_df.
      - Đảm bảo số dòng không đổi so với steel_df.

    Args:
        steel_df: DataFrame thép đã qua cleaning, có cột 'date' datetime.
        weather_df: DataFrame thờ tiết 15 phút đã qua resample & feature engineering.

    Returns:
        DataFrame gộp, số dòng bằng steel_df.
    """
    steel = steel_df.copy()
    weather = weather_df.copy()

    # Đảm bảo cùng kiểu index để join
    weather = weather.reset_index().rename(columns={"index": "date"})

    merged = steel.merge(weather, on="date", how="left")

    if len(merged) != len(steel):
        raise ValueError(
            f"Merge làm thay đổi số dòng: steel={len(steel)}, merged={len(merged)}"
        )

    return merged


# ── Orchestrator ────────────────────────────────────────────────────

def integrate_weather(
    steel_df: pd.DataFrame,
    weather_csv: Path,
) -> Tuple[pd.DataFrame, dict]:
    """
    Pipeline mini cho việc tích hợp thờ tiết.

    Args:
        steel_df: DataFrame thép sau bước clean.
        weather_csv: Đường dẫn CSV thờ tiết gốc.

    Returns:
        Tuple (DataFrame gộp, report dict).
    """
    report = {}

    # 1. Load
    weather_raw = load_weather_data(weather_csv)
    report["weather_raw_shape"] = weather_raw.shape

    # 2. Resample
    weather_15 = resample_weather_to_15min(weather_raw)
    report["weather_resampled_shape"] = weather_15.shape

    # 3. Feature engineering
    weather_feat = build_weather_features(weather_15)
    report["weather_features_added"] = [
        col
        for col in weather_feat.columns
        if col not in weather_raw.columns
    ]

    # 4. Merge
    merged = merge_weather_with_steel(steel_df, weather_feat)
    report["merged_shape"] = merged.shape
    report["nulls_after_merge"] = int(merged.isnull().sum().sum())

    return merged, report
