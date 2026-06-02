# Hướng dẫn Viết Data Codebook / Data Dictionary

> **Mục tiêu:** Đạt điểm A (Advanced/SOTA) tiêu chí 5 — Scientific Reporting & Ethics.  
> **Chuẩn mực:** Tham khảo rubric DS108 — mức Proficient (B) yêu cầu "Code Book / Data Dictionary rõ ràng"; mức Advanced (A) yêu cầu báo cáo đạt chất lượng hội nghị khoa học với tư duy phản biện xuất sắc.

---

## 1. Tại sao Codebook quan trọng?

Codebook là **hợp đồng giữa người tạo dữ liệu và người dùng dữ liệu**. Nó chứng minh bạn hiểu rõ từng byte trong tập dữ liệu mình tạo ra, không chỉ "chạy code xong output CSV".

Trong đồ án DS108, Codebook là **bắt buộc** ở mức B và là **cơ sở để tranh luận về Bias & Ethics** ở mức A.

---

## 2. Cấu trúc Codebook chuẩn (CSV)

Tạo file `data/processed/CODEBOOK.csv` (hoặc `CODEBOOK.md`) với các cột sau:

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| `column_name` | Tên cột trong CSV đầu ra | `Usage_kWh` |
| `data_type` | Kiểu dữ liệu kỹ thuật | `float64` |
| `unit` | Đơn vị đo lường | `kWh` |
| `source` | Nguồn gốc cột | `UCI raw / Engineered / Derived / Label` |
| `description_vi` | Mô tả bằng tiếng Việt | `Công suất tác dụng đo được từ đồng hồ thông minh` |
| `domain` | Miền giá trị hợp lý | `[0, 160.23]` |
| `physical_constraint` | Ràng buộc vật lý (nếu có) | `P ≥ 0` |
| `missing_strategy` | Cách xử lý missing | `None / Linear interpolation / Kept as 0` |
| `engineering_method` | Phương pháp tạo cột (nếu engineered) | `DWT db4 level-3, sliding window 64` |
| `notes` | Ghi chú đặc biệt | `CO2 chỉ có 8 unique values → biến tính toán` |

---

## 3. Phân loại cột theo nguồn gốc (Source Taxonomy)

Để thể hiện tư duy kiến trúc dữ liệu, phân loại rõ ràng:

| Loại | Ký hiệu | Ví dụ trong Electrimight |
|------|---------|--------------------------|
| **Raw** | Dữ liệu thô, chưa biến đổi | `date`, `Usage_kWh`, `CO2(tCO2)` |
| **Cleaned** | Đã qua làm sạch nhưng giữ nguyên semantic | `Lagging_Current_Power_Factor` (đã chia 100) |
| **Engineered** | Tạo từ thuật toán feature engineering | `lag_1`, `rolling_mean_24`, `dwt_cA3` |
| **Derived** | Tính toán từ công thức toán/vật lý | `apparent_power_S`, `phase_angle_phi` |
| **External** | Dữ liệu ngoại sinh merge vào | `temperature_2m`, `heat_index` |
| **Label** | Nhãn gán cho supervised learning | `anomaly_idling`, `anomaly_leakage` |
| **Meta** | Thông tin phụ trợ | `confidence_idling` |

---

## 4. Ví dụ điền Codebook cho Electrimight

### 4.1 Cột Raw

```csv
column_name,data_type,unit,source,description_vi,domain,physical_constraint,missing_strategy,engineering_method,notes
"date","datetime64[ns]","—","Raw","Thởi điểm đo lường từ hệ thống EMS nhà máy","2018-01-01 00:00 → 2018-12-31 23:45","—","None","—","Tần suất 15 phút; không có gap"
"Usage_kWh","float64","kWh","Raw","Công suất tác dụng đo từ đồng hồ thông minh cấp lò/cán","[0, 160.23]","P ≥ 0","None","—","Phân phối lệch phải mạnh (skew > 1)"
"CO2(tCO2)","float64","tCO2","Raw","Lượng CO₂ thải ra theo báo cáo EMS","{0,0.007,0.014,...}","—","None","—","Chỉ 8 giá trị khác biệt → biến tính toán từ Usage_kWh với hệ số cố định"
```

### 4.2 Cột Engineered (Time-Domain)

```csv
column_name,data_type,unit,source,description_vi,domain,physical_constraint,missing_strategy,engineering_method,notes
"lag_1","float64","kWh","Engineered","Giá trị Usage_kWh trễ 1 bước (15 phút)","[0, 160.23]","—","Forward fill cho edge","pandas.shift(1)","Dùng để bắt quán tính ngắn hạn"
"rolling_mean_96","float64","kWh","Engineered","Trung bình trượt 24 giờ (96 mẫu @ 15phút)","[0, 160.23]","—","center=False (không nhìn tương lai)","pandas.rolling(96).mean()","CRITICAL: center=False để tránh data leakage"
"NSM_sin","float64","—","Engineered","Mã hóa chu kỳ ngày của NSM (sin)","[-1, 1]","—","None","sin(2π·NSM/86400)","Đảm bảo tính liên tục tại nửa đêm"
```

### 4.3 Cột Derived (Physical)

```csv
column_name,data_type,unit,source,description_vi,domain,physical_constraint,missing_strategy,engineering_method,notes
"apparent_power_S","float64","kVA","Derived","Công suất biểu kiến: độ lớn phức của công suất trong mạch xoay chiều","[0, 170]","S = √(P²+Q²)","None","sqrt(Usage_kWh² + Q_lag²)","Chỉ báo quá tải nhiệt/cơ học của dây cáp & MBA"
"phase_angle_phi","float64","rad","Derived","Góc lệch pha giữa điện áp và dòng điện","[0, π/2]","φ = arccos(PF)","None","arccos(PF_lag)","Thang đo tuyến tính nhạy hơn PF khi phụ tải phi tuyến"
```

### 4.4 Cột Label (Anomaly)

```csv
column_name,data_type,unit,source,description_vi,domain,physical_constraint,missing_strategy,engineering_method,notes
"anomaly_idling","int8","—","Label","Nhãn chạy không tải (idling)","{0,1}","—","None","Rule-based: AND(Load_Type=='Light_Load', Off-hours, Usage>median, PF<0.50)","IEEE 519 severe penalty zone; confidence score kèm theo"
"anomaly_leakage","int8","—","Label","Nhãn rò rỉ năng lượng / concept drift","{0,1}","—","None","rolling_mean(672) > baseline × 1.05","ISO 50001 EnPI drift threshold; baseline = tuần đầu tiên"
"anomaly_overload","int8","—","Label","Nhãn quá tải cục bộ","{0,1}","—","None","Usage>P99.5 AND (Q>P99.5_Q OR PF<0.70)","IEEE C57.91; logic: extreme usage AND (reactive_high OR PF_collapse)"
```

---

## 5. Checklist trước khi nộp Codebook

- [ ] Tất cả cột trong `processed/` đều có mặt trong Codebook (không thiếu, không thừa).
- [ ] Mỗi cột có `description_vi` rõ ràng, không copy-paste tên cột.
- [ ] Cột **Engineered/Derived** phải ghi công thức hoặc thuật toán tạo ra.
- [ ] Cột có **missingness** phải giải thích tại sao missing và cách xử lý.
- [ ] Cột có **outliers** đã biết phải ghi chú (ví dụ: PF gốc > 1 do dạng %).
- [ ] Có cột `source` phân loại rõ Raw / Cleaned / Engineered / Derived / External / Label.
- [ ] Đơn vị đo lường (`unit`) được ghi đầy đủ cho mọi cột số.
- [ ] Ràng buộc vật lý (`physical_constraint`) được ghi cho các đại lượng điện năng.

---

## 6. Cách dùng Codebook để "ăn điểm A" trong báo cáo

Trong báo cáo IEEE, đừng chỉ liệt kê "Chúng tôi có Codebook". Hãy **biện luận**:

> *"Việc thiếu Codebook trong các tập dữ liệu công nghiệp công khai là một khoảng trống nghiêm trọng (Gebru et al., 2021). Chúng tôi xây dựng Codebook toàn diện cho 43 cột đầu ra, phân loại rõ nguồn gốc từng đặc trưng (Raw → Engineered → Derived). Điều này không chỉ đảm bảo tính tái lập, mà còn cho phép người dùng downstream đánh giá nhanh độ tin cậy của từng kênh dữ liệu — ví dụ, họ có thể loại bỏ các đặc trưng DWT nếu mô hình của họ không yêu cầu phân tích miền tần số."*

---

*Template này được thiết kế để đạt điểm tối đa tiêu chí 5 (Scientific Reporting & Ethics) trong rubric DS108 Capstone.*
