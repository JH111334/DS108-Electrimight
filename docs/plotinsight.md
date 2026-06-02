# Plot Insight Guide cho Streamlit UI

Tài liệu này hướng dẫn cách đọc các bảng biểu trong `streamlit_ui/app.py` và cách suy ra insight khi demo Electrimight. Nguyên tắc chung: mọi số liệu trên UI phải đối chiếu được với artifact do code project tạo ra, không lấy từ nguồn ngoài hoặc nhập tay khi đã có file kết quả.

## Nguồn số liệu chính

| Nhóm số liệu | Artifact / code nguồn | Cách kiểm tra |
| --- | --- | --- |
| Kích thước dữ liệu raw, weather, gold | `data/bronze/Steel_industry_data.csv`, `data/bronze/weather_gwangyang_2018.csv`, `data/gold/steel_final.csv`, `metadata/pipeline/pipeline_stats.json` | Chạy `python -m src.run_all` rồi xem `metadata/pipeline/pipeline_stats.json`. |
| Số lượng proxy anomaly | `data/gold/steel_final.csv`, `metadata/pipeline/pipeline_stats.json` | Tổng các cột `anomaly_*` và `anomaly_any`. |
| Ablation forecasting và proxy classification | `metadata/pipeline/ablation_results.csv`, `metadata/pipeline/ablation_summary.json`, `src/project_insights.py` | Chạy `python -m src.project_insights`. |
| GAN augmentation | `metadata/pipeline/gan_stats.json` | Đối chiếu `minority_samples`, `n_synthetic`, `mean_error_pct`, `correlation_mae`. |
| Kiểm thử | `metadata/pipeline/verification_summary.json` | Tạo từ lần chạy `python -m pytest` hoặc `python -m src.run_all`. |
| Hình phụ lục | `references/report-guides/figures/*.png` | Sinh bằng `python -m src.gold.generate_figures`. |

## Tab 1: Tổng quan

Tab này trả lời câu hỏi: project đã biến dữ liệu công tơ thô thành dataset thành phẩm như thế nào?

- `Dữ liệu gốc = 35.040 x 11`: số dòng 15 phút trong một năm và 11 cột raw ban đầu.
- `Gold dataset = 35.040 x 64`: cùng số dòng, nhưng được làm giàu thành 64 cột gồm weather, time, wavelet, physics và proxy labels.
- `Weather = 8.760 -> 35.040`: weather hourly được resample về 15 phút bằng linear interpolation, không dùng back-fill tương lai.
- `Proxy anomaly = 2.388 mẫu, 6,815%`: số dòng có ít nhất một proxy risk label.
- `Kiểm thử = 50 passed`: log kiểm thử gần nhất trong `metadata/pipeline/verification_summary.json`.

Insight nên nói: đóng góp chính không chỉ là mô hình, mà là một pipeline dataset-building có kiểm tra chất lượng, tích hợp weather và tạo label proxy có thể giải thích.

Không nên nói: đây là hệ thống phát hiện lỗi thật hoặc thay thế SCADA.

## Tab 2: Dữ liệu

Tab này dùng để đọc cấu trúc hành vi điện và phân bố proxy anomaly.

Biểu đồ timeline theo ngày:

- Đường xanh là `Usage_kWh` trung bình theo ngày.
- Cột đỏ là số proxy anomaly trong ngày.
- Nếu cột đỏ tăng ở một số giai đoạn, nên diễn giải là tín hiệu sàng lọc rủi ro proxy, không phải fault đã được xác nhận.

Biểu đồ usage profile theo giờ:

- Trục x là giờ trong ngày từ `NSM / 3600`.
- Trục y là `Usage_kWh` trung bình.
- Màu biểu diễn `Load_Type`.
- Insight chính là pattern tải có chu kỳ theo thời gian, vì vậy time features có ý nghĩa mạnh trong forecasting.

Biểu đồ số lượng proxy labels:

- `Leakage` chiếm nhiều nhất với 2.336 mẫu.
- `Overload` có 48 mẫu.
- `Idling` có 10 mẫu.
- Do các label có thể chồng lấn, không cộng máy móc ba cột để thay cho `anomaly_any`.

Biểu đồ tỷ lệ anomaly theo `Load_Type`:

- UI tính trực tiếp từ `data/gold/steel_final.csv`.
- Mutual information giữa `Load_Type` và `anomaly_any` xấp xỉ 0,0002, nên `Load_Type` không phải biến định nghĩa nhãn.
- Insight nên nói: rủi ro proxy không chỉ đơn giản là do nhóm tải cao/thấp, mà còn phụ thuộc vào pattern thời gian, weather và biến vật lý.

## Tab 3: Kiểm chứng

Tab này dùng để chứng minh insight feature engineering bằng ablation.

Forecasting `Usage_kWh(t+1h)`:

- Metric chính là RMSE, càng thấp càng tốt.
- Best config là `RAW + TIME` với RMSE khoảng 12,0087.
- `RAW + CONTEXT` có RMSE khoảng 13,0119.
- Insight: với dự báo tiêu thụ ngắn hạn, time features là ưu tiên nên làm đầu tiên vì cải thiện nhanh và không yêu cầu hạ tầng cảm biến phức tạp.

Proxy anomaly classification:

- Metric chính là PR-AUC vì nhãn anomaly mất cân bằng.
- Best full-track config là `RAW + TIME + WEATHER` với PR-AUC khoảng 0,3642.
- Rule-free track có PR-AUC rất thấp, tốt nhất khoảng 0,0178.
- Insight: weather context giúp proxy risk prediction rõ hơn, nhưng kết quả rule-free cho thấy project vẫn cần ground-truth SCADA/maintenance labels nếu muốn tiến tới phát hiện lỗi thật.

GAN augmentation:

- `minority_samples = 2.388`, `n_synthetic = 500`.
- `mean_error_pct = 8,20%`, `std_error_pct = 3,81%`.
- `correlation_mae = 0,116`.
- Insight: GAN có thể bổ sung mẫu minority để thử nghiệm, nhưng chưa phải bằng chứng rằng dữ liệu sinh đã thay thế dữ liệu thật.

## Tab 4: Giới hạn

Tab này dùng để chặn các diễn giải quá mạnh.

- Proxy labels có rule và confidence, nhưng không phải nhãn lỗi đã xác nhận bởi SCADA hoặc bảo trì.
- Dashboard là offline benchmark, không phải hệ thống real-time.
- Weather hữu ích cho proxy task, nhưng không phải lúc nào cũng cải thiện forecasting 1 giờ.
- Rule-free PR-AUC thấp là bằng chứng trung thực rằng bài toán cần nhãn thật nếu muốn bỏ hoàn toàn rule-defining variables.

## Cách diễn giải đóng góp khi demo

Nên nói:

> Electrimight cung cấp một dataset công nghiệp giàu ngữ cảnh và các ablation thực nghiệm để hỗ trợ ưu tiên kỹ thuật. Với forecasting ngắn hạn, time features là bước nên làm trước; với proxy risk prediction, time + weather đem lại PR-AUC tốt nhất. Dataset vì vậy hỗ trợ sàng lọc rủi ro và ra quyết định kỹ thuật, nhưng chưa khẳng định phát hiện lỗi thật.

Không nên nói:

> Dataset giúp phát hiện rủi ro chính xác, tự động giảm chi phí vận hành hoặc thay thế hệ thống giám sát điện.

## Cách tạo link demo Streamlit

Hiện tại app chạy bằng localhost nên giảng viên chỉ xem được trên máy của bạn. Cách đơn giản nhất để có link demo là deploy bằng Streamlit Community Cloud:

1. Đẩy repo lên GitHub.
2. Đảm bảo repo có `streamlit_ui/app.py`, `streamlit_ui/requirements.txt`, `data/gold/steel_final.csv`, `metadata/dataset/*`, `metadata/pipeline/*` và các figure cần hiển thị.
3. Vào `https://share.streamlit.io`, chọn `Create app`.
4. Chọn repository, branch và entrypoint file là `streamlit_ui/app.py`.
5. Nếu muốn URL dễ nhớ, điền custom subdomain; nếu bỏ trống, Streamlit sẽ tự cấp URL dạng `*.streamlit.app`.
6. Sau khi app chạy, nộp link demo đó trong phần link sản phẩm.

Nếu repo đang private, cần cấp quyền GitHub cho Streamlit Community Cloud hoặc chuyển repo sang public trong thời gian chấm. Nếu dataset quá lớn hoặc repo bị giới hạn dung lượng, phương án thay thế là deploy trên Hugging Face Spaces hoặc Render, nhưng Streamlit Community Cloud là lựa chọn nhanh nhất cho bài nộp dạng dashboard.
