# data/raw — CHỈ ĐỌC (Read-Only)

Thư mục này lưu trữ **duy nhất** tệp dữ liệu gốc:

```
data/raw/Steel_industry_data.csv
```

## ⚠️ Quy Tắc Bất Biến

> **TUYỆT ĐỐI KHÔNG** ghi, chỉnh sửa, hoặc xóa bất kỳ tệp nào trong thư mục này.

- Không có kịch bản (script), notebook, hay pipeline nào được phép **ghi đè** lên thư mục `data/raw/`.
- Mọi dữ liệu đã qua xử lý phải được lưu vào `data/processed/`.
- Quy tắc này đảm bảo **khả năng truy xuất nguồn gốc dữ liệu** (data provenance) và cho phép tái lập toàn bộ pipeline từ đầu bất kỳ lúc nào.

## Nguồn Dữ Liệu

`Steel_industry_data.csv` được lấy từ:
> [UCI Machine Learning Repository — Steel Industry Energy Consumption Dataset](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption)

Tải tệp và đặt vào thư mục này trước khi chạy pipeline.
