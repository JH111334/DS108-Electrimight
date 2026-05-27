"""
Physical-Domain Feature Engineering Module

Tái cấu trúc đặc trưng vật lý điện năng (Outlines §IV.3):
  - Công suất biểu kiến (Apparent Power, S): S = √(P² + Q²)
  - Góc lệch pha (Phase Angle, φ): φ = arccos(Power Factor)

Ý nghĩa: Những biến phái sinh này bộc lộ các bất thường mà
công suất tác dụng (P) đơn lẻ không thể phát hiện — ví dụ
kẹt rô-to gây Q tăng vọt trong khi P không đổi, hoặc bão hòa từ
tính làm S phình to cấu trúc năng lượng.

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục 3 (Physical Domain).
"""

import numpy as np
import pandas as pd


# ── Apparent Power ──────────────────────────────────────────────────

def compute_apparent_power(df: pd.DataFrame) -> pd.Series:
    """
    Tính Công suất biểu kiến (S) theo công thức tam giác công suất:

        S = √(P² + Q²)

    trong đó:
      - P = Usage_kWh (Công suất tác dụng)
      - Q = Lagging_Current_Reactive.Power_kVarh (Công suất phản kháng trễ)

    Biến S quyết định khả năng chịu tải giới hạn của hệ thống truyền tải.
    Khi P không đổi nhưng Q tăng (do kẹt rô-to, rò rỉ từ), S sẽ phình
    to — tín hiệu báo động cháy nổ cáp điện.

    Args:
        df: DataFrame chứa các cột Usage_kWh và
            Lagging_Current_Reactive.Power_kVarh.

    Returns:
        pd.Series chứa Apparent Power (S).
    """
    p_col = "Usage_kWh"
    q_col = "Lagging_Current_Reactive.Power_kVarh"

    P = df[p_col]
    Q = df[q_col]
    S = np.sqrt(P**2 + Q**2)
    S.name = "Apparent_Power_S"
    return S


# ── Phase Angle ─────────────────────────────────────────────────────

def compute_phase_angle(df: pd.DataFrame) -> pd.Series:
    """
    Tính Góc lệch pha (φ) từ Hệ số công suất:

        φ = arccos(Power Factor)

    Cung cấp thang đo tuyến tính sắc nét hơn Power Factor,
    giúp mô hình học máy nhận diện trạng thái hỗn loạn của phụ tải
    phi tuyến (VD: biểu đồ V-I trajectory).

    Args:
        df: DataFrame chứa cột Lagging_Current_Power_Factor.

    Returns:
        pd.Series chứa Phase Angle (φ, đơn vị radians).
    """
    pf_col = "Lagging_Current_Power_Factor"

    pf = df[pf_col].clip(0, 1)  # Đảm bảo PF trong [0, 1] cho arccos
    phi = np.arccos(pf)
    phi.name = "Phase_Angle_Phi"
    return phi


# ── Orchestrator ────────────────────────────────────────────────────

def build_physical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tổng hợp tất cả đặc trưng vật lý điện năng vào DataFrame gốc.

    Tính toán Apparent Power (S) và Phase Angle (φ), rồi nối
    vào DataFrame ban đầu.

    Args:
        df: DataFrame đầu vào chứa các cột điện năng cần thiết.

    Returns:
        DataFrame mới = df gốc + S + φ.
    """
    result = df.copy()
    result["Apparent_Power_S"] = compute_apparent_power(df)
    result["Phase_Angle_Phi"] = compute_phase_angle(df)
    return result
