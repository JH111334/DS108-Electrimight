# DS108-Electritight

Dự án tiền xử lý và mô hình hóa dữ liệu tiêu thụ điện năng ngành thép (Steel Industry Energy Consumption) sử dụng biến đổi Wavelet và tăng cường dữ liệu GAN, đồng thở tích hợp dữ liệu thở tiết ngoại sinh (exogenous variables) và phát hiện bất thường dựa trên chuẩn ngành.

---

## Giới Thiệu

**DS108-Electritight** là dự án học máy tập trung vào bộ dữ liệu `Steel_industry_data.csv` — ghi lại mức tiêu thụ điện năng theo thở gian thực của một nhà máy thép Hàn Quốc. Mục tiêu của dự án bao gồm:

- **EDA & Baseline**: Phân tích khám phá dữ liệu và xây dựng mô hình nền.
- **Data Quality Audit**: Kiểm tra sâu (deep audit) để phát hiện các vấn đề ẩn trong dữ liệu thô.
- **Feature Engineering**: Trích xuất đặc trưng toán học nâng cao bằng biến đổi Wavelet (PyWavelets), đặc trưng miền thở gian, đặc trưng vật lý (S, φ).
- **Weather Integration**: Thu thập dữ liệu thở tiết từ Open-Meteo API, resample và tích hợp vào bộ dữ liệu gốc.
- **Anomaly Detection**: Gán nhãn bất thường (Idling, Leakage, Overload) dựa trên chuẩn ngành IEEE 519 / ISO 50001 với Confidence Score và giải thích.
- **GAN Augmentation**: Tăng cường tập dữ liệu bằng mô hình sinh (Generative Adversarial Network) với TensorFlow/Keras.

---

## Cấu Trúc Kho

```
DS108-Electritight/
|
├── data/
│   ├── bronze/                     # [CHỈ ĐỌC] Tệp gốc + DATA_PROVENANCE.md
│   │   ├── Steel_industry_data.csv
│   │   ├── weather_gwangyang_2018.csv
│   │   └── DATA_PROVENANCE.md      # Log thu thập & audit dữ liệu thô
│   ├── silver/                     # Dữ liệu sạch/intermediate
│       ├── steel_clean.csv
│   └── gold/                       # Dữ liệu thành phẩm
│       └── steel_final.csv
│
├── notebooks/
│   ├── 01_data_profiling_and_eda.ipynb
│   ├── 01_eda_and_baseline.ipynb
│   ├── 02_feature_engineering_math.ipynb
│   └── 03_gan_augmentation.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # Tải, kiểm tra và làm sạch dữ liệu thô
│   ├── data_quality_audit.py       # Audit 5 nhóm vấn đề chất lượng dữ liệu
│   ├── time_features.py            # Đặc trưng miền thở gian (lag, rolling, trig)
│   ├── wavelet_features.py         # Trích xuất đặc trưng Wavelet (DWT)
│   ├── physical_features.py        # Đặc trưng vật lý (S, φ)
│   ├── weather.py                  # Thu thập dữ liệu thở tiết từ API (retry, batching)
│   ├── weather_loader.py           # Load, resample, feature engineering, merge weather
│   ├── anomaly_labels.py           # Gán nhãn bất thường với Confidence Score
│   ├── gan_augmentation.py         # Định nghĩa và huấn luyện mô hình GAN
│   ├── misc.py                     # Tham chiếu TensorFlow GAN (archive)
│   ├── pipeline.py                 # Pipeline đầu-cuối tích hợp tất cả bước
│   └── utils.py                    # Tiện ích dùng chung (logging, I/O, constants)
│
├── metadata/
│   ├── dataset/                    # Codebook, datasheet, labeling guideline
│   └── pipeline/                   # Stats, ablation, verification, insights
│
├── tests/
│   └── __init__.py
│
├── MODV1.md                        # Tài liệu tích hợp dữ liệu thở tiết
├── requirements.txt                # Phiên bản thư viện được cố định
└── README.md                       # Tài liệu này
```

> **Quy tắc bất biến**: Thư mục `data/bronze/` là **CHỈ ĐỌC**. Không có kịch bản hay notebook nào được phép ghi đè lên thư mục này. Mọi dữ liệu thành phẩm được lưu vào `data/gold/`, metadata được lưu vào `metadata/`.

---

## Mục Tiêu Tiền Xử Lý

| Bước | Mô Tả |
|------|-------|
| 1. Tải dữ liệu | Đọc `Steel_industry_data.csv`, kiểm tra kiểu dữ liệu, audit chất lượng |
| 2. Làm sạch | Loại trùng lặp, nội suy, scale PF từ % về hệ số, xác thực vật lý |
| 3. Weather Integration | Fetch API, resample 1h -> 15min, engineer 7 features, merge |
| 4. Time Features | Lag, rolling stats, trigonometric encoding |
| 5. Wavelet Features | DWT (Discrete Wavelet Transform) Daubechies-4 |
| 6. Physical Features | Công suất biểu kiến S, góc lệch pha φ |
| 7. Anomaly Detection | Idling (IEEE 519), Leakage (ISO 50001), Overload (Tukey/IEEE) |
| 8. GAN Augmentation | Sinh dữ liệu tổng hợp cân bằng lớp (tùy chọn) |
| 9. Lưu kết quả | Xuất tệp `.csv` vào `data/processed/` |

---

## Hướng Dẫn Tái Lập Môi Trường

### Yêu cầu
- Python 3.9+
- pip hoặc conda

### Cài đặt

```bash
# 1. Clone kho
git clone https://github.com/JH111334/DS108-Electritight.git
cd DS108-Electritight

# 2. Tạo môi trường ảo
python -m venv venv
source venv/bin/activate        # Linux/macOS
# hoặc: venv\Scripts\activate   # Windows

# 3. Cài đặt thư viện
pip install -r requirements.txt
```

### Đặt dữ liệu
Tải `Steel_industry_data.csv` và đặt vào:
```
data/bronze/Steel_industry_data.csv
```
> Tệp này có thể tải từ [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption).

---

## Quy Trình Chạy Pipeline

### Chạy notebook theo thứ tự

```bash
jupyter notebook
```

Mở và chạy tuần tự:
1. `notebooks/01_eda_and_baseline.ipynb`
2. `notebooks/02_feature_engineering_math.ipynb`
3. `notebooks/03_gan_augmentation.ipynb`

### Chạy pipeline bằng script Python

```bash
# Pipeline đầy đủ + metadata/insights
python -m src.run_all

# Chỉ chạy pipeline tạo gold dataset
python -m src.gold.pipeline

# Audit dữ liệu thô
python -m src.bronze.data_quality_audit

# Thu thập dữ liệu thở tiết (nếu cần fetch lại)
python -m src.silver.weather
```

---

## Dashboard Streamlit

Xem kết quả pipeline qua giao diện trực quan:

```bash
docker compose up streamlit
```

Mở `http://localhost:8505`. Xem thêm tại [`streamlit_ui/README.md`](streamlit_ui/README.md).

---

## Các Thư Viện Chính

| Thư Viện | Mục Đích |
|----------|----------|
| `pandas` | Xử lý và biến đổi dữ liệu dạng bảng |
| `numpy` | Tính toán số học mảng |
| `scikit-learn` | Tiền xử lý, đánh giá mô hình baseline |
| `PyWavelets` | Biến đổi Wavelet rời rạc (DWT) |
| `tensorflow` | Xây dựng và huấn luyện mô hình GAN |
| `matplotlib` / `seaborn` | Trực quan hóa dữ liệu |
| `requests` | Gọi API thở tiết Open-Meteo |

---

## Thành Viên Nhóm

Dự án DS108 — Môn Khoa Học Dữ Liệu
