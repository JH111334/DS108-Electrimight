# Data Provenance & Collection Log

Tài liệu này ghi lại toàn bộ quá trình thu thập, kiểm tra và đánh giá chất lượng dữ liệu thô. Đây là bằng chứng cho công sức bỏ ra để có được bộ dữ liệu gốc, cũng như các "khoảng trống" (data quality issues) cần xử lý trong giai đoạn tiền xử lý.

---

## 1. Nguồn Dữ Liệu Gốc

### 1.1 Steel Industry Energy Consumption

| Thuộc tính | Giá trị |
|-----------|---------|
| **Nguồn** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption |
| **Tác giả** | Sathishkumar V E, Jangwoo Park, Yongyun Cho (Dongguk University, Korea) |
| **Năm công bố** | 2021 |
| **Địa điểm** | Nhà máy thép POSCO Gwangyang, Hàn Quốc |
| **Thở gian** | 01/01/2018 - 31/12/2018 (365 ngày) |
| **Tần suất** | 15 phút / mẫu |
| **Tổng số mẫu** | 35,040 |
| **Số biến** | 11 |

**Quá trình thu thập:**
- Dataset được công bố trên UCI với mục đích nghiên cứu về tiêu thụ điện năng ngành thép.
- Bộ dữ liệu gốc được tác giả thu thập từ hệ thống EMS (Energy Management System) của nhà máy POSCO Gwangyang.
- Dữ liệu bao gồm các thông số điện năng: công suất tác dụng (P), công suất phản kháng (Q), hệ số công suất (PF), CO2, và các biến thở gian.
- Tác giả đã tiến hành các bước làm sạch cơ bản trước khi công bố, nhưng vẫn để lại nhiều vấn đề chất lượng tiềm ẩn (xem mục 3).

### 1.2 Dữ Liệu Thở Tiết Gwangyang

| Thuộc tính | Giá trị |
|-----------|---------|
| **Nguồn** | Open-Meteo Historical Weather API |
| **URL** | https://archive-api.open-meteo.com/v1/archive |
| **Địa điểm** | Gwangyang, Jeollanam-do, Hàn Quốc |
| **Tọa độ** | 34.975°N, 127.589°E |
| **Thở gian** | 01/01/2018 - 31/12/2018 |
| **Tần suất** | 1 giờ / mẫu (hourly) |
| **Tổng số mẫu** | 8,760 |
| **Số biến** | 4 (nhiệt độ, lượng mưa, độ ẩm, tốc độ gió) |

**Quá trình thu thập:**
- API được gọi bằng script Python tự động (`src/weather.py`).
- Do API giới hạn độ dài mỗi request, dữ liệu được chia thành 12 batch (12 tháng) để tránh timeout.
- Mỗi batch được retry tối đa 5 lần với exponential backoff (2s, 4s, 8s, 16s, 32s).
- Tổng thở gian thu thập: ~8-15 phút (phụ thuộc vào mạng và rate limit của server).
- Dữ liệu được validate ngay sau khi fetch: kiểm tra số dòng (phải = 8760), kiểm tra null, kiểm tra range nhiệt độ (Hàn Quốc mùa đông không thể > 40°C).
- Xem `src/weather.py` cho chi tiết kỹ thuật thu thập API.
- Xem `src/weather_loader.py` cho chi tiết xử lý và tích hợp dữ liệu thở tiết.

---

## 2. Cấu Trúc Dữ Liệu Thô

### Steel Data Schema

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| date | datetime | Thở điểm đo lường (15-min interval) |
| Usage_kWh | float64 | Công suất tác dụng P (kWh) |
| Lagging_Current_Reactive.Power_kVarh | float64 | Công suất phản kháng trễ Q_lag (kVarh) |
| Leading_Current_Reactive_Power_kVarh | float64 | Công suất phản kháng sớm Q_lead (kVarh) |
| CO2(tCO2) | float64 | Lượng CO2 thải ra (tCO2) |
| Lagging_Current_Power_Factor | float64 | Hệ số công suất trễ |
| Leading_Current_Power_Factor | float64 | Hệ số công suất sớm |
| NSM | int64 | Số giây từ nửa đêm |
| WeekStatus | category | Weekday / Weekend |
| Day_of_week | category | Mon - Sun |
| Load_Type | category | Light_Load / Medium_Load / Maximum_Load |

### Weather Data Schema

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| time | datetime | Thở điểm đo (hourly) |
| temperature_2m | float64 | Nhiệt độ không khí 2m (°C) |
| precipitation | float64 | Lượng mưa (mm) |
| relative_humidity_2m | float64 | Độ ẩm tương đối (%) |
| windspeed_10m | float64 | Tốc độ gió 10m (km/h) |

---

## 3. Vấn Đề Chất Lượng Dữ Liệu Phát Hiện (Audit Results)

Đây là kết quả từ module `src/data_quality_audit.py` - chạy toàn bộ 5 nhóm kiểm tra trên dữ liệu thô.

### 3.1 Vi Phạm Ràng Buộc Vật Lý (CRITICAL)

| Cột | Vấn đề | Tỷ lệ | Mô tả |
|-----|--------|-------|-------|
| Lagging_Current_Power_Factor | > 1 | 99.9971% | Được báo cáo dạng % (0-100), không phải hệ số (0-1) |
| Leading_Current_Power_Factor | > 1 | 99.9971% | Tương tự cột trên |

**Ý nghĩa vật lý:** Power Factor là tỷ số P/S, luôn nằm trong [0, 1]. Giá trị 87.96 không có ý nghĩa vật lý.

**Cách xử lý:** Chia cho 100 để chuyển về hệ số.

### 3.2 Giá Trị Bằng 0 Bất Thường (WARNING)

| Cột | Số lượng | Tỷ lệ | Đánh giá |
|-----|----------|-------|----------|
| Lagging_Current_Reactive.Power_kVarh | 7,194 | 20.53% | Q = 0 khi thiết bị không hoạt động hoặc do PF = 1 |
| Leading_Current_Reactive_Power_kVarh | 23,610 | 67.38% | Q_lead = 0 là bình thường vì hệ thống không bù sớm |
| CO2(tCO2) | 20,990 | 59.90% | CO2 = 0 khi không sản xuất hoặc không ghi nhận |
| Usage_kWh | 1 | 0.0029% | 1 điểm có P = 0 |

### 3.3 Độ Phân Giải Thấp (WARNING)

| Cột | Số giá trị unique | Tỷ lệ | Vấn đề |
|-----|-------------------|-------|--------|
| CO2(tCO2) | 8 | 0.0228% | Chỉ có 8 giá trị khác nhau -> độ phân giải cực kỳ thấp |

**Đánh giá:** CO2 có thể được tính toán từ Usage_kWh bằng hệ số cố định, không phải đo lường trực tiếp. Đây là biến "tính toán" (derived) chứ không phải biến đo đạc.

### 3.4 Outliers

| Cột | Số outliers | Tiêu chí |
|-----|-------------|----------|
| Lagging_Current_Reactive.Power_kVarh | 1 | Vượt quá 5-sigma |

### 3.5 Nhất Quán Thở Gian & Phân Loại

| Kiểm tra | Kết quả |
|----------|---------|
| Thiếu mốc thở gian | 0 (dữ liệu liên tục) |
| Trùng lặp timestamp | 0 |
| Khoảng thở gian không đều | 0 |
| NSM khớp với timestamp | 100% |
| Day_of_week khớp với timestamp | 100% |
| WeekStatus khớp với dayofweek | 100% |

---

## 4. Công Sức Thu Thập & Xử Lý

### 4.1 Đối Với Steel Data
- **Thở gian tìm kiếm dataset:** ~2 giờ tìm kiếm trên UCI, Kaggle, Google Dataset Search.
- **Tiêu chí lựa chọn:** Phải là dữ liệu thở gian thực (time-series), có đầy đủ thông số điện năng (P, Q, PF), phải có ít nhất 1 năm để thể hiện tính mùa vụ.
- **Đánh giá chất lượng ban đầu:** Đọc paper gốc, kiểm tra metadata, xem trước 100 dòng.
- **Audit sau tải về:** Chạy 5 nhóm kiểm tra (physical, temporal, categorical, measurement, derived) phát hiện 8+ vấn đề cần xử lý.
- **Các bước xử lý dự kiến:** Scale PF, xử lý Q = 0, đánh giá CO2, xử lý outlier.

### 4.2 Đối Với Weather Data
- **Thở gian nghiên cứu API:** ~1.5 giờ đọc tài liệu Open-Meteo, tìm hiểu các tham số khí tượng phù hợp.
- **Lựa chọn vị trí:** Phải đúng tọa độ nhà máy POSCO Gwangyang (34.975, 127.589), không dùng dữ liệu thành phố gần nhất.
- **Số lượng request:** 12 requests (1 tháng/request) với retry logic.
- **Thở gian chờ đợi:** ~8-15 phút tổng cộng.
- **Validation sau thu thập:** Kiểm tra số dòng (8760), range nhiệt độ, độ ẩm, tốc độ gió.
- **Xử lý sau thu thập:** Resample từ 1h xuống 15 phút bằng nội suy tuyến tính, tạo 7 đặc trưng phái sinh.

---

## 5. Tóm Tắt "Khoảng Trống" Cần Xử Lý

| STT | Vấn đề | Mức độ | File xử lý |
|-----|--------|--------|------------|
| 1 | PF dạng % (0-100), cần về hệ số (0-1) | CRITICAL | `src/data_loader.py` (clean_data) |
| 2 | CO2 độ phân giải thấp (8 unique values) | WARNING | EDA / Feature Selection |
| 3 | Q_lag = 0 ở 20.5% điểm | WARNING | `src/data_loader.py` / EDA |
| 4 | Outlier 5-sigma ở Q_lag | WARNING | `src/anomaly_labels.py` |
| 5 | Weather resample 1h -> 15min | INFO | `src/weather_loader.py` |
| 6 | Weather feature engineering (7 features) | INFO | `src/weather_loader.py` |

---

*Tài liệu này được cập nhật động trong quá trình phát triển project. Lần cập nhật cuối: 2026-05-07.*
