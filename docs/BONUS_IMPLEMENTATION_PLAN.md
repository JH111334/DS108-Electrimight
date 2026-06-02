# Bonus Implementation Plan - Streamlit Demo, Docker và LLM

Tài liệu này tách riêng các đề xuất bonus khỏi script thuyết trình chính. Mục tiêu là chọn hướng triển khai có lợi nhất cho đồ án DS108 Electrimight, một project thuộc nhóm tiền xử lý và xây dựng bộ dữ liệu, không phải hệ thống phát hiện lỗi vận hành real-time.

## Kết luận nhanh

Ưu tiên tốt nhất:

1. **Làm link demo Streamlit trước.** Đây là phần giảng viên có thể mở trực tiếp để xem sản phẩm, phù hợp nhất với yêu cầu nộp link demo.
2. **Làm Docker sau nếu còn thời gian.** Docker tăng điểm reproducibility, nhưng không thay thế demo link vì giảng viên vẫn phải build/run local.
3. **Không thêm LLM labeling làm chức năng chính.** Với project này, LLM dễ làm mờ tính kiểm toán của proxy labels. Nếu dùng LLM, chỉ dùng phụ trợ cho text explanation hoặc data dictionary.

Nói ngắn gọn: **nên làm cả link demo và Docker nếu kịp**, nhưng nếu phải chọn một thì chọn **link demo Streamlit**.

## Cơ sở tham khảo

- Streamlit Community Cloud cho phép deploy app từ GitHub bằng cách chọn repository, branch và entrypoint file; app có URL chia sẻ dạng `*.streamlit.app` sau khi deploy [Streamlit Deploy Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
- Streamlit Community Cloud chạy app từ root repository, cần khai báo dependencies và đưa các file app cần đọc vào repo; entrypoint có thể nằm trong subfolder như `streamlit_ui/app.py` [Streamlit File Organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization).
- Hugging Face Spaces cũng hỗ trợ Streamlit app và hoạt động như Git repository, phù hợp làm phương án dự phòng nếu Streamlit Cloud gặp giới hạn [Hugging Face Spaces Streamlit](https://huggingface.co/docs/hub/main/spaces-sdks-streamlit).
- Docker best practices khuyến nghị build image theo hướng nhỏ gọn, reproducible, có tag, và có thể tích hợp CI để build/test image [Docker Build Best Practices](https://docs.docker.com/build/building/best-practices/).

## Đánh giá Streamlit UI hiện tại

UI hiện tại đã đúng hướng cho một project data-building:

- Có dashboard tóm tắt gold dataset, weather, proxy anomaly và kiểm thử.
- Có phần giải thích pipeline: raw meter logs, weather resampling, feature groups và proxy labels.
- Có biểu đồ dữ liệu và ablation để chứng minh `RAW + TIME` tốt nhất cho forecasting và `RAW + TIME + WEATHER` tốt nhất cho proxy risk prediction.
- Có tab giới hạn, nhấn mạnh đây là offline benchmark, không phải hệ thống phát hiện lỗi thật.
- Số liệu chính đọc từ artifact project: `data/gold/steel_final.csv`, `metadata/pipeline/pipeline_stats.json`, `metadata/pipeline/gan_stats.json`, `metadata/pipeline/ablation_results.csv`, `metadata/pipeline/verification_summary.json`.

Điểm mạnh: UI đã phục vụ tốt phần demo kết quả và insight.

Điểm còn thiếu: UI chưa đủ mạnh ở vai trò **demo một sản phẩm dataset**. Người xem thấy chart và metric, nhưng chưa có cách tải/xem trực tiếp các artifact quan trọng như codebook, datasheet, ablation table đầy đủ hoặc sample của gold dataset.

## Nên thêm gì vào Streamlit UI

Các phần nên thêm, theo thứ tự ưu tiên:

1. **Artifact download panel**

   Thêm một panel hoặc tab nhỏ tên `Tải artifact` với các nút download:

   - `data/gold/steel_final.csv`
   - `metadata/dataset/CODEBOOK.csv` nếu có
   - `metadata/dataset/DATASHEET.md`
   - `metadata/pipeline/ablation_results.csv`
   - `metadata/pipeline/project_insights.md`
   - `metadata/pipeline/verification_summary.json`

   Lý do: với đồ án tiền xử lý và xây dựng dataset, sản phẩm chính là dataset và metadata. Cho phép giảng viên tải artifact sẽ làm demo thuyết phục hơn.

2. **Pipeline lineage rõ hơn**

   Thêm một sơ đồ hoặc bảng ngắn:

   `Bronze electricity 35.040 x 11` -> `Weather 8.760 hourly` -> `Resampled weather 35.040` -> `Merged silver` -> `Gold 35.040 x 64`.

   Lý do: phần resampling/merge là điểm kỹ thuật quan trọng của project. UI nên làm nổi bật việc giữ row alignment và timestamp semantics.

3. **Feature catalog mini table**

   Thêm bảng nhóm feature:

   | Nhóm | Cách tạo | Vai trò | Insight ablation |
   | --- | --- | --- | --- |
   | Time | lag, rolling, sin/cos | chu kỳ và lịch sử tải | RMSE thấp nhất |
   | Weather | hourly -> 15m, heat index | ngữ cảnh ngoại sinh | PR-AUC cao nhất khi kết hợp time |
   | Wavelet | DWT db4-L3, window 64 | xu hướng và spike đa tỉ lệ | phân tích tín hiệu |
   | Physical | `S`, `Q_net`, `phi` | diễn giải điện học | nền tảng proxy rules |

   Lý do: giúp người xem không chuyên code vẫn hiểu feature được tạo ra thế nào và dùng để làm gì.

4. **Ablation table đầy đủ**

   Hiện UI có bar chart cho RMSE và PR-AUC. Nên thêm expander `Bảng ablation đầy đủ` để hiển thị tất cả config từ `metadata/pipeline/ablation_results.csv`, gồm:

   - forecast RMSE/MAE/R2
   - proxy PR-AUC/F1/ROC-AUC
   - rule-free track

   Lý do: người chấm có thể kiểm tra claim "cao nhất/thấp nhất" ngay trong UI, không cần mở CSV.

5. **Quality and leakage checklist**

   Thêm checklist nhỏ:

   - 35.040 dòng sau merge
   - 64 cột gold
   - 0 missing ở core columns
   - weather không back-fill
   - rolling `center=False`
   - pytest `50 passed`
   - leakage audit pass nếu có artifact log

   Lý do: rubric DS108 đặt nặng methodological rigor và zero leakage.

## Không nên thêm gì vào UI

Không nên thêm các chức năng sau nếu thời gian hạn chế:

- Upload CSV rồi chạy lại pipeline trực tiếp trong UI. Việc này dễ lỗi, nặng, và làm UI lệch khỏi demo artifact đã kiểm thử.
- Train model trong UI. Demo nên đọc kết quả đã sinh từ code project, không chạy training mới để tránh chậm và không tái lập.
- LLM chatbot hoặc LLM gán nhãn anomaly. Chức năng này dễ bị hỏi về hallucination, ground truth và tính kiểm toán.
- Claim kiểu "phát hiện lỗi thật", "đảm bảo an toàn", "tự động ra quyết định". UI chỉ nên nói "proxy risk", "sàng lọc", "xếp hạng rủi ro ứng viên", "hỗ trợ quyết định".

## Link demo vs Docker

### Link demo Streamlit

Mục tiêu: giảng viên mở link và xem ngay.

Ưu điểm:

- Phù hợp trực tiếp với yêu cầu nộp link demo.
- Không cần cài Python, không cần build Docker.
- Dễ dùng trong buổi chấm và Q&A.
- Có thể cập nhật nhanh bằng GitHub push.

Nhược điểm:

- Phụ thuộc hosting.
- Repo cần chứa artifact hoặc dùng Git LFS nếu file lớn.
- Nếu repo private, cần cấu hình quyền truy cập hoặc public tạm thời.

Kết luận: **bắt buộc nên làm nếu muốn có demo thuyết phục**.

### Docker

Mục tiêu: người chấm hoặc người dùng kỹ thuật có thể tái lập môi trường chạy pipeline/UI.

Ưu điểm:

- Tăng điểm reproducibility.
- Giảm lỗi "máy em chạy được, máy thầy không chạy".
- Phù hợp rubric Engineering & Reproducibility.
- Có thể chạy được cả `pytest`, `src.project_insights` và Streamlit.

Nhược điểm:

- Không phải link demo công khai nếu chỉ nộp Dockerfile.
- Người chấm phải cài Docker và build image.
- Nếu làm vội, Dockerfile có thể trở thành phần thừa, chưa chứng minh thêm insight khoa học.

Kết luận: **nên làm sau Streamlit demo link**, không nên thay thế link demo bằng Docker.

## Phương án tốt nhất

Làm cả hai theo mức tối thiểu nhưng chắc:

1. Deploy Streamlit UI lên Streamlit Community Cloud.
2. Thêm Dockerfile để chạy local reproducible.
3. Trong README ghi rõ:

   - Demo online: `https://...streamlit.app`
   - Chạy local: `streamlit run streamlit_ui/app.py`
   - Chạy Docker: `docker build -t electrimight .` và `docker run -p 8501:8501 electrimight`

Cách này cho thấy project vừa có **demo dễ xem**, vừa có **khả năng tái lập kỹ thuật**.

## Docker triển khai thế nào là đủ

Dockerfile tối thiểu nên làm:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY streamlit_ui/requirements.txt streamlit_ui/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r streamlit_ui/requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

Nên thêm `.dockerignore`:

```text
.git
__pycache__/
.pytest_cache/
.venv/
*.pyc
notebooks/.ipynb_checkpoints/
```

Nếu muốn Docker phục vụ kiểm chứng tốt hơn, thêm README command:

```powershell
docker build -t ds108-electrimight .
docker run --rm -p 8501:8501 ds108-electrimight
docker run --rm ds108-electrimight python -m pytest
```

## LLM có nên dùng không?

Không nên dùng LLM để gán nhãn anomaly chính.

Lý do:

- Project đang có proxy labels dựa trên rule vật lý, confidence score và explanation. Đây là điểm mạnh vì kiểm toán được.
- LLM không có ground-truth SCADA/maintenance labels nên không thể xác nhận lỗi thật.
- Nếu để LLM gán nhãn, giảng viên có thể hỏi: LLM dựa vào chuẩn nào, hallucination kiểm soát ra sao, vì sao đáng tin hơn rule vật lý?
- LLM labeling có thể làm project bị xem là "quằng" thêm chức năng, trong khi insight chính đang nằm ở data engineering và ablation.

Nếu muốn dùng LLM như bonus nhẹ, chỉ nên dùng ở ba chỗ:

1. Sinh câu giải thích dễ hiểu từ `anomaly_explanation` đã có rule.
2. Chuẩn hóa mô tả cột trong codebook/data dictionary.
3. Tạo Q&A assistant đọc tài liệu project, nhưng phải ghi rõ là trợ lý tra cứu tài liệu, không gán nhãn và không ra quyết định kỹ thuật.

Kết luận: **LLM không phải hướng tăng điểm chính cho đồ án này**.

## Checklist triển khai bonus tốt nhất

### Bước 1: Làm demo link

- [ ] Đẩy repo lên GitHub.
- [ ] Đảm bảo repo có `streamlit_ui/app.py`, `streamlit_ui/requirements.txt` và các artifact UI đọc.
- [ ] Deploy trên Streamlit Community Cloud với entrypoint `streamlit_ui/app.py`.
- [ ] Kiểm tra app load đủ 4 tab.
- [ ] Ghi link vào README và file nộp sản phẩm.

### Bước 2: Nâng cấp UI đúng trọng tâm dataset

- [ ] Thêm download buttons cho gold dataset, datasheet, codebook, ablation CSV.
- [ ] Thêm pipeline lineage 35.040 x 11 -> weather 8.760 -> gold 35.040 x 64.
- [ ] Thêm feature catalog mini table.
- [ ] Thêm ablation table đầy đủ trong expander.
- [ ] Thêm quality/leakage checklist.

### Bước 3: Docker sau khi demo ổn

- [ ] Thêm `Dockerfile`.
- [ ] Thêm `.dockerignore`.
- [ ] Test `docker build`.
- [ ] Test `docker run -p 8501:8501`.
- [ ] Ghi commands vào README.

### Bước 4: Không mở rộng LLM labeling

- [ ] Không thêm LLM vào core pipeline.
- [ ] Nếu dùng LLM, chỉ dùng cho documentation/explanation phụ trợ.
- [ ] Không claim LLM phát hiện rủi ro hoặc tạo ground truth.

## Câu trả lời ngắn khi bị hỏi

Nếu giảng viên hỏi vì sao có demo link mà vẫn cần Docker:

> Demo link giúp thầy/cô xem sản phẩm ngay trên trình duyệt. Docker phục vụ reproducibility: người dùng kỹ thuật có thể chạy lại app, tests và pipeline trong môi trường cố định. Hai phần bổ sung nhau, nhưng demo link là ưu tiên trước vì phù hợp yêu cầu nộp sản phẩm.

Nếu giảng viên hỏi vì sao không dùng LLM gán nhãn:

> Vì project đang nhấn mạnh proxy labels có rule vật lý và có thể kiểm toán. LLM không có ground-truth SCADA/maintenance nên nếu dùng để gán nhãn lỗi sẽ làm giảm tính minh bạch. Nhóm chỉ xem LLM, nếu có, là công cụ hỗ trợ diễn giải hoặc documentation, không phải nguồn nhãn chính.
