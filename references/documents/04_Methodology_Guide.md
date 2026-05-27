# Hướng Dẫn Viết Methodology — IEEE Format

> Methodology là phần "trái tim" của báo cáo kỹ thuật. IEEE yêu cầu mô tả đủ chi tiết để người đọc có thể **tái lập (replicate)** công việc của bạn.

---

## 1. Cấu Trúc Đề Xuất Cho DS108

```
III. METHODOLOGY

    A. Dataset Overview
    B. Data Preprocessing Pipeline
    C. Time-Domain Feature Engineering
    D. Frequency-Domain Feature Extraction (DWT)
    E. Physical-Domain Feature Engineering
    F. Anomaly Labeling Strategy
    G. GAN-Based Data Augmentation
    H. Pipeline Integration
```

---

## 2. Chi Tiết Từng Subsection

### A. Dataset Overview
- Nguồn gốc: UCI Machine Learning Repository
- Tần suất: 15 phút
- Thờii gian thu thập: ghi rõ
- Các cột ban đầu: date, Usage_kWh, Lagging_Current_Reactive.Power_kVarh, 
  Leading_Current_Reactive.Power_kVarh, CO2(tCO2), Lagging_Current_Power_Factor, 
  Leading_Current_Power_Factor, NSM, WeekStatus, Day_of_week, Load_Type
- Số mẫu: ~35,000+ records

> **Gợi ý mở đầu:**
> *"The dataset used in this study is the Steel Industry Energy Consumption dataset [4], publicly available from the UCI Machine Learning Repository. It contains 35,040 observations recorded at 15-minute intervals from a South Korean steel manufacturing plant."*

---

### B. Data Preprocessing Pipeline
Mô tả 2 bước chính:

1. **Data Inspection**: kiểm tra shape, dtypes, missing values, duplicates
2. **Data Cleaning**:
   - Loại bỏ duplicates
   - Nội suy tuyến tính (linear interpolation) cho missing values — phù hợp chuỗi thời gian
   - Sắp xếp theo thời gian

**Công thức nội suy (nếu cần trình bày):**
```
y(t) = y(t₁) + (y(t₂) - y(t₁)) × (t - t₁) / (t₂ - t₁)          (1)
```

---

### C. Time-Domain Feature Engineering
Mô tả 3 nhóm đặc trưng:

#### 1) Lag Features
```
x_lag(k) = x(t - k)                                           (2)
```
với k ∈ {1, 2, 4, 96} tương ứng 15 phút, 30 phút, 1 giờ, 24 giờ.

#### 2) Rolling Window Statistics
```
μ_w(t) = (1/w) Σ_{i=0}^{w-1} x(t-i)                          (3)
σ_w(t) = √[(1/w) Σ_{i=0}^{w-1} (x(t-i) - μ_w)²]              (4)
```
với w ∈ {24, 48, 96} (6 giờ, 12 giờ, 24 giờ).

#### 3) Cyclical Encoding (NSM)
```
NSM_sin = sin(2π × NSM / 86400)                               (5)
NSM_cos = cos(2π × NSM / 86400)                               (6)
```

---

### D. Frequency-Domain Feature Extraction (DWT)

#### Lý thuyết DWT ngắn gọn:
DWT phân rã tín hiệu thành hệ số xấp xỉ (cA) và chi tiết (cD) qua các mức:
```
S(t) = cA_j(t) + Σ_{i=1}^{j} cD_i(t)                         (7)
```

#### Tham số sử dụng:
- **Wavelet**: Daubechies-4 (db4)
- **Level**: 3
- **Window**: 64 bước (16 giờ)

#### Đặc trưng trích xuất từ mỗi mức:
- Mean, Std, Energy, Max Absolute Value

**TABLE II gợi ý:**
```
TABLE II: DWT FEATURE EXTRACTED FROM EACH DECOMPOSITION LEVEL

| Decomposition | Coefficient | Features Extracted                  |
|---------------|-------------|-------------------------------------|
| Level 1       | cD3         | mean, std, energy, max_abs          |
| Level 2       | cD2         | mean, std, energy, max_abs          |
| Level 3       | cD1         | mean, std, energy, max_abs          |
| Approximation | cA3         | mean, std, energy, max_abs          |
```

---

### E. Physical-Domain Feature Engineering

#### 1) Apparent Power (S)
```
S = √(P² + Q²)                                                (8)
```
Trong đó:
- P = Usage_kWh (công suất tác dụng)
- Q = Lagging_Current_Reactive.Power_kVarh (công suất phản kháng)

#### 2) Phase Angle (φ)
```
φ = arccos(PF)                                                (9)
```
Trong đó PF = Lagging_Current_Power_Factor, được clip về [0, 1].

> **Giải thích ý nghĩa vật lý:** S quyết định khả năng chịu tải của hệ thống truyền tải. Khi P không đổi nhưng Q tăng (kẹt rô-to, rò rỉ từ), S phình to — báo động cháy nổ cáp điện. φ cung cấp thang đo tuyến tính sắc nét hơn PF.

---

### F. Anomaly Labeling Strategy

Mô tả 3 loại bất thường bằng bảng:

```
TABLE III: ANOMALY LABELING RULES

| Anomaly Type | Conditions                                | Physical Meaning            |
|--------------|-------------------------------------------|-----------------------------|
| Idling       | Light_Load ∧ off-hours ∧ Usage>median ∧  | Chạy không tải kéo dài      |
|              | PF < 0.5                                  | tiêu tốn điện               |
| Leakage      | Rolling mean > baseline + 5% (window=672) | Rò rỉ năng lượng tiệm tiến  |
| Overload     | Usage > Q3 + 3×IQR ∧ Q high ∧ PF < 0.7  | Quá tải cục bộ, sụp đổ PF   |
```

#### Chi tiết từng loại:

**Idling:**
```
anomaly_idling = (Load_Type = "Light_Load") ∧ 
                 (NSM < 21600 ∨ NSM > 75600 ∨ WeekStatus = "Weekend") ∧ 
                 (Usage_kWh > median) ∧ 
                 (PF < 0.5)                                           (10)
```

**Leakage (Concept Drift):**
```
anomaly_leakage = [(rolling_mean_672 - baseline) / baseline] > 5%    (11)
```

**Overload:**
```
anomaly_overload = (Usage_kWh > Q3 + 3×IQR) ∧ 
                   (Q > Q3_Q + 3×IQR_Q) ∧ 
                   (PF < 0.7)                                         (12)
```

---

### G. GAN-Based Data Augmentation

#### Kiến trúc GAN:

**Generator:**
```
Input: z ~ N(0, I) ∈ ℝ^{100}
  → Dense(128) → LeakyReLU(0.2) → BatchNorm
  → Dense(256) → LeakyReLU(0.2) → BatchNorm
  → Dense(512) → LeakyReLU(0.2) → BatchNorm
  → Dense(output_dim) → tanh
```

**Discriminator:**
```
Input: x ∈ ℝ^{output_dim}
  → Dense(512) → LeakyReLU(0.2) → Dropout(0.3)
  → Dense(256) → LeakyReLU(0.2) → Dropout(0.3)
  → Dense(128) → LeakyReLU(0.2)
  → Dense(1) → sigmoid
```

#### Hyperparameters:
```
TABLE IV: GAN HYPERPARAMETERS

| Parameter        | Value    | Description                     |
|------------------|----------|---------------------------------|
| Latent dim       | 100      | Chiều không gian ẩn z           |
| Epochs           | 2000     | Số epoch huấn luyện             |
| Batch size       | 64       | Kích thước batch                |
| Learning rate    | 0.0002   | Adam optimizer                  |
| Beta_1           | 0.5      | Adam momentum                   |
| n_synthetic      | 500      | Số mẫu sinh ra                  |
| Normalization    | [-1, 1]  | MinMaxScaler                    |
```

#### Hàm mất mát:
```
min_G max_D L(D,G) = E_{x~p_data}[ln D(x)] + E_{z~p_z}[ln(1-D(G(z)))]   (13)
```

---

### H. Pipeline Integration

Mô tả luồng tích hợp 7 bước:

```
Raw Data → [1] Load & Inspect → [2] Clean → [3] Time Features 
         → [4] Wavelet Features → [5] Physical Features 
         → [6] Anomaly Labels → [7] GAN Augmentation (optional)
         → Final Dataset
```

> Có thể dùng **Fig. 2** để vẽ sơ đồ pipeline.

---

## 3. Checklist Methodology

- [ ] Mỗi bước được giải thích rõ ràng, có thể replicate
- [ ] Công thức toán được đánh số liên tục, biến được định nghĩa
- [ ] Có ít nhất 2–3 bảng tham số (TABLE II, III, IV)
- [ ] Có sơ đồ pipeline (Fig. 2)
- [ ] Kiến trúc mô hình GAN được mô tả chi tiết
- [ ] Các ngưỡng (threshold) được lý giải vật lý
- [ ] DWT được giải thích ngắn gọn nhưng đầy đủ
- [ ] Có pseudo-code hoặc Python-like algorithm nếu cần
