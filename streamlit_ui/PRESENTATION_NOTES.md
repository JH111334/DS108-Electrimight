# Ghi chú thuyết trình Streamlit

Dashboard được dùng như “demo spine” khi chuyển giữa pitch deck và UI. Không đọc hết UI; mỗi lần mở dashboard chỉ trả lời một câu hỏi.

## Flow đề xuất

1. Slides 2-4: nêu problem/gap, rồi mở đầu dashboard để chốt câu hỏi demo.
2. Tab `1. Flow`: đi từ raw meter logs → weather/time/wavelet/physics → proxy labels.
3. Tab `2. Evidence`: chứng minh Load_Type khác anomaly bằng MI thấp và tỷ lệ anomaly theo load type.
4. Tab `3. Validation`: tách forecasting, proxy classification và GAN để tránh overclaim.
5. Tab `4. Backup`: chỉ mở khi Q&A hỏi về limitation, figures hoặc explanation.

## Script ngắn

Trong nhà máy thật, sự cố nghiêm trọng thường được xử lý bằng relay, SCADA hoặc condition monitoring. Nhưng các dữ liệu đó thường không công khai và cần cảm biến/log nội bộ. Gap của project này là biến dữ liệu công tơ 15 phút thành dataset giàu ngữ cảnh, có feature audit được và có proxy labels minh bạch cho phân tích offline.

Load_Type không thay thế anomaly. Load_Type mô tả chế độ vận hành, còn anomaly_any mô tả tín hiệu rủi ro ứng viên trong chế độ đó. Mutual information giữa hai biến rất thấp, khoảng 0,0002.

Ablation được tách thành hai mục đích: forecasting Usage_kWh(t+1h) và proxy anomaly classification. Time features giúp forecasting rõ nhất, còn Time + Weather tốt nhất trong proxy task full track. Rule-free PR-AUC thấp là giới hạn cần nói trung thực vì chưa có nhãn SCADA/maintenance thật.

GAN chỉ là thử nghiệm augmentation cho lớp anomaly proxy. Mean/std khá gần nhưng correlation MAE còn sai lệch, nên không kể như bằng chứng phát hiện lỗi thật.
