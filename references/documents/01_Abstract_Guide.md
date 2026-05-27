# Hướng Dẫn Viết Abstract — IEEE Format

> Abstract là "bản thu nhỏ" độc lập của toàn bộ báo cáo. Ngườii đọc thường đọc Abstract đầu tiên để quyết định có đọc tiếp hay không.

---

## 1. Quy Tắc Chung (IEEE)

| Yếu tố | Quy định |
|--------|----------|
| **Độ dài** | 150–250 từ (tối đa) |
| **Ngôi** | Ngôi thứ ba, thì quá khứ đơn (đã thực hiện) |
| **Tính độc lập** | Phải hiểu được mà **không cần đọc** bài báo |
| **Cấm** | KHÔNG được có: công thức toán, hình ảnh, bảng biểu, trích dẫn |
| **Từ khóa** | 3–5 từ khóa ngay sau Abstract |

---

## 2. Cấu Trúc 5 Phần Cổ Điển (Đề xuất)

```
[1] Bối cảnh & Động lực  → Tại sao chủ đề này quan trọng?
[2] Vấn đề nghiên cứu    → Thách thức/giới hạn hiện tại là gì?
[3] Phương pháp đề xuất  → Bạn đã làm gì?
[4] Kết quả chính        → Kết quả đạt được (số liệu nếu có)
[5] Ý nghĩa/Kết luận     → Đóng góp và tác động
```

---

## 3. Ví Dụ Abstract (Gợi Ý Cho DS108)

### Ví dụ 1 — Ngắn gọn (~180 từ)

```
Industrial electricity consumption forecasting and risk classification 
require high-quality datasets with rich features. This paper presents 
a comprehensive preprocessing pipeline for the Steel Industry Energy 
Consumption dataset, a real-world time-series dataset collected from 
a South Korean steel plant. We propose a multi-domain feature 
engineering framework that extracts time-domain statistics (lag and 
rolling features), frequency-domain characteristics via Discrete Wavelet 
Transform (DWT) with Daubechies-4 wavelets, and physical-domain 
derivatives including Apparent Power and Phase Angle. Furthermore, 
anomaly labels for idling, energy leakage, and local overload are 
generated using rule-based physical thresholds. To address class 
imbalance, a Generative Adversarial Network (GAN) is employed for 
synthetic data augmentation. The processed dataset expanded from 
7 original features to over 40 engineered features with three binary 
anomaly indicators. Experimental validation confirms that the 
extracted wavelet and physical features effectively capture 
non-stationary load behaviors and latent fault signatures, providing 
a robust foundation for downstream forecasting and anomaly 
detection models.

Keywords—Energy consumption, data preprocessing, discrete wavelet 
transform, feature engineering, generative adversarial network, 
anomaly detection, steel industry.
```

### Ví dụ 2 — Chi tiết hơn (~230 từ)

```
Accurate electricity demand forecasting and operational risk 
assessment in energy-intensive industries depend critically on 
well-constructed input datasets. Existing public datasets for 
steel industry energy consumption often lack derived physical 
features and explicit anomaly annotations, limiting the 
performance of supervised machine learning models. This study 
addresses this gap by developing an end-to-end preprocessing 
and feature engineering pipeline for the UCI Steel Industry 
Energy Consumption dataset. The pipeline comprises four stages: 
(1) data cleaning and temporal alignment; (2) time-domain 
feature extraction including lag variables (15-min to 24-h), 
rolling statistics (mean, standard deviation, skewness), and 
cyclical encoding of temporal variables; (3) frequency-domain 
decomposition using Discrete Wavelet Transform (DWT) at 3 
decomposition levels to isolate transient anomalies; and (4) 
physical-domain computation of Apparent Power (S) and Phase 
Angle (φ) to reveal hidden electrical faults. Additionally, 
three anomaly types—idling, gradual energy leakage, and local 
overload—are labeled via physics-informed thresholds. Finally, 
a fully connected GAN synthesizes 500 minority-class samples 
to mitigate severe class imbalance. The resulting dataset 
contains 40+ features and anomaly labels, ready for predictive 
modeling. This work demonstrates that integrating wavelet, 
physical, and generative features significantly enriches 
dataset expressiveness for industrial energy analytics.

Keywords—Steel industry, electricity forecasting, discrete wavelet 
transform, GAN data augmentation, feature engineering, anomaly 
labeling, energy risk classification.
```

---

## 4. Keywords Gợi Ý

Chọn **3–5 từ** từ danh sách sau, sắp xếp theo thứ tự bảng chữ cái:

- Anomaly detection
- Data augmentation
- Data preprocessing
- Discrete wavelet transform (DWT)
- Energy consumption
- Feature engineering
- GAN (Generative Adversarial Network)
- Load forecasting
- Risk classification
- Steel industry
- Time series

---

## 5. Những Câu "Vàng" Dùng Trong Abstract

| Mục đích | Câu gợi ý |
|----------|-----------|
| Bối cảnh | *"Accurate electricity demand forecasting in heavy industry requires high-quality, feature-rich datasets."* |
| Vấn đề | *"Existing datasets lack explicit anomaly annotations and derived physical features."* |
| Phương pháp | *"This paper presents an end-to-end preprocessing pipeline integrating time-domain, frequency-domain, and physical-domain feature extraction."* |
| DWT | *"Discrete Wavelet Transform with Daubechies-4 wavelet is applied to capture non-stationary transient behaviors."* |
| Physical features | *"Apparent Power (S) and Phase Angle (φ) are computed to expose hidden electrical stress conditions."* |
| Anomaly | *"Three anomaly classes—idling, leakage, and overload—are labeled using physics-informed rule engines."* |
| GAN | *"A Generative Adversarial Network generates synthetic samples to alleviate class imbalance."* |
| Kết quả | *"The enriched dataset contains 40+ engineered features, demonstrating improved separability in preliminary clustering experiments."* |
| Ý nghĩa | *"The proposed pipeline provides a robust foundation for downstream load forecasting and fault diagnosis models."* |

---

## 6. Checklist Abstract

- [ ] 150–250 từ (đếm kỹ)
- [ ] Không có công thức toán
- [ ] Không có hình/bảng
- [ ] Không có trích dẫn `[n]`
- [ ] Có đủ 5 phần: Context → Problem → Method → Results → Significance
- [ ] Ngôi thứ ba, thì quá khứ
- [ ] Có 3–5 Keywords ngay sau Abstract
- [ ] Keywords không trùng với từ trong tiêu đề quá nhiều
- [ ] Đọc lại: nếu chỉ đọc Abstract, có hiểu được bài báo không?
