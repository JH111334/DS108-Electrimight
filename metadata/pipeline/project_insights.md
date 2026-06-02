# Project Insights - DS108 Electrimight

File này tóm tắt các số liệu quan trọng nhất để giảng viên có thể chạy một lần và xem ngay giá trị của project.

## Dataset thành phẩm

- Gold dataset: **35,040 dòng x 69 cột**.
- Proxy anomaly labels: **2,388 dòng**, tương đương **6.815%**.

## Insight 1 - Forecasting

- Target: `Usage_kWh(t+1h)`.
- Config tốt nhất theo RMSE: **RAW + TIME**.
- RMSE tốt nhất: **12.0087**.
- RMSE raw/context: **13.0119**.
- Mức giảm RMSE: **1.0032**.

Kết luận: **RAW + TIME cho RMSE thấp nhất** trong ablation forecasting. Điều này hợp lý vì tiêu thụ điện công nghiệp phụ thuộc mạnh vào lịch sử gần và chu kỳ thời gian.

### Bảng chứng minh RMSE

| Rank | Config | RMSE | MAE | R2 |
|---:|---|---:|---:|---:|
| 1 | RAW + TIME | 12.0087 | 6.1976 | 0.8535 |
| 2 | ALL ENGINEERED | 12.1154 | 6.3956 | 0.8509 |
| 3 | RAW + TIME + WEATHER + WAVELET | 12.1988 | 6.3676 | 0.8488 |
| 4 | RAW + TIME + WEATHER | 12.2585 | 6.4565 | 0.8473 |
| 5 | RAW + CONTEXT | 13.0119 | 6.7041 | 0.8280 |

## Insight 2 - Proxy anomaly labels

- Target: `anomaly_any`.
- Config full-track tốt nhất theo cross-validation PR-AUC: **RAW + TIME + WEATHER**.
- PR-AUC tốt nhất: **0.3642**.
- PR-AUC tốt nhất ở rule-free track: **0.0178**.

Kết luận: **RAW + TIME + WEATHER cho PR-AUC cao nhất với proxy labels**. Weather có giá trị như contextual enrichment, nhưng rule-free PR-AUC thấp cho thấy nhãn proxy vẫn cần domain rules và không nên overclaim là phát hiện lỗi thật độc lập.

### Bảng chứng minh PR-AUC full-track

| Rank | Config | PR-AUC | F1 | Precision | Recall |
|---:|---|---:|---:|---:|---:|
| 1 | RAW + TIME + WEATHER | 0.3642 | 0.4232 | 0.5291 | 0.7214 |
| 2 | RAW + TIME + WEATHER + WAVELET | 0.3481 | 0.3851 | 0.4882 | 0.6310 |
| 3 | ALL ENGINEERED | 0.3432 | 0.3532 | 0.4612 | 0.5405 |
| 4 | RAW + CONTEXT | 0.1976 | 0.0250 | 0.0129 | 0.7500 |
| 5 | RAW + TIME | 0.1500 | 0.0796 | 0.0476 | 0.6143 |

### Bảng rule-free để làm rõ giới hạn

| Rank | Config | PR-AUC | F1 | Precision | Recall |
|---:|---|---:|---:|---:|---:|
| 1 | ALL ENGINEERED | 0.0178 | 0.0006 | 0.0003 | 0.0571 |
| 2 | RAW + TIME + WEATHER + WAVELET | 0.0178 | 0.0006 | 0.0003 | 0.0571 |
| 3 | RAW + TIME + WEATHER | 0.0114 | 0.0006 | 0.0003 | 0.0571 |
| 4 | RAW + TIME | 0.0027 | 0.0022 | 0.0012 | 0.0571 |
| 5 | RAW + CONTEXT | 0.0012 | 0.0014 | 0.0007 | 0.3429 |

## Insight 3 - GAN validation

- Mean error: **8.20%**.
- Std error: **3.81%**.
- Correlation MAE: **0.116**.

Kết luận: GAN hiện tại phù hợp để trình bày như baseline augmentation cho lớp anomaly proxy. Mean/std khá gần, nhưng correlation còn lệch nên chưa nên claim là mô hình sinh chuỗi thời gian tốt nhất.

## Câu chốt để trình bày

Electrimight tạo ra một dataset công nghiệp có thể kiểm thử từ meter logs thô: **RAW + TIME giúp dự báo điện tốt nhất**, còn **RAW + TIME + WEATHER giúp dự đoán proxy anomaly tốt nhất**. Kết quả này cũng chỉ ra giới hạn quan trọng: proxy labels hữu ích cho benchmark offline, nhưng cần SCADA/maintenance labels để xác nhận lỗi thật.
