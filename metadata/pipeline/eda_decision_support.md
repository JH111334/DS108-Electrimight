# EDA-driven Design Decisions

File này nối trực tiếp quan sát EDA với các quyết định tiền xử lý, feature engineering và GAN trong project.

## Bảng quyết định

| Quyết định | Bằng chứng EDA | Tác dụng |
| --- | --- | --- |
| Resample weather hourly xuống 15 phút trước khi merge. | Dữ liệu điện có bước thời gian 15 phút với 35,040 dòng; weather có bước thời gian 60 phút với 8,760 dòng. | Đưa hai nguồn về cùng timestamp grid, giữ nguyên 35.040 dòng điện và tránh lệch hàng khi merge. |
| Chọn linear interpolation cho weather. | Các biến weather thay đổi tương đối trơn theo giờ; ví dụ median absolute hourly change temperature=0.50, humidity=2.00. | Tạo giá trị 15 phút dễ kiểm toán, không dùng back-fill tương lai và không cần spline/MICE cho dữ liệu ngoại sinh đã đầy đủ. |
| Tạo lag, rolling và sin/cos time features. | Usage_kWh trung bình theo giờ biến thiên rõ; khoảng dao động hourly mean là 55.40 kWh. | Ablation xác nhận RAW + TIME có RMSE thấp nhất (12.0087) cho forecasting 1 giờ. |
| Giữ zero reactive power như tín hiệu vật lý, không coi là missing thường. | Leading reactive zero chiếm 67.38% và lagging PF < 0.50 chiếm 10.01%. | Các giá trị này hỗ trợ diễn giải tải cảm/kháng và tạo physical features/proxy rules có thể kiểm toán. |
| Thử GAN augmentation cho lớp anomaly proxy. | anomaly_any có 2,388 mẫu, chiếm 6.815% toàn bộ dataset. | GAN được dùng như baseline cân bằng lớp minority, không dùng làm bằng chứng lỗi thật. |
| Giới hạn claim của GAN ở mức baseline augmentation. | GAN mean error=8.20%, std error=3.81%, correlation MAE=0.116. | Mean/std khá gần nhưng correlation còn lệch, nên không overclaim synthetic data thay thế dữ liệu thật. |
| Bổ sung weather cho proxy risk prediction. | Weather là ngữ cảnh ngoại sinh sau resampling; ablation full track cho thấy A2_time_weather đạt PR-AUC 0.3642. | Weather nên được trình bày là contextual enrichment cho proxy labels, không phải nguyên nhân chắc chắn của lỗi. |

## Metrics nguồn

- `raw_rows`: 35040
- `raw_cols`: 11
- `raw_step_minutes`: 15.0
- `weather_rows`: 8760
- `weather_step_minutes`: 60.0
- `gold_rows`: 35040
- `gold_cols`: 69
- `pipeline_final_shape`: [35040, 69]
- `anomaly_any_count`: 2388
- `anomaly_any_pct`: 6.815068493150685
- `temperature_2m_median_abs_hourly_change`: 0.5
- `temperature_2m_p95_abs_hourly_change`: 2.3
- `relative_humidity_2m_median_abs_hourly_change`: 2.0
- `relative_humidity_2m_p95_abs_hourly_change`: 10.0
- `precipitation_median_abs_hourly_change`: 0.0
- `precipitation_p95_abs_hourly_change`: 0.6000000000000001
- `windspeed_10m_median_abs_hourly_change`: 1.1000000000000005
- `windspeed_10m_p95_abs_hourly_change`: 4.199999999999999
- `hourly_usage_mean_min`: 4.152547945205479
- `hourly_usage_mean_max`: 59.55145205479452
- `hourly_usage_mean_range`: 55.39890410958904
- `leading_reactive_zero_pct`: 67.38013698630137
- `lagging_reactive_zero_pct`: 20.530821917808222
- `lagging_pf_below_050_pct`: 10.005707762557076
- `gan_mean_error_pct`: 8.202837913153235
- `gan_std_error_pct`: 3.809620190229751
- `gan_correlation_mae`: 0.1157808179946601
