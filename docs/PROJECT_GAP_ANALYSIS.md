# Phân tích Gap: Code Project & Báo cáo vs Rubric DS108 Capstone

> **Ngày phân tích:** 26/05/2026  
> **Đối tượng:** DS108-Electrimight (Steel Industry Energy Consumption)  
> **Mục tiêu:** Xác định những gì đang thiếu để đạt mức Advanced/SOTA (A / 9.0–10đ) và đề xuất bổ sung hợp lý.

---

## Tóm tắt nhanh: Điểm hiện tại ước tính

| Tiêu chí | Trọng số | Hiện trạng | Điểm ước tính | Cần bổ sung |
|----------|----------|------------|---------------|-------------|
| 1. Formulation & Complexity | 20% | Đạt B (2 nguồn, 15 phút, 3 miền features) | ~7.5 | Thêm tranh luận về edge-cases, multi-source complexity |
| 2. Pre-processing & Rigor | 30% | Đạt B→A gần (pipeline, assertions, leakage audit) | ~7.5 | MCAR/MAR/MNAR test, GAN SOTA, justification sâu hơn |
| 3. EDA | 20% | Đạt B (có notebooks, bảng thống kê) | ~7.0 | Publication-ready figures, data storytelling, advanced FE |
| 4. Engineering & Reproducibility | 15% | Đạt B (clean code, requirements) | ~7.0 | Unit tests, Docker/Streamlit (bonus), version tags |
| 5. Scientific Reporting & Ethics | 15% | Đạt B (IEEE format, có template) | ~7.0 | Datasheet hoàn chỉnh, Codebook CSV, mở rộng báo cáo 10+ trang |
| **Tổng** | **100%** | | **~7.2** | **Cần bổ sung để đạt 9.0+** |

---

## 1. Formulation & Complexity (20%) — Gap Analysis

### ✅ Đã có (đạt B)
- Bài toán có giá trị ứng dụng: dự báo tải điện + phát hiện bất thường ngành thép.
- Khai thác dữ liệu từ 2 nguồn thực tế: UCI Repository + Open-Meteo API.
- Độ phân giải cao (15 phút), khối lượng lớn (35.040 mẫu), thời gian đầy đủ (1 năm).
- Có Ontology gán nhãn (LABELING_GUIDELINE.md) dựa trên IEEE 519 / ISO 50001.

### ❌ Thiếu để đạt A
- **Không phải multi-modal:** Chỉ có dữ liệu dạng bảng (tabular) + thời tiết; chưa có hình ảnh, văn bản, hoặc âm thanh.
- **Edge-cases trong gán nhãn chưa được bao quát đầy đủ:** Hiện tại chỉ có 3 loại bất thường. Chưa xử lý các trường hợp chồng chéo nhãn (ví dụ: idling + leakage đồng thời) hoặc các dạng bất thường chưa biết (unknown unknowns).
- **Chưa tranh luận về độ phức tạp:** Báo cáo chưa so sánh độ phức tạp của bài toán này với các benchmark dataset phổ biến (ví dụ: UCI Household Electric) để chứng minh "sự khác biệt".

### 🔧 Đề xuất bổ sung (Code + Báo cáo)
1. **Code:** Thêm phân tích các trường hợp chồng chéo nhãn (label overlap analysis) trong `src/anomaly_labels.py`.
2. **Báo cáo:** Thêm đoạn trong Introduction so sánh với các dataset hiện có, chứng minh gap mà Electrimight lấp đầy.

---

## 2. Pre-processing & Methodological Rigor (30%) — Gap Analysis

### ✅ Đã có (gần A)
- Pipeline OOP (`SteelPipeline` trong `src/pipeline.py`).
- Data Assertions (`src/data_assertions.py`).
- Leakage Audit (`src/leakage_audit.py`) — kiểm tra rolling window, DWT window, lag features, weather merge.
- Zero Data Leakage được tuyên bố và audit.
- Feature engineering đa miền: time (lag, rolling, cyclical), frequency (DWT db4 level 3), physical ($S$, $\varphi$).
- GAN augmentation cho imbalance.

### ❌ Thiếu để đạt A
- **Chưa có bằng chứng thống kê về cơ chế khuyết (MCAR/MAR/MNAR):** Dữ liệu UCI gốc không có null rõ ràng, nhưng có implicit missingness (zero values). Chưa có test thống kê (Little's MCAR test, pattern analysis) để chứng minh cơ chế khuyết.
- **Luận giải tiền xử lý chưa đủ sâu:** Báo cáo nêu "dùng linear interpolation" nhưng chưa giải thích tại sao KHÔNG dùng spline, Kriging, hoặc MICE. Chưa phân tích tác động của interpolation lên phương sai (variance) và ma trận hiệp phương sai.
- **GAN chưa phải SOTA:** Hiện tại là FC-GAN cơ bản. Chưa có TimeGAN, WGAN-GP, hoặc Conditional GAN — các kiến trúc được công nhận là SOTA cho time-series synthesis.
- **Chưa có phân tích tác động của tiền xử lý lên downstream model:** Báo cáo nói "cung cấp nền tảng vững chắc" nhưng chưa định lượng cụ thể: ví dụ, mô hình LSTM trên dữ liệu đã xử lý đạt MAPE bao nhiêu so với dữ liệu thô?

### 🔧 Đề xuất bổ sung (Code + Báo cáo)
1. **Code:** Thêm notebook/script phân tích MCAR/MAR/MNAR cho implicit missingness (zero values). Sử dụng `missingno` + Little's MCAR test (`pymice` hoặc tự viết).
2. **Code:** Nâng cấp GAN từ FC-GAN lên TimeGAN hoặc WGAN-GP (có thể dùng thư viện `ydata-synthetic`).
3. **Báo cáo:** Thêm subsection "Justification for Preprocessing Choices" trong Methodology, so sánh ít nhất 2 phương pháp interpolation và giải thích lý do chọn linear.
4. **Báo cáo:** Thêm bảng so sánh hiệu suất downstream (LSTM trên raw vs processed) — dù chỉ là baseline để định lượng tác động của tiền xử lý.

---

## 3. Exploratory Data Analysis (EDA) (20%) — Gap Analysis

### ✅ Đã có (đạt B)
- Có 5 notebooks EDA (`01_data_profiling_and_eda.ipynb`, `01_eda_and_baseline.ipynb`, `steel_eda_v3.ipynb`, v.v.).
- Báo cáo .tex có bảng thống kê mô tả (Bảng descriptive).
- Có mô tả về chu kỳ ngày, tuần, mùa; tương quan giữa Usage_kWh và CO2/Q.

### ❌ Thiếu để đạt A
- **Báo cáo thiếu publication-ready figures:** Hiện tại toàn bộ section Results chỉ có bảng (table) và placeholder văn bản `[Chèn đồ thị...]`. Không có figure nào thực sự trong .tex.
- **Thiếu data storytelling xuất sắc:** Báo cáo chưa "dẫn dắt" người đọc từ dữ liệu thô đến insights. Ví dụ: chưa có câu chuyện về "Tại sao chúng tôi phát hiện ra idling tập trung vào 2h–4h sáng thứ Hai?"
- **Thiếu feature engineering bậc cao (advanced FE):** DWT db4 level 3 là FE cơ bản. Chưa có: cross-correlation analysis giữa weather và electric load theo lag khác nhau; Granger causality test; hoặc feature selection dựa trên mutual information.
- **Thiếu multivariate visualization trong báo cáo:** Chưa có heatmap, pairplot, hoặc 3D scatter trong .tex.

### 🔧 Đề xuất bổ sung (Code + Báo cáo)
1. **Code:** Tạo script `src/visualization.py` hoặc notebook tạo các figure publication-ready:
   - Fig 1: Time-series plot của Usage_kWh với 3 chu kỳ (ngày/tuần/mùa) highlight.
   - Fig 2: Heatmap tương quan đa chiều (11 biến gốc + physical features).
   - Fig 3: DWT decomposition (cA3, cD3, cD2, cD1) cho 1 tuần mẫu.
   - Fig 4: Scatter plot S–$\varphi$ với màu theo Load_Type + đường ngưỡng.
   - Fig 5: PCA/t-SNE overlap (real vs GAN synthetic).
   - Fig 6: Timeline anomaly với 3 loại màu khác nhau.
2. **Báo cáo:** Chèn tất cả figure trên vào section Results với caption chi tiết theo chuẩn IEEE.
3. **Báo cáo:** Thêm subsection "Data Storytelling" hoặc "Key Insights" trong Results, kể 1–2 câu chuyện bất ngờ tìm được từ EDA.

---

## 4. Engineering & Reproducibility (15%) — Gap Analysis

### ✅ Đã có (đạt B)
- Clean code, OOP pipeline (`src/pipeline.py`).
- `requirements.txt` đầy đủ.
- Phân chia `data/raw/` và `data/processed/`.
- Có data assertions.
- `README.md` và `AGENTS.md` hướng dẫn.

### ❌ Thiếu để đạt A
- **`tests/` trống:** Chỉ có `.gitkeep`. Chưa có unit tests cho bất kỳ module nào (data loader, assertions, anomaly labels, GAN).
- **Không có Docker:** Chưa đóng gói pipeline bằng Dockerfile → khó tái lập trên môi trường khác.
- **Không có Streamlit/Gradio dashboard:** Mặc dù là bonus (+0.5đ), nhưng dashboard giúp giảng viên tương tác trực tiếp với EDA.
- **Không có Git tags/versioning:** Chưa thấy version tags cho các milestone của dataset.
- **Chưa publish dataset:** Chưa có trên Kaggle/HuggingFace/Zenodo (bonus +0.5đ).
- **Không có CI/CD:** Không có GitHub Actions để tự động chạy tests/assertions khi push.

### 🔧 Đề xuất bổ sung (Code — theo thứ tự ưu tiên)
1. **Cao ưu tiên:** Viết unit tests cho `src/data_loader.py`, `src/data_assertions.py`, `src/anomaly_labels.py` (dùng `pytest`).
2. **Trung ưu tiên:** Tạo `Dockerfile` đóng gói toàn bộ pipeline.
3. **Trung ưu tiên:** Tạo Streamlit app (`app.py`) để visualize EDA tương tác.
4. **Thấp ưu tiên:** Publish dataset lên Kaggle Datasets (tạo account, upload CSV + metadata).
5. **Thấp ưu tiên:** Thêm Git tags (`git tag v1.0`) cho phiên bản dataset.

---

## 5. Scientific Reporting & Ethics (15%) — Gap Analysis

### ✅ Đã có (đạt B)
- Báo cáo định dạng IEEEtran (2 cột).
- Có `LABELING_GUIDELINE.md`.
- Có `DATASHEETS_TEMPLATE.md` (nhưng chưa hoàn thiện).
- Có `CODEBOOK_GUIDELINE.md` (vừa tạo).

### ❌ Thiếu để đạt A
- **Báo cáo .tex quá ngắn:** ~484 dòng sections (~5 trang đôi). Yêu cầu tối thiểu 10 trang đôi, khuyến nghị 10–20 trang. Cần **gấp đôi** độ dài hiện tại.
- **Datasheet chưa hoàn chỉnh:** Template có nhưng nội dung chưa đạt mức A (thiếu bias critique sâu, ethical risk analysis, misuse cases).
- **Codebook CSV chưa tồn tại:** Chỉ có guideline, chưa có file thực tế.
- **Báo cáo thiếu Phụ lục:** Datasheets for Datasets và Codebook cần được đưa vào báo cáo như Appendices.
- **Văn phong chưa đủ học thuật:** Một số chỗ vẫn mang tính mô tả ("Chúng tôi làm A, B, C") hơn là biện luận ("Chúng tôi chọn A vì B, nếu dùng C sẽ gây D").

### 🔧 Đề xuất bổ sung (Báo cáo + Tài liệu)
1. **Tạo file `data/processed/CODEBOOK.csv`** theo `docs/CODEBOOK_GUIDELINE.md`.
2. **Hoàn thiện `docs/DATASHEETS_TEMPLATE.md`** theo `docs/DATASHEET_GUIDELINE.md`.
3. **Mở rộng báo cáo .tex để đạt 10+ trang đôi:**
   - Thêm subsection "Justification for Feature Engineering" trong Methodology.
   - Thêm subsection "Data Quality Audit" trong Methodology (chi tiết các violation đã phát hiện).
   - Thêm section "Discussion" riêng biệt (hoặc mở rộng Results & Discussion).
   - Thêm Phụ lục A: Datasheets for Datasets.
   - Thêm Phụ lục B: Data Codebook.
   - Thêm Phụ lục C: Labeling Guidelines (tóm tắt).
4. **Chuyển văn phong từ mô tả → biện luận:** Mỗi quyết định kỹ thuật phải có "vì sao" và "nếu không thì sao".

---

## Kế hoạch hành động tổng hợp (Roadmap)

### Giai đoạn 1: Hoàn thiện tài liệu & Dataset (1–2 ngày)
- [ ] Tạo `data/processed/CODEBOOK.csv` (43 cột đầy đủ).
- [ ] Hoàn thiện `docs/DATASHEETS_TEMPLATE.md` thành Datasheet ăn điểm A.
- [ ] Thêm Phụ lục A, B vào báo cáo .tex.

### Giai đoạn 2: Mở rộng báo cáo IEEE (2–3 ngày)
- [ ] Mở rộng Introduction (so sánh với các dataset hiện có, chứng minh gap).
- [ ] Mở rộng Methodology (justification cho từng bước, MCAR/MAR analysis).
- [ ] Chèn publication-ready figures (6 figures) vào Results.
- [ ] Thêm Discussion section (insights, limitations, future work).
- [ ] Đảm bảo độ dài ≥ 10 trang đôi.

### Giai đoạn 3: Củng cố Code & Engineering (2–3 ngày)
- [ ] Viết unit tests (`pytest`) cho ít nhất 3 module core.
- [ ] Thêm MCAR/MAR analysis notebook.
- [ ] (Optional) Tạo Dockerfile.
- [ ] (Optional) Tạo Streamlit dashboard (bonus +0.5đ).
- [ ] (Optional) Publish lên Kaggle (bonus +0.5đ).

### Giai đoạn 4: Nâng cấp Methodology (1–2 ngày)
- [ ] Thay FC-GAN bằng TimeGAN hoặc WGAN-GP.
- [ ] Thêm downstream evaluation (LSTM baseline) để định lượng tác động của tiền xử lý.
- [ ] Thêm cross-correlation / Granger causality giữa weather và load.

---

*Phân tích này được thực hiện dựa trên rubric DS108 Capstone Guidelines và hiện trạng project Electrimight ngày 26/05/2026.*
