# Project Insights - DS108-Electrimight

File này tóm tắt các bằng chứng mạnh nhất từ pipeline hiện tại. Heading giữ
English để đồng bộ với mục lục/ký hiệu kỹ thuật; phần diễn giải dùng tiếng Việt
có dấu và chỉ giữ English cho thuật ngữ chuyên ngành như `forecasting`,
`proxy anomaly`, `PR-AUC`, `GAN`, `rule-free track` và `ablation`.

## Gold Dataset

Gold dataset có **35.040 dòng và 69 cột**. Dataset bao phủ một năm dữ liệu tiêu
thụ điện công nghiệp ở tần suất 15 phút, kết hợp tín hiệu điện gốc, weather
context, engineered features và proxy anomaly labels.

Nhãn tổng hợp `anomaly_any` dương ở **2.388 dòng**, tương đương **6,815%** toàn
bộ dataset.

## Insight 1: Temporal Features Drive Forecasting Performance

Tác vụ `forecasting` dự đoán `Usage_kWh(t+1h)`. Trong ablation hiện tại, cấu
hình tốt nhất theo RMSE là **RAW + TIME**.

| Rank | Configuration | RMSE | MAE | R2 |
|---:|---|---:|---:|---:|
| 1 | RAW + TIME | 12.0087 | 6.1976 | 0.8535 |
| 2 | ALL ENGINEERED | 12.1154 | 6.3956 | 0.8509 |
| 3 | RAW + TIME + WEATHER + WAVELET | 12.1988 | 6.3676 | 0.8488 |
| 4 | RAW + TIME + WEATHER | 12.2585 | 6.4565 | 0.8473 |
| 5 | RAW + CONTEXT | 13.0119 | 6.7041 | 0.8280 |

Diễn giải: lịch sử tiêu thụ gần và chu kỳ thời gian giải thích phần lớn tín hiệu
forecasting ngắn hạn. Weather và wavelet features vẫn có giá trị phân tích,
nhưng chưa vượt temporal feature set cho target dự báo 1 giờ hiện tại.

## Insight 2: Weather Context Improves Proxy Anomaly Prediction

Với target `anomaly_any` trong full-track cross-validation, cấu hình mạnh nhất
theo PR-AUC là **RAW + TIME + WEATHER**.

| Rank | Configuration | PR-AUC | F1 | Precision | Recall |
|---:|---|---:|---:|---:|---:|
| 1 | RAW + TIME + WEATHER | 0.3642 | 0.4232 | 0.5291 | 0.7214 |
| 2 | RAW + TIME + WEATHER + WAVELET | 0.3481 | 0.3851 | 0.4882 | 0.6310 |
| 3 | ALL ENGINEERED | 0.3432 | 0.3532 | 0.4612 | 0.5405 |
| 4 | RAW + CONTEXT | 0.1976 | 0.0250 | 0.0129 | 0.7500 |
| 5 | RAW + TIME | 0.1500 | 0.0796 | 0.0476 | 0.6143 |

Diễn giải: weather variables nên được trình bày như contextual enrichment cho
proxy anomaly analysis. Không nên mô tả weather là bằng chứng nhân quả trực tiếp
của equipment faults.

## Insight 3: Rule-Free Results Define an Important Limitation

`Rule-free track` có PR-AUC thấp hơn nhiều. Cấu hình tốt nhất chỉ đạt
**0,0178 PR-AUC**, cho thấy proxy labels phụ thuộc mạnh vào domain rules và các
biến tạo nhãn.

| Rank | Configuration | PR-AUC | F1 | Precision | Recall |
|---:|---|---:|---:|---:|---:|
| 1 | ALL ENGINEERED | 0.0178 | 0.0006 | 0.0003 | 0.0571 |
| 2 | RAW + TIME + WEATHER + WAVELET | 0.0178 | 0.0006 | 0.0003 | 0.0571 |
| 3 | RAW + TIME + WEATHER | 0.0114 | 0.0006 | 0.0003 | 0.0571 |
| 4 | RAW + TIME | 0.0027 | 0.0022 | 0.0012 | 0.0571 |
| 5 | RAW + CONTEXT | 0.0012 | 0.0014 | 0.0007 | 0.3429 |

Diễn giải: project không nên overclaim khả năng phát hiện lỗi thật độc lập.
Framing học thuật mạnh hơn là Electrimight xây dựng một proxy-label benchmark có
thể audit và chỉ rõ nơi domain assumptions ảnh hưởng kết quả.

## Insight 4: GAN Augmentation Is a Baseline, Not the Main Claim

GAN experiment có giá trị như baseline augmentation cho minority proxy anomaly
class.

| Metric | Value |
|---|---:|
| Minority samples used for training | 2,388 |
| Synthetic samples generated | 500 |
| Mean error | 8.20% |
| Standard-deviation error | 3.81% |
| Correlation MAE | 0.116 |

Diễn giải: synthetic samples tái hiện mean/std tương đối tốt, nhưng correlation
error vẫn đáng kể. Vì vậy, GAN augmentation chỉ nên trình bày như exploratory
baseline, không phải thay thế dữ liệu công nghiệp thật.

## Final Reporting Position

Phát biểu bảo vệ tốt nhất:

> DS108-Electrimight chuyển raw industrial meter logs thành một analytical
> dataset có thể audit. Temporal features cho kết quả 1-hour forecasting tốt
> nhất, trong khi weather context cải thiện proxy anomaly prediction ở full-track
> ablation. Các anomaly labels vẫn là physics-informed proxy labels và cần
> maintenance hoặc SCADA evidence trước khi diễn giải như lỗi vận hành thật.
