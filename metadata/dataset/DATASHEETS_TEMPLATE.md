# Datasheets for Datasets — Template

> Theo chuẩn Gebru et al., 2021. Điền đầy đủ các mục dưới đây để minh bạch hóa bộ dữ liệu.

---

## 1. Motivation

**For what purpose was the dataset created?**
- Được tạo để hỗ trợ dự báo tiêu thụ điện năng và phát hiện bất thường trong ngành thép.

**Who created the dataset and on behalf of which entity?**
- Nhóm sinh viên DS108.

**Who funded the creation of the dataset?**
- Không có.

**Any other comments?**
- Đây là dữ liệu phương pháp luận (methodological dataset), không chứa thông tin cá nhân.

---

## 2. Composition

**What do the instances that comprise the dataset represent?**
- Mỗi hàng là một mốc đo lường 15 phút tại nhà máy thép POSCO Gwangyang.

**How many instances are there in total?**
- 35.040 mẫu gốc; 35.040+ sau preprocessing.

**Does the dataset contain all possible instances or is it a sample?**
- Toàn bộ năm 2018.

**What data does each instance consist of?**
- Thời gian, công suất tác dụng/phản kháng, hệ số công suất, CO₂, thời tiết, đặc trưng DWT, đặc trưng vật lý, nhãn bất thường.

**Is there a label or target associated with each instance?**
- Có: 3 nhãn bất thường nhị phân (idling, leakage, overload) + confidence score.

**Is any information missing from individual instances?**
- Không.

**Are relationships between individual instances made explicit?**
- Thời gian liên tục 15 phút.

**Are there recommended data splits?**
- Không có sẵn; đề nghị chia theo thời gian (train: 8 tháng, test: 4 tháng).

**Are there any errors, sources of noise, or redundancies in the dataset?**
- CO₂ có độ phân giải thấp (8 unique values). PF gốc được báo cáo dạng %, đã chuẩn hóa về hệ số.

**Is the dataset self-contained, or does it link to or otherwise rely on external resources?**
- Có dữ liệu thời tiết từ Open-Meteo API.

**Does the dataset contain data that might be considered confidential?**
- Không.

**Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?**
- Không.

**Does the dataset relate to people?**
- Không.

**Any other comments?**
- Dữ liệu đã qua xử lý feature engineering từ 11 → 40+ cột.

---

## 3. Collection Process

**How was the data associated with each instance acquired?**
- Steel data: UCI Repository (đã công bố).
- Weather data: Open-Meteo Historical API.

**What mechanisms or procedures were used to collect the data?**
- API call tự động với retry logic.

**If the dataset is a sample from a larger set, what was the sampling strategy?**
- Toàn bộ tập dữ liệu gốc.

**Who was involved in the data collection process?**
- Tác giả gốc (UCI) và nhóm DS108 (weather + preprocessing).

**Over what timeframe was the data collected?**
- 01/01/2018 – 31/12/2018.

**Were any ethical review processes conducted?**
- Không cần thiết vì dữ liệu công khai, không cá nhân.

**Does the dataset relate to people?**
- Không.

**Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources?**
- Từ nguồn thứ ba.

**Were the individuals in question notified about the data collection?**
- Không áp dụng.

**Did the individuals in question consent to the collection and use of their data?**
- Không áp dụng.

**If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?**
- Không áp dụng.

**Has an analysis of the potential impact of the dataset and its use on data subjects been conducted?**
- Không có data subjects.

**Any other comments?**

---

## 4. Preprocessing / Cleaning / Labeling

**Was any preprocessing/cleaning/labeling of the data done?**
- Có: làm sạch, feature engineering, gán nhãn, GAN augmentation.

**Was the "raw data" saved in addition to the preprocessed/cleaned/labeled data?**
- Có, trong `data/raw/`.

**Is the software used to preprocess/clean/label the instances available?**
- Có, trong `src/` và notebooks.

**Any other comments?**

---

## 5. Uses

**Has the dataset been used for any tasks already?**
- Chưa, được tạo cho đồ án DS108.

**Is there a repository that links to any or all papers or systems that use the dataset?**
- GitHub repository.

**What (other) tasks could the dataset be used for?**
- Dự báo tải điện, phân loại rủi ro, tối ưu hóa năng lượng.

**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**
- Nhãn bất thường dựa trên ngưỡng vật lý cố định; có thể cần điều chỉnh cho nhà máy khác.

**Are there tasks for which the dataset should not be used?**
- Không nên dùng để ra quyết định pháp lý mà không có chuyên gia kỹ thuật.

**Any other comments?**

---

## 6. Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?**
- Có thể, thông qua Kaggle hoặc Zenodo.

**How will the dataset be distributed?**
- CSV + metadata.

**When will the dataset be distributed?**
- Sau khi hoàn thiện đồ án.

**Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?**
- UCI License (CC BY 4.0 cho phần gốc).

**Have any third parties imposed IP-based or other restrictions on the data associated with the instances?**
- Không.

**Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?**
- Không.

**Any other comments?**

---

## 7. Maintenance

**Who is supporting/hosting/maintaining the dataset?**
- Nhóm DS108.

**How can the owner/curator/manager of the dataset be contacted?**
- Qua email hoặc GitHub Issues.

**Is there an erratum?**
- Chưa.

**Will the dataset be updated?**
- Không định kỳ, có thể mở rộng thêm năm 2019+ nếu có dữ liệu.

**If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances?**
- Không áp dụng.

**Will older versions of the dataset continue to be supported/hosted/maintained?**
- Có, thông qua Git tags.

**If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?**
- Fork repo và tạo Pull Request.

**Any other comments?**

---

*Template này được tạo dựa trên Gebru et al., "Datasheets for Datasets", Communications of the ACM, 2021.*
