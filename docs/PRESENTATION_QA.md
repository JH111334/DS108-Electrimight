# Q&A thuyết trình cuối kỳ - DS108 Electrimight

Tài liệu này chuẩn bị cho phần Hỏi đáp và phản biện sau bài trình bày tối đa 15 phút. Câu trả lời nên đi thẳng vào trọng tâm, tránh overclaim: Electrimight là pipeline làm giàu dữ liệu và benchmark nhãn proxy cho phân tích offline, không phải hệ thống bảo vệ điện real-time.

## 1. Bài toán và phạm vi

### 1. Bài toán chính của đồ án là gì?

Đồ án giải quyết bài toán biến dữ liệu công tơ điện công nghiệp dạng thô thành một dataset giàu ngữ cảnh, có thể kiểm thử và có thể giải thích cho hai hướng phân tích: dự báo tiêu thụ điện ngắn hạn và nhận diện rủi ro bất thường dạng proxy. Điểm chính không phải chỉ chạy model, mà là xây dựng pipeline tiền xử lý, tích hợp thời tiết, tạo đặc trưng miền thời gian, wavelet, vật lý và nhãn bất thường có guideline.

### 2. Vì sao không chỉ dùng dataset UCI gốc?

Dataset UCI gốc có 35,040 mẫu trong một năm nhưng chỉ có 11 cột, thiếu ngữ cảnh thời tiết, thiếu đặc trưng vật lý/tần số và không có nhãn lỗi SCADA hay maintenance. Nếu dùng trực tiếp, mô hình chỉ thấy meter logs thô nên khó phân tích nguyên nhân và khó đánh giá rủi ro vận hành.

### 3. Gap nghiên cứu của Electrimight là gì?

Các hệ thống SCADA, relay và condition monitoring mạnh hơn cho an toàn real-time nhưng thường cần sensor chuyên dụng và log nội bộ. Electrimight lấp khoảng trống ở phía dữ liệu công khai ít cảm biến: làm giàu meter logs 15 phút bằng weather, time, wavelet, physical features và weak/proxy labels để phục vụ nghiên cứu offline.

### 4. Đồ án có thay thế hệ thống phát hiện sự cố thật trong nhà máy không?

Không. Đây không phải safety-grade real-time system. Pipeline chỉ dùng cho offline analytics, benchmark và sàng lọc rủi ro ứng viên khi không có nhãn lỗi thật từ SCADA hoặc maintenance logs.

### 5. Tại sao bài thuyết trình nhấn mạnh "auditable"?

Vì mỗi bước xử lý đều có thể kiểm tra lại: dữ liệu bronze/silver/gold tách rõ, codebook và datasheet mô tả schema, anomaly labels có rule và confidence score, pipeline có assertions, leakage audit và unit tests. "Auditable" nghĩa là người khác có thể truy vết vì sao một feature hoặc nhãn được tạo ra.

## 2. Dataset và tiền xử lý

### 6. Dataset cuối cùng có quy mô như thế nào?

Dataset gold có 35,040 dòng và 64 cột, tương ứng dữ liệu 15 phút từ 2018-01-01 00:00 đến 2018-12-31 23:45. Dữ liệu gốc có 11 cột, sau khi tích hợp thời tiết và feature engineering được mở rộng thành 64 cột.

### 7. Weather được tích hợp như thế nào?

Weather lấy từ Open-Meteo theo tọa độ Gwangyang, Hàn Quốc. Dữ liệu thời tiết ban đầu theo giờ được resample về 15 phút bằng nội suy tuyến tính trước khi merge với dữ liệu điện, để giữ cùng tần suất với meter logs.

### 8. Vì sao weather là biến ngoại sinh?

Weather không được sinh ra từ tiêu thụ điện của nhà máy, mà đến từ môi trường bên ngoài. Do đó nó là biến ngoại sinh giúp bổ sung ngữ cảnh vận hành như nhiệt độ, độ ẩm, gió, mưa và heat index.

### 9. Có missing sau merge không?

Theo slide và pipeline summary, sau merge không còn missing ở các cột cần thiết. Một số feature dạng lag hoặc rolling/DWT có NaN ở đầu chuỗi do chưa đủ lịch sử; đây là missing hợp lệ về thuật toán, không phải lỗi dữ liệu.

### 10. Làm sao đảm bảo không làm lệch timestamp?

Pipeline giữ row alignment theo timestamp 15 phút. Weather được resample xuống cùng tần suất trước khi merge, và dữ liệu điện giữ đúng thứ tự thời gian. Đây là điểm quan trọng vì nếu lệch timestamp, mô hình có thể học sai ngữ cảnh.

## 3. Feature engineering

### 11. Vì sao mở rộng từ 11 lên 64 cột?

Vì dữ liệu gốc thiếu ngữ cảnh. 64 cột gồm nhóm raw/electrical, weather, weather-derived, time-domain, wavelet, physical-domain và anomaly labels. Mục tiêu là biến meter logs thành dataset giàu thông tin hơn cho dự báo và phân tích bất thường.

### 12. Time features đóng vai trò gì?

Time features nắm bắt chu kỳ ngày/tuần và lịch sử tiêu thụ: lag 15 phút, 30 phút, 1 giờ, 24 giờ; rolling mean/std/skew; mã hóa sin/cos cho thời gian trong ngày. Trong ablation forecasting, time features là nhóm đóng góp rõ nhất, giảm RMSE từ khoảng 13.01 xuống 12.01.

### 13. Vì sao dùng sin/cos thay vì dùng trực tiếp NSM?

NSM có điểm gãy nhân tạo ở nửa đêm: 23:45 và 00:00 gần nhau về thời gian nhưng giá trị số lại cách xa. Sin/cos encoding biến thời gian trong ngày thành chu kỳ tròn, giúp mô hình hiểu đúng tính tuần hoàn.

### 14. Wavelet db4 dùng để làm gì?

Wavelet tách tín hiệu tiêu thụ điện thành phần xu hướng và các thành phần dao động ở nhiều mức tần số. Nhờ đó có thể mô tả spike hoặc dao động cục bộ mà rolling mean thông thường có thể bỏ sót. Trong đồ án, wavelet là feature phân tích, không được claim là luôn cải thiện mọi mô hình.

### 15. Physical features S và phi có ý nghĩa gì?

`Apparent_Power_S` mô tả công suất biểu kiến từ quan hệ giữa công suất tác dụng P và phản kháng Q. `Phase_Angle_Phi` chuyển power factor thành góc lệch pha, giúp diễn giải mức suy giảm hệ số công suất. Hai feature này đưa kiến thức điện học vào dataset thay vì chỉ dùng số đo thô.

## 4. Proxy labeling và anomaly

### 16. Proxy labels là gì?

Proxy labels là nhãn xấp xỉ dựa trên rule miền chuyên môn, không phải ground truth lỗi thật. Đồ án dùng ba nhãn: idling, leakage drift và overload, kèm confidence score và explanation để người đọc biết vì sao mẫu bị gán nhãn.

### 17. Vì sao cần proxy labels?

Dataset công khai không có SCADA alarms hoặc maintenance records. Nếu không có nhãn thật, proxy labels là cách minh bạch để tạo benchmark ban đầu cho nghiên cứu, miễn là báo cáo nói rõ giới hạn và không claim đó là lỗi đã xác nhận.

### 18. Ba loại anomaly được định nghĩa thế nào?

Idling là tải nhẹ nhưng tiêu thụ cao trong bối cảnh không phù hợp và power factor thấp. Leakage drift là rolling mean Usage_kWh vượt baseline 4 tuần đầu hơn 5% trong một khoảng kéo dài. Overload là điểm cực trị khi Usage_kWh vượt P99.5 và đi kèm phản kháng cao hoặc power factor thấp.

### 19. Tỷ lệ anomaly là bao nhiêu?

Tổng `anomaly_any` là 2,388 trên 35,040 mẫu, tương đương khoảng 6.815%. Trong đó idling có 10 mẫu, leakage có 2,336 mẫu và overload có 48 mẫu.

### 20. Load_Type có thay thế anomaly label được không?

Không. Load_Type mô tả chế độ vận hành bình thường: Light, Medium, Maximum. Anomaly label mô tả dấu hiệu rủi ro bên trong các chế độ đó. Mutual information giữa Load_Type và `anomaly_any` chỉ khoảng 0.0002, nghĩa là gần như không đủ để xem Load_Type là proxy của anomaly.

### 21. Vì sao Maximum_Load không đồng nghĩa bất thường?

Maximum_Load có thể là chế độ vận hành bình thường khi nhà máy hoạt động ở tải cao. Bất thường chỉ xuất hiện khi có dấu hiệu vượt ngưỡng hoặc suy giảm điện học bất hợp lý, ví dụ usage cực trị đi kèm reactive power cao hoặc power factor thấp.

### 22. Nhãn leakage có rủi ro bị nhầm với mùa vụ hoặc sản xuất tăng không?

Có, đây là giới hạn quan trọng. Leakage drift dựa trên baseline và rolling mean nên có thể bắt cả thay đổi vận hành dài hạn, không chỉ thất thoát năng lượng thật. Vì vậy báo cáo gọi là proxy leakage/drift và cần kiểm chứng bằng log sản xuất hoặc maintenance nếu triển khai thật.

## 5. Kiểm thử, leakage và phương pháp luận

### 23. Data leakage được kiểm soát thế nào?

Lag chỉ dùng `shift > 0`, rolling windows không dùng centered window, weather không dùng thông tin tương lai để lấp ngược, và anomaly labels không được dùng làm feature cho task forecasting. Đây là lý do slide nhấn mạnh strict causal window và leakage audit.

### 24. Vì sao zero data leakage quan trọng với chuỗi thời gian?

Vì nếu feature tại thời điểm hiện tại vô tình dùng thông tin tương lai, kết quả đánh giá sẽ cao giả tạo. Trong bài toán forecasting hoặc anomaly benchmark, điều này làm mô hình nhìn trước đáp án và mất giá trị thực nghiệm.

### 25. Vì sao phải tách forecasting và anomaly trong ablation?

Hai task đo hai năng lực khác nhau. Forecasting kiểm tra khả năng dự báo `Usage_kWh(t+1h)`, còn proxy anomaly kiểm tra khả năng dự đoán nhãn weak/proxy. Nếu trộn hai task, rất dễ kết luận sai rằng feature tốt cho anomaly cũng tốt cho forecasting hoặc ngược lại.

### 26. Kết quả ablation forecasting nói gì?

Target là `Usage_kWh(t+1h)`. Time features đạt kết quả tốt nhất trong summary, RMSE khoảng 12.01 so với raw khoảng 13.01. Điều này cho thấy lịch sử tiêu thụ và chu kỳ thời gian là tín hiệu mạnh nhất cho dự báo ngắn hạn.

### 27. Kết quả ablation proxy anomaly nói gì?

Trong full track, Time + Weather đạt PR-AUC tốt nhất khoảng 0.364. Tuy nhiên rule-free track cao nhất chỉ khoảng 0.0178, cho thấy nếu bỏ domain rules thì tín hiệu proxy anomaly rất yếu. Kết luận đúng là weather giúp contextual enrichment, nhưng chưa đủ để chứng minh phát hiện lỗi thật độc lập.

### 28. Vì sao dùng PR-AUC cho anomaly thay vì chỉ accuracy?

Vì anomaly bị mất cân bằng lớp, chỉ khoảng 6.8% mẫu là positive. Accuracy có thể cao dù mô hình đoán toàn negative. PR-AUC tập trung vào precision và recall của lớp hiếm nên phù hợp hơn.

## 6. GAN và dữ liệu tổng hợp

### 29. GAN được dùng để làm gì?

GAN được dùng để sinh thêm dữ liệu cho lớp anomaly proxy nhằm thử hướng cân bằng lớp. Nó không được dùng làm bằng chứng rằng lỗi thật đã xảy ra, và cũng không thay thế dữ liệu vận hành thật.

### 30. Kết quả GAN cho thấy gì?

GAN sinh 500 mẫu synthetic từ 2,388 minority rows. Mean error khoảng 8.20% và std error khoảng 3.81%, tức phân phối biên tương đối gần. Nhưng correlation MAE khoảng 0.116, nghĩa là cấu trúc tương quan giữa các feature vẫn còn sai lệch.

### 31. Hạn chế chính của GAN hiện tại là gì?

Đây là tabular/FC-GAN baseline, chưa phải mô hình chuỗi thời gian SOTA như TimeGAN hoặc TTS-GAN. Nó mô phỏng phân phối tổng quát nhưng chưa đảm bảo giữ đúng động học thời gian và tương quan vật lý phức tạp.

### 32. Nếu giảng viên hỏi "GAN có làm sai dữ liệu thật không?", trả lời thế nào?

Không, dữ liệu synthetic được lưu riêng và dùng cho kiểm nghiệm augmentation. Raw data trong `data/bronze/` không bị ghi đè, và gold dataset thật vẫn có thể tái tạo từ pipeline.

## 7. Giới hạn, đạo đức và triển khai

### 33. Hạn chế lớn nhất của đồ án là gì?

Hạn chế lớn nhất là không có ground truth từ SCADA hoặc maintenance labels. Vì vậy anomaly labels chỉ là proxy có rule minh bạch, không phải xác nhận lỗi vận hành thật.

### 34. Dataset có khái quát hóa sang nhà máy khác được không?

Cần thận trọng. Dataset chỉ từ một nhà máy thép ở Gwangyang trong năm 2018. Nhà máy khác có công nghệ, lịch sản xuất, thiết bị và profile tải khác nên các ngưỡng PF, overload, leakage có thể cần hiệu chỉnh lại.

### 35. Vì sao weather theo tọa độ là một rủi ro?

Open-Meteo cung cấp thời tiết theo tọa độ địa lý, không phải sensor on-site trong nhà máy. Điều kiện thực tế trong khu công nghiệp có thể khác, đặc biệt với nhiệt độ cục bộ, gió hoặc mưa tại vị trí thiết bị.

### 36. Đồ án có rủi ro đạo đức hay misuse không?

Có rủi ro nếu người dùng lấy proxy labels làm kết luận lỗi thật hoặc dùng trực tiếp cho điều khiển an toàn. Cách dùng đúng là nghiên cứu, phân tích offline, benchmark và hỗ trợ ra quyết định có chuyên gia kiểm chứng.

### 37. Nếu được phát triển tiếp, ưu tiên cải tiến gì?

Ưu tiên cao nhất là có ground truth từ SCADA/maintenance để validate nhãn. Sau đó có thể thử TimeGAN hoặc mô hình sinh chuỗi thời gian, thêm cross-correlation/Granger causality với weather, và đánh giá trên nhiều nhà máy để kiểm tra generalization.

## 8. Câu trả lời nhanh khi bị phản biện

### 38. "Có phải nhóm đang tự tạo nhãn rồi tự chứng minh mô hình tốt không?"

Không nên trình bày như vậy. Nhóm tạo proxy labels minh bạch để có benchmark khi thiếu ground truth, rồi dùng ablation để kiểm tra feature có dự đoán được nhãn proxy hay không. Kết quả rule-free rất thấp cũng được báo cáo để tránh overclaim.

### 39. "Weather không cải thiện forecasting, vậy thêm weather để làm gì?"

Weather không cải thiện rõ forecasting `Usage_kWh(t+1h)` trong thí nghiệm này, nhưng giúp proxy anomaly trong full track khi kết hợp với time/context. Vì vậy kết luận phải tách rõ: weather hữu ích như contextual enrichment, không phải feature luôn tốt cho mọi task.

### 40. "Tại sao không dùng deep learning forecasting thay vì feature engineering?"

Mục tiêu môn học là tiền xử lý và xây dựng dataset có thể kiểm chứng. Feature engineering giúp tạo dataset interpretable và auditable trước; deep learning có thể là downstream task sau. Nếu dùng deep learning ngay, dễ mất khả năng giải thích và vẫn không giải quyết vấn đề thiếu ngữ cảnh/nhãn.

### 41. "Tại sao không dùng Load_Type làm target chính?"

Load_Type là target có sẵn nhưng chỉ phản ánh chế độ tải bình thường. Đồ án muốn đi xa hơn: tạo dataset phục vụ dự báo điện và phân tích rủi ro ứng viên. Hơn nữa, Load_Type gần như độc lập với `anomaly_any`, nên không đủ để trả lời câu hỏi bất thường.

### 42. "Điểm mạnh kỹ thuật quan trọng nhất của pipeline là gì?"

Điểm mạnh là pipeline có kiểm soát leakage và có thể tái lập: row alignment, resample weather đúng tần suất, feature engineering theo nhiều miền, nhãn proxy có guideline, codebook/datasheet và unit tests. Đây là nền tảng engineering để dataset dùng được cho nghiên cứu.

### 43. "Một câu kết luận ngắn gọn về đóng góp là gì?"

Electrimight không claim phát hiện lỗi thật trong nhà máy; đóng góp là biến public meter logs thành một dataset điện công nghiệp giàu ngữ cảnh, có feature vật lý/tần số, nhãn proxy minh bạch và pipeline kiểm thử được cho nghiên cứu offline.
