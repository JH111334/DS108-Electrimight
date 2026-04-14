"""
GAN Augmentation Module (Skeleton)

Mạng đối nghịch sinh (GAN) để tăng cường dữ liệu chuỗi thời gian
tiêu thụ điện năng — giải quyết bài toán mất cân bằng dữ liệu
(các điểm bất thường chiếm < 1%).

Kiến trúc đề xuất: 1D-DCGAN hoặc VAE tinh chỉnh cho chuỗi thời gian.
Generator học cấu trúc không gian-thời gian và tương quan giữa
P (công suất tác dụng), Q (phản kháng), PF (hệ số công suất)
để sinh mẫu sự cố nhân tạo mang tính thực tế cao.

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục Generative AI.
Xem src/misc.py cho bản triển khai TensorFlow đầy đủ.
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np


def build_generator(latent_dim: int = 100, output_dim: int = 1):
    """
    Xây dựng mạng Generator của GAN.

    Kiến trúc: Dense(128) → LeakyReLU → BN → Dense(256) → LeakyReLU
    → BN → Dense(512) → LeakyReLU → BN → Dense(output_dim, tanh).

    Args:
        latent_dim: Chiều của không gian ẩn (latent vector).
        output_dim: Số đặc trưng đầu ra.

    Returns:
        tf.keras.Model — Generator.
    """
    raise NotImplementedError(
        "TODO: Triển khai với TensorFlow/Keras. "
        "Xem src/misc.py cho bản triển khai tham chiếu."
    )


def build_discriminator(input_dim: int = 1):
    """
    Xây dựng mạng Discriminator của GAN.

    Kiến trúc: Dense(512) → LeakyReLU → Dropout(0.3) → Dense(256)
    → LeakyReLU → Dropout(0.3) → Dense(128) → LeakyReLU
    → Dense(1, sigmoid).

    Args:
        input_dim: Số đặc trưng đầu vào.

    Returns:
        tf.keras.Model — Discriminator.
    """
    raise NotImplementedError(
        "TODO: Triển khai với TensorFlow/Keras. "
        "Xem src/misc.py cho bản triển khai tham chiếu."
    )


def train_gan(
    real_data: np.ndarray,
    latent_dim: int = 100,
    epochs: int = 2000,
    batch_size: int = 64,
    sample_interval: int = 200,
    output_dir: Optional[Path] = None,
) -> Tuple:
    """
    Huấn luyện GAN trên dữ liệu thực.

    Quy trình:
    1. Xây dựng & biên dịch Discriminator (binary_crossentropy, Adam lr=0.0002)
    2. Xây dựng Generator
    3. Đóng băng Discriminator, tạo GAN kết hợp
    4. Vòng lặp epoch: train D trên real+fake → train G qua GAN kết hợp

    Args:
        real_data: Mảng 2-D (n_samples, n_features) đã chuẩn hóa [-1, 1].
        latent_dim: Chiều không gian ẩn.
        epochs: Số epoch huấn luyện.
        batch_size: Kích thước batch.
        sample_interval: Epoch giữa mỗi lần log.
        output_dir: Thư mục lưu checkpoint.

    Returns:
        Tuple (generator, discriminator).
    """
    raise NotImplementedError(
        "TODO: Triển khai với TensorFlow/Keras. "
        "Xem src/misc.py cho bản triển khai tham chiếu."
    )


def generate_synthetic_samples(
    generator,
    n_samples: int = 500,
    latent_dim: int = 100,
) -> np.ndarray:
    """
    Sinh dữ liệu tổng hợp từ Generator đã huấn luyện.

    Args:
        generator: Mô hình Generator đã huấn luyện.
        n_samples: Số mẫu cần sinh.
        latent_dim: Chiều không gian ẩn.

    Returns:
        Mảng numpy (n_samples, n_features).
    """
    raise NotImplementedError(
        "TODO: Triển khai với TensorFlow/Keras. "
        "Xem src/misc.py cho bản triển khai tham chiếu."
    )
