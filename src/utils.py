"""
Utilities Module

Các tiện ích dùng chung cho dự án DS108-Electritight:
logging, lưu/tải dữ liệu.
"""

import logging
from pathlib import Path

import pandas as pd


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Cấu hình logging.

    Args:
        level: Mức độ logging (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Logger object.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """
    Lưu DataFrame vào tệp CSV.

    Args:
        df: DataFrame cần lưu.
        filepath: Đường dẫn tệp đích.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def load_data(filepath: Path) -> pd.DataFrame:
    """
    Tải DataFrame từ tệp CSV.

    Args:
        filepath: Đường dẫn tệp nguồn.

    Returns:
        DataFrame đã tải.
    """
    return pd.read_csv(Path(filepath))
