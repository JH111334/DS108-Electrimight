# Template Báo Cáo IEEE — DS108 Electrimight

> Đây là template/outline hoàn chỉnh cho báo cáo. Bạn có thể copy và điền nội dung vào từng phần.

---

## [TITLE]

**Wavelet-Based Feature Engineering and GAN Augmentation for Steel Industry Energy Consumption Dataset Construction**

*Hoặc:*

**A Preprocessing Pipeline for Electricity Forecasting and Anomaly Detection in Steel Industry Using Discrete Wavelet Transform and Generative Adversarial Networks**

---

## [AUTHORS]

```
Author Name¹, Author Name², Author Name³

¹ Department of Data Science, University Name, City, Country
² Department of Electrical Engineering, University Name, City, Country
³ Department of Computer Science, University Name, City, Country

Email: author1@university.edu; author2@university.edu
```

---

## ABSTRACT

[150–250 từ]

**Background:** Industrial electricity consumption forecasting requires high-quality datasets...

**Problem:** Existing datasets lack derived physical features and anomaly annotations...

**Method:** This paper proposes a multi-domain preprocessing pipeline integrating time-domain statistics, Discrete Wavelet Transform (DWT), physical-domain features (Apparent Power S, Phase Angle φ), physics-informed anomaly labeling, and GAN-based data augmentation...

**Results:** The enriched dataset expanded from 11 to over 40 features with three binary anomaly indicators and 500 synthetic minority samples...

**Significance:** This work provides a robust foundation for downstream load forecasting and risk classification models in energy-intensive industries...

**Keywords**—Energy consumption, data preprocessing, discrete wavelet transform, feature engineering, generative adversarial network, anomaly detection, steel industry.

---

## I. INTRODUCTION

### Đoạn 1: Context
- Tầm quan trọng của dự báo điện năng trong công nghiệp
- Ngành thép: đặc thù tiêu thụ điện lớn, chu kỳ rõ rệt
- Nhu cầu dataset chất lượng cao cho học máy

### Đoạn 2: Problem
- Dataset công khai (UCI Steel Industry) chỉ có biến cơ bản
- Thiếu đặc trưng vật lý (S, φ)
- Thiếu nhãn bất thường
- Mất cân bằng lớp nghiêm trọng

### Đoạn 3: Contribution
- Contribution 1: Multi-domain feature engineering (time + wavelet + physical)
- Contribution 2: Physics-informed anomaly labeling (idling, leakage, overload)
- Contribution 3: GAN synthetic data augmentation

### Đoạn 4: Organization
- Section II: Related Work
- Section III: Methodology
- Section IV: Dataset and Experimental Setup
- Section V: Results and Discussion
- Section VI: Conclusion

---

## II. RELATED WORK

### A. Industrial Energy Consumption Forecasting
- [3]–[7]: Các phương pháp dự báo điện (ARIMA, LSTM, hybrid)
- Hạn chế: chỉ dùng aggregated data, thiếu granular industrial features

### B. Wavelet Transform in Time-Series Analysis
- [8]–[13]: DWT theory và ứng dụng trong power systems
- Ưu điểm so với FFT: time-frequency localization
- Hạn chế: chưa áp dụng cho anomaly detection trong steel industry

### C. GAN and Synthetic Data Augmentation
- [14]–[19]: GAN, TimeGAN, RGAN cho time series
- Ứng dụng trong energy data [16]
- Hạn chế: chưa kết hợp với physics-informed anomaly labels

### [TABLE I: COMPARISON OF RELATED WORKS]

| Ref | Forecast | DWT | Physical | Anomaly | GAN | Domain |
|-----|----------|-----|----------|---------|-----|--------|
| [3] | Yes | No | No | No | No | General |
| [6] | Yes | Yes | No | No | No | Power Grid |
| [16]| No | No | No | No | Yes | Manufacturing |
| Ours| Yes | Yes | Yes | Yes | Yes | Steel Industry |

---

## III. METHODOLOGY

### A. Dataset Overview
- UCI Steel Industry Energy Consumption [1]
- 35,040 records, 15-min intervals
- 11 original features

### B. Data Preprocessing
- Load & inspect
- Remove duplicates
- Linear interpolation for missing values (1)
- Temporal sorting

### C. Time-Domain Feature Engineering
- Lag features: k ∈ {1, 2, 4, 96} (2)
- Rolling statistics: mean, std, skewness (3)–(4)
- Cyclical encoding: NSM_sin, NSM_cos (5)–(6)

### D. Frequency-Domain Feature Extraction (DWT)
- Theory: Mallat [8], Daubechies [11]
- Wavelet: db4, level 3
- Window: 64 steps
- Features: mean, std, energy, max_abs per coefficient
- [TABLE II: DWT FEATURES]

### E. Physical-Domain Feature Engineering
- Apparent Power S = √(P² + Q²) (8)
- Phase Angle φ = arccos(PF) (9)
- Physical interpretation

### F. Anomaly Labeling Strategy
- Idling: (10)
- Leakage: (11)
- Overload: (12)
- [TABLE III: ANOMALY RULES]

### G. GAN-Based Data Augmentation
- Generator & Discriminator architecture
- Training parameters
- [TABLE IV: GAN HYPERPARAMETERS]
- Loss function (13)

### H. Pipeline Integration
- [Fig. 1: Pipeline Diagram]

---

## IV. DATASET AND EXPERIMENTAL SETUP

### A. Hardware & Software
- Python 3.9+, TensorFlow 2.16, PyWavelets 1.6
- Pandas, Scikit-learn, Matplotlib

### B. Dataset Splits
- Full dataset: 35,040 samples
- Training for GAN: 80% normal samples
- No test split (this is preprocessing paper)

### C. Evaluation Metrics
- Statistical fidelity (mean, std, quartile error)
- PCA/t-SNE overlap
- Feature correlation preservation

---

## V. RESULTS AND DISCUSSION

### A. Data Profiling
- [TABLE V: DESCRIPTIVE STATISTICS]
- [Fig. 2: Time-series plot with anomaly annotations]

### B. Feature Engineering Evaluation
- [Fig. 3: Correlation heatmap]
- [Fig. 4: DWT decomposition]
- [Fig. 5: S vs φ scatter plot]

### C. Anomaly Distribution
- [TABLE VI: ANOMALY LABEL DISTRIBUTION]
- [Fig. 6: Anomaly timeline]

### D. GAN Augmentation Quality
- [TABLE VII: REAL VS. SYNTHETIC COMPARISON]
- [Fig. 7: PCA visualization]
- [Fig. 8: t-SNE visualization]
- [Fig. 9: GAN training curves]
- [Fig. 10: Distribution comparison]

### E. Overall Comparison
- Raw vs. processed dataset metrics

---

## VI. CONCLUSION

### Summary
- Pipeline 7 bước
- 40+ features từ 11 features ban đầu
- 3 loại anomaly labels
- 500 synthetic samples

### Contributions (bullet points)
1. Multi-domain feature engineering
2. Physics-informed anomaly labeling
3. GAN augmentation with statistical fidelity

### Limitations
- Fixed thresholds
- Standard GAN mode collapse

### Future Work
1. Adaptive thresholding
2. TimeGAN / Conditional GAN
3. Downstream LSTM/Transformer evaluation

---

## ACKNOWLEDGMENT

The authors would like to thank the UCI Machine Learning Repository for providing the Steel Industry Energy Consumption dataset. This work was supported by [funding source if applicable].

---

## REFERENCES

[1]–[33] (xem file `07_References_Bibliography.md`)

---

## APPENDIX (Tùy chọn)

### A. Full Feature List
- Liệt kê đầy đủ 40+ features

### B. Python Implementation Snippets
- Pseudo-code cho pipeline chính

### C. Maintenance Log Cross-Reference
- So sánh anomaly labels với log bảo trì (nếu có)
