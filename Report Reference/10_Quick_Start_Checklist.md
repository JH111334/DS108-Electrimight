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

## Giai Đoạn 4: Nộp Báo Cáo

- [ ] File PDF chính thức
- [ ] File source (Word/LaTeX) đi kèm
- [ ] Code repository link (GitHub) nếu cần
- [ ] Tên file: `DS108_Report_Electrimight_IEEE.pdf`
- [ ] Kiểm tra lại 1 lần cuối bằng checklist trên

---

> **Chúc bạn viết báo cáo thành công!** 🎓
