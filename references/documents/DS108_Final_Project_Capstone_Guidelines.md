# 🎓 HƯỚNG DẪN ĐỒ ÁN CUỐI KỲ: TIỀN XỬ LÝ VÀ XÂY DỰNG BỘ DỮ LIỆU

**Course:** DS108 - Pre-processing & Constructing Dataset

**Level:** Undergraduate Capstone

**Philosophy:** Principle-Driven Data Architecture

## LỜI MỞ ĐẦU (EXECUTIVE SUMMARY)

Trong Khoa học Dữ liệu, có một nguyên lý bất di bất dịch: *\"Garbage In,
Garbage Out\"* (Dữ liệu rác tạo ra Mô hình rác).

Mục tiêu tối thượng của đồ án này **KHÔNG PHẢI** là huấn luyện mô hình
Machine Learning. Đồ án này là bài kiểm tra về khả năng của bạn trong
vai trò **Data Architect (Kiến trúc sư Dữ liệu)**: Khả năng đối mặt với
sự hỗn mang của thế giới thực, sử dụng các nguyên lý Toán học, Thống kê
và Kỹ thuật Phần mềm để chắt lọc, làm sạch và thiết kế ra một \"Nguyên
liệu AI\" (Benchmark Dataset) đạt chuẩn công nghiệp và học thuật.

Điểm số của bạn không được quyết định bởi việc bạn gõ bao nhiêu dòng
code, mà bởi **chiều sâu trong tư duy phương pháp luận (Methodological
Rigor)** và **sự biện luận khoa học** đằng sau mỗi dòng code đó.

## **PHẦN 1: CÁC KHUNG BÀI TOÁN TIÊU CHUẨN (THE DATA PROBLEM FRAMES)**

Mỗi nhóm sinh viên tự do lựa chọn đề tài, nhưng đề tài đó **bắt buộc**
phải rơi vào 1 trong 3 Khung bài toán (Problem Frames) dưới đây. Sự phân
chia này dựa trên cấu trúc tự nhiên của dữ liệu và các kỹ năng Kỹ
thuật/Nghiên cứu tương ứng.

### **🛤️ Frame 1: Data Integration & Tabular Architecture (Hướng Kỹ thuật Hệ thống)**

- **Bản chất:** Đối mặt với dữ liệu có cấu trúc (Tabular) nhưng bị phân
  mảnh, đa nguồn, đa định dạng và chứa nhiều dị biệt hệ thống.

- **Nguyên lý cốt lõi cần giải quyết:** 1. *Khả năng thu thập:* Thiết kế
  đường ống tự động lấy dữ liệu từ Web/APIs/Databases. 2. *Sự đồng
  nhất:* Giải quyết bài toán Entity Resolution (Gộp các bản ghi từ các
  nguồn khác nhau chỉ về cùng một thực thể). 3. *Xử lý dị biệt:* Chuẩn
  hóa các hệ quy chiếu (Thời gian, Tiền tệ, Đo lường), xử lý mâu thuẫn
  logic nghiệp vụ (Ví dụ: Tuổi = 20 nhưng Năm sinh = 2015).

### **🛤️ Frame 2: Unstructured Data & Scientific Annotation (Hướng Nghiên cứu AI)**

- **Bản chất:** Chuyển đổi dữ liệu phi cấu trúc (Văn bản, Hình ảnh, Âm
  thanh) thành dữ liệu có nhãn phục vụ Supervised Learning. Trọng tâm
  nằm ở Khoa học Gán nhãn (Annotation Science).

- **Nguyên lý cốt lõi cần giải quyết:**

  1.  *Ontology Design:* Xây dựng \"Bộ quy tắc gán nhãn\" (Annotation
      Codebook/Guidelines) cực kỳ tường minh, triệt tiêu sự cảm tính của
      con người.

  2.  *Đánh giá Độ tin cậy:* Bắt buộc áp dụng các phương pháp đo lường
      thống kê (Inter-Annotator Agreement - ví dụ Fleiss\' Kappa hoặc
      Cohen\'s Kappa) để chứng minh các nhãn dán là khách quan và có thể
      tái lập.

### **🛤️ Frame 3: Advanced Data Rescue & Algorithmic Imputation (Hướng Thuật toán)**

- **Bản chất:** Xử lý các bộ dữ liệu mang những vấn đề đặc trưng: Bị
  khuyết diện rộng (Massive Missingness), hoặc mất cân bằng cực đoan
  (Extreme Imbalance).

- **Nguyên lý cốt lõi cần giải quyết:**

  1.  *Chẩn đoán thống kê:* Phải chứng minh được cơ chế khuyết (MCAR,
      MAR, MNAR) bằng các bài test thống kê hoặc trực quan hóa trước khi
      chọn thuật toán.

  2.  *Bảo toàn Phân phối:* Áp dụng các thuật toán nội suy đa biến
      (Multivariate Imputation) hoặc kỹ thuật Resampling SOTA để làm
      sạch dữ liệu mà không làm sụp đổ phương sai (Variance) hay làm méo
      mó ma trận hiệp phương sai gốc.

## **PHẦN 2: QUY CHUẨN GIAO NỘP SẢN PHẨM (DELIVERABLES)**

Đồ án là một gói sản phẩm (Portfolio) phản ánh quy trình làm việc của
một nhóm Kỹ sư chuyên nghiệp. Mọi sự cẩu thả trong tổ chức file đều bị
trừ điểm.

1.  **The Codebase (Mã nguồn & Tính tái lập):** \* Nộp Link
    GitHub/GitLab hoặc file .zip có cấu trúc thư mục rõ ràng (/data,
    /notebooks, /src).

    - Mã nguồn phải chạy được (Reproducible), có requirements.txt và
      README.md hướng dẫn chi tiết. Bắt buộc rạch ròi giữa thư mục Dữ
      liệu thô (Raw) và Dữ liệu thành phẩm (Processed).

Cấu trúc thư mục tham khảo

project_name/

│

├── data/

│ ├── raw/ \<- Dữ liệu thô gốc (Tuyệt đối KHÔNG được sửa bằng tay/Excel)

│ └── processed/ \<- Dữ liệu đã làm sạch (Thành phẩm)

│

├── notebooks/ \<- Chứa các file source codes ( .ipynb, .py,\...)

│ ├── 01_data_collection.ipynb

│ ├── 02_data_cleaning_and_imputation.ipynb

│ └── 03_exploratory_data_analysis.ipynb

│

├── requirements.txt \<- Danh sách thư viện (pip freeze)

└── README.md \<- Hướng dẫn cách chạy code từ A-Z

2.  **The Data Artifact (Thành phẩm Dữ liệu & Code Book):**

    - File dữ liệu cuối cùng (CSV/Parquet/JSON).

    - Đi kèm một **Code Book (Data Dictionary)** giải thích rõ kiểu dữ
      liệu, miền giá trị và ý nghĩa của từng cột/nhãn.

3.  **The Technical Report (Báo cáo Khoa học - THE CORE):**

    - Định dạng IEEE hoặc ACM (2 cột), dài 10-20 trang.

    - Đây là nơi bạn **biện luận cho các quyết định kỹ thuật**. Không
      liệt kê *\"Tôi đã làm bước A, bước B\"*. Hãy viết *\"Tôi chọn
      phương pháp A vì phân phối dữ liệu có đặc tính B, nếu dùng phương
      pháp C sẽ gây ra sai số D\"*.

    - **BẮT BUỘC:** Phụ lục báo cáo phải chứa tài liệu **\"Datasheets
      for Datasets\"** (Theo chuẩn của Gebru et al., 2021) để minh bạch
      hóa quy trình tạo dữ liệu.

4.  **The Pitch Deck (Bản trình bày):** Tối đa 15 slides. Trình bày
    trong 10 phút.

    - Slides dùng để kể một câu chuyện dữ liệu (Data Storytelling). Nhấn
      mạnh vào thách thức kỹ thuật lớn nhất và những Insights (Tri thức)
      bất ngờ nhất tìm được qua quá trình EDA.

## PHẦN 3: MA TRẬN TIÊU CHÍ ĐÁNH GIÁ **(COMPETENCY-BASED RUBRIC)**

Đồ án được đánh giá dựa trên **Sự phức tạp của bài toán (Complexity)**,
**Sự chặt chẽ của Phương pháp luận (Methodological Rigor)**, và **Tính
Kỹ thuật (Engineering Standard)**. Thang điểm từ 0 đến 10.

+-------------------+-------------+-----------------+---------------------------------+-------------+
| **Tiêu chí Đánh   | **Mức Cơ    | **Mức Đạt chuẩn | **Mức Xuất sắc (Advanced/SOTA)  | **Trọng     |
| giá**             | bản (Basic) | (Proficient) B  | A / 9.0 - 10đ**                 | số**        |
|                   | C / 5.0 -   | / 7.0 - 8.5đ**  |                                 |             |
|                   | 6.5đ**      |                 |                                 |             |
+-------------------+-------------+-----------------+---------------------------------+-------------+
| **1. Formulation  | Bài toán    | Bài toán có giá | Bài toán có tính đột phá/nghiên | **20%**     |
| & Complexity**    | thiếu thực  | trị ứng dụng.   | cứu cao. Kiến trúc thu thập     |             |
|                   | tế hoặc quá | Khai thác dữ    | tinh vi, đối mặt với dữ liệu đa |             |
| *(Định hình bài   | đơn giản.   | liệu từ các     | phương thức (Multi-modal) hoặc  |             |
| toán & Độ phức    | Dữ liệu     | nguồn thực tế   | cấu trúc lồng ghép phức tạp. Hệ |             |
| tạp của dữ liệu)* | tĩnh, có    | (APIs, Web,     | thống Ontology gán nhãn bao     |             |
|                   | cấu trúc    | DBs). Đối với   | quát cả các \"edge-cases\"      |             |
|                   | phẳng, ít   | gán nhãn: Có    | (ngoại lệ khó).                 |             |
|                   | dị biệt.    | Ontology nhưng  |                                 |             |
|                   | Khối lượng  | chỉ giải quyết  |                                 |             |
|                   | hoặc độ     | các trường hợp  |                                 |             |
|                   | phức tạp    | (cases) cơ bản. |                                 |             |
|                   | không phản  |                 |                                 |             |
|                   | ánh được    |                 |                                 |             |
|                   | thách thức  |                 |                                 |             |
|                   | thực tiễn.  |                 |                                 |             |
|                   | Nguồn gốc   |                 |                                 |             |
|                   | dữ liệu     |                 |                                 |             |
|                   | không rõ    |                 |                                 |             |
|                   | ràng.       |                 |                                 |             |
+-------------------+-------------+-----------------+---------------------------------+-------------+
| **2.              | Xử lý dữ    | Phân tích được  | **\[Yêu cầu tuyệt đối: ZERO     | **30%**     |
| Pre-processing &  | liệu mang   | bản chất của dữ | DATA LEAKAGE\]**. Xử lý tối ưu  |             |
| Methodological    | tính cơ     | liệu (phân      | các bài toán khó (Imbalance,    |             |
| Rigor**           | học, mù     | phối, loại      | Missingness) bằng các thuật     |             |
|                   | quáng       | biến) để đưa ra | toán SOTA. Luận giải sâu sắc sự |             |
| *(Phương pháp     | (naive). Áp | quyết định xử   | tác động của việc tiền xử lý    |             |
| luận Tiền xử lý & | dụng thuật  | lý phù hợp.     | lên tính toàn vẹn của mô hình   |             |
| Làm sạch)*        | toán mà     | Phương pháp nội | thống kê phía sau.              |             |
|                   | không kiểm  | suy, mã hóa     |                                 |             |
|                   | tra giả     | (encoding) hoặc |                                 |             |
|                   | định phân   | chuẩn hóa       |                                 |             |
|                   | phối của dữ | (scaling) tuân  |                                 |             |
|                   | liệu. Bỏ    | thủ đúng nguyên |                                 |             |
|                   | qua hoặc    | lý toán học cơ  |                                 |             |
|                   | xóa bỏ dị   | bản.            |                                 |             |
|                   | biệt/khuyết |                 |                                 |             |
|                   | thiếu mà    |                 |                                 |             |
|                   | không có cơ |                 |                                 |             |
|                   | sở toán     |                 |                                 |             |
|                   | học/nghiệp  |                 |                                 |             |
|                   | vụ.         |                 |                                 |             |
+-------------------+-------------+-----------------+---------------------------------+-------------+
| **3. Exploratory  | Trực quan   | Phân tích tương | Biểu đồ đạt chuẩn xuất bản học  | **20%**     |
| Data Analysis     | hóa hời     | quan đa chiều   | thuật (Publication-ready). Data |             |
| (EDA)**           | hợt, chỉ    | (Multivariate). | Storytelling xuất sắc, dẫn dắt  |             |
|                   | dừng ở mức  | Biểu diễn được  | người đọc từ dữ liệu thô đến    |             |
| *(Khai phá & Kể   | độ thống kê | cấu trúc ẩn của | những kết luận (Insights) mang  |             |
| chuyện qua dữ     | mô tả đơn   | dữ liệu. Các đồ | tính phản biện hoặc giá trị     |             |
| liệu)*            | biến cơ     | thị được lựa    | cao. Thực hiện Feature          |             |
|                   | bản. Đồ thị | chọn đúng mục   | Engineering bậc cao.            |             |
|                   | không cung  | đích và có diễn |                                 |             |
|                   | cấp thêm    | giải logic      |                                 |             |
|                   | bất kỳ tri  | nghiệp vụ rõ    |                                 |             |
|                   | thức        | ràng.           |                                 |             |
|                   | (Insight)   |                 |                                 |             |
|                   | nào có giá  |                 |                                 |             |
|                   | trị.        |                 |                                 |             |
+-------------------+-------------+-----------------+---------------------------------+-------------+
| **4. Engineering  | Mã nguồn    | Mã nguồn sạch   | Kiến trúc mã nguồn được mô-đun  | **15%**     |
| &                 | hỗn độn,    | (Clean code),   | hóa cao                         |             |
| Reproducibility** | chạy sinh   | áp dụng quy     | (Modularization/OOP/Pipelines). |             |
|                   | lỗi         | chuẩn đặt tên.  | Tích hợp các hàm kiểm thử dữ    |             |
| *(Chuẩn mực Kỹ    | (crash).    | Chạy mượt mà từ | liệu (Data Assertions/Sanity    |             |
| thuật & Khả năng  | Phụ thuộc   | đầu đến cuối    | Checks) để tự động phát hiện    |             |
| tái lập)*         | vào môi     | (End-to-End).   | lỗi. Quản lý phiên bản (Version |             |
|                   | trường máy  | Quản lý thư     | control) chuyên nghiệp.         |             |
|                   | tính cá     | viện phụ thuộc  |                                 |             |
|                   | nhân. Có sự | (requirements)  |                                 |             |
|                   | can thiệp   | đầy đủ.         |                                 |             |
|                   | thủ công    |                 |                                 |             |
|                   | (chỉnh sửa  |                 |                                 |             |
|                   | bằng tay)   |                 |                                 |             |
|                   | vào dữ liệu |                 |                                 |             |
|                   | thô.        |                 |                                 |             |
+-------------------+-------------+-----------------+---------------------------------+-------------+
| **5. Scientific   | Báo cáo sai | Tuân thủ nghiêm | Báo cáo đạt chất lượng của một  | **15%**     |
| Reporting &       | định dạng,  | ngặt định dạng  | hội nghị khoa học. Phần         |             |
| Ethics**          | văn phong   | IEEE/ACM. Trình | \"Datasheets for Datasets\" thể |             |
|                   | lủng củng.  | bày logic, văn  | hiện tư duy phản biện xuất sắc: |             |
| *(Báo cáo Khoa    | Thiếu sự    | phong học thuật | Tự đánh giá trung thực về các   |             |
| học & Đạo đức     | luận giải,  | khách quan. Có  | Bias (Thiên lệch), rủi ro đạo   |             |
| AI)*              | chỉ tập     | tài liệu Code   | đức và giới hạn của bộ dữ liệu  |             |
|                   | trung mô tả | Book / Data     | do mình tạo ra.                 |             |
|                   | \"Đã code   | Dictionary rõ   |                                 |             |
|                   | gì\" thay   | ràng.           |                                 |             |
|                   | vì \"Vì sao |                 |                                 |             |
|                   | làm vậy\".  |                 |                                 |             |
+===================+=============+=================+=================================+=============+

## PHẦN 4: RED FLAGS (CÁC **VI PHẠM KỶ LUẬT NGHIÊM TRỌNG)**

Bất kỳ đồ án nào vi phạm 1 trong 3 nguyên tắc nền tảng sau đây của Khoa
học Dữ liệu sẽ bị **đánh rớt (Điểm F)** hoặc trừ điểm kịch khung, bất kể
các phần khác làm tốt đến đâu:

1.  **Sự can thiệp thủ công (Manual Data Manipulation):**

    - *Hành vi:* Sửa lỗi chính tả, xóa dòng trống, hoặc điền dữ liệu
      trực tiếp bằng phần mềm bên ngoài (như Microsoft Excel) lên tập dữ
      liệu thô, sau đó mới nạp vào hệ thống.

    - *Nguyên lý vi phạm:* Phá hủy \"Tính tái lập\" (Reproducibility).
      Mọi biến đổi dữ liệu, dù là nhỏ nhất, phải được thực thi thông qua
      Mã nguồn (Code) để tạo thành một Pipeline tự động.

2.  **Rò rỉ dữ liệu (Data Leakage) trong Tiền xử lý:**

    - *Hành vi:* Tính toán các tham số phân phối (Mean, Max, Min,
      Variance\...) trên TOÀN BỘ tập dữ liệu để thực hiện Scaling hoặc
      Imputation trước khi tiến hành chia tập (Train/Test Split).

    - *Nguyên lý vi phạm:* Rò rỉ thông tin từ \"tương lai chưa biết\"
      (Tập Test) vào \"quá khứ\" (Tập Train), dẫn đến sai lệch hoàn toàn
      tính hợp lệ của mọi mô hình Machine Learning sau này.

3.  **Đạo văn và Vi phạm liêm chính học thuật (Plagiarism):**

    - *Hành vi:* Sao chép nguyên bản toàn bộ Data Pipeline hoặc Notebook
      EDA từ Kaggle/GitHub của người khác và nhận là của mình.

    - *Nguyên lý vi phạm:* Việc tham khảo các đoạn code giải quyết vấn
      đề cục bộ (như StackOverflow) được cho phép nếu có trích dẫn
      (Citation). Tuy nhiên, việc sao chép toàn bộ kiến trúc giải quyết
      bài toán là hành vi phi đạo đức học thuật.

## **PHẦN 5: KHÔNG GIAN SÁNG TẠO & ĐIỂM THƯỞNG (THE EXTRA MILE)**

*Triết lý:* Khung điểm 10.0 đại diện cho việc bạn hoàn thành xuất sắc
các yêu cầu trong Đề cương môn học. Tuy nhiên, Khoa học Dữ liệu là một
lĩnh vực phát triển vũ bão. Nếu bạn chủ động bước ra khỏi vùng an toàn,
áp dụng các kỹ thuật SOTA (State-of-the-Art) nằm ngoài giáo trình, những
nỗ lực đó sẽ được vinh danh bằng **Điểm Thưởng (Bonus Points)**.

*Cơ chế:* Điểm thưởng là điểm cộng thêm (Tối đa +1.5đ vào điểm tổng,
tổng điểm không vượt quá 10.0). Việc không tham gia phần này **hoàn toàn
không làm giảm điểm** của đồ án.

### **🌟 Bonus 1: Open Science** & Đóng góp Cộng đồng (+0.5đ)

Nếu bộ dữ liệu bạn xây dựng không vi phạm quyền riêng tư và bản quyền:

- Hãy đóng gói và công bố nó lên các nền tảng Khoa học Mở như **Kaggle
  Datasets**, **HuggingFace Datasets**, hoặc **Zenodo**. Điều này chứng
  minh dữ liệu của bạn thực sự có giá trị cho cộng đồng nghiên cứu toàn
  cầu.

### **🌟 Bonus 2: Ứng dụng Generative** AI / LLMs (+0.5đ đến +1.0đ)

Tích hợp sức mạnh của Mô hình Ngôn ngữ Lớn vào quá trình tiền xử lý:

- Sử dụng Prompt Engineering (via APIs) để chuẩn hóa dữ liệu phi cấu
  trúc phức tạp (Ví dụ: Dùng LLM bóc tách một câu đánh giá nhà hàng lộn
  xộn thành file JSON có cấu trúc rõ ràng về Món ăn, Giá cả, Phục vụ).

- Thực hiện Zero-shot/Few-shot Annotation bằng LLMs và đánh giá chéo
  (Cross-validate) với kết quả gán nhãn của con người.

### **🌟 Bonus 3: Systems Engineering & MLOps (+0.5đ đến +1.0đ)**

Nâng cấp đồ án từ \"Jupyter Notebook\" thành một \"Hệ thống\":

- Xây dựng giao diện tương tác (Interactive Dashboard) bằng
  **Streamlit** hoặc **Gradio** để Giảng viên có thể trực tiếp truy vấn,
  lọc dữ liệu và tương tác với các biểu đồ EDA của bạn.

- Đóng gói toàn bộ Data Pipeline bằng **Docker**, hoặc sử dụng các công
  cụ điều phối luồng dữ liệu chuyên nghiệp (Orchestrators) như **Apache
  Airflow** hay **Dagster**.
