# Hướng Dẫn Trình Bày Hình Ảnh & Bảng Biểu — IEEE Format

> Hình ảnh và bảng biểu là "cửa sổ" giúp ngườii đọc hiểu nhanh kết quả. IEEE có quy tắc nghiêm ngặt về format.

---

## 1. Quy Tắc Chung

| Yếu tố | Quy định |
|--------|----------|
| **Độ phân giải hình** | ≥ 300 DPI (vector nếu có thể) |
| **Font trong hình** | Times New Roman hoặc Helvetica, ≥ 8 pt |
| **Kích thước hình** | Chiều rộng 1 cột (8.5 cm) hoặc 2 cột (17.5 cm) |
| **Màu sắc** | Đảm bảo vẫn đọc được khi in đen trắng |
| **Số hình/bảng** | Không giới hạn, nhưng mỗi cái phải có giá trị |

---

## 2. Figures (Hình Ảnh)

### 2.1 Quy Tắc Đánh Số & Caption
- Đánh số liên tục: **Fig. 1**, **Fig. 2**, **Fig. 3**...
- Caption đặt **BÊN DƯỚI** hình
- Cú pháp: `Fig. n. Mô tả đầy đủ.`
- Caption phải **tự giải thích** — không cần đọc text vẫn hiểu

### 2.2 Danh Sách Hình Gợi Ý Cho DS108

```
FIGURE GỢI Ý:

Fig. 1. Overall pipeline architecture of the proposed preprocessing 
framework, showing the flow from raw data ingestion through time-domain, 
wavelet, and physical feature extraction to final anomaly labeling and 
GAN augmentation.

Fig. 2. Time-series plot of Usage_kWh over a 7-day window, annotated 
with detected anomaly events (idling in yellow, overload in red).

Fig. 3. Correlation heatmap of engineered features, highlighting 
strong correlations between Usage_kWh, Apparent Power, and rolling 
statistics.

Fig. 4. Three-level DWT decomposition of Usage_kWh using db4 wavelet: 
(a) original signal, (b) approximation cA3, (c) detail cD3, 
(d) detail cD2, (e) detail cD1.

Fig. 5. Scatter plot of Apparent Power (S) versus Phase Angle (φ), 
colored by Load_Type. The elliptical region marks the anomaly cluster.

Fig. 6. Distribution of anomaly labels over time. Idling events 
concentrate during weekend night shifts; overload events align with 
peak weekday production hours.

Fig. 7. PCA visualization comparing real data (blue) and GAN-generated 
synthetic samples (orange), showing distributional overlap.

Fig. 8. t-SNE visualization of the augmented dataset, confirming that 
synthetic minority samples (red) intermingle with real anomaly points.

Fig. 9. GAN training curves: discriminator loss (solid) and generator 
loss (dashed) over 2000 epochs.

Fig. 10. Distribution comparison between real and synthetic data for 
(a) Usage_kWh, (b) Apparent Power, (c) Phase Angle.
```

### 2.3 Ví Dụ Trích Dẫn Hình Trong Text

```text
As depicted in Fig. 1, the proposed pipeline integrates four 
sequential stages. The DWT decomposition (Fig. 4) reveals that 
high-frequency transients are concentrated in cD1, whereas the 
slow-varying baseline is captured by cA3. Fig. 5 demonstrates 
that anomalous operations form a distinct cluster in the S–φ 
plane, validating the discriminative power of physical features.
```

---

## 3. Tables (Bảng Biểu)

### 3.1 Quy Tắc Đánh Số & Caption
- Đánh số liên tục: **TABLE I**, **TABLE II**, **TABLE III**...
- Caption đặt **BÊN TRÊN** bảng
- Cú pháp: `TABLE N: TITLE IN ALL CAPS`
- Sử dụng **ít đường kẻ** nhất có thể
- **Không** dùng đường kẻ dọc

### 3.2 Danh Sách Bảng Gợi Ý Cho DS108

```
TABLE GỢI Ý:

TABLE I: COMPARISON OF RELATED WORKS

TABLE II: DWT FEATURES EXTRACTED FROM EACH DECOMPOSITION LEVEL

TABLE III: ANOMALY LABELING RULES AND PHYSICAL CONDITIONS

TABLE IV: GAN HYPERPARAMETERS AND TRAINING CONFIGURATION

TABLE V: DESCRIPTIVE STATISTICS OF RAW DATASET

TABLE VI: ANOMALY LABEL DISTRIBUTION AND CLASS IMBALANCE RATIO

TABLE VII: STATISTICAL COMPARISON OF REAL VS. SYNTHETIC DATA

TABLE VIII: FEATURE COUNT AFTER EACH PIPELINE STAGE

TABLE IX: CORRELATION BETWEEN PHYSICAL FEATURES AND ANOMALY TYPES
```

### 3.3 Ví Dụ Format Bảng IEEE

```
TABLE V: DESCRIPTIVE STATISTICS OF RAW DATASET

Variable                    Mean      Std       Min       Max
---------------------------------------------------------------
Usage_kWh                   34.50     44.32     0.00      160.23
Reactive.Power_kVarh        12.34     15.67     0.00      89.45
Power_Factor                0.82      0.21      0.10      1.00
CO2(tCO2)                   0.015     0.019     0.000     0.070
NSM                         43200     25200     0         86340
---------------------------------------------------------------
```

> **Lưu ý**: Không có đường kẻ dọc. Chỉ có đường kẻ ngang phân cách header, body, và footer.

---

## 4. Công Thức Toán Học

### 4.1 Quy Tắc
- Đánh số liên tục, căn phải trong ngoặc đơn:
```
S = √(P² + Q²)                                      (1)
```
- Các biến phải được định nghĩa ngay sau công thức đầu tiên xuất hiện
- Dùng `equation` environment nếu dùng LaTeX

### 4.2 Danh Sách Công Thức Gợi Ý

```
(1)  Linear interpolation: 
     y(t) = y(t₁) + (y(t₂) - y(t₁)) × (t - t₁) / (t₂ - t₁)

(2)  Lag feature:
     x_lag(k) = x(t - k)

(3)  Rolling mean:
     μ_w(t) = (1/w) Σ_{i=0}^{w-1} x(t-i)

(4)  Rolling standard deviation:
     σ_w(t) = √[(1/w) Σ_{i=0}^{w-1} (x(t-i) - μ_w)²]

(5)  Cyclical encoding (sin):
     NSM_sin = sin(2π × NSM / 86400)

(6)  Cyclical encoding (cos):
     NSM_cos = cos(2π × NSM / 86400)

(7)  DWT decomposition:
     S(t) = cA_j(t) + Σ_{i=1}^{j} cD_i(t)

(8)  Apparent Power:
     S = √(P² + Q²)

(9)  Phase Angle:
     φ = arccos(PF)

(10) Idling anomaly:
     anomaly_idling = (Load_Type="Light_Load") ∧ (off-hours) 
                      ∧ (Usage>median) ∧ (PF<0.5)

(11) Leakage anomaly:
     anomaly_leakage = [(rolling_mean - baseline) / baseline] > 5%

(12) Overload anomaly:
     anomaly_overload = (Usage > Q3 + 3×IQR) ∧ (Q high) ∧ (PF < 0.7)

(13) GAN objective function:
     min_G max_D L(D,G) = E_x[ln D(x)] + E_z[ln(1-D(G(z)))]
```

---

## 5. Checklist Hình Ảnh & Bảng Biểu

- [ ] Tất cả hình ≥ 300 DPI hoặc vector format
- [ ] Font trong hình ≥ 8 pt, đọc được khi in đen trắng
- [ ] Mỗi figure có caption đặt bên dưới, tự giải thích được
- [ ] Mỗi table có caption đặt bên trên, ALL CAPS
- [ ] Không dùng đường kẻ dọc trong table
- [ ] Tất cả figure/table đều được tham chiếu ít nhất 1 lần trong text
- [ ] Công thức được đánh số và định nghĩa biến
- [ ] Đơn vị đo ghi rõ trong header bảng hoặc axis label
- [ ] Legend rõ ràng cho multi-series plots
- [ ] Axis labels có đơn vị (kWh, %, s, rad...)
