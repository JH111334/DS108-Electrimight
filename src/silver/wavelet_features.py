"""
Wavelet Features Module (Frequency-Domain)

Trích xuất đặc trưng tần số-thời gian bằng biến đổi Wavelet rời rạc (DWT)
sử dụng thư viện PyWavelets (Outlines §IV.2).

Ưu thế DWT so với FFT:
  - FFT chỉ cho biết TẦN SỐ nào tồn tại, không xác định THỜI ĐIỂM.
  - DWT sử dụng hàm sóng ngắn (wavelets) co giãn + tịnh tiến,
    định vị tín hiệu cả trong tần số LẪN thời gian.
  - Sự cố hỏng hóc đột ngột → bị tóm gọn trong hệ số chi tiết (cD),
    biến DWT thành công cụ tối thượng cho ngoại lai tần số cao.

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục 2 (Frequency Domain).
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

    - cA (Approximation): Thông tin xu hướng vĩ mô.
    - cD (Detail): Dao động vi mô — nơi bất thường tần số cao ẩn náu.

    Args:
        series: Mảng 1-D dữ liệu chuỗi thời gian.
        wavelet: Tên wavelet (mặc định "db4" — Daubechies bậc 4).
        level: Số mức phân rã (mặc định 3).
        prefix: Tiền tố cho tên đặc trưng.

    Returns:
        pd.Series chứa các đặc trưng đã trích xuất.
    """
    coeffs = pywt.wavedec(np.array(series, copy=True), wavelet=wavelet, level=level)
    features: dict = {}

    for i, coeff in enumerate(coeffs):
        label = f"{prefix}_cA" if i == 0 else f"{prefix}_cD{level - i + 1}"
        features[f"{label}_mean"] = float(np.mean(coeff))
        features[f"{label}_std"] = float(np.std(coeff))
        features[f"{label}_energy"] = float(np.sum(coeff**2))
        features[f"{label}_max_abs"] = float(np.max(np.abs(coeff)))

    return pd.Series(features)


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
