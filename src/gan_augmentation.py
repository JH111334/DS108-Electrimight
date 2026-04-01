"""
GAN Augmentation Module

Định nghĩa và huấn luyện mô hình Generative Adversarial Network (GAN)
để tăng cường dữ liệu chuỗi thời gian tiêu thụ điện năng.
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd


def build_generator(latent_dim: int = 100, output_dim: int = 1):
    """
    Xây dựng mạng Generator của GAN.

    Nhận vector nhiễu ngẫu nhiên (latent space) và sinh ra chuỗi
    dữ liệu tổng hợp.

    Args:
        latent_dim: Chiều của không gian ẩn (latent vector).
        output_dim: Số đặc trưng đầu ra (số cột dữ liệu cần sinh).

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

    Phân loại mẫu là thật (từ dữ liệu) hay giả (do Generator tạo ra).

    Args:
        input_dim: Số đặc trưng đầu vào (bằng output_dim của Generator).

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

    Args:
        real_data: Mảng 2-D (n_samples, n_features) đã được chuẩn hóa về [-1, 1].
        latent_dim: Chiều không gian ẩn.
        epochs: Số epoch huấn luyện.
        batch_size: Kích thước batch.
        sample_interval: Số epoch giữa mỗi lần lưu mẫu sinh.
        output_dir: Thư mục lưu checkpoint; bỏ qua nếu None.

    Returns:
        Tuple (generator, discriminator) — các mô hình đã huấn luyện.
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
        generator: Mô hình Generator (tf.keras.Model) đã huấn luyện.
        n_samples: Số mẫu cần sinh.
        latent_dim: Chiều không gian ẩn (phải khớp với khi huấn luyện).

    Returns:
        Mảng numpy (n_samples, n_features) chứa dữ liệu tổng hợp.
    """
    noise = np.random.normal(0, 1, (n_samples, latent_dim))
    return generator.predict(noise, verbose=0)
