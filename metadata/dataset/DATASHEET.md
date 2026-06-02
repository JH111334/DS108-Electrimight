# Datasheet for Datasets — DS108 Electrimight

> Theo chuẩn Gebru et al., *"Datasheets for Datasets"*, Communications of the ACM, 2021.

---

## 1. Motivation

**For what purpose was the dataset created?**

Bộ dữ liệu được tạo ra để hỗ trợ nghiên cứu về **dự báo tiêu thụ điện năng công nghiệp** và **sàng lọc rủi ro tải điện dạng proxy** trong bối cảnh tải công nghiệp.
Khác với các tập dữ liệu chuỗi thờ gian thông thường chỉ chứa giá trị đo lường, Electrimight bổ sung các đặc trưng miền tần số (DWT), miền vật lý (công suất biểu kiến, góc lệch pha), và nhãn bất thường có giải thích — tạo thành một methodological benchmark cho cộng đồng nghiên cứu về tiết kiệm năng lượng công nghiệp.

**Who created the dataset and on behalf of which entity?**

Nhóm nghiên cứu sinh viên **DS108**, thuộc Trường Đại học Công nghệ Thông tin, ĐHQG Thành phố Hồ Chí Minh, Việt Nam. Dataset này là sản phẩm của đồ án tốt nghiệp / nghiên cứu phương pháp luận.

**Who funded the creation of the dataset?**

Không có nguồn tài trợ bên ngoài. Công sức thu thập và xử lý dữ liệu được thực hiện hoàn toàn bởi nhóm tác giả.

**Any other comments?**

Đây là một *methodological dataset* — tức là bộ dữ liệu được thiết kế để minh họa và đánh giá các kỹ thuật tiền xử lý chuỗi thờ gian công nghiệp, không phải dữ liệu thương mại từ nhà máy thực tế. Dữ liệu không chứa thông tin cá nhân (PII) hay dữ liệu nhạy cảm về an ninh.

---

## 2. Composition

**What do the instances that comprise the dataset represent?**

Mỗi dòng là một **mốc đo lường 15 phút** tại nhà máy thép POSCO Gwangyang, Hàn Quốc, bao gồm các đại lượng điện năng, khí tượng ngoại sinh, đặc trưng kỹ thuật đa miền, và nhãn bất thường.

**How many instances are there in total?**

- **35.040 mẫu** (một năm đầy đủ, không thiếu mẫu nào).
- **69 cột** sau phần mở rộng physical-domain dùng cả reactive lagging/leading và power-factor đi kèm.

**Does the dataset contain all possible instances or is it a sample?**

Đây là **toàn bộ** dữ liệu một năm (2018) được cung cấp bởi tác giả gốc. Không phải mẫu chọn lọc.

**What data does each instance consist of?**

Mỗi mẫu bao gồm:
- **Điện năng:** Công suất tác dụng, phản kháng, hệ số công suất, CO₂.
- **Khí tượng:** Nhiệt độ, mưa, độ ẩm, gió (gốc + 7 đặc trưng phái sinh).
- **Thờ gian:** Lag, rolling statistics, mã hóa chu kỳ.
- **Tần số:** 16 đặc trưng wavelet (DWT db4, L=3) trên cửa sổ 64 mẫu.
- **Vật lý:** Công suất biểu kiến (S), reactive net/total, S_net, góc lệch pha lagging/leading.
- **Nhãn:** 3 loại bất thường (idling, leakage, overload) kèm confidence score.

**Is there a label or target associated with each instance?**

Có. Mỗi mẫu có **3 nhãn bất thường nhị phân** (boolean) và **3 confidence score** liên tục trong [0, 1]. Ngoài ra có cột `anomaly_any` (OR tổng hợp) và `anomaly_explanation` (văn bản giải thích nhãn chính).

**Is any information missing from individual instances?**

- Dữ liệu gốc: **không có missing** sau cleaning.
- Các cột lag (`lag_96`): 96 dòng đầu là NaN (không có đủ lịch sử).
- Các cột DWT: 63 dòng đầu là NaN (chưa đủ cửa sổ 64 mẫu).
- Các NaN này là **hợp lệ về mặt thuật toán** và được giữ nguyên để đảm bảo tính trung thực của pipeline.

**Are relationships between individual instances made explicit?**

Có, thông qua:
- Cột `date` (timestamp liên tục 15 phút).
- Các lag features (`lag_1`, `lag_2`, `lag_4`, `lag_96`).
- Các rolling window features (rmean, rstd, rskew).

**Are there recommended data splits?**

Không có sẵn trong file CSV. Tuy nhiên, **đề xuất chia theo thờ gian** (temporal split) để tránh data leakage:
- Train: tháng 1–9 (75%)
- Validation: tháng 10–11 (25%)
- Hoặc 80% đầu / 20% cuối cho bài toán forecasting.

**Are there any errors, sources of noise, or redundancies in the dataset?**

- `CO2(tCO2)`: Chỉ có 8 giá trị khác biệt (biến tính toán từ emission factor × energy, không phải đo trực tiếp). Độ phân giải thấp, có thể bỏ qua trong mô hình không cần giải thích carbon.
- `Leading_Current_Reactive_Power_kVarh`: Phần lớn = 0 do đặc thù tải cảm kháng chiếm ưu thế.
- Power Factor gốc được báo cáo dạng % (0–100), đã chuẩn hóa về hệ số (0–1) trong bước cleaning.

**Is the dataset self-contained, or does it link to external resources?**

**Bán tự chứa.** Dữ liệu khí tượng được thu thập từ Open-Meteo Historical API và đã được nội suy, tích hợp sẵn. Ngườ dùng không cần gọi API để tái tạo.

**Does the dataset contain data that might be considered confidential?**

Không. Dữ liệu gốc đã được công bố công khai trên UCI ML Repository.

**Does the dataset contain data that might be offensive, insulting, threatening, or cause anxiety?**

Không.

**Does the dataset relate to people?**

Không. Dữ liệu chỉ liên quan đến thiết bị công nghiệp và môi trường vận hành.

**Any other comments?**

Dataset đã trải qua pipeline kiểm định nghiêm ngặt: 50 unit tests (pytest), zero data leakage audit, và validation theo chuẩn ISO 50001 / IEEE 519.

---

## 3. Collection Process

**How was the data associated with each instance acquired?**

- **Dữ liệu điện năng:** Từ UCI Machine Learning Repository (dataset ID 851), được tác giả gốc thu thập từ hệ thống SCADA của nhà máy thép POSCO Gwangyang.
- **Dữ liệu khí tượng:** Từ Open-Meteo Historical API, tọa độ (34.975°N, 127.589°E), tần suất 1 giờ, sau đó nội suy tuyến tính về 15 phút.

**What mechanisms or procedures were used to collect the data?**

- API call tự động với retry logic (exponential backoff, max 5 lần).
- Thu thập theo tháng (batching) để tránh payload quá lớn.
- Rate limiting: 1 giây giữa các request.
- Validation sau fetch: kiểm tra số dòng, null, range nhiệt độ ([-20, 45]°C), range độ ẩm ([0, 100]%).

**If the dataset is a sample from a larger set, what was the sampling strategy?**

Không áp dụng — đây là toàn bộ tập dữ liệu một năm.

**Who was involved in the data collection process?**

- **Tác giả gốc (UCI):** Sathishkumar V E et al. (2021).
- **Nhóm DS108:** Thu thập dữ liệu khí tượng, thiết kế pipeline tiền xử lý, feature engineering, và gán nhãn bất thường.

**Over what timeframe was the data collected?**

01/01/2018 – 31/12/2018 (365 ngày, 35.040 mẫu @ 15 phút).

**Were any ethical review processes conducted?**

Không cần thiết. Dữ liệu công khai, không chứa PII, không liên quan đến con ngườ.

**Does the dataset relate to people?**

Không.

**Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources?**

Thu thập qua bên thứ ba: UCI ML Repository và Open-Meteo API.

**Were the individuals in question notified about the data collection?**

Không áp dụng.

**Did the individuals in question consent to the collection and use of their data?**

Không áp dụng.

**If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?**

Không áp dụng.

**Has an analysis of the potential impact of the dataset and its use on data subjects been conducted?**

Không có data subjects. Tuy nhiên, chúng tôi khuyến nghị ngườ dùng không nên áp dụng các ngưỡng bất thường (anomaly thresholds) trực tiếp vào hệ thống an toàn mà không có chuyên gia kỹ thuật điện xem xét.

**Any other comments?**

Không.

---

## 4. Preprocessing / Cleaning / Labeling

**Was any preprocessing/cleaning/labeling of the data done?**

Có, pipeline gồm 7 bước chính:

| Bước | Mô tả |
|------|-------|
| Cleaning | Loại trùng lặp, nội suy tuyến tính missing, scale PF từ %→[0,1], clip PF vào [0,1], sửa Usage_kWh âm về 0 |
| Weather Integration | Resample hourly→15min (linear interpolation), engineer 7 derived weather features, left-join với steel data |
| Time-Domain FE | Lag (1,2,4,96), rolling statistics (24,48,96), cyclical NSM encoding |
| Frequency-Domain FE | DWT db4-L3 trên cửa sổ 64 mẫu (mean, std, energy, max_abs cho cA3, cD3, cD2, cD1) |
| Physical-Domain FE | Tính S, Q_net, Q_total, S_net và φ từ power factor lagging/leading |
| Anomaly Labeling | Idling (IEEE 519 PF<0.50), Leakage (ISO 50001 +5% baseline), Overload (P99.5 + reactive surge) |
| Quality Audit | 49 pytest tests, data assertions (PF∈[0,1], P≥0, anomaly rate<10%, no nulls) |

**Was the "raw data" saved in addition to the preprocessed/cleaned/labeled data?**

Có. Cấu trúc thư mục phân cấp Bronze-Silver-Gold:
- `data/bronze/`: Dữ liệu thô gốc (không chỉnh sửa).
- `data/silver/`: Dữ liệu đã làm sạch + weather merged.
- `data/gold/`: Dữ liệu cuối cùng sau toàn bộ feature engineering và labeling.

**Is the software used to preprocess/clean/label the instances available?**

Có, toàn bộ mã nguồn được đặt trong thư mục `src/` và notebooks tại `notebooks/`. Pipeline được viết bằng Python 3.12, sử dụng Pandas, NumPy, PyWavelets, Scikit-learn. Tính tái lập được đảm bảo qua:
- OOP modular design (`ElectrimightPipeline` class).
- Git version control.
- `requirements.txt` đầy đủ.

**Any other comments?**

Pipeline đảm bảo **zero data leakage**: tất cả rolling windows dùng `center=False`, lag chỉ nhìn về quá khứ (`shift>0`), weather merge không dùng back-fill, và anomaly labels được tính như **physics-informed weak/proxy labels** (không phải feature huấn luyện, cũng không phải ground truth lỗi vận hành đã được SCADA xác nhận).

Pipeline hiện có thêm schema contract trong `src/schema.py`. Với dataset ngoài ngành thép, người dùng cần map tối thiểu cột timestamp và active energy/power; các cột reactive power, power factor, load type và weather là optional nhưng giúp tạo bộ đặc trưng giàu ngữ cảnh hơn. Vì vậy, project nên được hiểu là một pipeline có thể mở rộng cho meter data công nghiệp/nông nghiệp, không phải hệ thống plug-and-play cho mọi ngành mà không cần schema mapping.

---

## 5. Uses

**Has the dataset been used for any tasks already?**

Dataset đã được sử dụng nội bộ cho:
- Đánh giá tác động của kỹ thuật đặc trưng wavelet đến khả năng phát hiện bất thường.
- So sánh GAN augmentation vs SMOTE cho dữ liệu chuỗi thờ gian công nghiệp.
- Kiểm định pipeline tiền xử lý với 50 unit tests.

**Is there a repository that links to any or all papers or systems that use the dataset?**

Repository GitHub chính thức của dự án (private trong giai đoạn đồ án, dự kiến public sau khi hoàn thiện báo cáo).

**What (other) tasks could the dataset be used for?**

- Dự báo tải điện ngắn hạn (short-term load forecasting, STLF).
- Phân loại chế độ vận hành (Load_Type classification).
- Phát hiện bất thường không giám sát (unsupervised anomaly detection).
- Tối ưu hóa lịch trình bảo trì dựa trên dấu hiệu leakage.
- Nghiên cứu tác động của khí tượng đến tiêu thụ điện công nghiệp.

**Is there anything about the composition that might impact future uses?**

- **Nhãn bất thường** được thiết kế riêng cho nhà máy thép với tải cảm kháng chiếm ưu thế. Áp dụng cho nhà máy khác (ví dụ: nhôm, xi măng) có thể cần điều chỉnh ngưỡng PF và baseline.
- **Tỷ lệ anomaly thấp** (~6.8%) phù hợp cho bài toán imbalanced learning, nhưng có thể không đủ cho huấn luyện end-to-end deep learning mà không có augmentation.
- **Dữ liệu một nhà máy duy nhất** giới hạn khả năng khái quát hóa (generalization) nếu không fine-tune.

**Are there tasks for which the dataset should not be used?**

- **Không nên** dùng để ra quyết định pháp lý hoặc điều chỉnh hợp đồng điện mà không có chuyên gia kỹ thuật.
- **Không nên** dùng trực tiếp làm hệ thống SCADA real-time mà không qua thử nghiệm an toàn.
- **Không nên** dùng cho dự báo giá điện (không chứa thông tin giá hay thị trường).

**Any other comments?**

Không.

---

## 6. Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?**

Có, dự kiến sau khi hoàn thiện đồ án, thông qua:
- Kaggle Datasets (dễ tiếp cận cho cộng đồng data science).
- Zenodo (được cấp DOI, phù hợp cho trích dẫn học thuật).

**How will the dataset be distributed?**

Dạng CSV (`steel_final.csv`) kèm theo:
- File metadata này (`metadata/dataset/DATASHEET.md`).
- Data Codebook (`metadata/dataset/CODEBOOK.csv`).
- Pipeline metadata (`metadata/pipeline/`).
- Notebook minh họa pipeline (`notebooks/`).

**When will the dataset be distributed?**

Sau khi báo cáo khoa học được hoàn thiện và phê duyệt (dự kiến Q3/2026).

**Will the dataset be distributed under a copyright or other IP license, and/or under applicable terms of use (ToU)?**

- Phần dữ liệu gốc: UCI ML Repository License (CC BY 4.0 tương đương).
- Phần đặc trưng kỹ thuật và nhãn: MIT License (do nhóm DS108 tạo ra).

**Have any third parties imposed IP-based or other restrictions on the data associated with the instances?**

Không.

**Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?**

Không. Dữ liệu không chứa thông tin quốc phòng, an ninh, hoặc xuất khẩu bị hạn chế.

**Any other comments?**

Không.

---

## 7. Maintenance

**Who is supporting/hosting/maintaining the dataset?**

Nhóm nghiên cứu DS108, Trường ĐH Công nghệ Thông tin, ĐHQG-HCM.

**How can the owner/curator/manager of the dataset be contacted?**

- Email: [địa chỉ email nhóm].
- GitHub Issues trên repository chính thức.

**Is there an erratum?**

Chưa có. Mọi lỗi phát hiện sẽ được ghi nhận trong file `CHANGELOG.md` và thông báo qua GitHub Issues.

**Will the dataset be updated?**

Không có kế hoạch cập nhật định kỳ. Tuy nhiên, có thể mở rộng thêm:
- Dữ liệu năm 2019+ nếu tác giả gốc công bố.
- Thêm cảm biến nhiệt độ lò, độ rung động cơ (vibration) nếu có.

**If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances?**

Không áp dụng.

**Will older versions of the dataset continue to be supported/hosted/maintained?**

Có, thông qua Git tags và releases trên GitHub. Mỗi phiên bản dataset sẽ kèm theo changelog rõ ràng.

**If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?**

Có. Cộng đồng có thể:
- Fork repository và tạo Pull Request.
- Đề xuất thêm đặc trưng mới qua GitHub Issues.
- Sử dụng pipeline OOP hiện có để tích hợp dữ liệu mới.

**Any other comments?**

Chúng tôi hoan nghênh mọi phản hồi về chất lượng nhãn bất thường, đặc biệt từ các chuyên gia ngành điện và năng lượng. Nhãn hiện tại dựa trên ngưỡng vật lý chuẩn (IEEE 519, ISO 50001), nhưng có thể cần điều chỉnh cho từng loại hình nhà máy cụ thể.

---

*Datasheet này được soạn thảo theo khuyến nghị của Gebru et al., "Datasheets for Datasets", Communications of the ACM, 2021.*
