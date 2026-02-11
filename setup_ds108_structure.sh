#!/bin/bash

# ============================================
# Setup DS108-VN30-Stock Project Structure
# ============================================

REPO_URL="https://github.com/JH111334/DS108-VN30-Stock.git"
REPO_NAME="DS108-VN30-Stock"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   DS108-VN30-Stock - Project Structure Setup          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Kiểm tra Git đã cài chưa
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Download from: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git found: $(git --version)"
echo ""

# Kiểm tra folder đã tồn tại chưa
if [ -d "$REPO_NAME" ]; then
    echo "⚠️  Directory '$REPO_NAME' already exists!"
    read -p "Remove and clone fresh? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$REPO_NAME"
        echo "✅ Removed existing directory"
    else
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Clone repository
echo "📥 Cloning repository from GitHub..."
git clone "$REPO_URL"

if [ $? -ne 0 ]; then
    echo "❌ Failed to clone repository"
    exit 1
fi

echo "✅ Repository cloned successfully"
echo ""

# Chuyển vào thư mục repo
cd "$REPO_NAME"

# ============================================
# Tạo cấu trúc thư mục
# ============================================

echo "📁 Creating directory structure..."

# Data directories
mkdir -p data/raw
mkdir -p data/interim
mkdir -p data/processed

# Notebooks directory
mkdir -p notebooks

# Source code directory
mkdir -p src

# Reports directories
mkdir -p reports/figures
mkdir -p reports/data_quality_reports

# Docs directories
mkdir -p docs/decisions

# Tests directory
mkdir -p tests

echo "   ✓ Directories created"

# ============================================
# Tạo .gitkeep files
# ============================================

echo "📌 Creating .gitkeep files..."

touch data/raw/.gitkeep
touch data/interim/.gitkeep
touch data/processed/.gitkeep
touch reports/figures/.gitkeep
touch reports/data_quality_reports/.gitkeep
touch tests/.gitkeep

echo "   ✓ .gitkeep files created"

# ============================================
# Tạo Python source files
# ============================================

echo "🐍 Creating Python source files..."

# src/__init__.py
cat > src/__init__.py << 'EOF'
"""
VN30 Data Preprocessing Package

Package chứa các module để xử lý dữ liệu VN30
"""

__version__ = "1.0.0"
__author__ = "VN30 Team"

from . import data_collection
from . import data_quality
from . import data_cleaning
from . import feature_engineering
from . import utils
from . import pipeline

__all__ = [
    'data_collection',
    'data_quality',
    'data_cleaning',
    'feature_engineering',
    'utils',
    'pipeline'
]
EOF

# src/data_collection.py
cat > src/data_collection.py << 'EOF'
"""
Data Collection Module

Module này chứa các function để thu thập dữ liệu VN30 từ Vnstock
"""

import pandas as pd
from typing import List, Optional


def collect_all_vn30(start_date: str = "2015-01-01", 
                     end_date: str = "2025-12-31") -> pd.DataFrame:
    """
    Thu thập dữ liệu OHLCV cho tất cả mã VN30
    
    Args:
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)
        
    Returns:
        DataFrame chứa dữ liệu OHLCV
    """
    # TODO: Implement data collection logic
    pass
EOF

# src/data_quality.py
cat > src/data_quality.py << 'EOF'
"""
Data Quality Assessment Module

Module này chứa các function để đánh giá chất lượng dữ liệu
"""

import pandas as pd
from typing import Dict


def assess_data_quality(df: pd.DataFrame) -> Dict:
    """
    Đánh giá chất lượng dữ liệu theo 6 dimensions
    
    Args:
        df: DataFrame cần đánh giá
        
    Returns:
        Dictionary chứa kết quả đánh giá
    """
    # TODO: Implement quality assessment
    pass


def generate_quality_report(df: pd.DataFrame, output_path: str) -> None:
    """
    Tạo báo cáo chất lượng dữ liệu
    
    Args:
        df: DataFrame cần đánh giá
        output_path: Đường dẫn file output
    """
    # TODO: Implement report generation
    pass
EOF

# src/data_cleaning.py
cat > src/data_cleaning.py << 'EOF'
"""
Data Cleaning Module

Module này chứa các function để làm sạch dữ liệu
"""

import pandas as pd
from typing import Tuple


def handle_missing_values_advanced(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Xử lý missing values bằng MICE
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        Tuple gồm (DataFrame đã xử lý, imputation report)
    """
    # TODO: Implement MICE imputation
    pass


def detect_outliers_isolation_forest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Phát hiện outliers bằng Isolation Forest
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        DataFrame với cột is_outlier
    """
    # TODO: Implement outlier detection
    pass


def validate_ohlc_logic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Kiểm tra logic OHLC (Open, High, Low, Close)
    
    Args:
        df: DataFrame cần kiểm tra
        
    Returns:
        DataFrame với cột ohlc_valid
    """
    # TODO: Implement OHLC validation
    pass
EOF

# src/feature_engineering.py
cat > src/feature_engineering.py << 'EOF'
"""
Feature Engineering Module

Module này chứa các function để tạo features mới
"""

import pandas as pd


def create_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        DataFrame với technical indicators
    """
    # TODO: Implement technical indicators
    pass


def create_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo lag features
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        DataFrame với lag features
    """
    # TODO: Implement lag features
    pass


def create_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo datetime features với cyclical encoding
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        DataFrame với datetime features
    """
    # TODO: Implement datetime features
    pass


def create_macro_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo macro features (VNIndex, beta, alpha, correlation)
    
    Args:
        df: DataFrame cần xử lý
        
    Returns:
        DataFrame với macro features
    """
    # TODO: Implement macro features
    pass
EOF

# src/utils.py
cat > src/utils.py << 'EOF'
"""
Utilities Module

Module này chứa các utility functions
"""

import logging
from pathlib import Path
import pandas as pd


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger object
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """
    Lưu DataFrame vào file
    
    Args:
        df: DataFrame cần lưu
        filepath: Đường dẫn file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def load_data(filepath: Path) -> pd.DataFrame:
    """
    Load DataFrame từ file
    
    Args:
        filepath: Đường dẫn file
        
    Returns:
        DataFrame
    """
    return pd.read_csv(filepath)
EOF

# src/pipeline.py
cat > src/pipeline.py << 'EOF'
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
EOF

# tests/__init__.py
cat > tests/__init__.py << 'EOF'
"""
Test Package
"""
EOF

echo "   ✓ Python files created"

# ============================================
# Tạo Jupyter notebooks
# ============================================

echo "📓 Creating Jupyter notebooks..."

create_notebook() {
    local filename=$1
    local title=$2
    
    cat > "$filename" << EOF
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# $title\\n",
    "\\n",
    "**Project**: VN30 Data Preprocessing\\n",
    "**Date**: $(date +%Y-%m-%d)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Import libraries\\n",
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "import matplotlib.pyplot as plt\\n",
    "import seaborn as sns\\n",
    "\\n",
    "%matplotlib inline\\n",
    "sns.set_style('whitegrid')"
   ],
   "outputs": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF
}

create_notebook "notebooks/01_data_collection.ipynb" "01 - Data Collection"
create_notebook "notebooks/02_data_quality_assessment.ipynb" "02 - Data Quality Assessment"
create_notebook "notebooks/03_data_cleaning.ipynb" "03 - Data Cleaning"
create_notebook "notebooks/04_feature_engineering.ipynb" "04 - Feature Engineering"
create_notebook "notebooks/05_eda.ipynb" "05 - Exploratory Data Analysis"

echo "   ✓ Notebooks created"

# ============================================
# Tạo các file cần thiết nếu chưa có
# ============================================

echo "📄 Creating project files..."

# requirements.txt (chỉ tạo nếu chưa có)
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'EOF'
# ============================================
# VN30 Data Preprocessing - Requirements
# ============================================

# ---------- Data Manipulation ----------
pandas>=1.5.0
numpy>=1.21.0

# ---------- Data Collection ----------
vnstock>=0.2.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0

# ---------- Data Quality & Preprocessing ----------
scikit-learn>=1.1.0
missingno>=0.5.0
pandas-profiling>=3.6.0
great-expectations>=0.17.0

# ---------- Visualization ----------
matplotlib>=3.5.0
seaborn>=0.12.0
plotly>=5.10.0

# ---------- Statistical Analysis ----------
scipy>=1.9.0
statsmodels>=0.13.0

# ---------- Technical Analysis ----------
ta>=0.10.0
TA-Lib>=0.4.24

# ---------- Jupyter Environment ----------
jupyter>=1.0.0
ipykernel>=6.15.0
ipython>=8.0.0

# ---------- Utilities ----------
pyyaml>=6.0
python-dotenv>=0.20.0
tqdm>=4.64.0
joblib>=1.2.0

# ---------- Testing ----------
pytest>=7.1.0
pytest-cov>=4.0.0

# ---------- Code Quality ----------
black>=22.0.0
flake8>=5.0.0
isort>=5.10.0

# ---------- Documentation ----------
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
EOF
    echo "   ✓ requirements.txt created"
else
    echo "   ⊙ requirements.txt already exists"
fi

# .gitignore (chỉ tạo nếu chưa có hoặc merge)
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
venv/
ENV/
env/

# Jupyter Notebook
.ipynb_checkpoints

# Data files
data/raw/*.csv
data/interim/*.csv
data/processed/*.csv
data/raw/*.parquet
data/interim/*.parquet
data/processed/*.parquet

# Keep structure
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep

# Reports
reports/*.html
reports/*.pdf
reports/figures/*.png
reports/figures/*.jpg

# Keep structure
!reports/figures/.gitkeep
!reports/data_quality_reports/.gitkeep

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Secrets
.env
*.secret
*credentials*
EOF
    echo "   ✓ .gitignore created"
else
    echo "   ⊙ .gitignore already exists"
fi

# data_dictionary.md
if [ ! -f "docs/data_dictionary.md" ]; then
    echo "   ⚠️  docs/data_dictionary.md not found - please add manually"
else
    echo "   ✓ data_dictionary.md exists"
fi

# methodology.md
if [ ! -f "docs/methodology.md" ]; then
    cat > docs/methodology.md << 'EOF'
# Methodology

## Tổng quan

Tài liệu này mô tả phương pháp luận được sử dụng trong project VN30 Data Preprocessing.

## 1. Data Collection

### Nguồn dữ liệu
- **Primary Source**: Vnstock API (TCBS)
- **Macro Data**: VNIndex, Gold Price, Interest Rate

## 2. Data Quality Assessment

### Dimensions đánh giá
1. Completeness
2. Uniqueness
3. Validity
4. Consistency
5. Accuracy
6. Timeliness

## 3. Data Cleaning

### Missing Values Handling
- Method: MICE (Multiple Imputation by Chained Equations)

### Outlier Detection
- Method: Isolation Forest

## 4. Feature Engineering

### Technical Indicators
- Moving Averages (SMA, EMA)
- Momentum Indicators (RSI, MACD)
- Volatility Indicators (Bollinger Bands, ATR)

## 5. Data Transformation

### Scaling
- Method: StandardScaler
- Applied per ticker
EOF
    echo "   ✓ methodology.md created"
else
    echo "   ⊙ methodology.md already exists"
fi

echo "   ✓ Project files created"

# ============================================
# Git operations
# ============================================

echo ""
echo "🔧 Adding changes to Git..."

git add .
git status

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║            ✨ SETUP COMPLETE! ✨                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Project structure created in: $REPO_NAME"
echo ""
echo "📍 Next steps:"
echo ""
echo "1. Review changes:"
echo "   cd $REPO_NAME"
echo "   git status"
echo ""
echo "2. Commit changes:"
echo "   git commit -m 'Add project structure: data, notebooks, src, reports, docs, tests'"
echo ""
echo "3. Push to GitHub:"
echo "   git push origin main"
echo ""
echo "4. Setup Python environment:"
echo "   python -m venv venv"
echo "   source venv/bin/activate  # Linux/Mac"
echo "   # or: venv\\Scripts\\activate  # Windows"
echo "   pip install -r requirements.txt"
echo ""
echo "5. Start working:"
echo "   jupyter notebook"
echo ""
echo "🚀 Happy coding!"
echo ""
