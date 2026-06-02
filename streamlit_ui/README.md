# DS108 Electrimight Streamlit UI

Dashboard phục vụ phần báo cáo capstone, tổng hợp các kết quả chính từ pipeline:

Problem → Gap → Evidence → Validation → Limits.

App đọc trực tiếp các artifact hiện có trong repo:

- `data/gold/steel_final.csv`
- `metadata/dataset/CODEBOOK.csv`
- `metadata/dataset/DATASHEET.md`
- `metadata/dataset/LABELING_GUIDELINE.md`
- `metadata/pipeline/pipeline_stats.json`
- `metadata/pipeline/gan_stats.json`
- `metadata/pipeline/ablation_results.csv`
- `metadata/pipeline/verification_summary.json`
- `references/report-guides/figures/*.png`

## Chạy app

Từ root repository:

```powershell
pip install -r streamlit_ui/requirements.txt
streamlit run streamlit_ui/app.py
```

## Tạo link demo

Để nộp link demo thay vì localhost, deploy app lên Streamlit Community Cloud:

1. Push repository lên GitHub.
2. Vào `https://share.streamlit.io` và chọn `Create app`.
3. Chọn repository, branch và entrypoint file: `streamlit_ui/app.py`.
4. Streamlit sẽ cài dependencies từ `streamlit_ui/requirements.txt`.
5. Sau khi deploy xong, dùng URL dạng `https://<subdomain>.streamlit.app` làm link demo.

Lưu ý: repo cần chứa các artifact mà app đọc trực tiếp, đặc biệt là `data/gold/steel_final.csv`, các file trong `metadata/dataset`, các file trong `metadata/pipeline` và các figure trong `references/report-guides/figures/`.

Layout mới cần có:

- `metadata/dataset/*` cho datasheet, codebook, labeling guideline và feature catalog.
- `metadata/pipeline/*` cho stats, ablation, verification, EDA decisions và insight report.

## Chạy bằng Docker

Docker phục vụ reproducibility, không thay thế link demo public.

```powershell
docker build -t ds108-electrimight .
docker run --rm -p 8501:8501 ds108-electrimight
```

Sau đó mở `http://localhost:8501`.

## Chạy toàn bộ pipeline

```powershell
python -m src.run_all
```

Nếu chỉ muốn tái tạo dataset và metadata nhanh, bỏ qua phần nặng:

```powershell
python -m src.run_all --skip-ablation --skip-figures --skip-insights
```

## Ghi chú thuyết trình

Xem `streamlit_ui/PRESENTATION_NOTES.md`.

Nếu thiếu artefact ablation hoặc GAN, app vẫn chạy phần tổng quan và hiển thị fallback cho các số liệu pitch deck quan trọng.
