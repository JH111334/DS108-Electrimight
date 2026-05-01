# Hướng Dẫn Viết Related Work — IEEE Format

> Section Related Work (Literature Review) chứng minh bạn hiểu lĩnh vực và vị trí của công trình mình trong bối cảnh nghiên cứu hiện tại.

---

## 1. Cấu Trúc Đề Xuất

Chia thành **3 nhóm chủ đề** chính, mỗi nhóm 1 đoạn hoặc 1 subsection:

### A. Industrial Energy Consumption Forecasting & Dataset
- Các nghiên cứu dự báo điện trong công nghiệp
- Các dataset công khai (UCI Steel Industry, ISO-NE, etc.)
- Hạn chế: thiếu đặc trưng vật lý, thiếu nhãn bất thường

### B. Wavelet Transform in Time-Series Analysis
- FFT vs DWT: FFT chỉ có tần số, DWT có cả tần số + thời gian
- DWT trong dự báo điện (Daubechies, Symlet)
- DWT trong phát hiện bất thường chuỗi thời gian

### C. GAN and Synthetic Data Augmentation
- GAN cơ bản (Goodfellow et al., 2014)
- TimeGAN, RGAN, RCGAN cho chuỗi thời gian
- Data augmentation cho bài toán mất cân bằng lớp

---

## 2. Mẫu Viết Đoạn Related Work (Topic + Sentence Pattern)

### Pattern chuẩn IEEE:
```
[1] Tổng quan nhóm nghiên cứu A đã làm gì.
[2] Cụ thể: Author [n] proposed ... để giải quyết ...
[3] Tuy nhiên, hạn chế là ...
[4] Nhóm nghiên cứu B [m], [p] đã cải tiến bằng ...
[5] Dù vậy, vẫn chưa giải quyết được ...
[6] Khác biệt của công trình chúng tôi là ...
```

---

## 3. Ví Dụ Đoạn Văn (Gợi Ý)

### Đoạn A — Industrial Energy Forecasting

```
Industrial load forecasting has been extensively studied using 
statistical and machine learning approaches. Auto-regressive 
integrated moving average (ARIMA) models provide interpretable 
baselines but fail to capture nonlinear dynamics [1]. More 
recently, deep learning architectures such as Long Short-Term 
Memory (LSTM) networks have demonstrated superior accuracy in 
modeling temporal dependencies [2]. However, these studies 
predominantly rely on aggregated system-level data, whereas 
end-user industrial loads—particularly in steel manufacturing—
exhibit abrupt fluctuations driven by furnace scheduling and 
rolling mill operations [3]. Publicly available industrial 
datasets, such as the UCI Steel Industry Energy Consumption 
dataset [4], offer granular 15-minute resolution readings but 
lack derived physical features and explicit fault annotations, 
limiting their direct applicability to supervised anomaly 
detection tasks.
```

### Đoạn B — Wavelet Transform

```
Frequency-domain analysis complements time-domain methods by 
revealing transient behaviors invisible to rolling statistics. 
The Fast Fourier Transform (FFT) decomposes signals into 
frequency components but sacrifices temporal localization [5]. 
In contrast, the Discrete Wavelet Transform (DWT) employs 
scaled and translated mother wavelets to capture both frequency 
and time information, making it particularly suitable for 
non-stationary industrial load signals [6]. Zhang et al. [7] 
demonstrated that a DWT-LSTM hybrid model achieves MAPE as low 
as 0.59% for short-term load forecasting. Similarly, multi-level 
DWT decomposition with Daubechies wavelets has been applied to 
detect power network faults by isolating high-frequency detail 
coefficients [8]. Nevertheless, prior works primarily use DWT 
as a preprocessing step for prediction rather than as a feature 
source for anomaly characterization in industrial settings.
```

### Đoạn C — GAN Data Augmentation

```
Class imbalance poses a persistent challenge in anomaly 
detection, where abnormal events constitute less than 1% of 
observations [9]. Generative Adversarial Networks (GANs), 
introduced by Goodfellow et al. [10], have emerged as a 
powerful paradigm for synthetic data generation. For time-series 
applications, Yoon et al. [11] proposed TimeGAN, which combines 
adversarial training with supervised sequence modeling to 
preserve temporal dynamics. Tang et al. [12] applied an improved 
TimeGAN with multi-head self-attention to manufacturing energy 
data, achieving over 60% reduction in prediction RMSE after 
augmentation. Variants such as RGAN and RCGAN [13] leverage 
recurrent architectures to generate realistic multidimensional 
series. Despite these advances, the application of GAN-based 
augmentation to industrial electricity datasets with explicit 
physics-informed anomaly labels remains underexplored.
```

---

## 4. Danh Sách Tài Liệu Tham Khảo Gợi Ý (IEEE Format)

Dưới đây là các references bạn **NÊN trích dẫn**, đã format sẵn theo IEEE:

```
[1] H. S. Hippert, C. E. Pedreira, and R. C. Souza, "Neural 
networks for short-term load forecasting: A review and 
evaluation," *IEEE Trans. Power Syst.*, vol. 16, no. 1, 
pp. 44–55, Feb. 2001.

[2] S. Bouktif et al., "Optimal deep learning LSTM model for 
electric load forecasting using feature selection and 
genetic algorithm: Integration of reservoir computing with 
LSTM," *IEEE Access*, vol. 8, pp. 152431–152445, 2020.

[3] S. R. Khuntia, J. L. Rueda, and M. A. M. M. van der 
Meijden, "Forecasting the load of electrical power systems 
in mid- and long-term horizons: A review," *IET Gener. 
Transm. Distrib.*, vol. 10, no. 16, pp. 3971–3977, 2016.

[4] "Steel Industry Energy Consumption Dataset," UCI Machine 
Learning Repository. [Online]. Available: 
https://archive.ics.uci.edu/dataset/851/steel+industry+
energy+consumption

[5] E. Ordentlich et al., "A discrete fourier transform 
approach to clock offset estimation," in *Proc. IEEE 
International Conference on Communications (ICC)*, 
Kyoto, Japan, 2011, pp. 1–5.

[6] S. G. Mallat, "A theory for multiresolution signal 
decomposition: The wavelet representation," *IEEE Trans. 
Pattern Anal. Mach. Intell.*, vol. 11, no. 7, pp. 674–693, 
Jul. 1989.

[7] N. Zhang et al., "Deep learning modeling in electricity 
load forecasting," *Energy Rep.*, vol. 11, pp. 3544–3556, 
2024.

[8] A. S. Al-Fattah, "Optimal decomposition and reconstruction 
of discrete wavelet transformation for short-term load 
forecasting," *Energies*, vol. 12, no. 24, p. 4654, 2019.

[9] V. Chandola, A. Banerjee, and V. Kumar, "Anomaly detection: 
A survey," *ACM Comput. Surv.*, vol. 41, no. 3, pp. 1–58, 
2009.

[10] I. J. Goodfellow et al., "Generative adversarial nets," 
in *Advances in Neural Information Processing Systems 
(NeurIPS)*, Montreal, Canada, 2014, pp. 2672–2680.

[11] J. Yoon, D. Jarrett, and M. van der Schaar, "Time-series 
generative adversarial networks," in *Proc. 33rd Conference 
on Neural Information Processing Systems (NeurIPS)*, 
Vancouver, Canada, 2019, pp. 5509–5519.

[12] P. Tang et al., "Time series data augmentation for energy 
consumption data based on improved TimeGAN," *Sensors*, 
vol. 25, no. 2, p. 493, Jan. 2025.

[13] G. Esteban et al., "Real-valued (medical) time series 
generation with recurrent conditional GANs," in *Proc. 
ML4H Workshop at NeurIPS*, 2017, pp. 1–6.

[14] S. B. Kotsiantis, D. Kanellopoulos, and P. E. Pintelas, 
"Data preprocessing for supervised leaning," *Int. J. 
Comput. Sci.*, vol. 1, no. 2, pp. 111–117, 2006.

[15] M. S. Ahmed et al., "Multi-family wavelet-based feature 
engineering method for short-term time series forecasting," 
*Sci. Rep.*, vol. 15, no. 1, p. 8523, 2025.
```

---

## 5. Bảng So Sánh Related Work (Gợi Ý Cho Báo Cáo)

Bạn nên tạo một **TABLE I** so sánh công trình liên quan để thể hiện đóng góp của mình:

```
TABLE I: COMPARISON OF RELATED WORKS

| Ref | Domain      | DWT   | Physical Features | Anomaly Labels | GAN Aug. | Dataset       |
|-----|-------------|-------|-------------------|----------------|----------|---------------|
| [1] | Forecasting | No    | No                | No             | No       | Aggregated    |
| [7] | Forecasting | Yes   | No                | No             | No       | ISO-NE        |
| [8] | Forecasting | Yes   | No                | No             | No       | System load   |
| [12]| Augmentation| No    | No                | No             | Yes      | Manufacturing |
| Ours| Preprocess  | Yes   | Yes               | Yes            | Yes      | Steel Industry|
```

> **Lưu ý**: Table này rất mạnh trong IEEE — nó giúp reviewer nhìn thấy ngay khoảng trống (gap) mà bạn lấp đầy.

---

## 6. Checklist Related Work

- [ ] Ít nhất 10–15 references được trích dẫn
- [ ] References cân bằng giữa classic ( foundational) và recent (2019–2025)
- [ ] Mỗi nhóm nghiên cứu được mô tả ngắn gọn
- [ ] Hạn chế của từng nhóm được chỉ rõ
- [ ] Có ít nhất 1 bảng so sánh
- [ ] Kết thúc bằng "gap" mà công trình này lấp đầy
- [ ] Tất cả references trong text đều có trong danh sách cuối bài
