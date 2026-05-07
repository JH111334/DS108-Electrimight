# Labeling Guideline for Steel Industry Anomaly Detection

Tài liệu này định nghĩa các quy tắc và nguyên tắc gán nhãn bất thường (anomaly labeling)
trên dữ liệu tiêu thụ điện năng ngành thép. Mục tiêu là đảm bảo tính khách quan,
có cơ sở khoa học và có thể lặp lại được (reproducible).

---

## 1. Nguyên Tắc Chung

### 1.1 Cơ Sở Khoa Học

Tất cả các ngưỡng (threshold) và điều kiện gán nhãn phải dựa trên:
- **Chuẩn ngành điện:** IEEE 519, IEC 61000, ISO 50001
- **Tài liệu kỹ thuật:** ASHRAE Handbook, POSCO Energy Management Guidelines
- **Nghiên cứu liên quan:** Các công bố về anomaly detection trong ngành thép

### 1.2 Confidence Score

Mỗi nhãn được gán kèm theo **Confidence Score** (0.0 - 1.0):
- **1.0:** Chắc chắn (vi phạm ràng buộc vật lý rõ ràng)
- **0.7-0.9:** Rất khả nghi (nhiều điều kiện khớp)
- **0.4-0.6:** Khả nghi (một vài điều kiện khớp)
- **0.1-0.3:** Nhẹ nghi (dấu hiệu yếu)
- **0.0:** Không có dấu hiệu

### 1.3 Explainability

Mỗi nhãn phải có thể giải thích được (explainable). Không được dùng "black box"
hoặc ngưỡng tùy chọn không có lý do.

---

## 2. Định Nghĩa Các Loại Bất Thường

### 2.1 Idling (Chạy Không Tải / Lãng Phí Năng Lượng)

#### Định Nghĩa
Trạng thái thiết bị vẫn tiêu thụ điện nhưng không sản xuất ra công suất hữu ích.
Trong ngành thép, idling thường xảy ra:
- Luyện thép dừng máy nhưng vẫn duy trì nhiệt độ lò
- Hệ thống HVAC hoạt động khi nhà xưởng không có công nhân
- Máy biến áp không tải (no-load loss) kéo dài

#### Tiêu Chuẩn IEEE / IEC
- **IEEE 519-2014:** PF < 0.85 cho tải công nghiệp là không chấp nhận được.
  -> PF < 0.50 là **nguy hiểm nghiêm trọng** (severe penalty zone).
- **IEC 61000-3-6:** Hệ số công suất trung bình phải >= 0.90.

#### Điều Kiện Gán Nhãn (AND logic)

| Điều Kiện | Lý Do | Nguồn |
|-----------|-------|-------|
| Load_Type == "Light_Load" | Thiết bị đang ở chế độ tải nhẹ hoặc không tải | Dataset classification |
| Off-hours (NSM < 21600 hoặc NSM > 75600) HOẶC Weekend | Ngoài giờ sản xuất chính | ISO 50001 shift schedule |
| Usage_kWh > median(Usage_kWh) | Vẫn tiêu thụ điện cao bất thường | Statistical baseline |
| PF_lag < 0.50 | Hệ số công suất cực kỳ thấp - dấu hiệu idling | IEEE 519 severe threshold |

#### Confidence Score

```
score = 0.3 * I(Load_Type == "Light_Load")
      + 0.3 * I(Off-hours)
      + 0.2 * I(Usage_kWh > median)
      + 0.2 * I(PF_lag < 0.50)
```

Nếu tất cả 4 điều kiện đúng: score = 1.0
Nếu chỉ có PF < 0.50: score = 0.50 (nửa vùng nguy hiểm)

#### Ví Dụ
```
Timestamp: 2018-01-01 02:00 (Monday, early morning)
Load_Type: Light_Load
Usage_kWh: 12.5  (median = 4.57 -> cao bất thường)
PF_lag: 0.42     (< 0.50)
=> anomaly_idling = 1, confidence = 1.0
Explanation: "Light load off-hours with high consumption and critically low PF"
```

---

### 2.2 Leakage / Concept Drift (Rò Rỉ / Trôi Đặc Tính)

#### Định Nghĩa
Sự gia tăng tiềm ẩn của mức tiêu thụ điện ở cùng điều kiện vận hành qua thở gian.
Có thể do:
- Thiết bị cũ hóa, hiệu suất giảm
- Rò rỉ nhiệt qua vật liệu cách nhiệt
- Sai lệch cảm biến (sensor drift)
- Thay đổi chất lượng nguyên liệu

#### Tiêu Chuẩn ISO 50001
- **ISO 50001:2018:** Phải theo dõi EnPIs (Energy Performance Indicators) để phát hiện
  sự thay đổi bất thường trong hiệu suất năng lượng.
- Ngưỡng cảnh báo: +5% so với baseline (industry standard).

#### Điều Kiện Gán Nhãn

| Điều Kiện | Lý Do | Nguồn |
|-----------|-------|-------|
| Rolling mean(Usage_kWh, 672) > baseline * 1.05 | Tăng 5% so với baseline | ISO 50001 warning threshold |
| baseline = mean(tuần đầu tiên) | Chu kỳ sản xuất ổn định nhất | Domain assumption |

#### Confidence Score

```
pct_increase = (rolling_mean - baseline) / baseline * 100

if pct_increase > 20%:   score = 1.0  (nguy hiểm)
elif pct_increase > 10%: score = 0.7  (cảnh báo)
elif pct_increase > 5%:  score = 0.4  (nhẹ)
else:                    score = 0.0
```

#### Ví Dụ
```
Baseline (tuần 1): mean = 25.3 kWh
Rolling mean (tuần 20): 28.1 kWh
pct_increase = 11.1%
=> anomaly_leakage = 1, confidence = 0.7
Explanation: "Usage increased 11.1% above baseline over 20 weeks - possible equipment degradation"
```

---

### 2.3 Overload (Quá Tải Cục Bộ)

#### Định Nghĩa
Sự vượt quá công suất định mức của thiết bị hoặc hệ thống, dẫn đến:
- Quá nhiệt dây dẫn / máy biến áp
- Sụt áp nghiêm trọng
- Nguy cơ cháy nổ

#### Tiêu Chuẩn IEEE / IEC
- **IEEE C57.91:** Quá tải máy biến áp > 150% định mức chỉ được phép trong thở gian ngắn.
- **IEC 60909-0:** Dòng ngắn mạch phải được tính toán để bảo vệ quá tải.

#### Điều Kiện Gán Nhãn

| Điều Kiện | Lý Do | Nguồn |
|-----------|-------|-------|
| Usage_kWh > percentile 99.5 | Outlier cực đoan (top 0.5%) | Percentile-based robust outlier |
| Q_reactive > percentile 99.5_Q | Công suất phản kháng cũng cao bất thường | Domain knowledge |
| PF_lag < 0.70 | PF suy giảm rõ rệt dưới mức chấp nhận | IEEE 519 minimum |

Logic: `Usage_cao AND (Reactive_cao OR PF_thấp)`

#### Confidence Score

```
score = 0.5 * I(Usage extreme outlier)
      + 0.25 * I(Reactive extreme outlier)
      + 0.25 * I(PF_lag < 0.70)
```

#### Ví Dụ
```
Usage_kWh: 142.5  (P99.5 = 129.4 -> vượt ngưỡng)
Q_lag: 95.3       (rất cao)
PF_lag: 0.65      (< 0.70)
=> anomaly_overload = 1, confidence = 1.0
Explanation: "Near-extreme usage with high reactive power and PF collapse below 0.70"
```

---

## 3. Quy Trình Gán Nhãn

### Bước 1: Tiền Xử Lý
1. Chạy `data_quality_audit.py` để đảm bảo dữ liệu đã được làm sạch.
2. Kiểm tra PF đã được scale về [0, 1] (không còn dạng %).
3. Kiểm tra không còn null trong các cột quan trọng.

### Bước 2: Tính Toán Ngưỡng

```python
# Idling thresholds
usage_median = df["Usage_kWh"].median()
pf_critical = 0.50  # IEEE 519 severe

# Leakage thresholds
baseline_window = 672  # 1 tuần @ 15min
leakage_threshold_pct = 5.0  # ISO 50001

# Overload thresholds
usage_percentile = 0.995  # Top 0.5%

pf_overload_threshold = 0.70  # IEEE 519 minimum
```

### Bước 3: Gán Nhãn & Tính Confidence

Chạy từng hàm `label_idling()`, `label_leakage()`, `label_overload()`
với confidence score tương ứng.

### Bước 4: Validation

- Kiểm tra tỷ lệ anomalies (không nên > 10% tổng dữ liệu).
- Kiểm tra sự chồng chéo giữa các nhãn.
- Trực quan hóa các điểm anomalies để xác nhận.

---

## 4. Tham Khảo

1. **IEEE Std 519-2014** - IEEE Standard for Harmonic Control in Electric Power Systems
2. **IEC 61000-3-6** - Electromagnetic compatibility (EMC) - Assessment of emission limits
3. **ISO 50001:2018** - Energy management systems - Requirements with guidance for use
4. **IEEE C57.91-2011** - IEEE Guide for Loading Mineral-Oil-Immersed Transformers
5. **ASHRAE Handbook** - HVAC Applications, Industrial Facilities
6. Sathishkumar V E et al. "Steel Industry Energy Consumption Dataset", UCI ML Repository, 2021

---

*Guideline này là tài liệu sống và có thể được cập nhật khi có thêm thông tin từ chuyên gia ngành hoặc nghiên cứu mới.*
