# DS108-Electritight

Dự án tiền xử lý và mô hình hóa dữ liệu tiêu thụ điện năng ngành thép (Steel Industry Energy Consumption) sử dụng biến đổi Wavelet và tăng cường dữ liệu GAN.

---

## Giới Thiệu

**DS108-Electritight** là dự án học máy tập trung vào bộ dữ liệu `Steel_industry_data.csv` — ghi lại mức tiêu thụ điện năng theo thời gian thực của một nhà máy thép Hàn Quốc. Mục tiêu của dự án bao gồm:

- **EDA & Baseline**: Phân tích khám phá dữ liệu và xây dựng mô hình nền.
- **Feature Engineering**: Trích xuất đặc trưng toán học nâng cao bằng biến đổi Wavelet (PyWavelets).
- **GAN Augmentation**: Tăng cường tập dữ liệu bằng mô hình sinh (Generative Adversarial Network) với TensorFlow/Keras.

---

## Cấu Trúc Kho

```
DS108-Electritight/
│
├── data/
│   ├── raw/                  # [CHỈ ĐỌC] Tệp gốc Steel_industry_data.csv
│   └── processed/            # Dữ liệu đã qua toàn bộ pipeline (làm sạch, Wavelet, GAN)
│
├── notebooks/
│   ├── 01_eda_and_baseline.ipynb          # Phân tích khám phá & mô hình cơ sở
│   ├── 02_feature_engineering_math.ipynb  # Biến đổi Wavelet & đặc trưng toán học
│   └── 03_gan_augmentation.ipynb          # Tăng cường dữ liệu bằng GAN
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Tải, kiểm tra và làm sạch dữ liệu thô
│   ├── wavelet_features.py   # Trích xuất đặc trưng Wavelet
│   ├── gan_augmentation.py   # Định nghĩa và huấn luyện mô hình GAN
│   ├── pipeline.py           # Pipeline đầu-cuối tích hợp tất cả bước
│   └── utils.py              # Các tiện ích dùng chung (logging, I/O)
│
├── tests/
│   └── __init__.py
│
├── requirements.txt          # Phiên bản thư viện được cố định
└── README.md                 # Tài liệu này
```

> **Quy tắc bất biến**: Thư mục `data/raw/` là **CHỈ ĐỌC**. Không có kịch bản hay notebook nào được phép ghi đè lên thư mục này. Mọi dữ liệu đã xử lý đều được lưu vào `data/processed/`.

---

## Mục Tiêu Tiền Xử Lý

| Bước | Mô Tả |
|------|--------|
| 1. Tải dữ liệu | Đọc `Steel_industry_data.csv`, kiểm tra kiểu dữ liệu, xử lý giá trị thiếu |
| 2. EDA & Baseline | Thống kê mô tả, trực quan hóa, xây dựng mô hình hồi quy/phân loại cơ sở |
| 3. Feature Engineering | Áp dụng DWT (Discrete Wavelet Transform) để trích xuất đặc trưng tần số-thời gian |
| 4. GAN Augmentation | Huấn luyện GAN để sinh dữ liệu chuỗi thời gian tổng hợp cân bằng lớp |
| 5. Lưu kết quả | Xuất tệp `.csv` / `.parquet` vào `data/processed/` |

---

## Hướng Dẫn Tái Lập Môi Trường

### Yêu cầu
- Python 3.9+
- pip hoặc conda

### Cài đặt

```bash
# 1. Clone kho (sau khi repo được đổi tên sang DS108-Electritight trên GitHub)
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
data/raw/Steel_industry_data.csv
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
python -m src.pipeline
```

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

---

## Thành Viên Nhóm

Dự án DS108 — Môn Khoa Học Dữ Liệu
