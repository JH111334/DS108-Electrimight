"""
Utilities Module

Module này chứa các utility functions
"""

import logging
from pathlib import Path
import pandas as pd


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger object
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """
    Lưu DataFrame vào file
    
    Args:
        df: DataFrame cần lưu
        filepath: Đường dẫn file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def load_data(filepath: Path) -> pd.DataFrame:
    """
    Load DataFrame từ file
    
    Args:
        filepath: Đường dẫn file
        
    Returns:
        DataFrame
    """
    return pd.read_csv(filepath)
