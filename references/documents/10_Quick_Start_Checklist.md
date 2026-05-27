# Quick-Start Checklist — Viết Báo Cáo IEEE DS108

> File này giúp bạn kiểm tra tiến độ viết báo cáo từng bước. Đánh dấu ☑ khi hoàn thành.

---

## Giai Đoạn 1: Chuẩn Bị (Trước khi viết)

- [ ] Đọc kỹ file `00_IEEE_Format_Guidelines.md`
- [ ] Chọn tiêu đề báo cáo (tham khảo gợi ý trong file 00)
- [ ] Xác định 3–5 Keywords
- [ ] Liệt kê ít nhất 15 references từ file `07_References_Bibliography.md`
- [ ] Chuẩn bị sẵn các figure cần thiết (danh sách trong file `08_Figures_Tables_Guide.md`)

---

## Giai Đoạn 2: Viết Nội Dung Chính

### Abstract
- [ ] 150–250 từ
- [ ] Đủ 5 phần: Context → Problem → Method → Results → Significance
- [ ] Không có công thức, hình, bảng, trích dẫn
- [ ] Có 3–5 Keywords

### I. Introduction
- [ ] Đoạn 1: Context (tầm quan trọng ngành thép + dự báo điện)
- [ ] Đoạn 2: Problem (thiếu features, thiếu nhãn, mất cân bằng)
- [ ] Đoạn 3: Contribution (3 điểm chính)
- [ ] Đoạn 4: Organization (liệt kê các section)
- [ ] Không quá 2 trang
- [ ] Ít nhất 3–5 trích dẫn

### II. Related Work
- [ ] Subsection A: Industrial Energy Forecasting (3–4 refs)
- [ ] Subsection B: Wavelet Transform (3–4 refs)
- [ ] Subsection C: GAN & Data Augmentation (3–4 refs)
- [ ] TABLE I: Comparison of Related Works
- [ ] Kết thúc bằng "gap" mà bài báo lấp đầy

### III. Methodology
- [ ] Subsection A: Dataset Overview
- [ ] Subsection B: Data Preprocessing
- [ ] Subsection C: Time-Domain Features
- [ ] Subsection D: DWT Features
- [ ] Subsection E: Physical Features
- [ ] Subsection F: Anomaly Labeling
- [ ] Subsection G: GAN Augmentation
- [ ] Subsection H: Pipeline Integration
- [ ] Có ít nhất 3 bảng (DWT features, Anomaly rules, GAN params)
- [ ] Có Fig. 1: Pipeline diagram
- [ ] Công thức đánh số từ (1) đến (13+)

### IV. Dataset and Experimental Setup
- [ ] Hardware & Software environment
- [ ] Dataset statistics
- [ ] Evaluation metrics

### V. Results and Discussion
- [ ] TABLE V: Descriptive statistics
- [ ] TABLE VI: Anomaly distribution
- [ ] TABLE VII: Real vs. Synthetic comparison
- [ ] Fig. 2: Time-series with anomalies
- [ ] Fig. 3: Correlation heatmap
- [ ] Fig. 4: DWT decomposition
- [ ] Fig. 5: S vs φ scatter
- [ ] Fig. 6: Anomaly timeline
- [ ] Fig. 7: PCA visualization
- [ ] Fig. 8: t-SNE visualization
- [ ] Fig. 9: GAN training curves
- [ ] Fig. 10: Distribution comparison
- [ ] Mỗi figure/table được tham chiếu trong text

### VI. Conclusion
- [ ] Tóm tắt công trình
- [ ] 3 contributions dạng bullet points
- [ ] Thừa nhận hạn chế
- [ ] 2–3 hướng phát triển tương lai
- [ ] Không thêm thông tin mới

---

## Giai Đoạn 3: Hoàn Thiện & Kiểm Tra

### Format
- [ ] Font Times New Roman 10 pt (hoặc Computer Modern nếu dùng LaTeX)
- [ ] Lề 1 inch (2.54 cm) 4 cạnh
- [ ] Đúng cách đánh số section: I, II, III... A, B, C...
- [ ] Đúng style heading: cấp 1 ALL CAPS, cấp 2 Title Case, cấp 3 Sentence case.
- [ ] Tổng độ dài không vượt quá 20 trang đôi (2 cột) hoặc 40 trang đơn (1 cột)

### Trích Dẫn
- [ ] Tất cả references trong text đều có trong danh sách cuối bài
- [ ] Sắp xếp references theo thứ tự xuất hiện
- [ ] Định dạng đúng IEEE: `[n] A. Author, "Title," *Journal*, vol. x, no. x, pp. xxx–xxx, Year.`

### Hình Ảnh & Bảng Biểu
- [ ] Tất cả hình ≥ 300 DPI
- [ ] Caption figure đặt bên dưới
- [ ] Caption table đặt bên trên, ALL CAPS
- [ ] Không đường kẻ dọc trong table
- [ ] Tất cả figure/table được tham chiếu trong text

### Ngôn Ngữ
- [ ] Không lỗi chính tả tiếng Anh
- [ ] Ngôi thứ ba, giọng văn khách quan
- [ ] Passive voice khi mô tả phương pháp
- [ ] Không dùng "I", "we" quá nhiều

### Nội Dung Logic
- [ ] Abstract giống "bản thu nhỏ" của toàn bài
- [ ] Introduction giới thiệu đúng vấn đề
- [ ] Methodology đủ chi tiết để replicate
- [ ] Results chỉ trình bày kết quả đã làm
- [ ] Conclusion không thêm thông tin mới

---

## Giai Đoạn 3b: Nội Dung Bổ Sung Theo Rubric DS108

### Datasheets for Datasets (BẮT BUỘC — 15% điểm)
- [ ] Hoàn thành `docs/DATASHEETS_FOR_DATASETS.md` theo template `docs/DATASHEETS_TEMPLATE.md`
- [ ] Trả lởi đầy đủ 7 nhóm câu hỏi: Motivation, Composition, Collection, Preprocessing, Uses, Distribution, Maintenance
- [ ] Tự đánh giá trung thực về Bias, rủi ro đạo đức, giới hạn của dataset
- [ ] Đưa vào Appendix báo cáo (5–6 trang)

### Zero Data Leakage Audit (YÊU CẦU TUYỆT ĐỐI — 30% điểm)
- [ ] Kiểm tra rolling window: `center=False` (không dùng thông tin tương lai)
- [ ] Kiểm tra DWT window: không look-ahead quá `window/2`
- [ ] Giải thích trong báo cáo lý do scaler fit trên toàn bộ không gây leakage cho downstream
- [ ] Tạo notebook `04_leakage_audit.ipynb` hoặc script audit riêng

### Data Assertions & Sanity Checks (Nâng Engineering — 15%)
- [ ] Tạo `src/data_assertions.py` với các hàm kiểm tra tự động
- [ ] Tích hợp assertions vào pipeline sau mỗi bước
- [ ] Có ít nhất 5 assertions khác nhau

### Tests & Reproducibility
- [ ] Viết `tests/test_data_loader.py`, `tests/test_features.py`, `tests/test_anomaly_labels.py`
- [ ] Pipeline chạy end-to-end không lỗi trên máy mới (test reproducibility)
- [ ] Cập nhật `README.md` hướng dẫn chi tiết A–Z (cài đặt, chạy, cấu trúc)
- [ ] Cập nhật `requirements.txt` đầy đủ (`pip freeze`)

### Missingness Mechanism Analysis (Sáng tạo — Frame 3)
- [ ] Phân tích `Q_lead = 0` (67.38%) như implicit missingness
- [ ] Giải thích MCAR / MAR / MNAR
- [ ] Ảnh hưởng đến tính toán `S` và `φ`

### Feature Selection Định Lượng
- [ ] Tính Mutual Information giữa engineered features và anomaly labels
- [ ] Tính VIF cho physical features (phát hiện đa cộng tuyến)
- [ ] Tree-based feature importance để biện luận giữ/bỏ features

---

## Giai Đoạn 4: Nộp Báo Cáo

- [ ] File PDF chính thức
- [ ] File source (Word/LaTeX) đi kèm
- [ ] Code repository link (GitHub) nếu cần
- [ ] Tên file: `DS108_Report_Electrimight_IEEE.pdf`
- [ ] Kiểm tra lại 1 lần cuối bằng checklist trên

---

> **Chúc bạn viết báo cáo thành công!** 🎓
