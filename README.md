# DS108-Electrimight

DS108-Electrimight là project tiền xử lý dữ liệu có thể tái lập cho bài toán
phân tích tiêu thụ điện công nghiệp. Project bắt đầu từ bộ dữ liệu công khai
UCI Steel Industry Energy Consumption, tích hợp dữ liệu thời tiết ngoại sinh,
xây dựng các nhóm đặc trưng miền thời gian, miền tần số và đặc trưng
physics-informed, sau đó tạo ra gold dataset có thể kiểm toán cho bài toán
forecasting và phân tích proxy anomaly.

Repository được tổ chức như một artefact hoàn chỉnh để giảng viên có thể đọc và
đánh giá: mã nguồn, notebook, metadata, kết quả kiểm định, hình minh họa,
Streamlit dashboard và Docker deployment được đặt cùng nhau với provenance rõ
ràng.

## Tóm tắt Project

Dataset cuối cùng `data/gold/steel_final.csv` gồm **35.040 quan sát** và
**69 cột** ở độ phân giải 15 phút trong năm 2018. Mỗi quan sát kết hợp số đo
điện năng, ngữ cảnh thời tiết, đặc trưng thời gian, đặc trưng Discrete Wavelet
Transform, đặc trưng power triangle và các proxy anomaly labels dựa trên luật.

Các artefact chính:

- **Gold dataset:** `data/gold/steel_final.csv`
- **Mẫu synthetic cho minority class:** `data/gold/steel_synthetic_gan.csv`
- **Dataset metadata:** `metadata/dataset/`
- **Pipeline và experiment summaries:** `metadata/pipeline/`
- **Presentation dashboard:** `streamlit_ui/app.py`
- **Nguồn báo cáo IEEE:** `references/report-guides/`

## Cấu trúc Repository

```text
DS108-Electrimight/
|-- data/
|   |-- bronze/              # Dữ liệu nguồn và provenance; xem như read-only
|   |-- silver/              # Dữ liệu trung gian sau làm sạch
|   `-- gold/                # Dataset phân tích cuối cùng
|-- metadata/
|   |-- dataset/             # Datasheet, codebook, feature catalog, label notes
|   `-- pipeline/            # Metrics, ablation results, validation summaries
|-- notebooks/               # Notebook EDA, feature engineering và modeling
|-- references/
|   |-- documents/           # Tài liệu hướng dẫn báo cáo và nguồn tham khảo
|   `-- report-guides/       # Nguồn LaTeX report và generated figures
|-- src/
|   |-- bronze/              # Load dữ liệu thô, quality audit, weather loading
|   |-- silver/              # Feature engineering và proxy labels
|   `-- gold/                # Pipeline end-to-end, figures, GAN, ablation
|-- streamlit_ui/            # Streamlit dashboard để demo project
|-- tests/                   # Pytest cho schema, labels và assertions
|-- docker-compose.yml       # Compose profiles cho Streamlit và Jupyter
`-- Dockerfile               # Containerized Streamlit app
```

## Data Lineage

Project dùng bố cục dữ liệu Bronze-Silver-Gold:

| Layer | Path | Vai trò |
|---|---|---|
| Bronze | `data/bronze/` | Dữ liệu thép gốc từ UCI và dữ liệu thời tiết đã tải. Lớp này được giữ làm bằng chứng nguồn. |
| Silver | `data/silver/steel_clean.csv` | Dữ liệu điện đã làm sạch sau khi parse timestamp, chuẩn hóa power factor và chạy data-quality checks. |
| Gold | `data/gold/steel_final.csv` | Dataset phân tích cuối cùng sau weather merge, feature engineering, proxy anomaly labeling và validation. |

Ngày trong CSV gốc được parse với `dayfirst=True` vì bộ dữ liệu thép dùng định
dạng `DD/MM/YYYY`.

## Methodology

Pipeline triển khai năm nhóm xử lý và feature engineering chính:

1. **Data quality audit:** kiểm tra tính liên tục của timestamp, bản ghi trùng,
   miền giá trị power factor, giá trị vật lý bất hợp lý và các biến có độ phân
   giải thấp.
2. **Weather integration:** tải dữ liệu thời tiết lịch sử tại Gwangyang,
   resample dữ liệu thời tiết từ 1 giờ xuống 15 phút và left join với bản ghi
   tiêu thụ điện của nhà máy.
3. **Time-domain features:** tạo lag features, rolling statistics và cyclical
   encodings cho hành vi tiêu thụ theo thời điểm trong ngày.
4. **Frequency-domain features:** áp dụng rolling DWT với wavelet Daubechies-4
   để nắm bắt các transient của tải điện mà thống kê rolling thông thường khó
   thể hiện rõ.
5. **Physics-informed features and labels:** xây dựng apparent power, reactive
   power summaries, phase-angle features và proxy anomaly labels theo luật cho
   idling, leakage/concept drift và local overload.

Các anomaly labels trong project là **proxy labels**. Chúng phù hợp cho benchmark
và đánh giá phương pháp, nhưng không được xem là fault labels đã xác nhận bởi
SCADA hoặc log bảo trì thực tế.

## Evidence Hiện tại

Các artefact hiện tại ghi nhận:

| Evidence | Giá trị |
|---|---:|
| Gold dataset shape | 35.040 rows x 69 columns |
| Any proxy anomaly | 2.388 rows |
| Any proxy anomaly rate | 6,815% |
| Best forecasting configuration | RAW + TIME |
| Best forecasting RMSE | 12,0087 |
| Best proxy anomaly PR-AUC configuration | RAW + TIME + WEATHER |
| Best proxy anomaly PR-AUC | 0,3642 |
| GAN mean error | 8,20% |
| GAN std error | 3,81% |
| GAN correlation MAE | 0,116 |
| Validation summary | 52 pytest tests passed |

Các giá trị này được tạo từ `metadata/pipeline/*.json` và
`metadata/pipeline/ablation_results.csv`.

## Reproducibility

Môi trường khuyến nghị:

- Python 3.12
- Windows PowerShell hoặc shell tương thích
- Dependencies trong `requirements.txt`

Cài đặt dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r streamlit_ui/requirements.txt
```

Chạy pipeline chính:

```powershell
python -m src.run_all
```

Chạy các kiểm tra quan trọng:

```powershell
python -m pytest
python -m src.gold.pipeline
python -m src.data_assertions
python -m src.leakage_audit
python -m src.missingness_analysis
```

Chỉ tải lại dữ liệu thời tiết live khi cần tái tạo weather source:

```powershell
python -m src.silver.weather
```

## Streamlit Demo

Chạy local:

```powershell
streamlit run streamlit_ui/app.py
```

Hoặc chạy bằng Docker:

```powershell
docker build -t ds108-electrimight .
docker run --rm -p 8501:8501 ds108-electrimight
```

Sau đó mở `http://localhost:8501`.

Chạy bằng Docker Compose:

```powershell
docker compose up streamlit
```

Sau đó mở `http://localhost:8505`.

Jupyter profile tùy chọn có thể chạy bằng:

```powershell
docker compose --profile full up
```

Jupyter Lab được expose tại `http://localhost:8888`.

Các lệnh Streamlit và Docker ở trên là entry point có thể tái lập để giảng viên
review app local hoặc kiểm tra deployment preparation.

## Chính sách Large Dataset

Các CSV hiện đang được track vẫn nằm trong giới hạn thông thường của GitHub. Tuy
nhiên, các dataset hoặc model artifact phát sinh trong tương lai không nên commit
trực tiếp nếu chúng tiệm cận ngưỡng large-file. Workflow chuyên nghiệp là:

- giữ code, metadata, notebook và sample file nhỏ trên GitHub;
- công bố full dataset trên Kaggle hoặc Zenodo khi dataset cần được chia sẻ rộng;
- dùng DVC hoặc Git LFS khi large artifacts cần gắn với workflow versioning của
  repository;
- ghi rõ mọi external dataset URL trong `metadata/dataset/DATASHEET.md`.

## License

Source code được phân phối theo license của repository. Bộ dữ liệu thép gốc vẫn
tuân theo điều khoản của UCI dataset. Metadata, feature definitions và project
documentation phái sinh được cung cấp cho mục đích đánh giá học thuật và tái lập
kết quả.
