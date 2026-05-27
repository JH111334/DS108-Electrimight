# Hướng dẫn Viết Datasheets for Datasets — Ăn điểm A

> **Mục tiêu:** Đạt điểm A (Advanced/SOTA) tiêu chí 5 — Scientific Reporting & Ethics.  
> **Chuẩn mực:** Gebru et al., 2021. *Datasheets for Datasets*. Communications of the ACM.  
> **Điểm then chốt:** Không chỉ "trả lờii có/không", mà phải thể hiện **tư duy phản biện xuất sắc** về Bias, rủi ro đạo đức, và giới hạn của bộ dữ liệu.

---

## 1. Triết lý "Ăn điểm A" cho Datasheet

Rubric DS108 mức **Proficient (B)** chỉ yêu cầu: *"Tuân thủ nghiêm ngặt định dạng IEEE/ACM... Có tài liệu Code Book / Data Dictionary rõ ràng."*

Rubric mức **Advanced (A)** yêu cầu cao hơn hẳn:
> *"Phần 'Datasheets for Datasets' thể hiện tư duy phản biện xuất sắc: **Tự đánh giá trung thực** về các **Bias (Thiên lệch)**, **rủi ro đạo đức** và **giới hạn** của bộ dữ liệu do mình tạo ra."*

**Sai lầm phổ biến của sinh viên:**
- Chỉ copy template và điền "Không có" cho hầu hết các câu hỏi.
- Không thừa nhận bất kỳ thiên lệch hay giới hạn nào → giảng viên đánh giá là thiếu tư duy phản biện.
- Viết quá ngắn, thiếu luận giải.

**Chiến lược đúng:**
- Mỗi câu trả lờii phải có **luận giải** (justification), không chỉ trả lờii.
- Phải **chủ động chỉ ra ít nhất 3–5 bias/giới hạn** của dataset.
- Phải đề xuất **khuyến nghị sử dụng** (recommended use cases) và **cảnh báo sử dụng sai** (misuse cases).

---

## 2. Cấu trúc 7 phần của Datasheet (theo Gebru et al.)

| Phần | Trọng tâm để ăn điểm A | Độ dài khuyến nghị |
|------|------------------------|-------------------|
| 1. Motivation | Tại sao dataset này **cần thiết** cho cộng đồng? Gap gì đang tồn tại? | 2–3 đoạn |
| 2. Composition | Phân tích chi tiết về **đại diện** (representation): Ai/Cái gì được đại diện? Ai bị loại ra? | 3–4 đoạn |
| 3. Collection Process | Quy trình thu thập có **minh bạch** không? Có phụ thuộc vào API bên thứ ba không? | 2–3 đoạn |
| 4. Preprocessing | **Justify** từng bước tiền xử lý. Tại sao chọn linear interpolation? Tại sao GAN? | 3–4 đoạn |
| 5. Uses | **Use cases phù hợp** và **misuse cases nguy hiểm**. | 2–3 đoạn |
| 6. Distribution | License, access control, versioning. | 1–2 đoạn |
| 7. Maintenance | Ai chịu trách nhiệm? Cơ chế cập nhật/corrigendum? | 1–2 đoạn |

---

## 3. Ví dụ điền Datasheet cho Electrimight (Mẫu ăn điểm A)

### 3.1 Motivation — Tại sao dataset này cần thiết?

**❌ Cách viết mức C (Basic):**
> "Dataset được tạo để hỗ trợ dự báo tiêu thụ điện."

**✅ Cách viết mức A (Advanced):**
> "Các tập dữ liệu tiêu thụ điện công nghiệp công khai hiện nay (ví dụ: UCI Individual Household Electric Power Consumption) chủ yếu tập trung vào phụ tải dân dụng với tần suất thấp (1 giờ), thiếu các đặc trưng vật lý phái sinh ($S$, $\varphi$) và nhãn bất thường dựa trên chuẩn ngành. Điều này tạo ra một **khoảng trống nghiên cứu (research gap)**: không có benchmark dataset nào cho ngành thép ở độ phân giải 15 phút kết hợp đặc trưng wavelet, đặc trưng vật lý, và nhãn bất thường đa lớp. Electrimight được xây dựng nhằm lấp đầy khoảng trống này, cung cấp nền tảng để so sánh các phương pháp dự báo tải và phát hiện bất thường trong môi trường công nghiệp nặng."

---

### 3.2 Composition — Phân tích Bias & Representation

**❌ Cách viết mức C:**
> "Dataset có 35.040 mẫu, 11 biến gốc. Không có dữ liệu cá nhân."

**✅ Cách viết mức A (tập trung Bias critique):**
> "**Thiên lệch địa lý (Geographic Bias):** Dữ liệu chỉ thu thập tại một nhà máy thép duy nhất (POSCO Gwangyang, Jeollanam-do, Hàn Quốc, vĩ độ 34,975°N). Điều kiện khí hậu ôn đới ẩm, chu kỳ sản xuất 3 ca/ngày của nhà máy này có thể **không đại diện** cho các nhà máy thép ở vùng nhiệt đới (ví dụ: Việt Nam, Ấn Độ) nơi nhu cầu làm mát chiếm tỷ trọng lớn hơn. Dữ liệu thời tiết cũng chỉ phản ánh khí hậu Gwangyang, không tổng quát hóa cho các vùng khác.
>
> **Thiên lệch thời gian (Temporal Bias):** Dữ liệu chỉ bao phủ năm 2018. Năm này không có sự kiện bất thường vĩ mô lớn (đại dịch, khủng hoảng năng lượng). Các mô hình huấn luyện trên tập dữ liệu này có thể **không chịu được stress-test** trong điều kiện vận hành khẩn cấp hoặc suy thoái kinh tế.
>
> **Thiên lệch cảm biến (Sensor Bias):** Tần suất 15 phút có thể **bỏ lỡ các sự kiện transient** (ngắn hạn < 15 phút) như đóng cắt tụ điện, khởi động động cơ lớn, hoặc sự cố điện ngắn hạn. Các nhãn bất thường dựa trên ngưỡng vật lý cố định có thể không bắt được các dạng bất thường mới (unknown unknowns).
>
> **Thiên lệch nhãn (Label Bias):** Ba lớp bất thường (idling, leakage, overload) được định nghĩa bởi nhóm tác giả dựa trên chuẩn IEEE 519 và ISO 50001. Mặc dù có cơ sở kỹ thuật, các ngưỡng này là **subjective** ở mức độ nhất định: ví dụ, ngưỡng PF < 0.50 cho idling được chọn vì nó nằm trong "severe penalty zone" của IEEE 519, nhưng một kỹ sư vận hành khác có thể tranh luận rằng ngưỡng này quá nghiêm ngặt hoặc quá lỏng cho loại lò cụ thể. Confidence score (0–1) được tính bằng trọng số cố định, chưa được xác thực bằng đánh giá của chuyên gia ngành (inter-annotator agreement)."

---

### 3.3 Collection Process — Minh bạch & Phụ thuộc

**✅ Cách viết mức A:**
> "Dữ liệu điện năng được thu thập từ UCI Machine Learning Repository (đã công bố), tác giả gốc là Sathishkumar V E et al. từ Dongguk University, Hàn Quốc. Chúng tôi **không trực tiếp kiểm soát** quá trình thu thập ban đầu; metadata cho biết dữ liệu được ghi nhận từ hệ thống EMS của nhà máy thép POSCO Gwangyang, nhưng chúng tôi không có quyền truy cập vào log cảm biến gốc, thời gian hiệu chuẩn (calibration), hoặc log bảo trì thiết bị. Điều này tạo ra một **điểm mù (blind spot)**: nếu cảm biến bị lệch (sensor drift) trong một khoảng thời gian ngắn, chúng tôi không thể phát hiện hoặc điều chỉnh.
>
> Dữ liệu thời tiết được thu thập qua Open-Meteo Historical Weather API (open-meteo.com), một dịch vụ miễn phí cung cấp dữ liệu tái phân tích (reanalysis) từ mô hình khí tượng toàn cầu. Mặc dù Open-Meteo có độ tin cậy cao, dữ liệu này là **ước tính mô hình**, không phải quan trắc trực tiếp tại nhà máy. Sai số vị trí (tọa độ 34,975°N, 127,589°E so với vị trí chính xác của trạm đo) có thể gây chênh lệch nhỏ trong nhiệt độ và độ ẩm."

---

### 3.4 Preprocessing — Justification cho từng bước

**✅ Cách viết mức A:**
> **Interpolation:** "Dữ liệu thời tiết hourly được nội suy xuống 15 phút bằng linear interpolation. Lựa chọn này dựa trên giả định rằng các đại lượng khí tượng (nhiệt độ, độ ẩm) biến đổi liên tục theo thời gian. Tuy nhiên, **giả định này có thể sai** trong trường hợp mưa rào đột ngột hoặc gió giật, nơi linear interpolation sẽ làm mất biên độ cực đại. Các phương pháp khác như spline cubic hoặc Kriging có thể bảo toàn biên độ tốt hơn nhưng phức tạp hơn và không được áp dụng trong phiên bản này.
>
> **GAN Augmentation:** "Chúng tôi sử dụng GAN fully-connected để tổng hợp 500 mẫu cho lớp thiểu số. Quyết định này được đưa ra vì tỷ lệ bất thường chỉ 2,8%. Tuy nhiên, **GAN có rủi ro mode collapse**: generator có thể chỉ học được một vài "mẫu" bất thường phổ biến và bỏ qua các biến thể hiếm. Chúng tôi xác thực bằng PCA/t-SNE overlap và sai số Frobenius của ma trận tương quan, nhưng **không có cách nào đảm bảo 100%** rằng synthetic data bao phủ toàn bộ không gian phân phối của lớp thiểu số."

---

### 3.5 Uses — Use cases & Misuse cases

**✅ Cách viết mức A:**
> **Use cases phù hợp:**
> - Dự báo tải điện ngắn hạn (15 phút → 1 giờ) cho nhà máy thép có đặc điểm vận hành tương tự POSCO Gwangyang.
> - Phát hiện bất thường điện năng dựa trên ngưỡng vật lý cho các hệ thống EMS công nghiệp nặng.
> - Benchmarking các phương pháp feature engineering (DWT, physical features) trên dữ liệu chuỗi thời gian công nghiệp.
>
> **Misuse cases / Cảnh báo:**
> - **KHÔNG NÊN** dùng để ra quyết định bảo trì dự đoán (predictive maintenance) quan trọng mà không có sự xác nhận của kỹ sư vận hành. Nhãn bất thường là heuristic, không phải chẩn đoán kỹ thuật.
> - **KHÔNG NÊN** áp dụng trực tiếp cho nhà máy ở khí hậu nhiệt đới hoặc vĩ độ khác mà không có hiệu chuẩn lại ngưỡng.
> - **KHÔNG NÊN** dùng GAN-augmented data để huấn luyện mô hình quyết định pháp lý hoặc an toàn tuyệt đối (safety-critical) vì synthetic data có thể chứa artifacts không có trong thực tế.

---

### 3.6 Distribution & Maintenance

**✅ Cách viết mức A:**
> "Dataset được phân phối dưới giấy phép tương thích với UCI License (CC BY 4.0 cho phần dữ liệu gốc). Dữ liệu thời tiết từ Open-Meteo không có hạn chế bản quyền. Tuy nhiên, chúng tôi **khuyến nghị** người dùng trích dẫn cả bộ dữ liệu gốc (Sathishkumar et al., 2021) và bộ dữ liệu đã xử lý (Electrimight) khi sử dụng.
>
> **Hạn chế pháp lý:** Mặc dù không chứa thông tin cá nhân (PII), dữ liệu tiêu thụ điện chi tiết 15 phút của một nhà máy cụ thể có thể được coi là **thông tin mật kinh doanh (trade secret)** nếu nhà máy không đồng ý công khai. Chúng tôi dựa vào việc tác giả gốc đã công bố dữ liệu, nhưng người dùng tái phân phối cần lưu ý rủi ro này.
>
> **Maintenance:** Phiên bản hiện tại là v1.0 (tháng 6/2026). Không có kế hoạch cập nhật định kỳ. Các erratum sẽ được ghi nhận qua GitHub Issues. Nếu phát hiện lỗi trong nhãn bất thường hoặc feature engineering, chúng tôi sẽ phát hành phiên bản mới và giữ lại phiên bản cũ qua Git tags."

---

## 4. Checklist trước khi nộp Datasheet

- [ ] Đã trả lờii đầy đủ 7 phần của Gebru et al.
- [ ] Mỗi câu trả lờii có **luận giải** (justification), không chỉ "Có/Không".
- [ ] Đã chỉ ra ít nhất **3 bias** cụ thể của dataset (địa lý, thời gian, cảm biến, nhãn...).
- [ ] Đã phân tích **rủi ro đạo đức** (ethics): misuse cases, PII, trade secret, safety-critical.
- [ ] Đã thừa nhận **giới hạn** (limitations) một cách trung thực: những gì dataset KHÔNG thể làm.
- [ ] Đã đề xuất **khuyến nghị sử dụng** rõ ràng (recommended vs discouraged use cases).
- [ ] Đã giải thích **tại sao** chọn từng phương pháp tiền xử lý (không chỉ "làm gì").
- [ ] Datasheet được đặt trong báo cáo IEEE như một **Phụ lục (Appendix)**.

---

## 5. Cách trích dẫn trong báo cáo IEEE

> *"Theo chuẩn 'Datasheets for Datasets' [Gebru et al., 2021], Phụ lục A trình bày tài liệu minh bạch hóa toàn diện cho bộ dữ liệu Electrimight. Khác với các tập dữ liệu công nghiệp công khai thường thiếu tài liệu phụ lục, chúng tôi chủ động phân tích các thiên lệch địa lý, thời gian, và cảm biến; đồng thời cảnh báo các trường hợp sử dụng sai (misuse cases) có thể dẫn đến quyết định vận hành nguy hiểm. Điều này phản ánh tư duy phản biện về đạo đức AI mà một Data Architect chuyên nghiệp cần có."*

---

*Hướng dẫn này được thiết kế để đạt điểm tối đa tiêu chí 5 (Scientific Reporting & Ethics) — mức Advanced/SOTA (A / 9.0–10đ) trong rubric DS108 Capstone.*
