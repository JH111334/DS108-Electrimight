"""
Data Loader Module

Tải, kiểm tra và làm sạch bộ dữ liệu Steel_industry_data.csv.
Quy tắc: Chỉ đọc từ data/raw/ — không bao giờ ghi vào thư mục đó.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


RAW_DATA_PATH = Path("data/raw/Steel_industry_data.csv")


def load_steel_data(filepath: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Tải bộ dữ liệu thô từ data/raw/ (chỉ đọc).

    Args:
        filepath: Đường dẫn đến Steel_industry_data.csv.

    Returns:
        DataFrame chứa dữ liệu thô.

    Raises:
        FileNotFoundError: Nếu tệp không tồn tại tại filepath.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"Không tìm thấy tệp dữ liệu: {filepath}\n"
            "Hãy đặt Steel_industry_data.csv vào thư mục data/raw/."
        )
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    return df


def inspect_data(df: pd.DataFrame) -> dict:
    """
    Kiểm tra sơ bộ DataFrame: shape, kiểu dữ liệu, giá trị thiếu.

    Args:
        df: DataFrame cần kiểm tra.

    Returns:
        Dictionary chứa các thống kê kiểm tra.
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
    Làm sạch dữ liệu: xử lý giá trị thiếu, loại bỏ bản ghi trùng lặp,
    đảm bảo kiểu dữ liệu đúng.

    Args:
        df: DataFrame thô đã tải từ load_steel_data().

    Returns:
        Tuple gồm (DataFrame đã làm sạch, cleaning report dict).
    """
    report: dict = {}
    df = df.copy()

    # Loại bỏ bản ghi trùng lặp
    n_before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = n_before - len(df)

    # Xử lý giá trị thiếu bằng nội suy tuyến tính (phù hợp chuỗi thời gian)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    missing_before = df[numeric_cols].isnull().sum().sum()
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")
    report["missing_imputed"] = int(missing_before)

    # Sắp xếp theo thời gian
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)

    report["final_shape"] = df.shape
    return df, report
