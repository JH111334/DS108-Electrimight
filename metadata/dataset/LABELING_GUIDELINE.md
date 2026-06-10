# Proxy Anomaly Labeling Methodology

Tài liệu này mô tả phương pháp gán nhãn của DS108-Electrimight. Các nhãn được
thiết kế cho offline benchmarking và report analysis. Chúng là **proxy labels**,
không phải nhãn lỗi thiết bị đã được maintenance logs hoặc SCADA xác nhận.

## Scope

Implementation hiện tại gán ba nhóm pattern trong dữ liệu tiêu thụ điện công
nghiệp:

- idling hoặc energy-waste behavior;
- leakage/concept drift trong mức tiêu thụ kéo dài;
- local overload-risk behavior.

Dataset mặc định là UCI Steel Industry Energy Consumption. `src/schema.py` cho
phép mở rộng sang industrial meter data khác nếu có timestamp và active
energy/power. Reactive power, power factor, load type và weather fields giúp
tăng interpretability nhưng cần schema mapping cẩn thận khi đổi dataset.

## Labeling Principles

Thiết kế nhãn theo bốn nguyên tắc:

1. **Explainability:** mỗi positive label phải có lý do đọc được.
2. **Physical plausibility:** threshold bám vào hành vi điện, operating context
   hoặc robust statistics.
3. **No target leakage:** label columns là annotations/evaluation targets, không
   phải ordinary predictive features.
4. **Conservative reporting:** proxy labels chỉ biểu thị suspicious patterns,
   không khẳng định plant failures.

Mỗi label có confidence score trong khoảng 0 đến 1. Score phản ánh số lượng và
độ mạnh của các điều kiện bằng chứng.

## Label 1: Idling

Idling biểu thị tiêu thụ điện trong bối cảnh low-production/off-hours kèm bằng
chứng power factor kém. Trong nhà máy thép, pattern này có thể tương ứng thiết
bị vẫn được cấp điện trong khi tạo ít useful output.

Rule structure hiện tại:

| Evidence | Interpretation |
|---|---|
| Light-load status hoặc low-load proxy | Operating state tương thích với idling |
| Off-hours hoặc weekend timestamp | Production demand kỳ vọng thấp hơn |
| Usage above median | Vẫn có tiêu thụ đáng kể |
| Effective power factor below 0.50 | Bằng chứng power-factor degradation nghiêm trọng |

Logic chỉ gán `anomaly_idling` khi các điều kiện liên quan cùng xuất hiện. Gold
dataset hiện có **10 idling proxy rows**.

## Label 2: Leakage / Concept Drift

Leakage/concept drift biểu thị mức tiêu thụ tăng kéo dài so với baseline đầu kỳ.
Nhãn này dùng để phát hiện pattern suy giảm dần như thiết bị lão hóa, thermal
loss, sensor drift hoặc thay đổi quy trình.

Rule structure hiện tại:

| Evidence | Interpretation |
|---|---|
| rolling mean over 672 observations | Một tuần dữ liệu 15 phút |
| baseline from the early stable period | Mức tiêu thụ tham chiếu |
| increase above 5% | Tín hiệu yếu của drift/leakage-like behavior |
| larger increases | Confidence tier cao hơn |

Gold dataset hiện có **2.336 leakage/concept-drift proxy rows**. Đây là nhóm
proxy anomaly chiếm tỷ trọng lớn nhất.

## Label 3: Local Overload

Local overload biểu thị active usage cực trị đi kèm reactive-power hoặc
power-factor stress. Nhãn này đánh dấu các giai đoạn mà electrical load có vẻ
bất thường cao.

Rule structure hiện tại:

| Evidence | Interpretation |
|---|---|
| `Usage_kWh` above the 99.5th percentile | Robust extreme-usage evidence |
| reactive magnitude above high percentile | Electrical stress evidence |
| effective power factor below 0.70 | Degraded power quality evidence |

Gold dataset hiện có **48 overload proxy rows**.

## Aggregate Label

`anomaly_any` là union của ba proxy labels. Phân bố hiện tại:

| Metric | Value |
|---|---:|
| Total rows | 35,040 |
| `anomaly_any=True` | 2,388 |
| Rate | 6.815% |

Tỷ lệ này phù hợp cho imbalanced-learning experiments, nhưng cần trình bày là
proxy-label rate, không phải verified fault rate.

## Confidence Scores

Confidence scores là deterministic và auditable:

- `anomaly_idling_score` kết hợp load status, off-hours context, usage level và
  power-factor evidence;
- `anomaly_leakage_score` tăng theo phần trăm vượt baseline;
- `anomaly_overload_score` kết hợp extreme usage, reactive stress và low power
  factor;
- `anomaly_max_score` lưu mức proxy evidence mạnh nhất.

`anomaly_explanation` chọn label family nổi bật nhất và tạo lý do ngắn gọn cho
người đọc.

## Validation

Khi thay đổi label logic, cần chạy:

```powershell
python -m pytest tests/test_anomaly_labels.py
python -m src.data_assertions
python -m src.leakage_audit
```

Validation gần nhất ghi nhận **52 pytest tests passed** và toàn bộ dataset
assertions PASS.

## Reporting Guidance

Cách diễn đạt nên dùng trong báo cáo:

> Các cột anomaly là physics-informed proxy labels. Chúng tạo benchmark có thể
> giải thích cho offline evaluation, nhưng không phải ground-truth SCADA fault
> records.

Không nên viết rằng project đã phát hiện lỗi thiết bị thật nếu chưa có
maintenance logs hoặc xác nhận chuyên gia.
