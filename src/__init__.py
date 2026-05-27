"""
DS108-Electrimight Source Package

Package chứa các module cho dự án Steel Industry Energy Consumption.
Pipeline tiền xử lý Data-Centric AI theo kiến trúc Medallion (Bronze / Silver / Gold):
  Bronze — data_loader, weather_loader, data_quality_audit
  Silver — time_features, wavelet_features, physical_features, anomaly_labels
  Gold   — pipeline, gan_augmentation, generate_figures, misc

Shared — utils, data_assertions, missingness_analysis, leakage_audit

Lưu ý: Một số module (wavelet_features, misc) yêu cầu thư viện nặng
(pywt, tensorflow). Sử dụng import trực tiếp khi cần:
    from src.silver.wavelet_features import rolling_wavelet_features
"""

__version__ = "1.0.0"
__author__ = "DS108 Team"

# Core shared modules — luôn importable
from . import utils
from . import data_assertions
from . import missingness_analysis
from . import leakage_audit

# Bronze layer
from .bronze import data_loader
from .bronze import weather_loader
from .bronze import data_quality_audit

# Silver layer
from .silver import time_features
from .silver import physical_features
from .silver import anomaly_labels

# Gold layer
from .gold import gan_augmentation

# Heavy-dependency modules — import khi cần
# from src.silver import wavelet_features  # Requires pywt
# from src.gold import pipeline            # Requires pywt
# from src.gold import misc                # Requires tensorflow

__all__ = [
    "utils",
    "data_assertions",
    "missingness_analysis",
    "leakage_audit",
    "data_loader",
    "weather_loader",
    "data_quality_audit",
    "time_features",
    "physical_features",
    "anomaly_labels",
    "gan_augmentation",
    "wavelet_features",
    "pipeline",
    "misc",
]
