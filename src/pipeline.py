"""
DS108-Electrimight Pipeline

Pipeline đầu-cuối tích hợp toàn bộ bước tiền xử lý dữ liệu Steel Industry,
được cấu trúc theo khung 7 bước từ Outlines:

  1. Tải & kiểm tra dữ liệu thô (data/raw/ — chỉ đọc)
  2. Làm sạch dữ liệu (loại trùng lặp, nội suy, sắp xếp theo thời gian)
  3. Time-Domain Features (lag, rolling stats, trig encoding)
  4. Frequency-Domain Features (DWT Wavelet)
  5. Physical-Domain Features (Apparent Power S, Phase Angle φ)
  6. Anomaly Labeling (Idling, Leakage, Overload)
  7. (Tùy chọn) GAN Augmentation
  8. Lưu kết quả vào data/processed/
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.data_loader import load_steel_data, clean_data, inspect_data
from src.time_features import build_time_features
from src.wavelet_features import rolling_wavelet_features
from src.physical_features import build_physical_features
from src.anomaly_labels import label_all_anomalies
from src.utils import setup_logging, save_data, RAW_CSV, PROCESSED_DIR


class ElectrimightPipeline:
    """
    Pipeline chính cho dự án DS108-Electrimight.

    Workflow (theo Outlines 7 bước):
    1. Data Loading & Inspection
    2. Data Cleaning
    3. Time-Domain Feature Engineering
    4. Frequency-Domain Feature Extraction (Wavelet)
    5. Physical-Domain Feature Extraction (S, φ)
    6. Anomaly Labeling (Idling, Leakage, Overload)
    7. GAN Augmentation (tùy chọn)
    """

    def __init__(
        self,
        raw_path: Path = RAW_CSV,
        output_dir: Path = PROCESSED_DIR,
        log_level: str = "INFO",
        use_gan: bool = False,
        gan_epochs: int = 2000,
        n_synthetic: int = 500,
    ):
        """
        Khởi tạo pipeline.

        Args:
            raw_path: Đường dẫn tệp dữ liệu thô (chỉ đọc).
            output_dir: Thư mục lưu kết quả xử lý.
            log_level: Mức độ logging.
            use_gan: Có sử dụng GAN để tăng cường dữ liệu không.
            gan_epochs: Số epoch huấn luyện GAN.
            n_synthetic: Số mẫu tổng hợp GAN cần sinh.
        """
        self.raw_path = Path(raw_path)
        self.output_dir = Path(output_dir)
        self.use_gan = use_gan
        self.gan_epochs = gan_epochs
        self.n_synthetic = n_synthetic

        self.logger = setup_logging(log_level)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.raw_df: Optional[pd.DataFrame] = None
        self.clean_df: Optional[pd.DataFrame] = None
        self.time_df: Optional[pd.DataFrame] = None
        self.wavelet_df: Optional[pd.DataFrame] = None
        self.physical_df: Optional[pd.DataFrame] = None
        self.labeled_df: Optional[pd.DataFrame] = None
        self.final_df: Optional[pd.DataFrame] = None

    # ── Step 1: Load & Inspect ──────────────────────────────────────

    def run_loading(self) -> pd.DataFrame:
        """Bước 1: Tải và kiểm tra dữ liệu thô."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: DATA LOADING & INSPECTION")
        self.logger.info("=" * 60)

        self.raw_df = load_steel_data(self.raw_path)
        report = inspect_data(self.raw_df)
        self.logger.info(f"Shape: {report['shape']}")
        self.logger.info(f"Duplicates: {report['duplicates']}")
        self.logger.info(f"Missing values: {report['missing_count']}")
        return self.raw_df

    # ── Step 2: Clean ───────────────────────────────────────────────

    def run_cleaning(self) -> pd.DataFrame:
        """Bước 2: Làm sạch dữ liệu."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: DATA CLEANING")
        self.logger.info("=" * 60)

        self.clean_df, report = clean_data(self.raw_df)
        self.logger.info(f"Cleaning report: {report}")

        save_data(self.clean_df, self.output_dir / "steel_clean.csv")
        self.logger.info(f"Clean data saved → {self.output_dir / 'steel_clean.csv'}")
        return self.clean_df

    # ── Step 3: Time-Domain Features ────────────────────────────────

    def run_time_features(self) -> pd.DataFrame:
        """Bước 3: Trích xuất đặc trưng miền thời gian (lag, rolling, trig)."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: TIME-DOMAIN FEATURE ENGINEERING")
        self.logger.info("=" * 60)

        self.time_df = build_time_features(self.clean_df, target_col="Usage_kWh")
        self.logger.info(f"Columns after Time features: {len(self.time_df.columns)}")
        return self.time_df

    # ── Step 4: Frequency-Domain Features (Wavelet) ─────────────────

    def run_wavelet_features(self) -> pd.DataFrame:
        """Bước 4: Trích xuất đặc trưng Wavelet (DWT Daubechies)."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 4: FREQUENCY-DOMAIN FEATURE EXTRACTION (DWT)")
        self.logger.info("=" * 60)

        target_col = "Usage_kWh"
        wavelet_feats = rolling_wavelet_features(
            self.time_df, target_col=target_col, window=64
        )
        self.wavelet_df = pd.concat([self.time_df, wavelet_feats], axis=1)
        self.logger.info(f"Columns after Wavelet: {len(self.wavelet_df.columns)}")
        return self.wavelet_df

    # ── Step 5: Physical-Domain Features ────────────────────────────

    def run_physical_features(self) -> pd.DataFrame:
        """Bước 5: Trích xuất đặc trưng vật lý (Apparent Power S, Phase Angle φ)."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 5: PHYSICAL-DOMAIN FEATURE EXTRACTION")
        self.logger.info("=" * 60)

        self.physical_df = build_physical_features(self.wavelet_df)
        self.logger.info(f"Columns after Physical: {len(self.physical_df.columns)}")
        return self.physical_df

    # ── Step 6: Anomaly Labeling ────────────────────────────────────

    def run_anomaly_labeling(self) -> pd.DataFrame:
        """Bước 6: Gán nhãn bất thường (Idling, Leakage, Overload)."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 6: ANOMALY LABELING")
        self.logger.info("=" * 60)

        self.labeled_df = label_all_anomalies(self.physical_df)

        n_idling = self.labeled_df["anomaly_idling"].sum()
        n_leakage = self.labeled_df["anomaly_leakage"].sum()
        n_overload = self.labeled_df["anomaly_overload"].sum()
        self.logger.info(f"Idling: {n_idling} | Leakage: {n_leakage} | Overload: {n_overload}")
        return self.labeled_df

    # ── Step 7: GAN Augmentation (Optional) ─────────────────────────

    def run_gan_augmentation(self) -> pd.DataFrame:
        """Bước 7 (tùy chọn): Tăng cường dữ liệu bằng GAN."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 7: GAN AUGMENTATION")
        self.logger.info("=" * 60)

        from src.gan_augmentation import train_gan, generate_synthetic_samples
        from sklearn.preprocessing import MinMaxScaler

        numeric_cols = self.labeled_df.select_dtypes(include=[np.number]).columns.tolist()
        data_array = self.labeled_df[numeric_cols].dropna().values

        scaler = MinMaxScaler(feature_range=(-1, 1))
        data_scaled = scaler.fit_transform(data_array)

        generator, _ = train_gan(
            data_scaled,
            latent_dim=100,
            epochs=self.gan_epochs,
            batch_size=64,
        )

        synthetic_scaled = generate_synthetic_samples(
            generator, n_samples=self.n_synthetic, latent_dim=100
        )
        synthetic = scaler.inverse_transform(synthetic_scaled)
        synthetic_df = pd.DataFrame(synthetic, columns=numeric_cols)

        save_data(synthetic_df, self.output_dir / "steel_synthetic_gan.csv")
        self.logger.info(
            f"Synthetic data ({self.n_synthetic} samples) saved → "
            f"{self.output_dir / 'steel_synthetic_gan.csv'}"
        )

        self.final_df = pd.concat(
            [self.labeled_df[numeric_cols], synthetic_df], ignore_index=True
        )
        return self.final_df

    # ── Full Pipeline ───────────────────────────────────────────────

    def run_pipeline(self) -> pd.DataFrame:
        """Chạy toàn bộ pipeline đầu-cuối."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING DS108-ELECTRIMIGHT PIPELINE")
        self.logger.info("=" * 60)

        self.run_loading()
        self.run_cleaning()
        self.run_time_features()
        self.run_wavelet_features()
        self.run_physical_features()
        self.run_anomaly_labeling()

        if self.use_gan:
            self.run_gan_augmentation()
        else:
            self.final_df = self.labeled_df

        save_data(self.final_df, self.output_dir / "steel_final.csv")

        self.logger.info("=" * 60)
        self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        self.logger.info(f"Final dataset shape: {self.final_df.shape}")
        self.logger.info("=" * 60)
        return self.final_df


def main():
    """Chạy pipeline với cấu hình mặc định."""
    pipeline = ElectrimightPipeline(
        log_level="INFO",
        use_gan=False,
    )
    final_data = pipeline.run_pipeline()

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Final dataset shape: {final_data.shape}")
    print("=" * 60)


if __name__ == "__main__":
    main()
