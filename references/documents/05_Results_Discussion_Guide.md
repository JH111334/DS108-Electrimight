# Hướng Dẫn Viết Results & Discussion — IEEE Format

> Results trình bày **dữ kiện**; Discussion giải thích **ý nghĩa** của dữ kiện đó. Trong IEEE, hai phần này thường gộp chung thành **"Results and Discussion"**.

---

## 1. Cấu Trúc Đề Xuất

```
V. RESULTS AND DISCUSSION

    A. Data Profiling and Preprocessing Results
    B. Feature Engineering Evaluation
    C. Anomaly Label Distribution
    D. GAN Augmentation Quality Assessment
    E. Comparative Analysis
```

---

## 2. Hướng Dẫn Từng Subsection

### A. Data Profiling and Preprocessing Results

**Nội dung cần trình bày:**
- Thống kê mô tả dataset gốc (TABLE V)
- Số lượng duplicates đã xóa
- Số lượng missing values đã nội suy
- Phân phối các biến chính (Fig. 3 — histogram)

**TABLE V gợi ý:**
```
TABLE V: DESCRIPTIVE STATISTICS OF RAW DATASET

| Variable               | Mean    | Std     | Min     | Max     | Missing |
|------------------------|---------|---------|---------|---------|---------|
| Usage_kWh              | 34.50   | 44.32   | 0.00    | 160.23  | 0       |
| Reactive.Power_kVarh   | 12.34   | 15.67   | 0.00    | 89.45   | 0       |
| Power_Factor           | 0.82    | 0.21    | 0.10    | 1.00    | 0       |
| CO2(tCO2)              | 0.015   | 0.019   | 0.000   | 0.070   | 0       |
| NSM                    | 43200   | 25200   | 0       | 86340   | 0       |
```

**Gợi ý nhận xét:**
> *"The raw dataset contains 35,040 records with no missing values. Usage_kWh exhibits high variance (σ = 44.32), reflecting the heterogeneous operational modes of the steel plant."*

---

### B. Feature Engineering Evaluation

**Nội dung cần trình bày:**
1. **Time-domain features**: số lượng features tạo ra, tương quan với target
2. **DWT features**: minh họa decomposition (Fig. 4 — cA3 và cD1-cD3)
3. **Physical features**: phân phối S và φ (Fig. 5)

**Các hình gợi ý:**
- Fig. 3: Heatmap tương quan giữa các features
- Fig. 4: DWT decomposition của một đoạn tín hiệu Usage_kWh
- Fig. 5: Scatter plot S vs φ, tô màu theo Load_Type

**Gợi ý nhận xét về DWT:**
> *"The DWT decomposition with db4 wavelet at level 3 successfully isolates transient spikes into cD1 (high-frequency detail coefficients), while cA3 captures the low-frequency baseline trend. This multiresolution property is essential for detecting abrupt fault events superimposed on slowly varying operational loads."*

**Gợi ý nhận xét về Physical features:**
> *"Apparent Power S ranges from X to Y kVA, with anomalous points clustering at S > threshold. Phase Angle φ reveals that low-PF operations (φ > 1.2 rad) are predominantly associated with Light_Load conditions, suggesting potential idling scenarios."*

---

### C. Anomaly Label Distribution

**Nội dung cần trình bày:**
- Số lượng và tỷ lệ từng loại anomaly (TABLE VI)
- Minh họa thời gian xuất hiện anomaly (Fig. 6 — timeline plot)
- Phân tích chồng chéo (overlap) giữa các loại anomaly

**TABLE VI gợi ý:**
```
TABLE VI: ANOMALY LABEL DISTRIBUTION

| Anomaly Type | Count | Percentage | Primary Conditions        |
|--------------|-------|------------|---------------------------|
| Normal       | 34,200| 97.6%      | —                         |
| Idling       | 450   | 1.28%      | Light_Load, off-hours     |
| Leakage      | 280   | 0.80%      | Gradual increase > 5%     |
| Overload     | 110   | 0.31%      | Extreme usage + low PF    |
```

**Gợi ý nhận xét:**
> *"The severe class imbalance (anomalies < 3%) justifies the need for GAN-based augmentation. Idling events are the most frequent anomaly type, concentrated during weekend night shifts. Overload events, though rare, coincide with peak production periods and pose the highest safety risk."*

---

### D. GAN Augmentation Quality Assessment

**Nội dung cần trình bày:**
- So sánh thống kê giữa real data và synthetic data (TABLE VII)
- PCA/t-SNE visualization (Fig. 7)
- Kết quả huấn luyện GAN (D loss, G loss qua epochs — Fig. 8)

**TABLE VII gợi ý:**
```
TABLE VII: STATISTICAL COMPARISON OF REAL VS. SYNTHETIC DATA

| Metric          | Real Data | Synthetic Data | Error (%) |
|-----------------|-----------|----------------|-----------|
| Mean            | 34.50     | 34.12          | 1.10%     |
| Std Dev         | 44.32     | 42.85          | 3.32%     |
| 1st Quartile    | 8.45      | 8.62           | 2.01%     |
| Median          | 18.23     | 17.98          | 1.37%     |
| 3rd Quartile    | 45.67     | 44.12          | 3.39%     |
```

**Gợi ý nhận xét:**
> *"The synthetic samples preserve the first-order statistics (mean error < 2%) but exhibit slightly reduced variance (3.32% error), a known limitation of standard GANs. The PCA plot (Fig. 7) confirms that synthetic points overlap substantially with real data clusters, indicating acceptable distributional fidelity."*

---

### E. Comparative Analysis

**Nội dung cần trình bày:**
So sánh dataset trước và sau preprocessing:

| Tiêu chí | Raw Dataset | Processed Dataset | Thay đổi |
|----------|------------|-------------------|----------|
| Features | 11 | 40+ | +29 features |
| Anomaly labels | 0 | 3 binary | New |
| Synthetic samples | 0 | 500 | New |
| Time resolution | 15 min | 15 min | Unchanged |
| Physical features | 0 | 2 (S, φ) | New |

**Gợi ý nhận xét tổng hợp:**
> *"The proposed pipeline enriches the original 11-column dataset into a 40+ feature dataset with explicit anomaly annotations and synthetic minority samples. The integration of wavelet, physical, and generative features addresses three critical limitations of the raw corpus: lack of frequency-domain information, absence of physics-informed indicators, and severe class imbalance."*

---

## 3. Quy Tắc Trình Bày Hình Ảnh Trong Results

### Quy tắc "3×3" cho mỗi Figure:
1. **Giới thiệu** trong text trước khi xuất hiện figure
2. **Caption đầy đủ** — tự giải thích được
3. **Phân tích** ngay sau figure

**Ví dụ:**
```text
Fig. 4 illustrates the three-level DWT decomposition of the 
Usage_kWh signal over a 7-day window. The approximation 
coefficient cA3 captures the daily periodic baseline, while 
the detail coefficients cD1–cD3 isolate transient spikes 
corresponding to furnace ignition events.

[FIGURE 4 ĐẶT Ở ĐÂY]

Fig. 4. Three-level DWT decomposition of Usage_kWh using db4 
wavelet. From top to bottom: original signal, cA3 (approximation), 
cD3, cD2, and cD1 (detail coefficients).

The high-frequency cD1 band exhibits sharp peaks at hours 36 
and 142, coinciding with documented overload events in the 
maintenance log. This observation validates that DWT detail 
coefficients serve as effective anomaly precursors.
```

---

## 4. Checklist Results & Discussion

- [ ] Có ít nhất 4–6 figures (histogram, heatmap, DWT decomposition, scatter, timeline, PCA)
- [ ] Có ít nhất 4–5 tables (descriptive stats, features, anomaly dist., GAN quality, comparison)
- [ ] Mỗi figure/table đều được tham chiếu trong text
- [ ] Results (dữ kiện) và Discussion (nhận xét) xen kẽ hợp lý
- [ ] Có so sánh trước/sau preprocessing
- [ ] Có phân tích hạn chế (limitation) của GAN / DWT / labeling
- [ ] Không giới thiệu phương pháp mới (đã có ở Methodology)
- [ ] Số liệu cụ thể, có đơn vị
