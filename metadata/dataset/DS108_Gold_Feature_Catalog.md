# DS108-Electrimight Gold Feature Catalog

Catalog này tóm tắt các nhóm đặc trưng trong `data/gold/steel_final.csv`. Bảng
định nghĩa cấp cột đầy đủ nằm trong `metadata/dataset/CODEBOOK.csv`. Heading và
tên nhóm giữ English để thống nhất với `Table of Contents`/schema, còn phần diễn
giải dùng tiếng Việt có dấu, giữ các thuật ngữ kỹ thuật như `time-domain`,
`DWT`, `physics-informed`, `proxy labels`, `forecasting` và `ablation`.

## Dataset Overview

| Item | Value |
|---|---|
| Dataset path | `data/gold/steel_final.csv` |
| Shape | 35,040 rows x 69 columns |
| Frequency | 15 minutes |
| Time range | 2018-01-01 00:00 to 2018-12-31 23:45 |
| Location | POSCO Gwangyang steel plant, South Korea |
| Primary target for forecasting | `Usage_kWh(t+1h)` |
| Proxy anomaly target | `anomaly_any` |

Thiết kế đặc trưng được tổ chức theo nguồn bằng chứng. Cách này giúp phần
`ablation` dễ diễn giải: project có thể so sánh raw context, temporal history,
weather context, wavelet features, physical features và GAN-augmented minority
samples.

## Feature Groups

| Group | Columns | Purpose |
|---|---:|---|
| Raw electrical and calendar variables | 11 | Giữ tín hiệu đo gốc và ngữ cảnh vận hành |
| Weather variables | 4 | Bổ sung ngữ cảnh ngoại sinh |
| Weather-derived variables | 7 | Tóm tắt động học thời tiết và interaction |
| Time-domain variables | 15 | Nắm bắt quán tính tải và chu kỳ thời gian |
| DWT wavelet variables | 16 | Nắm bắt dao động/transient miền tần số |
| Physics-informed variables | 7 | Biểu diễn quan hệ tam giác công suất |
| Proxy anomaly variables | 9 | Cung cấp weak labels và explanation có thể audit |
| **Total** | **69** |  |

## 1. Raw Electrical and Calendar Variables

Nhóm đầu tiên được load từ UCI steel dataset và làm sạch trong bước
Bronze-to-Silver. Nhóm này gồm timestamp, active usage, lagging/leading reactive
power, CO2, power factor, seconds from midnight, weekday/weekend status, weekday
name và load type.

Quyết định xử lý quan trọng:

- `date` được parse với `dayfirst=True`;
- power-factor columns được chuyển từ thang phần trăm về `[0, 1]`;
- zero reactive-power hợp lệ được giữ lại vì phản ánh trạng thái vận hành;
- source layer ở `data/bronze/` được xem là read-only.

## 2. Weather Variables

Weather data đến từ Open-Meteo tại tọa độ Gwangyang. Tần suất gốc là hourly,
pipeline resample về lưới 15 phút trước khi merge.

Variables:

- `temperature_2m`
- `precipitation`
- `relative_humidity_2m`
- `windspeed_10m`

Weather được xem là contextual enrichment. Nó không phải bằng chứng nguyên nhân
trực tiếp của lỗi thiết bị, nhưng giúp đặt biến động tải trong bối cảnh môi
trường.

## 3. Weather-Derived Variables

Nhóm weather-derived gồm:

- rolling 24-hour temperature;
- 24-hour temperature difference;
- heat index;
- extreme-hot và extreme-cold flags;
- humidity-temperature interaction;
- rolling 6-hour wind speed.

Nhóm này hỗ trợ proxy anomaly analysis. Kết quả ablation cho thấy weather context
cải thiện phân loại proxy anomaly trong full-track setting.

## 4. Time-Domain Variables

Time-domain features được tạo từ `Usage_kWh`:

- lag 15 phút, 30 phút, 1 giờ và 24 giờ;
- rolling mean, standard deviation và skewness trên cửa sổ 6 giờ, 12 giờ và
  24 giờ;
- sine/cosine encoding của seconds from midnight.

Các feature này là causal vì chỉ dùng thông tin hiện tại/quá khứ. Đây là nhóm
đóng góp mạnh nhất cho tác vụ 1-hour-ahead forecasting, nơi cấu hình RAW + TIME
đạt RMSE tốt nhất.

## 5. Frequency-Domain DWT Variables

Pipeline tính rolling DWT với cấu hình:

- wavelet: Daubechies-4 (`db4`);
- decomposition level: 3;
- rolling window: 64 observations, tương đương 16 giờ.

Với mỗi coefficient band (`cA`, `cD3`, `cD2`, `cD1`), pipeline trích xuất:

- mean;
- standard deviation;
- energy;
- maximum absolute value.

Nhóm DWT giúp nắm bắt transient và load oscillations khó thấy bằng rolling
statistics thông thường.

## 6. Physics-Informed Variables

Nhóm physics-informed tạo các đại lượng điện từ active power, reactive power và
power factor:

- apparent power;
- net reactive power;
- total reactive magnitude;
- apparent power from net reactive power;
- lagging và leading phase-angle features.

Các feature này làm cho electrical stress và power-factor degradation dễ audit
hơn so với chỉ dùng black-box input.

## 7. Proxy Anomaly Variables

Nhóm cuối cùng ghi lại proxy anomaly labels:

- `anomaly_idling`
- `anomaly_leakage`
- `anomaly_overload`
- `anomaly_any`
- confidence scores cho từng label type;
- `anomaly_max_score`;
- `anomaly_explanation`.

Các nhãn này dựa trên rule và có explanation. Chúng nên được dùng như benchmark
annotations, không phải confirmed operational ground truth.

Phân bố nhãn:

| Label | Count | Rate |
|---|---:|---:|
| Idling | 10 | 0.03% |
| Leakage/concept drift | 2,336 | 6.67% |
| Overload | 48 | 0.14% |
| Any proxy anomaly | 2,388 | 6.815% |

## Pipeline Order

1. `src/bronze/data_loader.py` load và clean dữ liệu steel gốc.
2. `src/bronze/weather_loader.py` load, resample và merge weather data.
3. `src/silver/time_features.py` tạo lag, rolling và cyclic features.
4. `src/silver/wavelet_features.py` tạo DWT wavelet features.
5. `src/silver/physical_features.py` tạo electrical-domain features.
6. `src/silver/anomaly_labels.py` tạo proxy anomaly labels.
7. `src/gold/pipeline.py` ghi gold dataset.

## Interpretation for Reporting

Feature catalog củng cố claim chính của project: Electrimight là một pipeline
tiền xử lý và xây dựng dataset theo hướng feature-centric. Temporal history là
nhóm mạnh nhất cho forecasting, còn weather context giúp proxy anomaly
classification trong full-track ablation. Vì vậy, báo cáo nên mô tả project như
một nghiên cứu dataset-building có thể audit, không phải production
fault-detection system.
