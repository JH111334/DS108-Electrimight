"""
DS108-Electrimight Source Package

Package chứa các module cho dự án Steel Industry Energy Consumption.
Pipeline tiền xử lý Data-Centric AI theo 7 bước:
  1. data_loader      — Tải, kiểm tra, làm sạch dữ liệu thô
  2. time_features    — Đặc trưng miền thời gian (lag, rolling, trig)
  3. wavelet_features — Đặc trưng miền tần số (DWT)
  4. physical_features— Đặc trưng vật lý điện năng (S, φ)
  5. anomaly_labels   — Gán nhãn bất thường (Idling, Leakage, Overload)
  6. gan_augmentation — Tăng cường dữ liệu GAN (skeleton)
  7. pipeline         — Pipeline đầu-cuối tích hợp tất cả bước

Lưu ý: Một số module (wavelet_features, misc) yêu cầu thư viện nặng
(pywt, tensorflow). Sử dụng import trực tiếp khi cần:
    from src.wavelet_features import rolling_wavelet_features
"""

__version__ = "1.0.0"
__author__ = "DS108 Team"

# Core modules — luôn importable
from . import utils
from . import data_loader
from . import time_features
from . import physical_features
from . import anomaly_labels
from . import gan_augmentation

# Heavy-dependency modules — import khi cần
# from . import wavelet_features  # Requires pywt
# from . import pipeline          # Requires pywt (via wavelet_features)
# from . import misc              # Requires tensorflow

__all__ = [
    'utils',
    'data_loader',
    'time_features',
    'physical_features',
    'anomaly_labels',
    'gan_augmentation',
    'wavelet_features',
    'pipeline',
    'misc',
]
