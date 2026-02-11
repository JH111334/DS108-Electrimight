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
