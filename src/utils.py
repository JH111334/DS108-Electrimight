"""
Utilities Module

Các tiện ích dùng chung cho dự án DS108-Electrimight:
logging, lưu/tải dữ liệu, và hằng số đường dẫn trung tâm.
"""

import logging
from pathlib import Path

import pandas as pd


# ── Centralized Path Constants ──────────────────────────────────────
# Tất cả module trong src/ phải sử dụng các hằng số này
# thay vì hardcode đường dẫn riêng.

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_CSV = RAW_DIR / "Steel_industry_data.csv"
WEATHER_CSV = RAW_DIR / "weather_gwangyang_2018.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ── Logging ─────────────────────────────────────────────────────────

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


# ── Data I/O ────────────────────────────────────────────────────────

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
