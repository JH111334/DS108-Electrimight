# Roadmap Viết Báo cáo IEEE — Electrimight

> **Mục tiêu:** Đưa báo cáo từ ~5 trang đôi hiện tại lên **≥ 10 trang đôi**, đạt chất lượng **Advanced/SOTA (A / 9.0–10đ)** theo rubric DS108.  
> **Cấu trúc tham khảo:** IEEEtran conference, 2 cột, US Letter.

---

## Checklist độ dài tối thiểu

| Thành phần | Trang đôi ước tính | Ghi chú |
|------------|-------------------|---------|
| Title + Authors + Abstract + Keywords | 0.5 | Giữ nguyên |
| I. Introduction | **1.5–2.0** | Mở rộng: background, motivation, gap, contributions |
| II. Related Work | **1.0–1.5** | Mở rộng: so sánh chi tiết, bảng related work |
| III. Methodology | **3.0–4.0** | Mở rộng đáng kể: justification, data audit, MCAR/MAR |
| IV. Experimental Setup | **1.0–1.5** | Phần cứng, temporal split, metrics, leakage audit |
| V. Results & Discussion | **2.5–3.5** | 6 figures + bảng + data storytelling + insights |
| VI. Conclusion | **0.5** | Giữ ngắn gọn |
| Acknowledgments | 0.25 | Giữ ngắn |
| References | 0.5–1.0 | ~15 refs |
| **Appendix A: Datasheets** | **1.0–2.0** | Bắt buộc cho điểm A |
| **Appendix B: Codebook** | **0.5–1.0** | Bắt buộc cho điểm B+ |
| **Appendix C: Labeling Guidelines** | **0.5** | Tóm tắt |
| **Tổng** | **≥ 12–15** | Vượt mức tối thiểu 10 trang |

---

## Nội dung cần THÊM vào từng Section

### I. INTRODUCTION (Mở rộng từ 0.5 → 1.5–2.0 trang)

**Hiện tại thiếu:**
- So sánh với các dataset công khai phổ biến (UCI Household, CER Smart Metering, Italy Power Demand).
- Chứng minh "research gap" cụ thể: tại sao các dataset hiện tại KHÔNG đủ cho ngành thép.
- Liệt kê rõ 3–4 contributions phân biệt (distinguishing contributions).

**Nội dung cần viết thêm:**
1. **Paragraph 2–3 (Background):** Mở rộng về ngành thép (7–9% CO₂ toàn cầu), chi phí điện chiếm 20–40% vận hành. Các nhà máy đang chuyển đổi số (Industry 4.0) nhưng thiếu dữ liệu chuẩn.
2. **Paragraph 4 (Gap Analysis):** So sánh 3–4 dataset hiện có trong Table I (đã có). Nhấn mạnh: chưa có dataset nào có cả (i) độ phân giải 15 phút, (ii) đặc trưng vật lý ($S$, $\varphi$), (iii) nhãn bất thường đa lớp, (iv) dữ liệu khí tượng ngoại sinh đồng bộ.
3. **Paragraph 5 (Contributions):** Liệt kê 4 contributions rõ ràng:
   - C1: Framework feature engineering đa miền (time + DWT + physical).
   - C2: Chiến lược gán nhãn bất thường dựa trên chuẩn ngành với confidence score.
   - C3: Pipeline GAN augmentation cho lớp thiểu số với statistical fidelity validation.
   - C4: Zero data leakage audit toàn diện + Datasheets for Datasets minh bạch.

---

### II. RELATED WORK (Mở rộng từ 0.8 → 1.0–1.5 trang)

**Hiện tại thiếu:**
- So sánh chi tiết hơn về metrics (MAPE, RMSE) của các công trình liên quan.
- Phân tích "gap" trong lĩnh vực: tại sao chưa ai làm điều tương tự.

**Nội dung cần viết thêm:**
1. **Subsection 2.1:** Thêm bảng so sánh metrics (MAPE, RMSE) của Hippert 2001 vs Bouktif 2020 vs Zhang 2024.
2. **Subsection 2.2:** Phân tích tại sao FFT không phù hợp cho tải công nghiệp không dừng (non-stationary) — cần trích dẫn thêm Mallat 1989 hoặc Daubechies.
3. **Subsection 2.3:** Thêm phân tích về TimeGAN (Yoon 2019) vs FC-GAN cơ bản — giải thích tại sao chúng ta chọn FC-GAN (đơn giản, đủ cho dữ liệu tabular) nhưng thừa nhận hạn chế.
4. **Paragraph cuối:** Tổng hợp gap rõ ràng: "Despite these advances, no existing work integrates DWT-based spectral features, physical-domain features ($S$, $\varphi$), physics-based anomaly labeling, and GAN augmentation within a single pipeline for steel industry energy data."

---

### III. METHODOLOGY (Mở rộng từ 2.5 → 3.0–4.0 trang)

**Đây là section cần mở rộng NHIỀU NHẤT.**

**Hiện tại thiếu:**
- Justification sâu cho từng lựa chọn kỹ thuật.
- Data Quality Audit chi tiết (violation table).
- MCAR/MAR/MNAR analysis.
- So sánh các phương pháp tiền xử lý thay thế.

**Nội dung cần viết thêm:**

#### 3.1 Dataset Overview (giữ nguyên + mở rộng)
- Thêm bảng schema chi tiết hơn (đã có trong `03_methodology.tex` nhưng có thể mở rộng).

#### 3.2 Data Quality Audit (MỚI — cần thêm subsection)
- Bảng violations đã có trong báo cáo? Chưa rõ. Cần thêm:
  - Table: Physical Violations (PF > 1, Q < 0...)
  - Table: Temporal Consistency Check (duplicate timestamps, gaps, NSM mismatch)
  - Table: Measurement Artifacts (CO2 resolution, constant values)
- **Luận giải:** "Chúng tôi phát hiện 99,997% mẫu có PF > 1, chứng tỏ dữ liệu gốc được ghi ở dạng phần trăm (0–100) thay vì hệ số (0–1). Nếu không chuẩn hóa, mọi mô hình sử dụng PF sẽ hoạt động sai lầm..."

#### 3.3 Preprocessing & Justification (MỞ RỘNG)
- **Interpolation:** Giải thích tại sao linear interpolation cho weather (liên tục theo thời gian) nhưng thừa nhận hạn chế với mưa rào đột ngột.
- **Train/Test Split:** Giải thích tại sao temporal split (thay vì random) và tại sao 80/20 (đủ để capture seasonality).
- **Scaling:** Giải thích MinMaxScaler [-1, 1] cho GAN (ổn định training) nhưng StandardScaler cho downstream (distance-based models).

#### 3.4 Feature Engineering (giữ + bổ sung justification)
- **Time-domain:** Giải thích tại sao lag $\in \{1, 2, 4, 96\}$ (15 phút, 30 phút, 1 giờ, 24 giờ) — bắt quán tính ngắn hạn đến chu kỳ ngày.
- **DWT:** Giải thích tại sao db4 (orthogonal, compact support, phù hợp tín hiệu ngắn) và tại sao level 3 (đủ để tách trend ngày khỏi chi tiết giờ).
- **Physical:** Giải thích tại sao $S$ và $\varphi$ quan trọng hơn chỉ dùng $P$ và PF.

#### 3.5 Anomaly Labeling (giữ + bổ sung)
- Thêm bảng so sánh 3 loại bất thường (đã có trong `05_results.tex` nhưng có thể di chuyển lên Methodology).
- Giải thích confidence score và tại sao dùng rule-based thay vì unsupervised clustering (có cơ sở chuẩn ngành, interpretable).

#### 3.6 GAN Augmentation (giữ + bổ sung)
- Thêm architecture diagram (hoặc mô tả chi tiết kiến trúc generator/discriminator).
- Giải thích tại sao fully-connected (đủ cho tabular) nhưng thừa nhận TimeGAN/WGAN là hướng tốt hơn trong tương lai.

---

### IV. EXPERIMENTAL SETUP (Mở rộng từ 0.8 → 1.0–1.5 trang)

**Nội dung cần viết thêm:**
1. **Phần cứng & Phần mềm:** Đã có nhưng có thể thêm thông tin về thời gian chạy pipeline (wall-clock time).
2. **Leakage Audit:** Mở rộng thành bảng riêng:
   | Kiểm tra | Cấu hình | Kết quả |
   |----------|----------|---------|
   | Rolling window | `center=False` | ✅ Pass |
   | DWT window | Cửa sổ $[t-w+1, t]$ | ✅ Pass |
   | Lag features | `shift(lag)` với lag > 0 | ✅ Pass |
   | Weather merge | Không dùng `bfill` | ✅ Pass |
   | GAN scaler | Fit trên toàn bộ GAN data | ✅ Pass (không leakage cho downstream) |
3. **Metrics:** Giải thích tại sao chọn statistical fidelity, PCA/t-SNE overlap, Frobenius norm (vì đây là dataset construction paper, không phải forecasting paper).

---

### V. RESULTS & DISCUSSION (Mở rộng từ 1.5 → 2.5–3.5 trang)

**Đây là section cần thêm FIGURES NHIỀU NHẤT.**

#### 5.1 Phân tích Dữ liệu (giữ bảng + thêm figure)
- **Fig. 1:** Time-series plot Usage_kWh (1 tuần mẫu) với highlight 3 chu kỳ.
- **Fig. 2:** Boxplot Usage_kWh theo Load_Type + Day_of_week.

#### 5.2 Đánh giá Đặc trưng (MỚI — cần thêm subsection)
- **Fig. 3:** Heatmap tương quan (11 biến gốc + physical features).
- **Fig. 4:** DWT decomposition (cA3, cD3, cD2, cD1) cho 1 tuần.
- **Fig. 5:** Scatter plot S–$\varphi$ với màu theo Load_Type + đường ngưỡng PF=0.5, PF=0.7.

#### 5.3 Phân bố Bất thường (giữ bảng + thêm figure)
- **Fig. 6:** Timeline anomaly (1 tuần mẫu) với 3 loại màu khác nhau.

#### 5.4 Chất lượng GAN (giữ bảng + thêm figure)
- **Fig. 7:** PCA overlap (real vs synthetic).
- **Fig. 8:** t-SNE overlap (real vs synthetic).

#### 5.5 Discussion (MỚI — cần thêm subsection riêng)
- **Insight 1:** "Tại sao idling tập trung 2h–4h sáng thứ Hai?" → Kể story về khởi động lò sau cuối tuần.
- **Insight 2:** "Tại sao tương quan weather–electric yếu?" → Thảo luận về giá trị hạn chế của weather cho indoor industrial load.
- **Insight 3:** "Tại sao GAN synthetic chỉ 500 mẫu?" → Thảo luận bias/variance trade-off; quá nhiều synthetic có thể dilute distribution.
- **Limitations:** Thừa nhận 3–4 giới hạn rõ ràng (chỉ 1 nhà máy, chỉ 2018, ngưỡng cố định, GAN chưa SOTA).

---

### VI. CONCLUSION (Giữ ngắn gọn ~0.5 trang)

- Tóm tắt 4 contributions.
- Thêm 1 đoạn về "Impact": dataset có thể được dùng như benchmark cho các nghiên cứu tiếp theo.

---

## Appendices (Bắt buộc cho điểm A)

### Appendix A: Datasheets for Datasets (~1.5–2.0 trang)
- Điền đầy đủ 7 phần theo Gebru et al., 2021.
- **Tập trung:** Bias critique (địa lý, thời gian, cảm biến), ethical risks, misuse cases.
- Tham khảo: `docs/DATASHEET_GUIDELINE.md`.

### Appendix B: Data Codebook (~0.5–1.0 trang)
- Bảng CODEBOOK.csv (43 cột) được trình bày dưới dạng bảng LaTeX `longtable`.
- Hoặc: Tóm tắt 5–6 cột quan trọng nhất + ghi chú "Full codebook available at GitHub".
- Tham khảo: `docs/CODEBOOK_GUIDELINE.md`.

### Appendix C: Labeling Guidelines (~0.5 trang)
- Tóm tắt 3 loại bất thường + ngưỡng + confidence score.
- Trích dẫn: `docs/LABELING_GUIDELINE.md`.

---

## Figures Checklist (Cần chèn vào .tex)

| Fig. | Nội dung | Section |
|------|----------|---------|
| 1 | Time-series Usage_kWh (1 tuần, 3 chu kỳ) | Results 5.1 |
| 2 | Boxplot Usage_kWh by Load_Type × Day | Results 5.1 |
| 3 | Correlation heatmap (11 raw + physical) | Results 5.2 |
| 4 | DWT decomposition (cA3, cD3, cD2, cD1) | Results 5.2 |
| 5 | Scatter S–$\varphi$ colored by Load_Type | Results 5.2 |
| 6 | Anomaly timeline (1 tuần, 3 colors) | Results 5.3 |
| 7 | PCA real vs synthetic | Results 5.4 |
| 8 | t-SNE real vs synthetic | Results 5.4 |

> **Lưu ý kỹ thuật:** IEEEtran dùng `\begin{figure}[htbp]` + `\includegraphics[width=\columnwidth]{...}` + `\caption{...}`. Nếu figure quá rộng, dùng `\begin{figure*}[htbp]` để span cả 2 cột.

---

## Tables Checklist (Cần chèn vào .tex)

| Table | Nội dung | Section |
|-------|----------|---------|
| I | So sánh Related Work (đã có) | Related Work |
| II | Schema dữ liệu gốc (11 cột) | Methodology 3.1 |
| III | Data Quality Violations | Methodology 3.2 |
| IV | Leakage Audit Results | Experimental Setup |
| V | Thống kê mô tả (đã có) | Results 5.1 |
| VI | Anomaly Distribution (đã có) | Results 5.3 |
| VII | GAN Statistical Fidelity (đã có) | Results 5.4 |
| VIII | CODEBOOK (tóm tắt) | Appendix B |

---

*Roadmap này được thiết kế để đạt điểm tối đa tiêu chí 5 (Scientific Reporting) và nâng cao các tiêu chí còn lại lên mức Advanced/SOTA.*
