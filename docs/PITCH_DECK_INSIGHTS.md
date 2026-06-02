# Insights & Pitch Deck Strategy — DS108 Electrimight

> Tài liệu này phục vụ cho cả **báo cáo viết (50% grade)** và **thuyết trình (50% grade)**.
> Mục tiêu: hiểu sâu bài toán, kể một câu chuyện dữ liệu (Data Storytelling) thuyết phục trong 10 phút.

---

## Phần 1: Kiến thức & Tài nguyên cần học

### A. Domain Knowledge — Ngành Thép & Điện Công Nghiệp

Để thuyết trình có chiều sâu, bạn cần hiểu **tại sao** các feature điện năng lại quan trọng, không chỉ **là gì**.

| Chủ đề | Tại sao cần học | Tài nguyên gợi ý |
|--------|----------------|------------------|
| **Power Triangle** (P, Q, S, PF) | Hiểu mối liên hệ giữa công suất tác dụng, phản kháng, biểu kiến | Khan Academy: *AC Circuit Analysis*; YouTube: "Power Factor explained" (The Engineering Mindset) |
| **IEEE 519 & Power Factor Penalty** | Giải thích tại sao PF < 0.50 là "severe penalty zone" | YouTube: "IEEE 519 Harmonics and Power Factor"; Tài liệu IEEE 519-2014 (miễn phí qua university library) |
| **ISO 50001 Energy Baseline** | Hiểu cơ sở gán nhãn Leakage (+5% threshold) | YouTube: "ISO 50001 Energy Management Systems Explained"; Coursera: *Energy Management* (DelftX) |
| **Steel Plant Load Profile** | Tại sao có 3 chế độ (Light/Medium/Maximum), tại sao tải cảm kháng chiếm ưu thế | YouTube: "Steel Manufacturing Process" (POSCO官方); Paper: *Energy consumption in steel industries* (Elsevier) |
| **SCADA & Industrial Metering** | Hiểu nguồn gốc dữ liệu 15 phút | YouTube: "SCADA Explained" (RealPars) |

**Insight quan trọng nhất để nhớ:**
> Trong nhà máy thép, tải cảm kháng (inductive load) chiếm ưu thế do lò điện, máy cán, và HVAC. Điều này giải thích tại sao `Leading_Reactive_Power` gần như = 0, và tại sao PF thấp là dấu hiệu idling nguy hiểm.

---

### B. Time Series Preprocessing & Feature Engineering

| Chủ đề | Tại sao cần học | Tài nguyên gợi ý |
|--------|----------------|------------------|
| **Zero Data Leakage** | Đây là điểm mạnh kỹ thuật lớn của pipeline | Blog: "Data Leakage in Time Series" (Towards Data Science); YouTube: *Machine Learning Mastery* — Time Series Forecasting |
| **Rolling Window `center=False`** | Tránh đưa thông tin tương lai vào hiện tại | Document: pandas `rolling()` official docs (phần `center`) |
| **Lag Features** | Tại sao lag 1,2,4,96? (15m, 30m, 1h, 24h) | YouTube: "Time Series Feature Engineering" (Krish Naik) |
| **Cyclical Encoding (sin/cos)** | Tại sao không dùng raw NSM? Vì 23:59 và 00:01 chỉ cách 2 phút | Blog: "Encoding Time in Machine Learning" (fast.ai); YouTube: *StatQuest* — Feature Engineering |
| **Discrete Wavelet Transform (DWT)** | Hiểu cA (trend) vs cD (detail), tại sao dùng db4 | YouTube: "Wavelet Transform Explained" (Steve Brunton); PyWavelets docs; Paper: *Wavelet-based feature extraction for load forecasting* |
| **MODWT vs DWT** | Hiểu hạn chế DWT hiện tại và hướng cải tiến | Paper: Liu et al. 2022 (đã cite trong báo cáo) |
| **Heat Index (Rothfusz)** | Hiểu công thức NOAA, tại sao T < 26.7°C thì HI = T | NOAA Heat Index Calculator docs |
| **Physical Features (S, φ)** | Tại sao không dùng P đơn thuần? Vì Q tăng vọt khi kẹt rô-to nhưng P không đổi | Physics textbook: *Electric Power Systems* (B.M. Weedy); YouTube: "Apparent Power vs Real Power" |

---

### C. Anomaly Detection — Labeling & Domain Rules

| Chủ đề | Tại sao cần học | Tài nguyên gợi ý |
|--------|----------------|------------------|
| **Percentile-based vs IQR** | Hiểu tại sao Overload dùng P99.5 thay vì Tukey 3×IQR | Blog: "When IQR fails" (Towards Data Science) |
| **CUSUM & Drift Detection** | Hiểu cơ sở gán nhãn Leakage | YouTube: "CUSUM Control Charts Explained"; Paper: Abraham et al. 2021 |
| **Confidence Scoring** | Tại sao không dùng nhãn hard binary? | Blog: "Uncertainty Quantification in Anomaly Detection" |
| **Class Imbalance (6.8%)** | Tại sao cần GAN/SMOTE? | YouTube: "Handling Imbalanced Data" (StatQuest); Blog: SMOTE vs GAN comparison |

---

### D. GAN & Synthetic Data Generation

| Chủ đề | Tại sao cần học | Tài nguyên gợi ý |
|--------|----------------|------------------|
| **Vanilla FC-GAN limitations** | Hiểu vì sao FC-GAN chỉ nên là baseline augmentation: mean/std khá ổn nhưng correlation MAE vẫn còn sai lệch | Paper: Goodfellow 2014 (GAN original); Blog: "Why GANs fail on tabular data" |
| **TimeGAN / TTS-GAN** | Hướng cải tiến cho future work | Paper: Yoon et al. 2019 (TimeGAN); Paper: Li et al. 2022 (TTS-GAN); YouTube: "TimeGAN Explained" |
| **SMOTE vs GAN** | Hiểu SMOTE như baseline tương lai, nhưng không đưa vào official results nếu chưa có artifact tái lập trong pipeline | Blog: "SMOTE: Synthetic Minority Over-sampling" (imbalanced-learn docs) |

---

### E. EDA & Data Storytelling

| Chủ đề | Tại sao cần học | Tài nguyên gợi ý |
|--------|----------------|------------------|
| **Data Storytelling** | Kỹ năng quan trọng nhất cho thuyết trình 50% | Book: *Storytelling with Data* (Cole Nussbaumer Knaflic); YouTube: "The beauty of data visualization" (TED: David McCandless) |
| **Matplotlib/Seaborn best practices** | Trình bày figure đẹp, rõ ràng | YouTube: "How to make publication-quality figures" (Joshua Starmer — StatQuest) |
| **Correlation Heatmap Interpretation** | Hiểu tại sao Usage_kWh vs CO₂ có r ≈ 0.95 | Blog: "Correlation does not imply causation" examples |

---

## Phần 2: Pitch Deck Strategy — 10 phút, 13-15 Slides

### Narrative chính

Thông điệp nên nói xuyên suốt:

> Các hệ thống relay, SCADA và condition monitoring có thể đã tồn tại trong nhà máy, nhưng chúng thường cần cảm biến chuyên dụng, log nội bộ hoặc nhãn bảo trì thật. Gap của Electrimight không phải là thay thế các hệ thống an toàn đó, mà là xây dựng một pipeline dữ liệu ít phụ thuộc hạ tầng cảm biến: từ dữ liệu công tơ 15 phút, bổ sung weather, time, wavelet, physical features và weak/proxy anomaly labels để phục vụ phân tích offline, forecasting và sàng lọc rủi ro ứng viên.

Nói ngắn gọn trong thuyết trình:

> "Chúng tôi không claim đây là hệ thống bảo vệ điện real-time. Chúng tôi giải quyết bài toán trước đó: khi chỉ có dữ liệu công tơ công nghiệp công khai, làm sao biến nó thành một dataset giàu ngữ cảnh, có feature audit được và có nhãn proxy đủ minh bạch để nghiên cứu?"

### Cấu trúc đề xuất

| # | Slide | Nội dung nên nói | Số liệu/figure cần đưa |
|---|-------|------------------|------------------------|
| 1 | **Hook** | Nhà máy thép tiêu thụ điện lớn, nhưng dữ liệu công khai thường chỉ là meter logs thô. Muốn dự báo và nhận biết rủi ro thì cần ngữ cảnh, feature vật lý và nhãn có thể giải thích. | 35,040 mẫu, 1 năm, tần suất 15 phút. |
| 2 | **Problem** | Dữ liệu gốc chỉ có 11 cột, không có maintenance/SCADA alarm labels, không có weather context, không có feature vật lý/wavelet. | Before: 11 cột raw. |
| 3 | **Gap Analysis** | Existing overload protection/condition monitoring mạnh hơn cho safety, nhưng phụ thuộc sensor/log nội bộ. Gap của project là low-instrumentation dataset enrichment và weak-label benchmark cho offline analytics. | 1 sơ đồ 2 cực: "SCADA/condition monitoring" vs "public meter dataset"; Electrimight nằm giữa. |
| 4 | **Research Motivation** | Load_Type chỉ nói chế độ vận hành bình thường; anomaly labels nói dấu hiệu bất thường ứng viên bên trong chế độ đó. Đây là lý do project không chỉ dự báo lại Load_Type. | MI(Load_Type, anomaly_any) = 0,0002. |
| 5 | **Dataset Overview** | UCI steel electricity + Open-Meteo. Weather 1 giờ được resample xuống 15 phút trước khi merge với điện 15 phút. | Raw 35,040 x 11; weather resampled 35,040 x 4; final 35,040 x 64. |
| 6 | **Data Quality Insight** | Pipeline giữ row alignment, không missing sau merge, không dùng future data trong lag/rolling. | Nulls after merge = 0; `python -m pytest`: 50 passed. |
| 7 | **Feature Engineering** | 11 -> 64 cột qua time features, weather context, wavelet db4, physical features S và phi. | Nhóm feature theo 4 miền. |
| 8 | **Proxy Labeling** | 3 weak/proxy labels: idling, leakage, overload. Nhấn rằng pipeline dùng `metadata/dataset/LABELING_GUIDELINE.md` để chuẩn hóa rule, confidence score và explanation; đây không phải ground truth lỗi thật. | Idling 10; Leakage 2,336; Overload 48; anomaly_any 2,388 (6,815%); trích `tab:anomaly` và `tab:proxy_validation`. |
| 9 | **Load_Type vs Anomaly** | Maximum_Load không đồng nghĩa bất thường; Light_Load không đồng nghĩa an toàn. Leakage trải đều, overload tập trung hơn ở Maximum_Load, idling chỉ ở Light_Load. | Bảng tỷ lệ theo Load_Type: Light 6,336%, Medium 7,189%, Maximum 7,508%. |
| 10 | **Ablation: Forecasting** | Với Usage_kWh(t+1h), time features là đóng góp rõ nhất; weather không cải thiện forecasting trong thí nghiệm này. Vai trò của phần này là chứng minh pipeline có giá trị cho bài toán dự báo tải, không chỉ anomaly. | RMSE raw 13,0119; time 12,0087; time+weather 12,2585; all 12,1781. |
| 11 | **Ablation: Proxy Anomaly** | Với proxy anomaly labels, Time + Weather tốt nhất trong full track, nhưng rule-free rất thấp. Điều này nghĩa là weather có giá trị contextual enrichment, nhưng chưa đủ để claim phát hiện lỗi thật độc lập. | PR-AUC full: raw 0,198; time 0,150; time+weather 0,364. Rule-free max 0,0178. |
| 12 | **GAN Validation** | GAN dùng để thử cân bằng lớp anomaly proxy, không dùng làm bằng chứng lỗi thật. Kết quả official cho thấy mean/std khá gần nhưng correlation còn sai lệch. | 2,388 minority rows; 500 synthetic; mean error 8,20%; std error 3,81%; correlation MAE 0,116. |
| 13 | **Limitations & Risks** | Không có SCADA/maintenance labels, chỉ 1 nhà máy, weather là dữ liệu theo tọa độ, proxy labels phụ thuộc rule, không dùng cho điều khiển real-time. | Đưa trực tiếp 4 bullet limitation. |
| 14 | **Contribution** | Dataset enrichment, weak/proxy labeling, ablation study tách forecasting/proxy/rule-free, datasheet/codebook/testable pipeline. | 64 cột, CODEBOOK, Datasheet, 50 tests. |
| 15 | **Closing** | Giá trị của project là làm rõ một benchmark có thể tái lập cho nghiên cứu điện công nghiệp khi chưa có nhãn lỗi thật. | Một câu kết: "From raw meter logs to auditable industrial electricity analytics." |

Nếu chỉ có 10 phút, gộp slide 5-6 và 13-14 để còn 13 slides.

---

### Các insight quan trọng nhất nên đưa vào

1. **Gap thực sự:** Không thay thế relay/SCADA/condition monitoring; project lấp khoảng trống dữ liệu ít cảm biến, tái lập được, phục vụ offline analytics.
2. **Weather là contextual enrichment:** Weather 1 giờ được resample xuống 15 phút và merge không missing. Kết quả ablation cho thấy weather không giúp rõ cho Usage_kWh forecasting, nhưng giúp proxy anomaly classification trong full track khi kết hợp với time/operational context.
3. **Load_Type khác anomaly:** Load_Type là chế độ vận hành bình thường; `anomaly_any` là dấu hiệu rủi ro ứng viên. Mutual information chỉ 0,0002 nên anomaly không đơn giản là mã hóa lại Load_Type.
4. **Proxy labels valid nhưng không phải ground truth:** Weak/proxy labeling là hướng nghiên cứu hợp lệ khi thiếu nhãn thật, nhưng validation hiện tại chỉ chứng minh consistency với labeling rules và context, chưa chứng minh fault detection thực địa.
5. **Ablation giúp tránh overclaim:** Forecasting và proxy anomaly là hai task khác nhau. Forecasting chứng minh time features hữu ích cho dự báo tải; proxy classification kiểm tra weather/context có giúp dự đoán nhãn yếu hay không; rule-free cho thấy giới hạn của nhãn proxy.
6. **GAN đã được validate lại:** FC-GAN không nên được kể như "phát hiện lỗi"; nó chỉ là augmentation cho lớp anomaly proxy, với mean error 8,20%, std error 3,81%, correlation MAE 0,116.
7. **Wavelet/Physics hữu ích nhưng phải nói đúng mức:** DWT giúp nhìn biến động đa tỉ lệ và các spike tần số cao, còn $S$--$\varphi$ giúp diễn giải chế độ vận hành. Tuy nhiên, ablation cho thấy chúng chưa cải thiện rõ forecasting 1 giờ và rule-free proxy detection; future work nên kiểm tra MODWT/adaptive wavelet và đối chiếu $S$--$\varphi$ với cảm biến asset-level.

---

### Cách dùng số liệu để dẫn chứng

| Claim cần nói | Số liệu nên dùng | Ý nghĩa |
|---------------|------------------|---------|
| Dataset được làm giàu thật sự | 11 cột raw -> 64 cột gold | Chứng minh project không chỉ chạy model, mà xây dựng dataset. |
| Weather integration hợp lệ về kỹ thuật | 8,760 hourly rows -> 35,040 rows 15 phút; nulls after merge = 0 | Chứng minh weather được căn chỉnh đúng tần suất điện 15 phút. |
| Proxy anomaly có quy mô đủ phân tích | anomaly_any = 2,388/35,040 = 6,815% | Không quá hiếm để không học được, nhưng vẫn mất cân bằng. |
| Load_Type không thay thế anomaly | MI = 0,0002; anomaly rate theo Load_Type chỉ chênh nhẹ | Chứng minh task anomaly không vòng vo dự đoán lại Load_Type. |
| Time features giúp forecasting | RMSE raw 13,0119 -> time 12,0087 | Dẫn chứng đóng góp cho Usage_kWh(t+1h). |
| Weather giúp proxy trong full track | PR-AUC time+weather 0,364 cao hơn raw 0,198 và time 0,150 | Dẫn chứng contextual enrichment cho proxy labels. |
| Không overclaim fault detection | rule-free PR-AUC cao nhất 0,0178 | Nói rõ thiếu SCADA/maintenance labels nên chưa validate lỗi thật độc lập. |
| Pipeline reproducible | 50 pytest passed | Chứng minh chất lượng engineering. |

### Bảng/Figure nên lấy trực tiếp từ báo cáo

| Mục đích trên slide | Lấy từ báo cáo | Cách dùng |
|---------------------|----------------|-----------|
| Mô tả dữ liệu gốc | `tab:descriptive`, Fig. `fig:timeseries` | Dẫn vào vấn đề: dữ liệu 15 phút có chu kỳ ngày/tuần nhưng còn thô. |
| Chứng minh DWT có ý nghĩa phân tích | Fig. `fig:dwt` | Nói DWT tách trend `cA3` và spike tần số cao `cD1`/`cD2`, nhưng không overclaim là cải thiện model. |
| Chứng minh Physics features có ý nghĩa | Fig. `fig:sphi`, Fig. `fig:physical_dist`, `tab:physical` | Nói $S$--$\varphi$ phân tách Load_Type và giúp diễn giải điện học. |
| Chứng minh labeling guideline được áp dụng | `tab:anomaly`, `tab:proxy_validation`, `metadata/dataset/LABELING_GUIDELINE.md` | Nói nhãn có rule, score, explanation và limitation; không phải nhãn SCADA thật. |
| Chứng minh anomaly khác Load_Type | `tab:loadtype_anomaly` | Nói MI = 0,0002 và anomaly rate giữa Load_Type không chênh lớn. |
| Chứng minh feature impact | `tab:ablation_forecast`, Fig. `fig09_ablation_forecast_rmse.png` | Nói time features giảm RMSE rõ nhất cho Usage_kWh(t+1h). |
| Chứng minh weather contextual enrichment | `tab:ablation_proxy`, Fig. `fig10_ablation_proxy_pr_auc.png` | Nói Time + Weather tốt nhất ở full track, nhưng rule-free thấp. |
| Chứng minh GAN chỉ là augmentation | `tab:gan`, `metadata/pipeline/gan_stats.json` | Nói mean/std ổn hơn, correlation MAE còn hạn chế; không phải bằng chứng lỗi thật. |

---

### Script ngắn cho phần Problem -> Gap -> Motivation

Bạn có thể nói theo mạch này:

> "Trong nhà máy thật, quá tải hay sự cố điện nghiêm trọng thường được xử lý bằng relay bảo vệ, SCADA alarm hoặc condition monitoring. Nhưng các dữ liệu đó thường không công khai, cần cảm biến chuyên dụng và log bảo trì nội bộ. Trong khi đó, dataset công khai thường chỉ có meter readings thô. Gap của project này nằm ở giữa: làm sao từ dữ liệu công tơ 15 phút có thể xây dựng một dataset giàu ngữ cảnh, có đặc trưng vật lý, weather, wavelet và weak/proxy labels để nghiên cứu offline?"

Sau đó nối sang Load_Type:

> "Một câu hỏi quan trọng là liệu anomaly label có chỉ lặp lại Load_Type không. Kết quả cho thấy không: mutual information giữa Load_Type và anomaly_any chỉ 0,0002. Load_Type nói nhà máy đang ở chế độ tải nhẹ, trung bình hay tối đa; anomaly label nói trong chế độ đó có dấu hiệu rủi ro ứng viên hay không."

Rồi nối sang ablation:

> "Vì vậy chúng tôi validate bằng hai task. Task 1 là dự báo Usage_kWh(t+1h), nơi time features đóng góp rõ nhất. Task 2 là dự đoán proxy anomaly labels, nơi Time + Weather đạt PR-AUC tốt nhất trong full track. Nhưng rule-free track rất thấp, nên kết luận đúng phải là: weather giúp contextual enrichment cho proxy labels, chứ chưa chứng minh phát hiện lỗi thật nếu không có SCADA hoặc maintenance labels."

---

### Q&A Dự phòng

| Câu hỏi | Câu trả lời ngắn gọn |
|---------|----------------------|
| "Có phải project đang thay thế hệ thống phát hiện overload thật không?" | "Không. Relay/SCADA là safety-grade real-time. Project này là offline dataset enrichment và proxy-risk analysis khi không có log lỗi thật." |
| "Weak/proxy labels có valid không?" | "Có valid như một phương pháp nghiên cứu khi thiếu ground truth, nếu rule minh bạch, có guideline, có limitation và không claim là lỗi thật đã xác nhận." |
| "Weather có thực sự hữu ích không?" | "Có trong proxy anomaly full track khi kết hợp với time/context: PR-AUC 0,364. Nhưng không cải thiện rõ forecasting Usage_kWh, nên báo cáo phải tách hai task." |
| "Proxy anomaly có khác Load_Type không?" | "Có. Load_Type là chế độ vận hành bình thường; anomaly là dấu hiệu rủi ro ứng viên. MI chỉ 0,0002 nên Load_Type gần như không giải thích được anomaly_any." |
| "Code có phát hiện energy_drift không?" | "Không có cột tên `energy_drift`. Code phát hiện drift năng lượng dưới nhãn `anomaly_leakage`: rolling mean Usage_kWh vượt baseline 4 tuần hơn 5%." |
| "Có data leakage không?" | "Pipeline kiểm soát leakage: lag dùng `shift>0`, rolling không centered, weather không back-fill, và labels không dùng làm feature trong forecasting." |

---

*File này sẽ được cập nhật khi có thêm insights mới từ EDA hoặc phản hồi từ rehearsal.*
