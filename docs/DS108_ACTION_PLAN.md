# DS108 Electrimight - Ke Hoach Hanh Dong Tiep Theo

## Tom Tat Phan Tich

Do an DS108 - Preprocessing & Constructing Dataset duoc danh gia tren 5 tieu chi voi trong so:
1. Formulation & Complexity (20%)
2. Pre-processing & Methodological Rigor (30%) - yeu cau ZERO DATA LEAKAGE
3. Exploratory Data Analysis (20%)
4. Engineering & Reproducibility (15%)
5. Scientific Reporting & Ethics (15%) - bat buoc Datasheets for Datasets

Du an hien tai da co pipeline 7 buoc, nhung con nhieu khoang trong can lap day de dat diem xuat sac va dam bao tinh sang tao.

---

## PHAN 1: BAO CAO IEEE (20 Trang Doi)

### Cac Muc Da Co Huong Dan
- Abstract, Introduction, Methodology, Results, Conclusion da co outline trong report-guides.

### Viec Can Lam Ngay

#### A. Viet Noi Dung Bao Cao
- [ ] Abstract (150-250 tu, 5 phan: Context -> Problem -> Method -> Results -> Significance)
- [ ] I. Introduction (khong qua 2 trang, 3-5 trich dan)
- [ ] II. Related Work + TABLE I: Comparison
- [ ] III. Methodology (day du 8 subsections A-H)
- [ ] IV. Dataset & Experimental Setup
- [ ] V. Results and Discussion (4-6 figures, 4-5 tables)
- [ ] VI. Conclusion (khong them thong tin moi)
- [ ] Appendix: Datasheets for Datasets (5-6 trang, bat buoc)

#### B. Tao Figures Publication-Ready
- [ ] Fig. 1: Pipeline Diagram (draw.io / TikZ)
- [ ] Fig. 2: Time-series with anomaly annotations
- [ ] Fig. 3: Correlation heatmap (40+ features)
- [ ] Fig. 4: DWT decomposition (db4, level 3)
- [ ] Fig. 5: S vs phi scatter by Load_Type
- [ ] Fig. 6: Anomaly timeline
- [ ] Fig. 7: PCA real vs synthetic
- [ ] Fig. 8: t-SNE real vs synthetic
- [ ] Fig. 9: GAN training curves
- [ ] Fig. 10: Distribution comparison (KDE)
- **Yeu cau ky thuat:** Do phan giai >= 300 DPI, font >= 8 pt, mau sac phu hop in den trang.

#### C. Tao Tables
- [ ] TABLE I: Comparison of Related Works
- [ ] TABLE II: DWT Features per Level
- [ ] TABLE III: Anomaly Labeling Rules
- [ ] TABLE IV: GAN Hyperparameters
- [ ] TABLE V: Descriptive Statistics (Raw)
- [ ] TABLE VI: Anomaly Distribution
- [ ] TABLE VII: Real vs Synthetic Statistical Comparison
- [ ] TABLE VIII: Comparative Raw vs Processed

#### D. Hoan Thien References
- [ ] Chon 15-20 references tu file 07_References_Bibliography.md
- [ ] Danh so lai theo thu tu xuat hien trong bai
- [ ] Dam bao dinh dang IEEE chuan

---

## PHAN 2: CODE & PIPELINE

### A. Kiem Tra & Khac Phuc Data Leakage (Uu Tien Cao Nhat)
- [ ] Audit toan bo pipeline: kiem tra rolling window co center=True khong
- [ ] Kiem tra DWT window co su dung future information khong
- [ ] Giai thich trong bao cao: vi sao scaler fit tren toan bo khong gay leakage cho downstream
- [ ] Them notebook 04_leakage_audit.ipynb

### B. Hoan Thien GAN Module
- [ ] Hien tai src/gan_augmentation.py la skeleton (NotImplementedError)
- [ ] Trien khai day du build_generator, build_discriminator, train_gan
- [ ] Them evaluation: KS test, Wasserstein distance, MMD
- [ ] So sanh voi SMOTE baseline

### C. Data Assertions & Sanity Checks
- [ ] Tao src/data_assertions.py
- [ ] assert_no_negative_usage
- [ ] assert_pf_in_range([0,1])
- [ ] assert_temporal_sorted
- [ ] assert_anomaly_rate_below(0.10)
- [ ] assert_feature_correlation_preserved(real, synthetic)
- [ ] Tich hop assertions vao pipeline sau moi buoc

### D. Tests & Reproducibility
- [ ] Viet unit tests cho cac ham chinh (pytest)
- [ ] Test data_loader, time_features, physical_features, anomaly_labels
- [ ] Tao run_pipeline_test.py
- [ ] Viet README.md chi tiet (huong dan A-Z)
- [ ] Dam bao requirements.txt day du (pip freeze)

### E. Missingness Mechanism Analysis (Sang Tao)
- [ ] Phan tich Q_lead = 0 (67.38%) nhu implicit missingness
- [ ] Giai thich MCAR/MAR/MNAR
- [ ] Anh huong den S va phi
- [ ] Them vao bao cao Methodology hoac Discussion

### F. Feature Selection Dinh Luong
- [ ] Tinh Mutual Information giua features va anomaly labels
- [ ] Tinh VIF cho physical features (phat hien da cong tuyen)
- [ ] Tree-based feature importance (Random Forest don gian)
- [ ] Them vao bao cao de bien luan giu/bo features

---

## PHAN 3: SANG TAO & BONUS

### Huong 1: Datasheets for Datasets (Bat Buoc, Khong Phai Bonus)
- [ ] Tra loi 50+ cau hoi theo chuan Gebru et al. 2021
- [ ] Cac nhom: Motivation, Composition, Collection, Preprocessing, Uses, Distribution, Maintenance
- [ ] File: docs/DATASHEETS_FOR_DATASETS.md (5-6 trang)

### Huong 2: Streamlit Dashboard (Bonus +0.5-1.0d)
- [ ] Ung dung tuong tac: upload CSV, chay pipeline, xem anomaly, so sanh real/synthetic
- [ ] File: app.py

### Huong 3: Cong Bo Kaggle (Bonus +0.5d)
- [ ] Dong goi steel_final.csv + metadata
- [ ] Viet Kaggle Kernel huong dan

### Huong 4: Docker Container (Bonus)
- [ ] Dockerfile cho toan bo pipeline
- [ ] docker-compose cho reproducibility

### Huong 5: LLM Integration (Bonus +0.5-1.0d)
- [ ] Dung LLM de generate explanation text cho anomaly labels
- [ ] Hoac dung LLM de standardize Data Dictionary

---

## PHAN 4: RED FLAGS CAN Kiem Tra

1. **Manual Data Manipulation:** Dam bao raw/ chi doc, khong sua bang tay.
2. **Data Leakage:** ZERO TOLERANCE. Moi buoc preprocessing phai co ly luan chong leakage.
3. **Plagiarism:** Code phai co trich dan neu tham khao. Pipeline la cua nhom.

---

## PHAN 5: Lich Trinh De Xuat

| Tuan | Cong Viec | Muc Tieu |
|------|-----------|----------|
| 1 | Hoan thien code (GAN, assertions, tests) | Pipeline chay end-to-end khong loi |
| 2 | Viet bao cao (Abstract -> Conclusion) | Du noi dung 15-18 trang |
| 3 | Tao figures/tables publication-ready | >= 10 figures, >= 8 tables |
| 4 | Leakage audit + Datasheets + Sang tao | Hoan thien rubric va bonus |
| 5 | Review, chinh sua, format IEEE | Final PDF + source files |

---

*Tai lieu nay duoc tao tu dong sau khi phan tich DS108 Final Project Capstone Guidelines va trang thai hien tai cua du an.*
