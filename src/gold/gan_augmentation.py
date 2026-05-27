"""
GAN Augmentation Module

Mạng đối nghịch sinh (GAN) để tăng cường dữ liệu chuỗi thờ gian
tiêu thụ điện năng — giải quyết bài toán mất cân bằng dữ liệu
(các điểm bất thường chiếm < 3%).

Kiến trúc: Fully Connected GAN với hàm kích hoạt LeakyReLU.
Generator học phân phối của các mẫu bất thường để sinh synthetic samples.

Tham chiếu: "Hướng dẫn đồ án tiền xử lý dữ liệu" — mục Generative AI.
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
    import tensorflow as tf
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Dense(128, input_dim=latent_dim),
            keras.layers.LeakyReLU(0.2),
            keras.layers.BatchNormalization(momentum=0.8),
            keras.layers.Dense(256),
            keras.layers.LeakyReLU(0.2),
            keras.layers.BatchNormalization(momentum=0.8),
            keras.layers.Dense(512),
            keras.layers.LeakyReLU(0.2),
            keras.layers.BatchNormalization(momentum=0.8),
            keras.layers.Dense(output_dim, activation="tanh"),
        ],
        name="generator",
    )
    return model


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
    import tensorflow as tf
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Dense(512, input_dim=input_dim),
            keras.layers.LeakyReLU(0.2),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(256),
            keras.layers.LeakyReLU(0.2),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(128),
            keras.layers.LeakyReLU(0.2),
            keras.layers.Dense(1, activation="sigmoid"),
        ],
        name="discriminator",
    )
    return model


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
    import tensorflow as tf
    from tensorflow import keras

    n_samples, n_features = real_data.shape

    # Xây dựng và biên dịch Discriminator
    discriminator = build_discriminator(input_dim=n_features)
    discriminator.compile(
        loss="binary_crossentropy",
        optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5),
        metrics=["accuracy"],
    )

    # Xây dựng Generator
    generator = build_generator(latent_dim=latent_dim, output_dim=n_features)

    # Xây dựng GAN kết hợp (chỉ train Generator, đóng băng Discriminator)
    discriminator.trainable = False
    gan_input = keras.Input(shape=(latent_dim,))
    gan_output = discriminator(generator(gan_input))
    gan = keras.Model(gan_input, gan_output, name="gan")
    gan.compile(
        loss="binary_crossentropy",
        optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5),
    )

    real_labels = np.ones((batch_size, 1))
    fake_labels = np.zeros((batch_size, 1))

    for epoch in range(1, epochs + 1):
        # --- Huấn luyện Discriminator ---
        idx = np.random.randint(0, n_samples, batch_size)
        real_batch = real_data[idx]

        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        fake_batch = generator.predict(noise, verbose=0)

        d_loss_real = discriminator.train_on_batch(real_batch, real_labels)
        d_loss_fake = discriminator.train_on_batch(fake_batch, fake_labels)
        d_loss = 0.5 * (d_loss_real[0] + d_loss_fake[0])

        # --- Huấn luyện Generator ---
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        g_loss = gan.train_on_batch(noise, real_labels)

        if epoch % sample_interval == 0:
            print(f"Epoch {epoch}/{epochs}  |  D loss: {d_loss:.4f}  |  G loss: {g_loss:.4f}")

    return generator, discriminator


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
    noise = np.random.normal(0, 1, (n_samples, latent_dim))
    return generator.predict(noise, verbose=0)
