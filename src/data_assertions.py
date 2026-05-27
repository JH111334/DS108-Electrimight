# -*- coding: utf-8 -*-
"""
Data Assertions & Sanity Checks Module

Module này cung cấp các hàm kiểm tra khẳng định (assertions) để tự động
phát hiện lỗi dữ liệu sau mỗi bước pipeline. Đây là yêu cầu của rubric
Engineering & Reproducibility (15%) — mức xuất sắc đòi hỏi các hàm
kiểm thử dữ liệu (Data Assertions / Sanity Checks).

Tham chiếu: DS108 Final Project Capstone Guidelines — mục Engineering.
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


class DataAssertionError(AssertionError):
    """Ngoại lệ riêng cho vi phạm assertions dữ liệu."""
    pass


# ── Physical Constraints ────────────────────────────────────────────

def assert_no_negative_usage(
    df: pd.DataFrame,
    col: str = "Usage_kWh",
    strict: bool = True,
) -> None:
    """
    Khẳng định công suất tác dụng P không âm.

    Args:
        df: DataFrame cần kiểm tra.
        col: Tên cột công suất tác dụng.
        strict: Nếu True, raise DataAssertionError khi vi phạm.
              Nếu False, trả về bool.

    Raises:
        DataAssertionError: Nếu tồn tại giá trị âm và strict=True.
    """
    n_negative = int((df[col] < 0).sum())
    if n_negative > 0:
        msg = f"[ASSERT FAIL] {col} có {n_negative} giá trị âm."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


def assert_pf_in_range(
    df: pd.DataFrame,
    cols: Optional[List[str]] = None,
    bounds: Tuple[float, float] = (0.0, 1.0),
    strict: bool = True,
) -> None:
    """
    Khẳng định Power Factor nằm trong [0, 1].

    Args:
        df: DataFrame cần kiểm tra.
        cols: Danh sách cột PF. Mặc định các cột Lagging/Leading PF.
        bounds: Khoảng giá trị hợp lệ.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu PF ngoài bounds.
    """
    if cols is None:
        cols = ["Lagging_Current_Power_Factor", "Leading_Current_Power_Factor"]

    for col in cols:
        if col not in df.columns:
            continue
        lo, hi = bounds
        n_invalid = int(((df[col] < lo) | (df[col] > hi)).sum())
        if n_invalid > 0:
            msg = f"[ASSERT FAIL] {col} có {n_invalid} giá trị ngoài {bounds}."
            if strict:
                raise DataAssertionError(msg)
            else:
                print(msg)


def assert_physical_consistency(
    df: pd.DataFrame,
    tolerance: float = 1e-3,
    strict: bool = True,
) -> None:
    """
    Khẳng định tính nhất quán vật lý: S² ≈ P² + Q².

    Args:
        df: DataFrame chứa S, P, Q.
        tolerance: Sai số chấp nhận được.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu tồn tại sai lệch vượt tolerance.
    """
    p_col = "Usage_kWh"
    q_col = "Lagging_Current_Reactive.Power_kVarh"
    s_col = "Apparent_Power_S"

    if s_col not in df.columns:
        # Tính S tạm thời nếu chưa có
        S_calc = np.sqrt(df[p_col] ** 2 + df[q_col] ** 2)
    else:
        S_calc = df[s_col]

    S_theory = np.sqrt(df[p_col] ** 2 + df[q_col] ** 2)
    diff = np.abs(S_calc - S_theory)
    n_viol = int((diff > tolerance).sum())

    if n_viol > 0:
        msg = f"[ASSERT FAIL] {n_viol} điểm vi phạm S² = P² + Q² (tol={tolerance})."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


# ── Temporal Constraints ────────────────────────────────────────────

def assert_temporal_sorted(
    df: pd.DataFrame,
    date_col: str = "date",
    strict: bool = True,
) -> None:
    """
    Khẳng định DataFrame đã sắp xếp tăng dần theo thời gian.

    Args:
        df: DataFrame cần kiểm tra.
        date_col: Tên cột thời gian.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu không sorted.
    """
    if date_col not in df.columns:
        return
    ts = pd.to_datetime(df[date_col], dayfirst=True)
    if not ts.is_monotonic_increasing:
        msg = "[ASSERT FAIL] Dữ liệu chưa sắp xếp tăng dần theo thời gian."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


def assert_no_duplicate_timestamps(
    df: pd.DataFrame,
    date_col: str = "date",
    strict: bool = True,
) -> None:
    """
    Khẳng định không có timestamp trùng lặp.

    Args:
        df: DataFrame cần kiểm tra.
        date_col: Tên cột thời gian.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu có trùng lặp.
    """
    if date_col not in df.columns:
        return
    n_dup = int(df[date_col].duplicated().sum())
    if n_dup > 0:
        msg = f"[ASSERT FAIL] Có {n_dup} timestamp trùng lặp."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


def assert_nsm_consistency(
    df: pd.DataFrame,
    date_col: str = "date",
    nsm_col: str = "NSM",
    strict: bool = True,
) -> None:
    """
    Khẳng định NSM khớp với timestamp (hour*3600 + minute*60 + second).

    Args:
        df: DataFrame cần kiểm tra.
        date_col: Tên cột thời gian.
        nsm_col: Tên cột NSM.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu có sai lệch.
    """
    if date_col not in df.columns or nsm_col not in df.columns:
        return
    ts = pd.to_datetime(df[date_col], dayfirst=True)
    expected_nsm = ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second
    n_mismatch = int((df[nsm_col] != expected_nsm).sum())
    if n_mismatch > 0:
        msg = f"[ASSERT FAIL] {n_mismatch} điểm NSM không khớp timestamp."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


# ── Completeness Constraints ────────────────────────────────────────

def assert_no_nulls(
    df: pd.DataFrame,
    exclude_cols: Optional[List[str]] = None,
    strict: bool = True,
) -> None:
    """
    Khẳng định không có giá trị null trong các cột số (trừ exclude_cols).

    Args:
        df: DataFrame cần kiểm tra.
        exclude_cols: Cột được phép null (ví dụ: cột text).
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu tồn tại null.
    """
    check_df = df.copy()
    if exclude_cols:
        check_df = check_df.drop(columns=[c for c in exclude_cols if c in check_df.columns])
    n_null = int(check_df.isnull().sum().sum())
    if n_null > 0:
        msg = f"[ASSERT FAIL] Có {n_null} giá trị null trong DataFrame."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


# ── Anomaly Constraints ─────────────────────────────────────────────

def assert_anomaly_rate_below(
    df: pd.DataFrame,
    labels: Optional[List[str]] = None,
    threshold: float = 0.10,
    strict: bool = True,
) -> None:
    """
    Khẳng định tỷ lệ anomaly không vượt quá ngưỡng cho phép.

    Theo LABELING_GUIDELINE.md, tỷ lệ anomaly không nên > 10%.

    Args:
        df: DataFrame chứa cột nhãn anomaly.
        labels: Danh sách cột nhãn. Mặc định 3 loại anomaly.
        threshold: Ngưỡng tối đa (0.10 = 10%).
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu tỷ lệ vượt ngưỡng.
    """
    if labels is None:
        labels = ["anomaly_idling", "anomaly_leakage", "anomaly_overload"]

    available = [c for c in labels if c in df.columns]
    if not available:
        return

    any_anomaly = df[available].any(axis=1)
    rate = any_anomaly.mean()
    if rate > threshold:
        msg = (
            f"[ASSERT FAIL] Tỷ lệ anomaly {rate:.2%} vượt ngưỡng "
            f"{threshold:.0%}."
        )
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


# ── Feature Engineering Constraints ─────────────────────────────────

def assert_feature_count(
    df: pd.DataFrame,
    min_features: int = 40,
    strict: bool = True,
) -> None:
    """
    Khẳng định số lượng cột đạt tối thiểu sau feature engineering.

    Args:
        df: DataFrame cần kiểm tra.
        min_features: Số cột tối thiểu yêu cầu.
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu ít hơn min_features.
    """
    n_cols = len(df.columns)
    if n_cols < min_features:
        msg = f"[ASSERT FAIL] Chỉ có {n_cols} cột, yêu cầu ≥ {min_features}."
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


def assert_correlation_preserved(
    real_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    threshold: float = 0.90,
    strict: bool = True,
) -> None:
    """
    Khẳng định ma trận tương quan của synthetic data gần với real data.

    Tính Frobenius norm của hiệu ma trận correlation, so sánh với ngưỡng.

    Args:
        real_df: DataFrame dữ liệu thực.
        synthetic_df: DataFrame dữ liệu tổng hợp.
        numeric_cols: Cột số để tính correlation. Mặc định tất cả.
        threshold: Ngưỡng tương quang tối thiểu (theo Pearson mean abs diff).
        strict: Raise error hay chỉ in cảnh báo.

    Raises:
        DataAssertionError: Nếu tương quan không được bảo toàn.
    """
    if numeric_cols is None:
        numeric_cols = real_df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c in synthetic_df.columns]

    corr_real = real_df[numeric_cols].corr().fillna(0)
    corr_syn = synthetic_df[numeric_cols].corr().fillna(0)

    # Mean absolute difference of correlation matrices
    diff = np.abs(corr_real - corr_syn).values
    mean_diff = diff[np.isfinite(diff)].mean()

    if mean_diff > (1 - threshold):
        msg = (
            f"[ASSERT FAIL] Ma trận tương quan sai lệch trung bình "
            f"{mean_diff:.4f}, vượt ngưỡng {1-threshold:.4f}."
        )
        if strict:
            raise DataAssertionError(msg)
        else:
            print(msg)


# ── Orchestrator: Run All Assertions ────────────────────────────────

def run_pipeline_assertions(
    df: pd.DataFrame,
    stage: str = "post_cleaning",
    synthetic_df: Optional[pd.DataFrame] = None,
    strict: bool = True,
) -> dict:
    """
    Chạy toàn bộ assertions phù hợp với giai đoạn pipeline.

    Các giai đoạn hỗ trợ:
      - "post_cleaning": Sau bước làm sạch (data_loader).
      - "post_time_features": Sau time-domain features.
      - "post_wavelet": Sau wavelet features.
      - "post_physical": Sau physical features.
      - "post_labeling": Sau gán nhãn anomaly.
      - "post_gan": Sau GAN augmentation (cần synthetic_df).

    Args:
        df: DataFrame hiện tại.
        stage: Tên giai đoạn pipeline.
        synthetic_df: DataFrame synthetic (chỉ dùng cho stage="post_gan").
        strict: Nếu True, dừng ngay khi assertion fail.

    Returns:
        Dict kết quả: {assertion_name: "PASS" | "FAIL: message"}.
    """
    results: dict = {}

    # Các assertions chung cho mọi giai đoạn
    checks = [
        ("temporal_sorted", lambda: assert_temporal_sorted(df, strict=strict)),
        ("no_duplicate_timestamps", lambda: assert_no_duplicate_timestamps(df, strict=strict)),
        ("nsm_consistency", lambda: assert_nsm_consistency(df, strict=strict)),
        ("no_nulls", lambda: assert_no_nulls(df, strict=strict)),
    ]

    if stage in ("post_cleaning", "post_time_features", "post_wavelet",
                 "post_physical", "post_labeling", "post_gan"):
        checks += [
            ("no_negative_usage", lambda: assert_no_negative_usage(df, strict=strict)),
            ("pf_in_range", lambda: assert_pf_in_range(df, strict=strict)),
        ]

    if stage in ("post_physical", "post_labeling", "post_gan"):
        checks += [
            ("physical_consistency", lambda: assert_physical_consistency(df, strict=strict)),
        ]

    if stage in ("post_labeling", "post_gan"):
        checks += [
            ("anomaly_rate_below", lambda: assert_anomaly_rate_below(df, strict=strict)),
            ("feature_count", lambda: assert_feature_count(df, strict=strict)),
        ]

    if stage == "post_gan" and synthetic_df is not None:
        checks += [
            ("correlation_preserved", lambda: assert_correlation_preserved(df, synthetic_df, strict=strict)),
        ]

    for name, check_fn in checks:
        try:
            check_fn()
            results[name] = "PASS"
        except DataAssertionError as e:
            results[name] = f"FAIL: {e}"
            if strict:
                raise

    return results


if __name__ == "__main__":
    # Demo: chạy assertions trên dữ liệu thô
    from src.bronze.data_loader import load_steel_data, clean_data
    from src.utils import RAW_CSV

    raw = load_steel_data(RAW_CSV)
    clean, _ = clean_data(raw)
    report = run_pipeline_assertions(clean, stage="post_cleaning", strict=False)
    print("\n=== ASSERTION REPORT ===")
    for k, v in report.items():
        print(f"  {k}: {v}")
