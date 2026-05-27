"""
Data Loader Module

Tai, kiem tra va lam sach bo du lieu Steel_industry_data.csv.
Quy tac: Chi doc tu data/bronze/ — khong bao gio ghi vao thu muc do.

Cac buoc lam sach chinh:
  1. Loai bo ban ghi trung lap
  2. Xu ly gia tri thieu (interpolation tuyen tinh)
  3. Scale Power Factor tu % (0-100) ve he so (0-1)
  4. Xac thuc rang buoc vat ly (PF trong [0,1], P >= 0, Q >= 0)
  5. Sap xep theo thoi gian
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from src.utils import RAW_CSV


def load_steel_data(filepath: Path = RAW_CSV) -> pd.DataFrame:
    """
    Tai bo du lieu tho tu data/bronze/ (chi doc).

    Args:
        filepath: Duong dan den Steel_industry_data.csv.

    Returns:
        DataFrame chua du lieu tho.

    Raises:
        FileNotFoundError: Neu tep khong ton tai tai filepath.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"Khong tim thay tep du lieu: {filepath}\n"
            "Hay dat Steel_industry_data.csv vao thu muc data/bronze/."
        )
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    return df


def inspect_data(df: pd.DataFrame) -> dict:
    """
    Kiem tra so bo DataFrame: shape, kieu du lieu, gia tri thieu.

    Args:
        df: DataFrame can kiem tra.

    Returns:
        Dictionary chua cac thong ke kiem tra.
    """
    report = {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "missing_count": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "duplicates": int(df.duplicated().sum()),
    }
    return report


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Lam sach du lieu: xu ly gia tri thieu, loai bo ban ghi trung lap,
    dam bao kieu du lieu dung, va xu ly cac van de vat ly dac biet.

    Cac van de duoc xu ly:
      1. Loai bo trung lap
      2. Noi suy gia tri thieu (phu hop chuoi thoi gian)
      3. Scale Power Factor tu % ve he so (0-1)
      4. Validation PF sau scale
      5. Xac thuc rang buoc vat ly co ban

    Args:
        df: DataFrame tho da tai tu load_steel_data().

    Returns:
        Tuple gom (DataFrame da lam sach, cleaning report dict).
    """
    report: dict = {}
    df = df.copy()

    # 1. Loai bo ban ghi trung lap
    n_before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = n_before - len(df)

    # 2. Xu ly gia tri thieu bang noi suy tuyen tinh (phu hop chuoi thoi gian)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    missing_before = df[numeric_cols].isnull().sum().sum()
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")
    report["missing_imputed"] = int(missing_before)

    # 3. Scale Power Factor tu dang % (0-100) ve he so (0-1)
    # Day la van de CRITICAL phat hien boi data_quality_audit.py
    pf_cols = ["Lagging_Current_Power_Factor", "Leading_Current_Power_Factor"]
    pf_scaled_count = 0
    for col in pf_cols:
        if col in df.columns:
            max_val = df[col].max()
            if max_val > 1.0:
                # Du lieu dang o dang %, can chia 100
                df[col] = df[col] / 100.0
                pf_scaled_count += 1
                report[f"{col}_scaled"] = True
                report[f"{col}_max_before"] = float(max_val)
            else:
                report[f"{col}_scaled"] = False
    report["pf_columns_scaled"] = pf_scaled_count

    # 4. Validation PF sau scale: dam bao nam trong [0, 1]
    for col in pf_cols:
        if col in df.columns:
            invalid = (df[col] < 0) | (df[col] > 1)
            n_invalid = int(invalid.sum())
            if n_invalid > 0:
                # Clip ve [0, 1]
                df[col] = df[col].clip(0, 1)
                report[f"{col}_invalid_clipped"] = n_invalid

    # 5. Xac thuc rang buoc vat ly co ban
    # P (Usage_kWh) khong the am
    n_negative_usage = int((df["Usage_kWh"] < 0).sum())
    if n_negative_usage > 0:
        df.loc[df["Usage_kWh"] < 0, "Usage_kWh"] = 0
        report["negative_usage_corrected"] = n_negative_usage

    # 6. Sap xep theo thoi gian
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)

    report["final_shape"] = df.shape
    return df, report
