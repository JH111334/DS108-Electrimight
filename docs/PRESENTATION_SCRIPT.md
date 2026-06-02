# Script thuyết trình cuối kỳ - DS108 Electrimight

Nguyên tắc khi nói:

- Không đọc hết chữ trên slide; mỗi slide chỉ giữ một thông điệp chính.
- Trọng tâm là resampling, merge dữ liệu, feature engineering, proxy labeling và ablation.
- Luôn nói đúng phạm vi: pipeline dữ liệu và benchmark proxy cho phân tích offline, không phải hệ thống phát hiện lỗi thật hoặc điều khiển an toàn real-time.

## Phân bổ thời gian

| Slide | Nội dung | Thời gian |
|---|---|---:|
| 1 | Mở đầu | 0:30 |
| 2 | Dữ liệu gốc thiếu ngữ cảnh | 0:55 |
| 3 | Gap analysis | 0:55 |
| 4 | Động cơ của đồ án | 0:55 |
| 5 | Dataset và resampling weather | 1:35 |
| 6 | Chất lượng dữ liệu và leakage | 1:00 |
| 7 | Feature engineering đa miền | 2:35 |
| 8 | Proxy labeling | 1:05 |
| 9 | Load_Type vs anomaly | 0:45 |
| 10 | Ablation forecasting | 0:55 |
| 11 | Ablation proxy anomaly | 1:00 |
| 12 | GAN validation | 0:45 |
| 13 | Hạn chế | 0:55 |
| 14 | Đóng góp | 0:55 |
| 15 | Kết thúc | 0:20 |
| Tổng |  | khoảng 14:15 |

## Slide 1 - Mở đầu

Thời gian: 30 giây.

Kính chào thầy/cô và các bạn. Nhóm em xin trình bày đồ án DS108 Electrimight, với mục tiêu xây dựng một dataset điện công nghiệp giàu đặc trưng từ dữ liệu công tơ thô.

Thông điệp chính của đồ án không phải là chỉ huấn luyện một mô hình dự báo. Nhóm tập trung vào lớp dữ liệu trước mô hình: tích hợp weather, tạo đặc trưng thời gian, wavelet, vật lý điện, gán nhãn proxy và kiểm tra leakage để tạo một benchmark có thể tái lập cho dự báo tiêu thụ điện và phân tích rủi ro tải điện dạng proxy.

Chuyển slide: Nhóm bắt đầu từ bài toán của dữ liệu gốc.

## Slide 2 - Dữ liệu gốc thiếu ngữ cảnh

Thời gian: 55 giây.

Dữ liệu gốc là dữ liệu tiêu thụ điện của một nhà máy thép, tần suất 15 phút trong một năm. Điểm mạnh là chuỗi thời gian đầy đủ với 35.040 mẫu, nhưng điểm yếu là dữ liệu chỉ có 11 cột công tơ thô.

Nếu đưa trực tiếp dữ liệu này vào model, ta thiếu ba lớp thông tin quan trọng. Thứ nhất là ngữ cảnh ngoại sinh như thời tiết. Thứ hai là pattern thời gian như chu kỳ ngày, tuần và lịch sử tải gần. Thứ ba là các tín hiệu có ý nghĩa vật lý như công suất biểu kiến, góc lệch pha hoặc power factor thấp.

Vì vậy câu hỏi chính là: làm sao biến meter logs thô thành một dataset có đủ ngữ cảnh để vừa dự báo tiêu thụ điện, vừa phân tích rủi ro tải điện dạng proxy?

Chuyển slide: Từ câu hỏi này, nhóm xác định gap của đồ án.

## Slide 3 - Gap analysis

Thời gian: 55 giây.

Trong nhà máy thật, SCADA, relay bảo vệ hoặc condition monitoring là các hệ thống mạnh để giám sát an toàn. Nhưng dữ liệu đó thường là dữ liệu nội bộ, phụ thuộc cảm biến chuyên dụng và khó công khai.

Ngược lại, public meter dataset thì dễ tái lập hơn, nhưng thường chỉ phục vụ load forecasting thuần. Nó thiếu weather context, thiếu đặc trưng vật lý và thiếu nhãn lỗi thật.

Gap của Electrimight nằm ở giữa hai hướng này. Nhóm không thay thế SCADA. Nhóm xây dựng một pipeline data-centric để làm giàu dữ liệu công tơ công khai thành một dataset có feature và proxy labels minh bạch, phù hợp cho phân tích offline và kiểm chứng phương pháp.

Chuyển slide: Vậy vì sao cần nhãn anomaly riêng, thay vì chỉ dùng `Load_Type`?

## Slide 4 - Động cơ của đồ án

Thời gian: 55 giây.

Dataset gốc có biến `Load_Type`, gồm Light, Medium và Maximum Load. Nhưng `Load_Type` chỉ mô tả chế độ tải bình thường của nhà máy, không trả lời câu hỏi trong chế độ đó có dấu hiệu rủi ro hay không.

Nhóm kiểm tra mutual information giữa `Load_Type` và `anomaly_any`, kết quả chỉ khoảng 0,0002. Nghĩa là `Load_Type` gần như không giải thích được nhãn anomaly proxy.

Vì vậy nhóm tách rõ hai bài toán: forecasting là dự báo `Usage_kWh`, còn proxy anomaly là dự đoán các dấu hiệu rủi ro ứng viên như idling, leakage drift và overload. Cách tách này giúp tránh nhầm lẫn giữa tải cao và bất thường.

Chuyển slide: Tiếp theo là phần quan trọng đầu tiên của pipeline: đồng bộ dữ liệu điện và weather.

## Slide 5 - Dataset và resampling weather

Thời gian: 1 phút 35 giây.

Pipeline dùng hai nguồn dữ liệu. Nguồn thứ nhất là UCI Steel Industry Electricity, gồm 35.040 dòng ở tần suất 15 phút. Nguồn thứ hai là Open-Meteo Weather, gồm 8.760 dòng theo giờ.

Điểm kỹ thuật là hai nguồn không cùng tần suất. Nếu merge trực tiếp, mỗi giờ chỉ có một điểm weather, còn dữ liệu điện có bốn điểm 15 phút. Vì vậy nhóm resample weather từ hourly về 15 phút trước khi merge.

Cách hoạt động là: tạo một time index 15 phút cho weather, sau đó dùng nội suy tuyến tính giữa hai mốc giờ liên tiếp. Ví dụ nếu nhiệt độ lúc 10:00 và 11:00 đã biết, thì các giá trị 10:15, 10:30 và 10:45 được tính theo đường thẳng nối hai mốc đó. Công thức là:

`w(t) = w(t1) + (w(t2) - w(t1)) / (t2 - t1) * (t - t1)`.

Nhóm chọn linear interpolation vì weather biến đổi tương đối trơn ở thang 15 phút, dễ kiểm toán và không làm thay đổi row count của dữ liệu điện. Nhóm không dùng back-fill. Nếu triển khai real-time, weather nên thay bằng forecast hoặc sensor on-site; trong đồ án này weather là ngữ cảnh ngoại sinh cho phân tích offline.

Sau resampling, weather có 35.040 dòng, cùng timestamp với electricity. Pipeline merge bằng timestamp và giữ nguyên số dòng của dữ liệu điện. Sau toàn bộ feature engineering và labeling, gold dataset đạt 35.040 dòng và 64 cột.

Chuyển slide: Khi đã merge nhiều nguồn dữ liệu, bước tiếp theo là kiểm tra chất lượng và leakage.

## Slide 6 - Chất lượng dữ liệu và chống leakage

Thời gian: 1 phút.

Slide này tóm tắt các kiểm soát để dataset không chỉ tạo được, mà còn kiểm tra lại được.

Thứ nhất là kiểm tra shape và timestamp: pipeline giữ đủ 35.040 dòng, timestamp tăng dần, không trùng lặp và không làm lệch hàng khi merge weather.

Thứ hai là kiểm tra ràng buộc vật lý: `Usage_kWh` không âm, power factor nằm trong `[0,1]`, và các biến vật lý như công suất biểu kiến không tạo ra giá trị bất khả thi.

Thứ ba là chống leakage. Lag features chỉ dùng quá khứ bằng `shift`; rolling windows dùng `center=False`; weather không back-fill; và labeling được tách khỏi feature evaluation để tránh mô hình chỉ học lại rule. Pipeline hiện có kiểm thử tự động, với log gần nhất là 50 tests passed.

Chuyển slide: Sau khi dữ liệu đã đồng bộ và kiểm tra được, nhóm xây dựng các nhóm feature chính.

## Slide 7 - Feature engineering đa miền

Thời gian: 2 phút 35 giây.

Đây là phần kỹ thuật trọng tâm của đồ án. Từ 11 cột raw, nhóm mở rộng thành 64 cột bằng bốn nhóm feature: time, weather, wavelet và physical.

Nhóm thứ nhất là time features. Ý nghĩa của nhóm này là nắm bắt tính tự tương quan và chu kỳ vận hành. Trong tải điện công nghiệp, tiêu thụ hiện tại thường phụ thuộc mạnh vào 15 phút trước, 1 giờ trước và cùng thời điểm hôm trước.

Cách tạo time features gồm ba phần. Một là lag features: `lag_1`, `lag_2`, `lag_4`, `lag_96`, tương ứng 15 phút, 30 phút, 1 giờ và 24 giờ trước. Hai là rolling statistics trên các cửa sổ 24, 48 và 96 mẫu để lấy trung bình, độ lệch chuẩn và độ skewness gần đây. Ba là mã hóa chu kỳ bằng `NSM_sin` và `NSM_cos`, để model hiểu 23:45 và 00:00 là hai thời điểm gần nhau.

Tác dụng của time features được xác nhận bằng ablation: với forecasting 1 giờ, cấu hình `RAW + TIME` đạt RMSE thấp nhất, khoảng 12,0087. Vì vậy nếu doanh nghiệp cần cải thiện nhanh bài toán dự báo tiêu thụ, time features là nhóm nên ưu tiên đầu tiên.

Nhóm thứ hai là weather features. Ý nghĩa là bổ sung ngữ cảnh ngoại sinh: nhiệt độ, độ ẩm, mưa và gió có thể ảnh hưởng đến tải phụ trợ, làm mát hoặc điều kiện vận hành. Cách tạo là resample weather hourly về 15 phút, merge theo timestamp, rồi tạo thêm biến phát sinh như heat index, rolling temperature và tương tác nhiệt-ẩm. Tác dụng của weather không mạnh nhất cho forecasting ngắn hạn, nhưng lại giúp proxy risk prediction: cấu hình `RAW + TIME + WEATHER` đạt PR-AUC cao nhất trong full track.

Nhóm thứ ba là wavelet features. Ý nghĩa của wavelet là nhìn tín hiệu ở miền tần số-thời gian, không chỉ nhìn giá trị thô. Cách hoạt động là dùng DWT với wavelet db4, level 3, trên cửa sổ 64 mẫu. DWT tách tín hiệu thành thành phần xấp xỉ `cA`, đại diện cho xu hướng, và các thành phần chi tiết `cD`, đại diện cho dao động hoặc spike cục bộ. Từ mỗi nhóm hệ số, pipeline lấy thống kê như mean, std, energy và max_abs.

Nhóm thứ tư là physical features. Ý nghĩa là đưa kiến thức điện học vào dataset. Thay vì chỉ nhìn `Usage_kWh`, pipeline tính công suất phản kháng ròng, công suất biểu kiến `S = sqrt(P^2 + Q_net^2)`, và góc lệch pha `phi = arccos(PF)`. Cách hoạt động là dùng các cột điện gốc như active power, lagging/leading reactive power và power factor đã chuẩn hóa. Tác dụng là giúp giải thích các trạng thái như power factor thấp, tải cảm kháng hoặc nghi ngờ quá tải cục bộ.

Tóm lại, bốn nhóm feature không có vai trò giống nhau. Time features mạnh nhất cho forecasting; weather giúp proxy risk trong full track; wavelet mô tả biến động đa tỉ lệ; physical features giúp giải thích và tạo rule proxy có cơ sở miền điện.

Chuyển slide: Từ các feature này, nhóm xây dựng nhãn proxy.

## Slide 8 - Proxy labeling

Thời gian: 1 phút 5 giây.

Nhóm tạo ba nhãn weak/proxy: suspected idling, suspected leakage drift và suspected overload. Cần nói rõ: đây là nhãn ứng viên dựa trên rule minh bạch, không phải ground-truth lỗi thật từ SCADA hoặc maintenance logs.

Idling mô tả tình huống tải nhẹ hoặc ngoài giờ nhưng có dấu hiệu tiêu thụ không hợp lý, đi kèm power factor thấp. Leakage drift dựa trên rolling mean của `Usage_kWh` vượt baseline 4 tuần đầu hơn 5% trong một khoảng kéo dài. Overload dựa trên các điểm cực trị như `Usage_kWh` vượt P99.5, kết hợp với reactive power cao hoặc power factor thấp.

Mỗi nhãn có cờ boolean, confidence score và `anomaly_explanation`. Vì vậy người đọc có thể truy vết vì sao một dòng được xem là rủi ro ứng viên. Tổng `anomaly_any` là 2.388 trên 35.040 mẫu, tương đương 6,815%.

Chuyển slide: Một kiểm tra quan trọng là nhãn proxy này có chỉ lặp lại `Load_Type` hay không.

## Slide 9 - Load_Type vs anomaly

Thời gian: 45 giây.

Kết quả cho thấy `Load_Type` không phải proxy tốt cho anomaly. Tỷ lệ anomaly theo ba nhóm tải khá gần nhau: Light khoảng 6,336%, Medium khoảng 7,189%, Maximum khoảng 7,508%.

Điều này có nghĩa Maximum_Load không đồng nghĩa bất thường, vì tải tối đa có thể là chế độ sản xuất bình thường. Ngược lại, Light_Load cũng không đồng nghĩa an toàn, vì vẫn có thể có idling hoặc leakage drift.

Vì vậy nhóm giữ `Load_Type` như biến mô tả chế độ vận hành, không dùng nó thay thế anomaly label.

Chuyển slide: Sau phần xây dựng dataset, nhóm kiểm chứng vai trò feature bằng ablation.

## Slide 10 - Ablation: Forecasting

Thời gian: 55 giây.

Task đầu tiên là dự báo `Usage_kWh(t+1h)`, tức dự báo tiêu thụ trước 1 giờ. Metric chính là RMSE, càng thấp càng tốt.

Kết quả cho thấy `RAW + TIME` là cấu hình tốt nhất, RMSE khoảng 12,0087. Trong khi đó `RAW + CONTEXT` khoảng 13,0119. Điều này phù hợp với bản chất chuỗi thời gian: với dự báo ngắn hạn, lịch sử gần và chu kỳ ngày là tín hiệu mạnh nhất.

Điểm cần nhấn mạnh là không phải càng thêm nhiều feature càng tốt cho mọi task. Với forecasting ngắn hạn, time features là ưu tiên rõ ràng và tiết kiệm nhất.

Chuyển slide: Với proxy anomaly, kết quả lại khác.

## Slide 11 - Ablation: Proxy anomaly

Thời gian: 1 phút.

Task thứ hai là dự đoán `anomaly_any` dạng proxy. Vì lớp anomaly mất cân bằng, nhóm dùng PR-AUC thay vì chỉ nhìn accuracy.

Trong full track, cấu hình `RAW + TIME + WEATHER` đạt PR-AUC cao nhất, khoảng 0,3642. Điều này cho thấy weather có giá trị khi bài toán không chỉ là dự báo mức tiêu thụ, mà là nhận diện bối cảnh rủi ro proxy.

Tuy nhiên rule-free track rất thấp, tốt nhất khoảng 0,0178. Đây không phải thất bại cần che đi, mà là bằng chứng giúp nhóm diễn giải đúng phạm vi. Nếu bỏ các biến trực tiếp tham gia rule, tín hiệu phát hiện lỗi độc lập còn yếu vì dataset không có nhãn SCADA/maintenance thật.

Kết luận đúng là: time + weather giúp dự đoán proxy labels tốt nhất trong full track, nhưng chưa chứng minh phát hiện lỗi thật.

Chuyển slide: Nhóm cũng thử augmentation cho lớp minority bằng GAN.

## Slide 12 - GAN validation

Thời gian: 45 giây.

GAN được dùng như thử nghiệm augmentation cho lớp anomaly proxy, không dùng làm bằng chứng xác nhận lỗi. Nhóm huấn luyện trên 2.388 minority rows và sinh 500 synthetic samples.

Kết quả mean error khoảng 8,20%, std error khoảng 3,81%, nhưng correlation MAE khoảng 0,116. Nghĩa là phân phối biên tương đối gần, nhưng cấu trúc tương quan vẫn lệch.

Vì vậy FC-GAN hiện tại chỉ nên xem là baseline augmentation. Nếu phát triển tiếp, hướng hợp lý hơn là TimeGAN hoặc conditional time-series generator.

Chuyển slide: Từ đó nhóm xác định rõ các hạn chế.

## Slide 13 - Hạn chế

Thời gian: 55 giây.

Hạn chế lớn nhất là không có SCADA hoặc maintenance labels, nên proxy labels không thể được xác nhận là lỗi thật.

Hạn chế thứ hai là dữ liệu chỉ đến từ một nhà máy thép trong một năm. Khi áp dụng sang nhà máy khác, pattern tải, quy trình sản xuất và ngưỡng power factor có thể thay đổi.

Hạn chế thứ ba là weather đến từ Open-Meteo theo tọa độ, không phải sensor on-site. Vì vậy weather nên được hiểu là contextual enrichment, không phải nguyên nhân chắc chắn của rủi ro.

Do đó cách dùng đúng của Electrimight là phân tích offline, benchmark, xếp hạng rủi ro ứng viên và hỗ trợ chuyên gia ưu tiên kiểm tra. Không dùng dataset này để tự động điều khiển SCADA, đảm bảo an toàn hoặc kết luận lỗi thật.

Chuyển slide: Với phạm vi đó, nhóm tổng kết đóng góp.

## Slide 14 - Đóng góp

Thời gian: 55 giây.

Đóng góp của Electrimight có hai lớp.

Lớp thứ nhất là đóng góp dữ liệu theo hướng data-centric. Trong bối cảnh nhiều bài toán dự báo điện còn tập trung vào cải tiến model cho load forecasting thuần, Electrimight xây dựng một dataset công nghiệp có thể kiểm thử, có weather context, time features, wavelet features, physical features và proxy labels có giải thích. Vì vậy đóng góp không chỉ nằm ở kết quả mô hình, mà còn ở nền dữ liệu có thể dùng để phân tích mối liên hệ giữa feature engineering và proxy risk prediction.

Lớp thứ hai là đóng góp insight để hỗ trợ quyết định và ưu tiên kỹ thuật. Ablation cho thấy doanh nghiệp không nhất thiết phải triển khai mọi kỹ thuật phức tạp ngay từ đầu. Với forecasting ngắn hạn, time features là bước nên ưu tiên trước. Với proxy risk prediction, time + weather cho PR-AUC tốt nhất trong full track.

Câu tóm gọn cho slide là: dataset không chỉ là đầu ra dữ liệu, mà còn là bằng chứng thực nghiệm giúp ưu tiên kỹ thuật: time features cho forecasting, time + weather cho proxy risk prediction. Điều này hỗ trợ xếp hạng rủi ro ứng viên, ưu tiên đầu tư kỹ thuật và ra quyết định vận hành thận trọng hơn, nhưng không khẳng định phát hiện lỗi thật.

Chuyển slide: Em xin kết thúc bằng thông điệp chính.

## Slide 15 - Kết thúc

Thời gian: 20 giây.

Tóm lại, Electrimight không thay thế SCADA hay hệ thống bảo vệ điện real-time. Đóng góp của nhóm là biến public meter logs thành một dataset điện công nghiệp giàu ngữ cảnh, có feature vật lý và tần số, có proxy labels minh bạch, và có pipeline có thể kiểm thử cho nghiên cứu offline.

Nhóm em xin cảm ơn thầy/cô và các bạn đã lắng nghe. Nhóm sẵn sàng cho phần Q&A.

## Bản rút gọn nếu gần hết giờ

Nếu còn dưới 3 phút từ slide 12, dùng bản rút gọn sau:

### Slide 12 rút gọn

GAN chỉ là baseline augmentation cho anomaly proxy. Mean/std khá gần, với mean error 8,20% và std error 3,81%, nhưng correlation MAE 0,116 cho thấy tương quan giữa feature còn lệch. Vì vậy không dùng GAN làm bằng chứng lỗi thật.

### Slide 13 rút gọn

Ba hạn chế chính là không có SCADA/maintenance labels, chỉ có một nhà máy, và weather theo tọa độ chứ không phải sensor on-site. Do đó pipeline phù hợp phân tích offline và xếp hạng rủi ro ứng viên, không dùng cho điều khiển real-time.

### Slide 14 rút gọn

Đóng góp gồm hai phần: một là dataset data-centric giàu ngữ cảnh, có feature thời gian, weather, wavelet, vật lý và proxy labels; hai là insight ablation giúp ưu tiên kỹ thuật: time features cho forecasting, time + weather cho proxy risk prediction.

## Câu mở đầu và kết thúc nên thuộc lòng

Mở đầu:

> Nhóm em không chỉ xây dựng một mô hình dự báo, mà xây dựng một pipeline biến dữ liệu công tơ điện thô thành dataset có ngữ cảnh, có feature vật lý, có nhãn proxy minh bạch và có thể kiểm thử lại.

Kết thúc:

> Electrimight không thay thế hệ thống SCADA hay bảo vệ điện real-time. Đóng góp của nhóm là một benchmark dữ liệu công nghiệp có thể tái lập cho phân tích offline khi chỉ có public meter logs.
