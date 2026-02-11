"""
VN30 Data Preprocessing Pipeline

Module này chứa pipeline chính để xử lý dữ liệu VN30 từ đầu đến cuối.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd
import numpy as np

# Import các module từ project
from src.data_collection import collect_all_vn30
from src.data_quality import assess_data_quality, generate_quality_report
from src.data_cleaning import (
    handle_missing_values_advanced,
    detect_outliers_isolation_forest,
    validate_ohlc_logic
)
from src.feature_engineering import (
    create_technical_indicators,
    create_lag_features,
    create_datetime_features,
    create_macro_features
)
from src.utils import setup_logging, save_data, load_data


class VN30Pipeline:
    """
    Pipeline chính để xử lý dữ liệu VN30
    
    Workflow:
    1. Data Collection
    2. Data Quality Assessment
    3. Data Cleaning
    4. Feature Engineering
    5. Data Transformation
    6. Save Results
    """
    
    def __init__(self, 
                 start_date: str = "2015-01-01",
                 end_date: str = "2025-12-31",
                 output_dir: str = "data",
                 log_level: str = "INFO"):
        """
        Khởi tạo pipeline
        
        Args:
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            output_dir: Thư mục lưu output
            log_level: Level của logging (DEBUG, INFO, WARNING, ERROR)
        """
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = Path(output_dir)
        
        # Setup logging
        self.logger = setup_logging(log_level)
        self.logger.info("Initialized VN30 Pipeline")
        
        # Tạo thư mục nếu chưa tồn tại
        (self.output_dir / "raw").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "interim").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "processed").mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.raw_data = None
        self.clean_data = None
        self.featured_data = None
        self.final_data = None
        
    def run_data_collection(self) -> pd.DataFrame:
        """
        Bước 1: Thu thập dữ liệu
        
        Returns:
            DataFrame chứa dữ liệu thô
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: DATA COLLECTION")
        self.logger.info("=" * 60)
        
        try:
            # Thu thập dữ liệu VN30
            self.logger.info(f"Collecting VN30 data from {self.start_date} to {self.end_date}")
            self.raw_data = collect_all_vn30(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Lưu raw data
            raw_path = self.output_dir / "raw" / "vn30_raw.csv"
            save_data(self.raw_data, raw_path)
            self.logger.info(f"Raw data saved to {raw_path}")
            
            # Log statistics
            self.logger.info(f"Total records: {len(self.raw_data):,}")
            self.logger.info(f"Date range: {self.raw_data['time'].min()} to {self.raw_data['time'].max()}")
            self.logger.info(f"Tickers: {self.raw_data['ticker'].nunique()}")
            
            return self.raw_data
            
        except Exception as e:
            self.logger.error(f"Error in data collection: {str(e)}")
            raise
    
    def run_quality_assessment(self) -> Dict:
        """
        Bước 2: Đánh giá chất lượng dữ liệu
        
        Returns:
            Dictionary chứa kết quả đánh giá
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: DATA QUALITY ASSESSMENT")
        self.logger.info("=" * 60)
        
        try:
            # Assess quality
            quality_metrics = assess_data_quality(self.raw_data)
            
            # Generate report
            report_path = "reports/data_quality_reports/quality_report.html"
            generate_quality_report(self.raw_data, output_path=report_path)
            
            self.logger.info("Quality Assessment Results:")
            for metric, value in quality_metrics.items():
                self.logger.info(f"  {metric}: {value:.2f}%")
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error in quality assessment: {str(e)}")
            raise
    
    def run_data_cleaning(self) -> pd.DataFrame:
        """
        Bước 3: Làm sạch dữ liệu
        
        Returns:
            DataFrame đã được làm sạch
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: DATA CLEANING")
        self.logger.info("=" * 60)
        
        try:
            # Validate OHLC logic
            self.logger.info("Validating OHLC logic...")
            self.raw_data = validate_ohlc_logic(self.raw_data)
            
            # Handle missing values
            self.logger.info("Handling missing values with MICE...")
            self.clean_data, imputation_report = handle_missing_values_advanced(
                self.raw_data
            )
            
            # Detect outliers
            self.logger.info("Detecting outliers with Isolation Forest...")
            self.clean_data = detect_outliers_isolation_forest(self.clean_data)
            
            # Lưu clean data
            clean_path = self.output_dir / "interim" / "vn30_clean.csv"
            save_data(self.clean_data, clean_path)
            self.logger.info(f"Clean data saved to {clean_path}")
            
            return self.clean_data
            
        except Exception as e:
            self.logger.error(f"Error in data cleaning: {str(e)}")
            raise
    
    def run_feature_engineering(self) -> pd.DataFrame:
        """
        Bước 4: Feature Engineering
        
        Returns:
            DataFrame với features mới
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 4: FEATURE ENGINEERING")
        self.logger.info("=" * 60)
        
        try:
            # Technical indicators
            self.logger.info("Creating technical indicators...")
            self.featured_data = create_technical_indicators(self.clean_data)
            
            # Lag features
            self.logger.info("Creating lag features...")
            self.featured_data = create_lag_features(self.featured_data)
            
            # Datetime features
            self.logger.info("Creating datetime features...")
            self.featured_data = create_datetime_features(self.featured_data)
            
            # Macro features
            self.logger.info("Creating macro features...")
            self.featured_data = create_macro_features(self.featured_data)
            
            # Lưu featured data
            featured_path = self.output_dir / "interim" / "vn30_features.csv"
            save_data(self.featured_data, featured_path)
            self.logger.info(f"Featured data saved to {featured_path}")
            
            self.logger.info(f"Total features: {len(self.featured_data.columns)}")
            
            return self.featured_data
            
        except Exception as e:
            self.logger.error(f"Error in feature engineering: {str(e)}")
            raise
    
    def run_transformation(self) -> pd.DataFrame:
        """
        Bước 5: Transformation và Scaling
        
        Returns:
            DataFrame đã được transform
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 5: DATA TRANSFORMATION")
        self.logger.info("=" * 60)
        
        try:
            from sklearn.preprocessing import StandardScaler
            
            # Identify numeric columns to scale
            numeric_cols = self.featured_data.select_dtypes(
                include=[np.number]
            ).columns.tolist()
            
            # Exclude certain columns
            exclude_cols = ['time', 'ticker', 'is_outlier', 'is_imputed', 'ohlc_valid']
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
            
            # Scale per ticker
            self.final_data = self.featured_data.copy()
            scaler = StandardScaler()
            
            for ticker in self.final_data['ticker'].unique():
                mask = self.final_data['ticker'] == ticker
                self.final_data.loc[mask, numeric_cols] = scaler.fit_transform(
                    self.final_data.loc[mask, numeric_cols]
                )
            
            # Lưu final data
            final_path = self.output_dir / "processed" / "vn30_final.csv"
            save_data(self.final_data, final_path)
            self.logger.info(f"Final data saved to {final_path}")
            
            return self.final_data
            
        except Exception as e:
            self.logger.error(f"Error in transformation: {str(e)}")
            raise
    
    def run_pipeline(self) -> pd.DataFrame:
        """
        Chạy toàn bộ pipeline
        
        Returns:
            DataFrame cuối cùng
        """
        self.logger.info("=" * 60)
        self.logger.info("STARTING VN30 DATA PREPROCESSING PIPELINE")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Data Collection
            self.run_data_collection()
            
            # Step 2: Quality Assessment
            self.run_quality_assessment()
            
            # Step 3: Data Cleaning
            self.run_data_cleaning()
            
            # Step 4: Feature Engineering
            self.run_feature_engineering()
            
            # Step 5: Transformation
            self.run_transformation()
            
            self.logger.info("=" * 60)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 60)
            
            return self.final_data
            
        except Exception as e:
            self.logger.error("=" * 60)
            self.logger.error("PIPELINE FAILED")
            self.logger.error("=" * 60)
            self.logger.error(f"Error: {str(e)}")
            raise


def main():
    """
    Main function để chạy pipeline
    """
    # Khởi tạo pipeline
    pipeline = VN30Pipeline(
        start_date="2015-01-01",
        end_date="2025-12-31",
        output_dir="data",
        log_level="INFO"
    )
    
    # Chạy pipeline
    final_data = pipeline.run_pipeline()
    
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total records: {len(final_data):,}")
    print(f"Total features: {len(final_data.columns)}")
    print(f"Tickers: {final_data['ticker'].nunique()}")
    print(f"Date range: {final_data['time'].min()} to {final_data['time'].max()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
