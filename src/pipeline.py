"""
DS108-Electritight Pipeline

Pipeline đầu-cuối tích hợp toàn bộ bước xử lý dữ liệu Steel Industry:
1. Tải & kiểm tra dữ liệu thô (data/raw/ — chỉ đọc)
2. Làm sạch dữ liệu
3. Trích xuất đặc trưng Wavelet
4. Tăng cường dữ liệu GAN
5. Lưu kết quả vào data/processed/
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.data_loader import load_steel_data, clean_data, inspect_data
from src.wavelet_features import apply_wavelet_features_to_df, rolling_wavelet_features
from src.utils import setup_logging, save_data, load_data


PROCESSED_DIR = Path("data/processed")


class ElectritightPipeline:
    """
    Pipeline chính cho dự án DS108-Electritight.

    Workflow:
    1. Data Loading & Inspection
    2. Data Cleaning
    3. Wavelet Feature Extraction
    4. GAN Augmentation (tuỳ chọn)
    5. Save Results
    """

    def __init__(
        self,
        raw_path: str = "data/raw/Steel_industry_data.csv",
        output_dir: str = "data/processed",
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
        self.featured_df: Optional[pd.DataFrame] = None
        self.final_df: Optional[pd.DataFrame] = None

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

    def run_cleaning(self) -> pd.DataFrame:
        """Bước 2: Làm sạch dữ liệu."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: DATA CLEANING")
        self.logger.info("=" * 60)

        self.clean_df, report = clean_data(self.raw_df)
        self.logger.info(f"Cleaning report: {report}")

        save_data(self.clean_df, self.output_dir / "steel_clean.csv")
        self.logger.info(f"Clean data saved to {self.output_dir / 'steel_clean.csv'}")
        return self.clean_df

    def run_wavelet_features(self) -> pd.DataFrame:
        """Bước 3: Trích xuất đặc trưng Wavelet."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: WAVELET FEATURE EXTRACTION")
        self.logger.info("=" * 60)

        numeric_cols = self.clean_df.select_dtypes(include=[np.number]).columns.tolist()

        # Rolling wavelet features cho cột mục tiêu chính
        target_col = "Usage_kWh" if "Usage_kWh" in self.clean_df.columns else numeric_cols[0]
        wavelet_df = rolling_wavelet_features(
            self.clean_df, target_col=target_col, window=64
        )

        self.featured_df = pd.concat([self.clean_df, wavelet_df], axis=1)
        self.logger.info(f"Total features after Wavelet: {len(self.featured_df.columns)}")

        save_data(self.featured_df, self.output_dir / "steel_wavelet_features.csv")
        self.logger.info(
            f"Featured data saved to {self.output_dir / 'steel_wavelet_features.csv'}"
        )
        return self.featured_df

    def run_gan_augmentation(self) -> pd.DataFrame:
        """Bước 4 (tuỳ chọn): Tăng cường dữ liệu bằng GAN."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 4: GAN AUGMENTATION")
        self.logger.info("=" * 60)

        from src.gan_augmentation import train_gan, generate_synthetic_samples

        numeric_cols = self.featured_df.select_dtypes(include=[np.number]).columns.tolist()
        data_array = self.featured_df[numeric_cols].dropna().values

        # Chuẩn hóa về [-1, 1] cho GAN
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
            f"Synthetic data ({self.n_synthetic} samples) saved to "
            f"{self.output_dir / 'steel_synthetic_gan.csv'}"
        )

        # Gộp dữ liệu thực và tổng hợp
        self.final_df = pd.concat(
            [self.featured_df[numeric_cols], synthetic_df], ignore_index=True
        )
        return self.final_df

    def run_pipeline(self) -> pd.DataFrame:
        """Chạy toàn bộ pipeline đầu-cuối."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING DS108-ELECTRITIGHT PIPELINE")
        self.logger.info("=" * 60)

        self.run_loading()
        self.run_cleaning()
        self.run_wavelet_features()

        if self.use_gan:
            self.run_gan_augmentation()
        else:
            self.final_df = self.featured_df

        save_data(self.final_df, self.output_dir / "steel_final.csv")

        self.logger.info("=" * 60)
        self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        self.logger.info(f"Final dataset shape: {self.final_df.shape}")
        self.logger.info("=" * 60)
        return self.final_df


def main():
    """Chạy pipeline với cấu hình mặc định."""
    pipeline = ElectritightPipeline(
        raw_path="data/raw/Steel_industry_data.csv",
        output_dir="data/processed",
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
