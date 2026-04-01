"""
Wavelet Features Module

Trích xuất đặc trưng tần số-thời gian bằng biến đổi Wavelet rời rạc (DWT)
sử dụng thư viện PyWavelets.
"""

from typing import List, Optional

import numpy as np
import pandas as pd
import pywt


def extract_wavelet_features(
    series: np.ndarray,
    wavelet: str = "db4",
    level: int = 3,
    prefix: str = "wt",
) -> pd.Series:
    """
    Trích xuất đặc trưng thống kê từ hệ số DWT của một chuỗi 1-D.

    Với mỗi mức phân rã, hàm tính: mean, std, energy, max_abs của
    các hệ số chi tiết (cD) và xấp xỉ cuối cùng (cA).

    Args:
        series: Mảng 1-D dữ liệu chuỗi thời gian.
        wavelet: Tên wavelet (mặc định "db4" — Daubechies bậc 4).
        level: Số mức phân rã (mặc định 3).
        prefix: Tiền tố cho tên đặc trưng.

    Returns:
        pd.Series chứa các đặc trưng đã trích xuất.
    """
    coeffs = pywt.wavedec(series, wavelet=wavelet, level=level)
    features: dict = {}

    for i, coeff in enumerate(coeffs):
        label = f"{prefix}_cA" if i == 0 else f"{prefix}_cD{level - i + 1}"
        features[f"{label}_mean"] = float(np.mean(coeff))
        features[f"{label}_std"] = float(np.std(coeff))
        features[f"{label}_energy"] = float(np.sum(coeff ** 2))
        features[f"{label}_max_abs"] = float(np.max(np.abs(coeff)))

    return pd.Series(features)


def apply_wavelet_features_to_df(
    df: pd.DataFrame,
    target_cols: Optional[List[str]] = None,
    wavelet: str = "db4",
    level: int = 3,
) -> pd.DataFrame:
    """
    Áp dụng extract_wavelet_features lên từng cột số trong DataFrame
    bằng cách tính đặc trưng trên toàn bộ chuỗi của mỗi cột.

    Args:
        df: DataFrame đầu vào (đã được sắp xếp theo thời gian).
        target_cols: Danh sách cột cần xử lý; mặc định là tất cả cột số.
        wavelet: Tên wavelet.
        level: Số mức phân rã.

    Returns:
        pd.Series (một hàng đặc trưng tổng hợp cho toàn bộ tập dữ liệu),
        hoặc DataFrame nếu cần đặc trưng theo từng hàng (xem rolling variant).
    """
    if target_cols is None:
        target_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    all_features = {}
    for col in target_cols:
        col_features = extract_wavelet_features(
            df[col].values, wavelet=wavelet, level=level, prefix=col
        )
        all_features.update(col_features.to_dict())

    return pd.Series(all_features)


def rolling_wavelet_features(
    df: pd.DataFrame,
    target_col: str,
    window: int = 64,
    wavelet: str = "db4",
    level: int = 3,
) -> pd.DataFrame:
    """
    Tính đặc trưng Wavelet theo cửa sổ trượt (rolling window) để tạo
    đặc trưng theo từng thời điểm trong chuỗi.

    Args:
        df: DataFrame đầu vào (sắp xếp theo thời gian).
        target_col: Tên cột cần xử lý.
        window: Kích thước cửa sổ trượt (số bước thời gian).
        wavelet: Tên wavelet.
        level: Số mức phân rã.

    Returns:
        DataFrame các đặc trưng Wavelet với cùng số hàng như df
        (các hàng đầu không đủ window sẽ là NaN).
    """
    results = []
    series = df[target_col].values

    for i in range(len(series)):
        if i < window - 1:
            results.append(None)
        else:
            window_data = series[i - window + 1 : i + 1]
            feats = extract_wavelet_features(
                window_data, wavelet=wavelet, level=level, prefix=target_col
            )
            results.append(feats)

    valid_results = [r for r in results if r is not None]
    if not valid_results:
        return pd.DataFrame(index=df.index)

    feat_df = pd.DataFrame(valid_results)
    feat_df.index = df.index[window - 1 :]
    return feat_df.reindex(df.index)
