# Overleaf Upload Guide — DS108 Electrimight IEEE Report

## Cách Upload lên Overleaf

1. **Zip toàn bộ thư mục** `references/report-guides/` (bao gồm `main.tex`, `sections/`, `figures/`).
2. Trên Overleaf, chọn **Upload > Upload from Computer > ZIP**.
3. Đặt **Main Document** là `main.tex`.
4. Compile bằng **pdfLaTeX** (hoặc XeLaTeX nếu gặp lỗi font T5).

## Cấu trúc File

```
report-guides/
├── main.tex                          # Orchestrator
├── sections/
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex            # Đã mở rộng: MCAR/MAR/MNAR, Algorithm
│   ├── 04_experimental_setup.tex     # Đã mở rộng: Missingness results
│   ├── 05_results.tex                # Đã mở rộng: 8 figures, discussion
│   ├── 06_conclusion.tex
│   ├── 07_acknowledgments_references.tex
│   ├── 08_appendix_a.tex             # Datasheet for Datasets
│   ├── 09_appendix_b.tex             # Data Codebook
│   └── 10_appendix_c.tex             # Test Results
└── figures/
    ├── fig01_time_series.png
    ├── fig02_correlation_heatmap.png
    ├── fig03_dwt_decomposition.png
    ├── fig04_s_phi_scatter.png
    ├── fig05_anomaly_timeline.png
    ├── fig06_missingness_pattern.png
    ├── fig07_physical_distribution.png
    └── fig08_feature_impact.png
```

## Lưu ý Quan trọng

- **Không** đổi tên thư mục `sections/` hoặc `figures/`.
- Các figure đã render sẵn ở DPI=300, sẵn sàng cho in ấn.
- Nếu cần thêm figure, lưu vào `figures/` và reference bằng `\includegraphics[width=\linewidth]{figures/ten_file.png}`.
