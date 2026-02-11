"""
Data Collection Module

Module này chứa các function để thu thập dữ liệu VN30 từ Vnstock
"""

import pandas as pd
from typing import List, Optional


def collect_all_vn30(start_date: str = "2015-01-01", 
                     end_date: str = "2025-12-31") -> pd.DataFrame:
    """
    Thu thập dữ liệu OHLCV cho tất cả mã VN30
    
    Args:
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)
        
    Returns:
        DataFrame chứa dữ liệu OHLCV
    """
    # TODO: Implement data collection logic
    pass
