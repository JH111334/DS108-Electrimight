# Hướng Dẫn Mở Rộng Sáng Tạo — DS108 Electrimight

> Tài liệu này liệt kê các hướng đi "Extra Mile" phù hợp với đồ án DS108.

---

## 1. Phân Tích Cơ Chế Khuyết (Missingness Mechanism)

Phù hợp Frame 3. Dataset không có missing values rõ ràng, nhưng Q_lead = 0 ở 67.38% có thể là implicit missingness.
- Thực hiện Little's MCAR Test hoặc giải thích MCAR/MAR/MNAR.
- Ảnh hưởng đến tính toán S và φ.

## 2. Kiểm Tra Zero Data Leakage

Yêu cầu tuyệt đối trong Rubric (30%).
- Audit GAN scaler fit trên toàn bộ dữ liệu (giải thích trong báo cáo).
- Kiểm tra rolling window có dùng center=True không.
- Kiểm tra DWT window có look-ahead không.

## 3. Data Assertions & Sanity Checks

Thêm module `src/data_assertions.py`:
- assert_no_negative_usage
- assert_pf_in_range
- assert_temporal_sorted
- assert_anomaly_rate_below(threshold=0.10)

## 4. Đánh Giá Fidelity Cho GAN

Vượt ra ngoài PCA/t-SNE:
- Kolmogorov-Smirnov test từng feature.
- Wasserstein distance hoặc MMD.
- Correlation matrix difference (Frobenius norm).
- Downstream utility: Random Forest trên real vs synthetic.

## 5. Streamlit Dashboard (Bonus 3)

Ứng dụng tương tác cho phép:
- Tải lên CSV, chạy pipeline từng bước.
- Trực quan anomaly, so sánh real vs synthetic.

## 6. Datasheets for Datasets (Bắt Buộc)

Theo Gebru et al. (2021). Trả lời 50+ câu hỏi về:
- Motivation, Composition, Collection, Preprocessing, Uses, Distribution, Maintenance.

## 7. Feature Selection Định Lượng

- Mutual Information giữa features và anomaly labels.
- VIF để phát hiện đa cộng tuyến (S, φ, PF, P, Q).
- Feature importance từ tree-based model đơn giản.

## 8. So Sánh Với SMOTE Baseline

So sánh Real vs SMOTE vs GAN về:
- KS test fidelity.
- Correlation preservation.
- Kết luận GAN tốt hơn trong không gian vật lý.

## Checklist Sáng Tạo

| STT | Hướng đi | Độ khó | Giá trị |
|-----|---------|--------|---------|
| 1 | Missingness Analysis | TB | Cao |
| 2 | Leakage Audit | TB | Rất cao |
| 3 | Data Assertions | Dễ | Cao |
| 4 | GAN Fidelity Metrics | TB | Rất cao |
| 5 | Streamlit Dashboard | TB | Bonus |
| 6 | Datasheets | TB | Bắt buộc |
| 7 | Feature Selection | TB | Cao |
| 8 | SMOTE Baseline | Dễ | Cao |
