---
title: "DS108 Electrimight - Kế Hoạch Hành Động Tiếp Theo"
subtitle: "Báo Cáo và Code Project - Preprocessing and Constructing Dataset"
author: "Phân Tích Tự Động"
date: "2026-05-21"
---

# 1. TÓM TẮT PHÂN TÍCH TIÊU CHÍ

Đồ án DS108 - Preprocessing and Constructing Dataset được đánh giá trên 5 tiêu chí:

| Tiêu Chí | Trọng Số | Yêu Cầu Xuất Sắc |
|----------|----------|------------------|
| 1. Formulation and Complexity | 20% | Kiến trúc thu thập tinh vi, đa phương thức, ontology bao quát edge-cases |
| 2. Pre-processing and Methodological Rigor | 30% | ZERO DATA LEAKAGE, luận giải sâu sắc cho từng bước, SOTA algorithms |
| 3. Exploratory Data Analysis | 20% | Publication-ready figures, multivariate analysis, feature engineering bậc cao |
| 4. Engineering and Reproducibility | 15% | Modularization, data assertions, version control, clean code |
| 5. Scientific Reporting and Ethics | 15% | IEEE format, Datasheets for Datasets, văn phong học thuật |

**Giới hạn:** 20 trang đôi (IEEE 2 cột) hoặc 40 trang đơn.

**Triết lý:** Không phải huấn luyện mô hình ML, mà là xây dựng "nguyên liệu AI" (benchmark dataset) đạt chuẩn công nghiệp và học thuật.

---

# 2. TRẠNG THÁI HIỆN TẠI VÀ KHOẢNG TRỐNG (GAP ANALYSIS)

## Đã Có (Strengths)
- Pipeline OOP 7–8 bước: load → clean → weather → time → wavelet → physical → anomaly → GAN
- Data Quality Audit 5 nhóm kiểm tra (physical, temporal, categorical, measurement, derived)
- Data Provenance log chi tiết (UCI + Open-Meteo API)
- Labeling Guideline dựa trên IEEE 519, ISO 50001, IEC 61000
- 5 notebooks EDA, feature engineering, GAN
- Weather integration (API fetch + resample 1h → 15min)

## Còn Thiếu (Gaps)
- **Báo cáo:** Chưa có file .tex/.docx chính thức; chưa viết nội dung văn bản các section
- **GAN:** `gan_augmentation.py` vẫn là skeleton (NotImplementedError)
- **Tests:** `tests/` chỉ có `__init__.py`, chưa có unit tests
- **Data Assertions:** Chưa có module sanity checks tự động
- **Leakage Audit:** Chưa kiểm tra chính thức zero data leakage trong pipeline
- **Datasheets:** Chưa viết Datasheets for Datasets (bắt buộc)
- **Figures:** Chưa có figures publication-ready (≥300 DPI)
- **README:** Quá ngắn, chưa hướng dẫn A–Z
- **Requirements.txt:** Cần kiểm tra đầy đủ

---

# 3. VIỆC CẦN LÀM CHO BÁO CÁO IEEE

## 3.1. Viết Nội Dung Văn Bản

### Abstract (150–250 từ)
- 5 phần: Context → Problem → Method → Results → Significance
- Không có công thức, hình, bảng, trích dẫn
- 3–5 Keywords

### I. Introduction (tối đa 2 trang)
- Đoạn 1: Context (ngành thép + dự báo điện)
- Đoạn 2: Problem (thiếu features, thiếu nhãn, mất cân bằng)
- Đoạn 3: 3 Contributions (multi-domain features, physics-informed labels, GAN augmentation)
- Đoạn 4: Organization (liệt kê các section)
- Ít nhất 3–5 trích dẫn

### II. Related Work
- A. Industrial Energy Forecasting (3–4 refs)
- B. Wavelet Transform (3–4 refs)
- C. GAN and Data Augmentation (3–4 refs)
- TABLE I: Comparison of Related Works (có cột "Ours")
- Kết thúc bằng "gap" mà bài báo lấp đầy

### III. Methodology (trái tim báo cáo)
- A. Dataset Overview
- B. Data Preprocessing
- C. Time-Domain Features
- D. DWT Features (db4, level 3)
- E. Physical Features (S, φ)
- F. Anomaly Labeling (Idling, Leakage, Overload)
- G. GAN Augmentation
- H. Pipeline Integration
- Công thức đánh số từ (1) đến (13+)
- Ít nhất 3 bảng: DWT Features, Anomaly Rules, GAN Params

### IV. Dataset and Experimental Setup
- Hardware and Software
- Dataset splits (nếu có)
- Evaluation metrics cho GAN fidelity

### V. Results and Discussion
- A. Data Profiling (TABLE V)
- B. Feature Engineering Evaluation
- C. Anomaly Distribution (TABLE VI)
- D. GAN Augmentation Quality (TABLE VII)
- E. Comparative Analysis Raw vs Processed
- 4–6 figures, 4–5 tables

### VI. Conclusion
- Tóm tắt công trình
- 3 contributions dạng bullet
- Thừa nhận hạn chế
- 2–3 hướng phát triển
- **KHÔNG thêm thông tin mới**

### Appendix: Datasheets for Datasets (BẮT BUỘC)
- Theo chuẩn Gebru et al. 2021
- Trả lời 50+ câu hỏi: Motivation, Composition, Collection, Preprocessing, Uses, Distribution, Maintenance
- 5–6 trang

## 3.2. Tạo Figures Publication-Ready

| Figure | Nội Dung | Yêu Cầu Kỹ Thuật |
|--------|----------|-----------------|
| Fig. 1 | Pipeline Diagram | draw.io hoặc TikZ, vector format |
| Fig. 2 | Time-series + Annotations | 300 DPI, font ≥ 8 pt |
| Fig. 3 | Correlation Heatmap | 40+ features, không bị chữ chồng |
| Fig. 4 | DWT Decomposition | db4 level 3, cA3 + cD1–cD3 |
| Fig. 5 | S vs φ Scatter | Tô màu theo Load_Type |
| Fig. 6 | Anomaly Timeline | 3 loại anomaly trên cùng trục thời gian |
| Fig. 7 | PCA Real vs Synthetic | Overlay, legend rõ ràng |
| Fig. 8 | t-SNE Real vs Synthetic | |
| Fig. 9 | GAN Training Curves | D loss, G loss theo epoch |
| Fig. 10 | Distribution Comparison | KDE real vs synthetic |

## 3.3. Tạo Tables

- TABLE I: Comparison of Related Works
- TABLE II: DWT Feature Extracted
- TABLE III: Anomaly Labeling Rules
- TABLE IV: GAN Hyperparameters
- TABLE V: Descriptive Statistics
- TABLE VI: Anomaly Label Distribution
- TABLE VII: Real vs Synthetic Comparison
- TABLE VIII: Raw vs Processed Dataset Comparison

## 3.4. References
- Chọn 15–20 refs từ file `07_References_Bibliography.md`
- Đánh số lại theo thứ tự xuất hiện
- Định dạng IEEE chuẩn

---

# 4. VIỆC CẦN LÀM CHO CODE PROJECT

## 4.1. Ưu Tiên Cao Nhất: Kiểm Tra Data Leakage
- [ ] Audit rolling window: kiểm tra `center=True` / `center=False`
- [ ] Audit DWT window: đảm bảo không look-ahead quá `window/2`
- [ ] Giải thích trong báo cáo: scaler fit trên toàn bộ dữ liệu không gây leakage cho downstream vì downstream sẽ refit scaler riêng trên train split
- [ ] Tạo notebook `04_leakage_audit.ipynb`

## 4.2. Hoàn Thiện GAN Module
- [ ] Triển khai `build_generator`, `build_discriminator` trong `gan_augmentation.py`
- [ ] Thêm evaluation metrics: KS test, Wasserstein distance, MMD
- [ ] So sánh với SMOTE baseline
- [ ] Lưu synthetic data với metadata đầy đủ

## 4.3. Data Assertions and Sanity Checks
- [ ] Tạo `src/data_assertions.py`
- [ ] `assert_no_negative_usage(df)`
- [ ] `assert_pf_in_range(df, [0,1])`
- [ ] `assert_temporal_sorted(df)`
- [ ] `assert_anomaly_rate_below(df, threshold=0.10)`
- [ ] `assert_correlation_preserved(real_df, synthetic_df)`
- [ ] Tích hợp vào pipeline sau mỗi bước

## 4.4. Tests and Reproducibility
- [ ] Viết pytest cho `data_loader`, `time_features`, `physical_features`, `anomaly_labels`
- [ ] Tạo `tests/test_pipeline.py`
- [ ] Cập nhật `README.md` chi tiết (cài đặt, chạy pipeline, cấu trúc thư mục)
- [ ] Cập nhật `requirements.txt` (`pip freeze`)

## 4.5. Missingness Mechanism Analysis (Sáng Tạo)
- [ ] Phân tích `Q_lead = 0` (67.38%) như implicit missingness
- [ ] Giải thích MCAR / MAR / MNAR
- [ ] Ảnh hưởng đến tính toán `S` và `φ`

## 4.6. Feature Selection Định Lượng
- [ ] Mutual Information giữa engineered features và anomaly labels
- [ ] VIF (Variance Inflation Factor) cho physical features
- [ ] Tree-based feature importance (Random Forest đơn giản)

---

# 5. HƯỚNG SÁNG TẠO TIỀM NĂNG (BONUS)

## 5.1. Datasheets for Datasets (Bắt Buộc)
File: `docs/DATASHEETS_FOR_DATASETS.md` (5–6 trang)

## 5.2. Streamlit Dashboard (Bonus +0.5–1.0đ)
- Ứng dụng tương tác: upload CSV, chạy pipeline từng bước
- Trực quan anomaly, so sánh real vs synthetic
- File: `app.py`

## 5.3. Công Bố Kaggle / HuggingFace (Bonus +0.5đ)
- Đóng gói `steel_final.csv` + metadata + notebook hướng dẫn

## 5.4. Docker Container (Bonus)
- `Dockerfile` + `docker-compose` cho toàn bộ pipeline

## 5.5. LLM Integration (Bonus +0.5–1.0đ)
- Dùng LLM để generate explanation text cho anomaly
- Hoặc standardize Data Dictionary

---

# 6. LỊCH TRÌNH ĐỀ XUẤT

| Tuần | Công Việc | Mục Tiêu Đầu Ra |
|------|-----------|-----------------|
| 1 | Code: GAN, assertions, tests, leakage audit | Pipeline end-to-end không lỗi |
| 2 | Viết báo cáo: Abstract đến Conclusion | Đủ nội dung 15–18 trang đôi |
| 3 | Figures and Tables publication-ready | ≥ 10 figures, ≥ 8 tables |
| 4 | Datasheets + Sáng tạo + Review | Hoàn thiện rubric và bonus |
| 5 | Final review, format, export PDF | Nộp PDF + source + code link |

---

# 7. CHECKLIST TỔNG HỢP TRƯỚC KHI NỘP

- [ ] Báo cáo đúng format IEEE, font Times New Roman 10pt
- [ ] Abstract 150–250 từ, đủ 5 phần
- [ ] Không có data leakage trong preprocessing
- [ ] Mỗi figure/table được tham chiếu trong text
- [ ] References đánh số theo thứ tự xuất hiện
- [ ] Có Datasheets for Datasets trong Appendix
- [ ] Code chạy được từ A–Z (README đầy đủ)
- [ ] Không sửa dữ liệu thô bằng tay (`raw/` chỉ đọc)
- [ ] Không đạo văn (có trích dẫn nếu tham khảo code)
- [ ] File đặt tên: `DS108_Report_Electrimight_IEEE.pdf`

---

*Tài liệu được tạo tự động sau khi phân tích DS108 Final Project Capstone Guidelines và trạng thái hiện tại của dự án.*
