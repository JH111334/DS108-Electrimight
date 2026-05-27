# Hướng Dẫn Format Báo Cáo IEEE — DS108 Electrimight

> Tài liệu này tóm tắt các quy tắc format IEEE áp dụng cho báo cáo đồ án **DS108: Tiền xử lý và xây dựng bộ dữ liệu — Dự báo điện & Phân loại rủi ro điện**.

---

## 1. Cấu Trúc Tổng Quan Báo Cáo IEEE

IEEE (Institute of Electrical and Electronics Engineers) yêu cầu cấu trúc báo cáo kỹ thuật theo thứ tự sau:

| STT | Thành phần | Mô tả |
|-----|-----------|-------|
| 1 | **Title** | Ngắn gọn, rõ ràng, chứa từ khóa chính |
| 2 | **Author(s) & Affiliation** | Tên tác giả, tổ chức, email |
| 3 | **Abstract** | 150–250 từ, tóm tắt toàn bộ nội dung |
| 4 | **Keywords** | 3–5 từ khóa, phân cách bằng dấu phẩy |
| 5 | **I. Introduction** | Bối cảnh, vấn đề, mục tiêu, đóng góp |
| 6 | **II. Related Work** | Tổng quan nghiên cứu liên quan |
| 7 | **III. Methodology** | Phương pháp, thiết kế, công thức, giải thuật |
| 8 | **IV. Experimental Setup / Dataset** | Dữ liệu, môi trường, tham số |
| 9 | **V. Results and Discussion** | Kết quả, bảng biểu, đồ thị, phân tích |
| 10 | **VI. Conclusion** | Tóm tắt, hạn chế, hướng phát triển |
| 11 | **Acknowledgments** (tùy chọn) | Lợi cảm ơn |
| 12 | **References** | Danh sách tài liệu tham khảo đánh số [1], [2], ... |

---

## 2. Quy Tắc Trình Bày (Typography & Layout)

### 2.0 Giới Hạn Độ Dài Báo Cáo
- **Tổng độ dài tối đa**: 20 trang đôi (2 cột) hoặc tương đương 40 trang đơn (1 cột)
- Giới hạn này bao gồm toàn bộ nội dung từ Abstract đến References, không tính Appendix

### 2.1 Font & Kích Thước
- **Font chính**: Times New Roman, 10 pt
- **Tiêu đề bài báo**: 14 pt, bold, centered
- **Tiêu đề mục cấp 1 (I, II, III...)**: 10 pt, **bold**, ALL CAPS, centered hoặc left-aligned
- **Tiêu đề mục cấp 2 (A, B, C...)**: 10 pt, **bold**, Title Case, left-aligned
- **Tiêu đề mục cấp 3**: 10 pt, **bold**, sentence case, indented, kết thúc bằng dấu chấm.

### 2.2 Lề & Cột
- **Lề**: 1 inch (2.54 cm) tất cả các cạnh
- **Số cột**: Thường 2 cột (IEEE conference/journal style)
- **Khoảng cách dòng**: Single spacing
- **Khoảng cách đoạn**: 1 dòng trống giữa các đoạn
- **Indent**: Không thụt đầu dòng; căn trái toàn bộ

### 2.3 Đánh Số
- **Mục chính**: I, II, III, IV, V, VI...
- **Mục phụ**: A, B, C... hoặc 1), 2), 3)...
- **Mục con**: 1, 2, 3... hoặc a, b, c...

---

## 3. Quy Tắc Trích Dẫn (IEEE Citation Style)

IEEE sử dụng hệ thống **đánh số trong ngoặc vuông** `[1]` theo thứ tự xuất hiện trong văn bản.

### 3.1 In-Text Citation
```
The DWT method has been widely applied in load forecasting [1], [2].
As shown in [3], the Daubechies wavelet provides optimal decomposition.
Several studies [4]–[6] have demonstrated GAN effectiveness.
```

### 3.2 Reference List Format

**Journal Article:**
```
[1] A. B. Author, "Title of article," *Abbrev. Title of Journal*, vol. x, no. x, pp. xxx–xxx, Month Year.
```

**Conference Paper:**
```
[2] A. B. Author, "Title of paper," in *Proc. Conference Name*, City, Country, Year, pp. xxx–xxx.
```

**Book:**
```
[3] A. B. Author, *Title of Book*. City, State/Country: Publisher, Year.
```

**Online/Dataset:**
```
[4] "Dataset Name," Source/Repository. [Online]. Available: URL
```

**Website:**
```
[5] Author/Organization, "Page Title." Website Name. [Online]. Available: URL
```

---

## 4. Quy Tắc Hình Ảnh & Bảng Biểu

### 4.1 Hình (Figures)
- Đánh số liên tục: Fig. 1, Fig. 2, Fig. 3...
- Caption đặt **bên dưới** hình, centered hoặc left-aligned
- Cú pháp: `Fig. 1. Mô tả chi tiết về hình ảnh.`
- Hình phải rõ nét, độ phân giải ≥ 300 DPI
- Trong văn bản phải có tham chiếu đến hình: `"As shown in Fig. 1, ..."`

### 4.2 Bảng (Tables)
- Đánh số liên tục: TABLE I, TABLE II, TABLE III...
- Caption đặt **bên trên** bảng, centered, ALL CAPS
- Cú pháp: `TABLE I: PERFORMANCE COMPARISON`
- Sử dụng đường kẻ ngang tối thiểu; tránh đường kẻ dọc
- Đơn vị đo rõ ràng trong header

### 4.3 Công Thức Toán Học
- Đánh số công thức nằm bên phải trong ngoặc đơn:
  ```
  S = √(P² + Q²)                                      (1)
  ```
- Các biến phải được định nghĩa ngay sau công thức

---

## 5. Các Lỗi Thường Gặp Cần Tránh

| ❌ Sai | ✅ Đúng |
|-------|--------|
| Trích dẫn theo kiểu APA (Author, Year) | `[1]`, `[2]`, `[3]` |
| Abstract quá dài (>250 từ) | 150–250 từ |
| Thêm nội dung mới trong Conclusion | Chỉ tóm tắt, không thêm mới |
| Hình không được tham chiếu trong text | Mọi hình phải có ít nhất 1 lần tham chiếu |
| Sử dụng ngôi thứ nhất (I, we) nhiều | Dùng passive voice hoặc ngôi thứ ba |
| Tiêu đề quá dài, mơ hồ | Ngắn gọn, chứa từ khóa |
| Thiếu đơn vị đo trong bảng | Ghi rõ đơn vị (kWh, %, s...) |

---

## 6. Gợi Ý Tiêu Đề Báo Cáo

Dưới đây là một số gợi ý tiêu đề phù hợp IEEE cho dự án này:

**Gợi ý 1 (Ngắn gọn):**
> *Wavelet-Based Feature Engineering and GAN Augmentation for Steel Industry Energy Consumption Dataset*

**Gợi ý 2 (Chi tiết hơn):**
> *A Preprocessing Pipeline for Electricity Forecasting and Anomaly Detection in Steel Industry Using Discrete Wavelet Transform and Generative Adversarial Networks*

**Gợi ý 3 (Tập trung đóng góp):**
> *Multi-Domain Feature Extraction and Synthetic Data Generation for Industrial Energy Risk Classification*

---

## 7. Checklist Trước Khi Nộp

- [ ] Đúng font Times New Roman 10 pt
- [ ] Lề 1 inch (2.54 cm) 4 cạnh
- [ ] Abstract 150–250 từ
- [ ] Có 3–5 Keywords
- [ ] Các mục đánh số I, II, III... liên tục
- [ ] Tất cả hình ảnh, bảng biểu đều được tham chiếu trong text
- [ ] Công thức được đánh số và định nghĩa biến
- [ ] Trích dẫn theo định dạng IEEE `[n]`
- [ ] References sắp xếp theo thứ tự xuất hiện
- [ ] Không có lỗi chính tả, ngữ pháp
- [ ] Không thêm nội dung mới trong Conclusion
- [ ] File đặt tên theo quy định (ví dụ: `DS108_Report_IEEE.pdf`)

---

> **Lưu ý**: Nếu dùng LaTeX, nên sử dụng class `IEEEtran.cls`. File template LaTeX đi kèm trong thư mục này: `IEEE_Report_Template.tex`.
