# Datasheet for DS108-Electrimight

Tài liệu này mô tả dataset được tạo bởi pipeline DS108-Electrimight. Cấu trúc
giữ theo khung "Datasheets for Datasets" để người đọc dễ đối chiếu, nhưng phần
diễn giải được viết bằng tiếng Việt có dấu, giữ nguyên các thuật ngữ chuyên
ngành như `forecasting`, `proxy labels`, `feature engineering`, `DWT`, `GAN`,
`SCADA` và `data leakage` khi chúng rõ nghĩa hơn.

## 1. Motivation

DS108-Electrimight được xây dựng để phục vụ nghiên cứu và đồ án về tiền xử lý dữ
liệu tiêu thụ điện công nghiệp. Dataset hướng đến hai nhóm tác vụ chính:

- `short-term load forecasting` cho tiêu thụ điện công nghiệp;
- phân tích `proxy anomaly` dạng offline cho các tín hiệu nghi ngờ lãng phí năng
  lượng, leakage/concept drift và overload risk.

Project mở rộng UCI Steel Industry Energy Consumption dataset bằng dữ liệu thời
tiết ngoại sinh, đặc trưng `time-domain`, đặc trưng `DWT`, đặc trưng vật lý điện
và các nhãn yếu có thể giải thích. Vì vậy, dataset nên được hiểu là một
benchmark phương pháp luận cho tiền xử lý và xây dựng dữ liệu, không phải hệ
thống giám sát vận hành thương mại.

Dataset được chuẩn bị bởi nhóm sinh viên DS108, Trường Đại học Công nghệ Thông
tin, ĐHQG-HCM. Project không sử dụng nguồn tài trợ bên ngoài.

## 2. Dataset Composition

Mỗi dòng biểu diễn một mốc đo 15 phút tại nhà máy thép POSCO Gwangyang, Hàn
Quốc trong năm 2018. Dataset gold hiện tại có:

- **35.040 dòng**, tương ứng một năm đầy đủ ở tần suất 15 phút;
- **69 cột**, gồm tín hiệu gốc, ngữ cảnh thời tiết, đặc trưng kỹ thuật và
  `proxy anomaly labels`;
- khoảng thời gian liên tục từ **2018-01-01 00:00** đến
  **2018-12-31 23:45**.

Các nhóm biến chính:

| Group | Count | Description |
|---|---:|---|
| Raw electrical and calendar variables | 11 | Biến điện và ngữ cảnh lịch từ UCI dataset |
| Weather variables | 4 | Dữ liệu Open-Meteo cho khu vực Gwangyang |
| Weather-derived variables | 7 | Đặc trưng phái sinh từ thời tiết |
| Time-domain variables | 15 | Lag, rolling statistics và cyclic encoding |
| DWT wavelet variables | 16 | Đặc trưng miền tần số từ rolling Daubechies-4 |
| Physics-informed variables | 7 | Công suất biểu kiến, reactive power và phase angle |
| Proxy anomaly variables | 9 | Nhãn, confidence score và explanation text |

Mô tả cấp cột nằm trong `metadata/dataset/CODEBOOK.csv` và
`metadata/dataset/DS108_Gold_Feature_Catalog.md`.

## 3. Source Data

### Steel Industry Energy Consumption

Nguồn dữ liệu điện đến từ UCI Machine Learning Repository:

- Dataset: Steel Industry Energy Consumption
- URL: https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption
- Original authors: Sathishkumar V. E., Jangwoo Park và Yongyun Cho
- Location: POSCO Gwangyang steel plant, South Korea
- Time range: 01/01/2018 đến 31/12/2018
- Frequency: 15 phút

File gốc dùng định dạng ngày `DD/MM/YYYY`, vì vậy pipeline đọc ngày với
`dayfirst=True`.

### Weather Data

Dữ liệu thời tiết được thu từ Open-Meteo Historical Weather API tại tọa độ
Gwangyang:

- Latitude: 34.975 N
- Longitude: 127.589 E
- Frequency trước khi merge: hourly
- Variables: temperature, precipitation, relative humidity và wind speed

Weather được xem là biến ngoại sinh. Pipeline resample dữ liệu hourly về 15 phút
trước khi merge với chuỗi tiêu thụ điện.

## 4. Preprocessing and Feature Engineering

Pipeline dùng cấu trúc Bronze-Silver-Gold:

| Layer | Path | Description |
|---|---|---|
| Bronze | `data/bronze/` | CSV gốc và dữ liệu thời tiết đã tải |
| Silver | `data/silver/steel_clean.csv` | Dữ liệu điện đã làm sạch và chuẩn hóa power factor |
| Gold | `data/gold/steel_final.csv` | Dataset cuối sau weather merge, feature engineering và labeling |

Các bước xử lý chính:

- kiểm tra timestamp, duplicate và tính liên tục 15 phút;
- chuẩn hóa power factor từ thang phần trăm về `[0, 1]`;
- giữ các giá trị reactive power bằng 0 hợp lệ như tín hiệu vận hành;
- resample weather hourly về 15 phút bằng linear interpolation;
- tạo lag features và rolling statistics theo hướng causal;
- mã hóa chu kỳ ngày bằng sine/cosine;
- tính đặc trưng `DWT` trên rolling window 64 mẫu;
- tạo đặc trưng vật lý như apparent power, net/total reactive power và phase
  angle;
- tạo `proxy anomaly labels` với confidence score và explanation.

Các giá trị thiếu ở đầu chuỗi của lag/window features là hệ quả thuật toán hợp
lý, không phải lỗi dữ liệu. Chúng được giữ minh bạch để tránh data leakage.

## 5. Labels and Intended Interpretation

Dataset có ba nhóm `proxy anomaly labels`:

| Label | Interpretation | Evidence basis |
|---|---|---|
| `anomaly_idling` | Tiêu thụ trong bối cảnh low-load/off-hours và power factor thấp | Operating schedule, usage level, power factor |
| `anomaly_leakage` | Mức tiêu thụ tăng kéo dài so với baseline | Rolling mean so với baseline đầu kỳ |
| `anomaly_overload` | Usage cực trị kèm reactive-power hoặc power-factor stress | Robust percentile và electrical stress indicators |

Các nhãn này là **physics-informed weak/proxy labels**. Chúng phù hợp để
benchmark offline và phân tích có giải thích, nhưng không phải `ground truth`
lỗi vận hành. Muốn triển khai thực tế cần đối chiếu thêm maintenance logs,
SCADA events hoặc đánh giá của chuyên gia điện.

Phân bố nhãn hiện tại:

| Metric | Value |
|---|---:|
| Idling proxy rows | 10 |
| Leakage/concept-drift proxy rows | 2,336 |
| Overload proxy rows | 48 |
| Any proxy anomaly rows | 2,388 |
| Any proxy anomaly rate | 6.815% |

## 6. Quality and Validation

Validation summary hiện báo PASS cho các nhóm kiểm tra:

- temporal ordering;
- duplicate timestamps;
- NSM consistency;
- null checks;
- non-negative usage;
- power-factor range;
- physical consistency;
- anomaly-rate threshold;
- feature-count expectation.

Kết quả test hiện tại là **52 passed**. Leakage audit xác nhận lag/rolling
features chỉ dùng thông tin quá khứ, weather merge không dùng future back-fill,
và proxy labels được giữ như target/annotation thay vì feature huấn luyện thông
thường.

## 7. Uses

Các mục đích sử dụng phù hợp:

- `short-term load forecasting`;
- phân tích quyết định tiền xử lý và `feature engineering`;
- ablation study theo nhóm đặc trưng;
- benchmark `proxy anomaly` dạng offline;
- so sánh tác động của raw, temporal, weather, wavelet, physical và synthetic
  augmentation feature groups.

Các mục đích cần thận trọng:

- quyết định an toàn vận hành;
- quyết định pháp lý/hợp đồng liên quan đến tiêu thụ điện;
- triển khai trực tiếp vào SCADA real-time;
- tổng quát hóa sang nhà máy khác nếu chưa schema mapping và hiệu chỉnh
  thresholds.

## 8. Distribution

Ở snapshot hiện tại, dataset vẫn có thể đi kèm repository vì file
`steel_final.csv` chưa vượt hard limit của GitHub. Nếu artifact tăng kích thước,
kế hoạch phân phối chuyên nghiệp là:

- GitHub lưu code, metadata, notebooks và artifact nhỏ;
- Kaggle Datasets cung cấp link tải public cho cộng đồng data science;
- Zenodo dùng cho snapshot học thuật cần DOI;
- DVC hoặc Git LFS chỉ dùng khi cần versioning artifact lớn gắn với Git workflow.

Các bước publish cụ thể nên ghi trong release notes hoặc deployment notes khi
nộp bài.

## 9. Maintenance

Nhóm DS108 chịu trách nhiệm duy trì dataset cho mục đích học thuật. Khi cập nhật
phiên bản cần:

- ghi changelog hoặc release note rõ ràng;
- cập nhật `CODEBOOK.csv` nếu schema thay đổi;
- cập nhật feature catalog nếu công thức feature thay đổi;
- cập nhật labeling methodology nếu threshold hoặc rule thay đổi;
- regenerate pipeline summaries và validation outputs.

Các phiên bản cũ nên được truy vết bằng Git tags, Kaggle versions hoặc release
archives.
