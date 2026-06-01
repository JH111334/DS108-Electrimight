# Proxy Labeling Guideline for Steel Energy Anomaly Signals

**Phiên bản:** 2.5
**Ngày cập nhật:** 2026-06-01
**Phạm vi áp dụng:** Phân tích offline, Kỹ thuật đặc trưng, và Baseline Weak Supervision.

---

## Changelog

### v2.4 → v2.5

| # | Mục | Thay đổi |
| :--- | :--- | :--- |
| I1 | Toàn bộ | Thay `Apparent_Power` → `Apparent_Power_S` khi tham chiếu cột dữ liệu thực tế (đồng bộ với codebook). |
| I2 | Toàn bộ | Thay `PF_abs` phái sinh → `PF_rule = Lagging_Current_Power_Factor / 100` làm nguồn PF chính trong rule. `PF_abs`, `PF_signed`, `Reactive_Power_Ratio`, `Power_Factor_Volatility` chuyển về trạng thái internal/diagnostic trừ khi được materialize. |
| I3 | Mục 3 | Tách bảng Input Features thành A. Persistent columns (dùng trực tiếp) và B. Internal quantities (tính toán nội bộ). Không ám chỉ internal quantities là cột dataframe. |
| I4 | Mục 6 | Cập nhật định nghĩa rule: Overload dùng `Apparent_Power_S` và `(Lagging_Current_Power_Factor / 100)`; Idling thêm diễn giải idle-waste; Leakage_Drift thể hiện đầy đủ OR condition với PF/reactive nội bộ. |
| I5 | Mục 6.3 | Implementation đã đồng bộ hoàn toàn với guideline, bao gồm Apparent_Power_S, PF_rule, context-aware baselines, duration post-processing, priority resolution và 9 canonical label columns. |
| I6 | Mục 9 | Chuyển Confidence Scoring từ required output → "Optional / Future Extension". Hiện confidence_score không được materialize trong Gold table. |
| I7 | Mục 10 | Cấu trúc lại Output Schema: A. Current Gold persistent label columns; B. Optional diagnostic / future columns; C. Event-level aggregation schema. |
| I8 | Mục 1, 13 | Giữ nguyên safe/unsafe uses, củng cố từ khóa: weak/proxy labels, energy inefficiency drift, idle-waste behavior, high-stress proxy signal. |
| I9 | Mục 3 | `Hour` được suy ra từ NSM/date bên trong labeling functions; không cần được materialize thành cột persistent trong Gold table. |
| I10 | Mục 7, toàn bộ | Cập nhật số liệu nhãn cuối cùng: Idling 204 (0.582%), Leakage 3,444 (9.829%), Overload 3 (0.009%), anomaly_any 3,651 (10.420%). |
| I11 | Mục 10.1 | Làm rõ `baseline_warning` là audit flag, không phải lỗi dữ liệu hoặc cờ loại trừ. |

### v2.3 → v2.4

| # | Mục | Thay đổi |
| :--- | :--- | :--- |
| H1 | Mục 2.2 | Thay "Nghiêm cấm global threshold" bằng phân biệt rõ: cấm ngưỡng toàn cục cho biến phụ thuộc ngữ cảnh (`Usage_kWh`, `Apparent_Power`); cho phép ngưỡng domain-inspired cố định (`PF`) với yêu cầu ghi rõ lý do. |
| H2 | Mục 9 — Idling | Sửa lỗi điện học: "hơn 50% công suất biểu kiến là phản kháng" → diễn giải chính xác về tam giác công suất (PF = P/S; Q/S = √(1−PF²)). |
| H3 | Mục 3 | Thêm ghi chú phân biệt `PF_abs` phái sinh (tính từ `Usage_kWh`/`Q_net`) với `Lagging_Current_Power_Factor` gốc của dataset. Cảnh báo không trộn lẫn hai nguồn trong cùng một rule. |
| H4 | Mục 7 | Đổi "Phân rã mong đợi" → **"Phân rã tham chiếu quan sát được"** để tránh hiểu nhầm đây là target bắt buộc. |
| H5 | Mục 12.2 | Sửa câu Idling/WeekStatus check: từ logic ngược → "không tập trung bất thường vào một nhóm `WeekStatus` nếu không có lý do từ rule hoặc dữ liệu". |
| H6 | Mục 12.6 | Đổi MI < 0.01 hard threshold → soft: báo cáo giá trị + giải thích nếu cao, vì Idling bắt buộc Light\_Load và Overload bias Maximum\_Load nên MI thấp là không thực tế. |

### v2.2 → v2.3

| # | Mục | Thay đổi |
| :--- | :--- | :--- |
| G1 | Mục 1 | Rewrite mục tiêu downstream: phân tách rõ **safe uses** (post-hoc analysis, ablation, sample weights trong thí nghiệm có kiểm soát) vs **unsafe uses** (feature trực tiếp cho load forecasting cùng timestamp). Loại bỏ câu dễ gây hiểu nhầm về "categorical features". |
| G2 | Mục 4 | Thêm alias `Suspected_Idle_Waste` và caption tiếng Anh tường minh: *"Idling = idle-waste behavior, not machine shutdown"*. Giải thích lý do giữ tên gốc. |
| G3 | Mục 10.3 | Sửa hard filter `PF_abs > 1.0`: thay bằng **clip + log warning** khi vượt ngưỡng nhỏ (tolerance = 1e-4). Chỉ exclude khi vi phạm nghiêm trọng (> 1.01). |
| G4 | Mục 10.3 | Hạ "Missing context ban đêm" từ **hard filter → warning flag** `night_simplified_baseline_warning`. Không tự động exclude; thêm cột cờ vào Output Schema. |
| G5 | Mục 9 | Sửa Leakage Drift confidence score: thêm `I(rolling_28d_increase ≥ 5%)` với trọng số **0.25** — điều kiện cốt lõi của nhãn phải xuất hiện trong score. Tái phân bổ các trọng số còn lại. |
| G6 | Mục 11 (mới) | Thêm **Implementation Order** — 9 bước thực thi có thứ tự dependency rõ ràng. |
| G7 | Mục 12 (mới) | Thêm **Validation Checklist** — danh sách báo cáo bắt buộc sau khi gán nhãn. |

### v2.1 → v2.2 (giữ nguyên để tham chiếu)

| # | Mục | Thay đổi |
| :--- | :--- | :--- |
| F1 | Mục 4 | Làm rõ "Leakage" là alias thống kê, không phải insulation leakage vật lý. |
| F2 | Mục 7 | Đổi hard assertion `< 10%` thành soft warning có thể cấu hình. |
| F3 | Mục 5.2 + 6.2 | Nâng Idling baseline lên context-aware với 3-tier fallback. |
| F4 | Mục 6.1 | Ghi rõ Overload là high-confidence subset (precision over recall). |
| F5 | Mục 10 | Thêm Output Schema đầy đủ (row-level, event-level, hard filters). |
| F+ | Mục 9 | Thêm lý do trọng số Idling confidence score. |

### v2.0 → v2.1 (giữ nguyên để tham chiếu)

| # | Mục | Thay đổi |
| :--- | :--- | :--- |
| 1 | Mục 4 | Đổi tên `Suspected_Inefficiency_Drift` → `Suspected_Leakage_Drift`. |
| 2 | Mục 6.1 | P99 → P99.5; OR → AND; `PF < P25_context` → `PF < 0.70`. |
| 3 | Mục 6.2 | Sửa hướng tiêu thụ Idling: `z_usage < −2.0` → `P > Median + PF < 0.50`. |
| 4 | Mục 7 | Thêm định nghĩa union `anomaly_any` và bảng phân rã. |

---

## 1. Mục đích và Phạm vi

Tài liệu này định nghĩa quy trình gán nhãn proxy cho các tín hiệu nghi ngờ bất thường trong dữ liệu tiêu thụ điện năng ngành thép. Do bộ dữ liệu công khai không bao gồm nhãn lỗi chính thức, cảnh báo SCADA, nhật ký bảo trì, trạng thái bật/tắt thiết bị hoặc ngưỡng định mức theo từng máy, các nhãn trong tài liệu này **không được xem là ground truth**.

> **[G1 — v2.3] Phân tách safe uses vs unsafe uses:**

**Sử dụng được phép (safe uses):**

- Phân tích hậu kiểm (post-hoc): phân bố nhãn theo thời gian, Load\_Type, giờ, mùa.
- Ablation study: đánh giá đóng góp tương đối của các nhóm đặc trưng theo nhãn proxy.
- Phân tầng lỗi dự báo (forecast error stratification): phân tích xem mô hình dự báo tải có sai lệch hệ thống trong các giai đoạn được gán nhãn bất thường không.
- Sample weights trong thí nghiệm có kiểm soát: tăng trọng số cho nhóm anomaly khi huấn luyện — **chỉ khi scaler và baseline được fit độc lập trên tập train**.
- Xây dựng benchmark weak supervision cho nghiên cứu dữ liệu năng lượng.
- Thí nghiệm weak-supervision có kiểm soát (controlled weak-supervision experiments).

**Không được phép (unsafe uses):**

- **Dùng `anomaly_any` hoặc `dominant_label` như feature đầu vào cho mô hình dự báo `Usage_kWh` cùng timestamp.** Nhãn được tạo từ `Usage_kWh`, `Apparent_Power_S`, và `Lagging_Current_Power_Factor` — dùng chúng làm feature sẽ gây circular leakage: mô hình học lại labeling rules thay vì học pattern thực.
- Dùng như cảnh báo vận hành thời gian thực hoặc kích hoạt ngắt mạch (real-time trip/SCADA decisions).
- Dùng làm bằng chứng chẩn đoán lỗi phần cứng không có xác nhận từ kỹ sư điện (confirmed equipment fault diagnosis).

**Lưu ý cốt lõi:** Các nhãn được diễn giải là các tín hiệu nghi ngờ (suspected anomaly signals), không sử dụng như bằng chứng chẩn đoán lỗi vật lý.

---

## 2. Nguyên tắc Chung

### 2.1. Proxy Label, không phải Confirmed Fault

Một điểm dữ liệu được gán nhãn bất thường chỉ mang ý nghĩa điểm đó vi phạm các ràng buộc thống kê và vật lý được định nghĩa trước. Ví dụ, `Suspected_Overload` không khẳng định thiết bị cháy/hỏng do quá tải, mà chỉ chỉ ra rằng tín hiệu tải biểu kiến đang tạo ra một mức *stress* điện năng cao bất thường so với bối cảnh tương ứng.

### 2.2. Gán nhãn theo Ngữ cảnh (Contextual Labeling)

**Không sử dụng ngưỡng toàn cục cho các biến phụ thuộc mạnh vào bối cảnh vận hành** như `Usage_kWh` hoặc `Apparent_Power_S`, do tính chất chu kỳ của tải công nghiệp. Các baseline thống kê cho những biến này phải được tính toán dựa trên các phân nhóm ngữ cảnh, ưu tiên theo thứ tự:

1. `Load_Type × Hour × WeekStatus`
2. `Hour × WeekStatus`
3. `Load_Type`

**Ngưỡng domain-inspired cố định** như `(Lagging_Current_Power_Factor / 100) < 0.50` hoặc `< 0.70` là ngoại lệ được phép — đây là cutoff xuất phát từ hiểu biết vật lý về hệ số công suất, không phải ngưỡng thống kê theo ngữ cảnh. Khi dùng ngưỡng loại này, phải ghi rõ lý do domain trong `label_reason` và trong guideline để đảm bảo tính kiểm toán.

### 2.3. Ưu tiên cấp độ Sự kiện (Event-level) cho hiện tượng kéo dài

Với tần suất lấy mẫu 15 phút, một điểm dị biệt đơn lẻ có thể chỉ là nhiễu (noise). Do đó, `Suspected_Idling` và `Suspected_Leakage_Drift` yêu cầu thời lượng duy trì tối thiểu 4 dòng liên tiếp (tương đương 1 giờ). Riêng `Suspected_Overload` được phép giữ ở mức dị biệt điểm (point anomaly) vì các gai (spike) dòng điện thường diễn ra chớp nhoáng.

> **Lưu ý triển khai:** Điều kiện "≥ 4 dòng liên tiếp" phải được enforce bằng một bước post-processing riêng biệt (ví dụ: rolling count hoặc groupby consecutive runs) sau khi các điều kiện điểm (point conditions) được tính xong. Không được giả định logic ngữ cảnh giờ tự động thỏa mãn yêu cầu thời lượng. Xem thứ tự triển khai ở Mục 11.

### 2.4. Tính Giải thích (Explainability)

Mỗi nhãn bất thường nên đi kèm trường `label_reason` trong Gold output hoặc audit log. Nếu chưa materialize thành cột persistent, pipeline phải lưu được điều kiện kích hoạt tương ứng trong log hoặc báo cáo kiểm toán. Không chấp nhận các nhãn được tạo ra từ mô hình hộp đen (black-box) mà không thể truy vết điều kiện kích hoạt.

### 2.5. Tiêu chuẩn Công nghiệp là Nguồn Cảm hứng

Các tiêu chuẩn (IEEE 519, IEC 61000, ISO 50001, IEEE C57.91) được sử dụng để xây dựng logic và công thức, nhưng **không** được xem là bài kiểm tra tuân thủ (compliance test) do thiếu hụt dữ liệu đo lường cấp thiết bị (asset-level).

---

## 3. Không gian Đặc trưng Đầu vào (Input Features)

Quy trình gán nhãn yêu cầu tập dữ liệu (lớp Silver/Gold) đã hoàn tất trích xuất các đặc trưng sau.

### A. Persistent Columns — dùng trực tiếp bởi rule

| Đặc trưng | Vai trò & Ý nghĩa |
| :--- | :--- |
| `Usage_kWh` | Mức tiêu thụ điện hữu ích (chu kỳ 15 phút). |
| `Apparent_Power_S` | Tải biểu kiến proxy (*apparent-load proxy*): √(P² + Q_net²) — định lượng tổng áp lực (stress) lên hệ thống điện. Tên cột được giữ trong dataset; không ám chỉ phép đo kVA tức thời. |
| `Lagging_Current_Power_Factor` | Hệ số công suất trễ đo trực tiếp từ đồng hồ điện (%); dùng để tính `PF_rule`. |
| `Load_Type` | Chế độ tải theo hợp đồng (Light\_Load / Medium\_Load / Maximum\_Load). |
| `Hour` | Giờ trong ngày ∈ [0, 23] — ngữ cảnh lịch trình vận hành. Được suy ra từ `NSM // 3600` hoặc `date.dt.hour` bên trong labeling functions; không cần được materialize thành cột persistent trong bảng Gold cuối cùng. |
| `WeekStatus` | Loại ngày: Weekday / Weekend — ngữ cảnh lịch trình vận hành. |

### B. Internal Quantities — tính toán nội bộ cho logic gán nhãn

Các đại lượng dưới đây được tính trong bộ nhớ khi thực thi rule. **Không ám chỉ chúng là cột dataframe cố định** trừ khi được materialize tường minh trong pipeline.

| Đại lượng nội bộ | Công thức / Mô tả | Dùng cho |
| :--- | :--- | :--- |
| `Q_net` | `Lagging_kVarh` − `Leading_kVarh` | Cơ sở tính `Apparent_Power_S` và `Reactive_Power_Ratio` |
| `PF_rule` | `Lagging_Current_Power_Factor / 100` | Nguồn PF chính cho tất cả rule (Overload, Idling, Leakage_Drift) |
| `PF_derived_abs` | `Usage_kWh / (Apparent_Power_S + ε)`, clip [0, 1] | Chỉ dùng nội bộ để audit hoặc đối chiếu với PF_rule; không trộn lẫn trong rule |
| `Power_Factor_Volatility` | Rolling std của `PF_rule` trên cửa sổ có thể cấu hình; mặc định 1 giờ nếu được triển khai | Leakage_Drift sub-condition (nội bộ) |
| `Reactive_Power_Ratio` | `Q_net / (Usage_kWh + ε)` | Leakage_Drift sub-condition (nội bộ) |
| `rolling_28d_Apparent_Power_S` | Rolling mean 28 ngày của `Apparent_Power_S` | Leakage_Drift: kiểm tra xu hướng tải biểu kiến |

> **Công thức cốt lõi:**
>
> - `Q_net` = `Lagging_kVarh` − `Leading_kVarh`
> - `Apparent_Power_S` = √(`Usage_kWh`² + `Q_net`²)
> - `PF_rule` = `Lagging_Current_Power_Factor` / 100
>
> **Lưu ý về nguồn PF:** `PF_rule` dùng `Lagging_Current_Power_Factor` gốc từ dataset (đo trực tiếp từ đồng hồ điện), không phải `PF_derived_abs` tính lại từ tam giác công suất. Hai giá trị có thể không đồng nhất do sai số đo và làm tròn. Không trộn lẫn hai nguồn PF trong cùng một rule.

---

## 4. Phân loại Nhãn (Label Taxonomy)

Bộ nhãn cuối cùng bao gồm 4 nhóm.

> **[F1 — v2.2] Làm rõ thuật ngữ "Leakage":**
> Tên `Suspected_Leakage_Drift` sử dụng "Leakage" theo nghĩa **thống kê** — chỉ sự rò rỉ năng lượng sang dạng tổn hao nhiệt hoặc công suất phản kháng không cần thiết (energy inefficiency drift), **không phải** rò rỉ dòng điện vật lý qua cách điện bị hỏng (insulation leakage current).
> - *Insulation leakage (vật lý):* đòi hỏi đo bằng megohmmeter hoặc cảm biến dòng rò chuyên dụng — nằm ngoài phạm vi dữ liệu công tơ 15 phút.
> - *Energy inefficiency drift (thống kê):* được phát hiện qua PF thấp kéo dài, biến động PF cao, và xu hướng tải biểu kiến tăng dần — đây là điều guideline này đo lường.
>
> **Bất kỳ diễn giải nào liên kết nhãn này với lỗi cách điện vật lý đều là không chính xác.**

> **[G2 — v2.3] Idling alias và caption tường minh:**
> Tên chính thức trong pipeline và bài báo là **`Suspected_Idling`**. Alias kỹ thuật là **`Suspected_Idle_Waste`** — phản ánh chính xác hơn hành vi được đo: tiêu thụ điện không sinh công hữu ích, không phải ngừng hoạt động.
>
> *Caption chuẩn (dùng trong bảng kết quả và thuyết minh):*
> **"In this guideline, Idling refers to idle-waste behavior: non-negligible consumption under Light\_Load with poor power factor (PF_rule < 0.50), not machine shutdown or unexpected production halt."**
>
> Tên `Suspected_Idling` được giữ vì đã xuất hiện trong paper (Table III, IV, Results). Thay đổi tên ở giai đoạn này sẽ gây mâu thuẫn với manuscript đã nộp.

| Nhãn (Label) | Alias kỹ thuật | Diễn giải |
| :--- | :--- | :--- |
| **Normal** | — | Hoạt động bình thường, không vi phạm quy tắc dị biệt nào. |
| **Suspected_Idling** | `Suspected_Idle_Waste` | *Idle-waste behavior:* Tải thực tế cao hơn median context nhưng `PF_rule` < 0.50 trong trạng thái Light\_Load — năng lượng bị tiêu tán dưới dạng công suất phản kháng, không phải ngừng máy. |
| **Suspected_Overload** | — | *High-stress proxy signal:* `Apparent_Power_S` đạt cực trị (> P99.5) *đồng thời* `PF_rule` thấp (< 0.70) — high-confidence subset, recall thấp có chủ ý. |
| **Suspected_Leakage_Drift** | `Suspected_Inefficiency_Drift` *(v2.0 name)* | *Energy inefficiency drift* (không phải rò rỉ điện vật lý): PF thấp, biến động PF cao, hoặc mất cân bằng phản kháng kéo dài kèm xu hướng `Apparent_Power_S` tăng dần so với baseline 4 tuần. |

---

## 5. Xây dựng Baseline Ngữ cảnh (Context Baseline)

### 5.1. Z-score theo Ngữ cảnh cho Công suất tác dụng

$$z\_{usage} = \frac{\text{Usage\_kWh} - \text{median}(\text{Usage\_kWh} \mid \text{Context})}{\text{std}(\text{Usage\_kWh} \mid \text{Context})}$$

- **Context ưu tiên:** `Load_Type × Hour × WeekStatus`.
- **Fallback:** Nếu kích thước nhóm quá nhỏ (n < 10) hoặc std = 0, lùi về `Hour × WeekStatus`. Nếu vẫn không tính được, gán std = 1 và bật cờ `baseline_warning = True`.

### 5.2. Phân vị (Percentiles) theo Ngữ cảnh

| Phân vị | Grouping | Dùng cho |
| :--- | :--- | :--- |
| **P99.5**(`Apparent_Power_S`) | `Load_Type × Hour × WeekStatus` | Overload — Condition A |
| P25(`PF_rule`) | `Load_Type` | Phân tích phân phối PF (nội bộ, không dùng trong rule) |
| P95(`Power_Factor_Volatility`) | `Load_Type` | Leakage Drift — sub-condition 2 (nội bộ) |
| [P5, P95](`Reactive_Power_Ratio`) | `Load_Type` | Leakage Drift — sub-condition 3 (nội bộ) |
| **Median**(`Usage_kWh`) | **`Load_Type=Light_Load × Hour × WeekStatus`** | Idling — context-aware baseline *(xem ghi chú F3)* |

> **[F3 — v2.2] Idling baseline — Context-aware với fallback rõ ràng:**
> Baseline Idling được nâng từ `Median(Light_Load)` toàn cục lên `Median(Usage_kWh | Light_Load × Hour × WeekStatus)`.
> **Lý do:** Tiêu thụ median lúc 2h sáng ngày thường khác rất nhiều so với 10h sáng ngày thường trong cùng nhóm Light\_Load.
>
> **Fallback theo thứ tự:**
> 1. `Load_Type=Light_Load × Hour × WeekStatus` *(ưu tiên, n ≥ 10)*
> 2. `Load_Type=Light_Load × Hour` *(nếu n < 10 do WeekStatus)*
> 3. `Load_Type=Light_Load` *(simplified baseline — bias đã biết, ghi vào `baseline_level = 3`)*
>
> **Bias đã biết khi dùng fallback cấp 3:** Median toàn nhóm Light\_Load bao gồm cả giờ cao điểm lẫn giờ thấp điểm, nên ngưỡng bị kéo lên so với giờ đêm → tăng recall nhưng giảm precision cho các điểm đêm. Khi `baseline_level = 3` và `Hour ∈ {0–5}`, cờ `night_simplified_baseline_warning` được bật *(xem Mục 10.3)*.

---

## 6. Định nghĩa Quy tắc (Rule Definitions) & Ưu tiên (Priority)

Nếu một điểm dữ liệu vi phạm nhiều quy tắc, áp dụng thứ tự gán nhãn:
**(1) Overload → (2) Idling → (3) Leakage Drift → (4) Normal**

---

### 6.1. Suspected_Overload (Ưu tiên 1)

**Định nghĩa:** Tín hiệu stress điện cao bất thường kèm theo hệ số công suất kém (*high-stress proxy signal*).

> **[F4 — v2.2] High-confidence subset — thiết kế có chủ ý:**
> AND + P99.5 + `PF_rule` < 0.70 tối ưu **precision trên recall**: đỉnh tải hợp lệ với PF tốt không bị gán nhãn. Nếu cần recall cao hơn (sàng lọc ban đầu), có thể dùng OR logic với P99 như v2.0 — nhưng đó là use case khác, không phải mục tiêu của nhãn này.

**Quy tắc (AND):**

- *Condition A:* `Apparent_Power_S` > **P99.5**(`Apparent_Power_S` | `Load_Type × Hour × WeekStatus`)
- *Condition B:* `(Lagging_Current_Power_Factor / 100)` < **0.70**

**Thời lượng tối thiểu:** Dị biệt điểm (Point anomaly) — không yêu cầu thời lượng tối thiểu.

**Diễn giải an toàn:** Cảnh báo sớm về stress điện cực trị kèm chất lượng công suất kém; không khẳng định quá tải vật lý (not confirmed equipment fault).

---

### 6.2. Suspected_Idling / Suspected_Idle_Waste (Ưu tiên 2)

**Định nghĩa (idle-waste behavior):** Thiết bị tiêu thụ điện cao hơn mức bình thường của ngữ cảnh tương ứng trong trạng thái Light\_Load, nhưng phần lớn là công suất phản kháng — năng lượng bị tiêu tán thay vì chuyển hóa thành công hữu ích. Đây **không phải** sự kiện ngừng máy hoặc sản lượng thấp bất thường.

**Quy tắc (AND):**

- `Load_Type` = Light\_Load
- `Usage_kWh` > **Median(`Usage_kWh` | `Light_Load × Hour × WeekStatus`)** *(context-aware, xem fallback Mục 5.2)*
- `(Lagging_Current_Power_Factor / 100)` < **0.50**
- **Thời lượng tối thiểu:** ≥ 4 dòng liên tiếp (1 giờ)

**Diễn giải an toàn:** Hành vi idle-waste: tiêu thụ không sinh công hữu ích dưới chế độ tải nhẹ. Không khẳng định động cơ quay không tải ở cấp phần cứng. Nếu cần phát hiện production halt bất ngờ, dùng quy tắc bổ sung: `z_usage < −2.0` trong giờ sản xuất định mức.

---

### 6.3. Suspected_Leakage_Drift (Ưu tiên 3)

*(Alias: `Suspected_Inefficiency_Drift` — v2.0. Xem Mục 4: "Leakage" = energy inefficiency drift, không phải insulation leakage vật lý.)*

**Định nghĩa:** Mất ổn định điện năng kéo dài kèm xu hướng tải biểu kiến tăng dần, báo hiệu suy giảm hiệu suất năng lượng so với baseline 4 tuần.

**Quy tắc (AND):**

- `Usage_kWh` > 1 (loại trừ nhiễu khi tắt máy hoàn toàn)
- Rolling 28-day mean của `Apparent_Power_S` tăng **≥ 5%** so với baseline của nhóm `Load_Type` tương ứng
- **Tồn tại ít nhất 1** trong 3 điều kiện phụ về PF/phản kháng (OR):
  1. `(Lagging_Current_Power_Factor / 100)` < **0.50**
  2. `Power_Factor_Volatility` (nội bộ) > P95(`Power_Factor_Volatility` | `Load_Type`)
  3. `Reactive_Power_Ratio` (nội bộ) nằm ngoài khoảng [P5, P95](`Reactive_Power_Ratio` | `Load_Type`)
- **Thời lượng tối thiểu:** ≥ 4 dòng liên tiếp (1 giờ)

**Diễn giải an toàn:** Tín hiệu vận hành kém tối ưu về phản kháng và xu hướng suy giảm dài hạn; không phải bằng chứng rò rỉ điện vật lý, lỗi cách điện, hay hư hỏng thiết bị đã xác nhận (not physical leakage, not insulation failure, not confirmed equipment fault).

> **Implementation status — v2.5 final:** Phiên bản hiện tại đã đồng bộ với guideline v2.5, bao gồm `Apparent_Power_S`, `PF_rule = Lagging_Current_Power_Factor / 100`, context-aware baselines với fallback, duration post-processing cho Idling và Leakage (≥4 dòng liên tiếp), priority resolution (Overload > Idling > Leakage > Normal), và 9 canonical label columns theo data codebook Table A-IV.

---

## 7. Tổng hợp nhãn `anomaly_any` (Union Definition)

Cột `anomaly_any` là **union (OR logic)** của ba nhãn thành phần:

```
anomaly_any = (
    Suspected_Idling == 1
    OR Suspected_Overload == 1
    OR Suspected_Leakage_Drift == 1
)
```

**Quy tắc xử lý chồng lấp (overlap):**

- Một điểm dữ liệu chỉ được gán **một nhãn thành phần duy nhất** theo thứ tự ưu tiên: Overload > Idling > Leakage\_Drift.
- `anomaly_any = 1` nếu bất kỳ nhãn thành phần nào được kích hoạt.
- Cột `dominant_label` lưu nhãn thắng ưu tiên; `anomaly_any` lưu trạng thái nhị phân tổng hợp.

> **[F2 — v2.2] Soft warning — không phải hard assertion:**
> Pipeline **không dừng** khi tỷ lệ vượt ngưỡng. Thay vào đó ghi log:
>
> ```
> WARNING: anomaly_any rate = {rate:.1%}, vượt WARNING_THRESHOLD={threshold:.0%}.
> Kiểm tra: (1) baseline percentiles có shift không?
>            (2) scaler fit đúng tập không?
>            (3) phân phối đầu vào có thay đổi không?
> ```
>
> `WARNING_THRESHOLD = 0.10` (mặc định, có thể cấu hình). Không dùng hard assertion vì nhà máy có thể thực sự trải qua giai đoạn vận hành kém kéo dài.

**Phân rã tham chiếu quan sát được (Gwangyang 2018 — không phải target bắt buộc):**

| Nhãn | Số mẫu | Tỷ lệ | Ghi chú |
| :--- | ---: | ---: | :--- |
| Suspected\_Idling | 204 | 0,582% | Chỉ Light\_Load, `PF_rule` < 0.50, có duration filter |
| Suspected\_Leakage\_Drift | 3.444 | 9,829% | Drift dài hạn so với baseline 4 tuần, có duration filter |
| Suspected\_Overload | 3 | 0,009% | Point anomaly, ngưỡng context-aware rất ngặt |
| `anomaly_any` (union) | 3.651 | 10,420% | 572 chồng lấp trước ưu tiên (chủ yếu Idling+Leakage) |

---

## 8. Tổng hợp cấp Sự kiện (Event-Level Aggregation)

Các điểm dị biệt liên tiếp có chung nhãn (không bị ngắt quãng quá 15 phút) được gộp thành sự kiện. Bảng `event_level` chứa: `event_id`, `event_label`, `start_time`, `end_time`, `duration_minutes`, `avg_usage_kwh`, `max_apparent_power_s`, `avg_pf_rule`, `dominant_load_type`, `label_reason`, `row_count`.

---

## 9. Chấm điểm Tin cậy (Confidence Scoring) — Optional / Future Extension

> **[I6 — v2.5] Confidence scoring là phần mở rộng được khuyến nghị và không nên được liệt kê như cột output bắt buộc trừ khi đã được triển khai trong pipeline hiện tại.**

Confidence Score đo lường **độ mạnh của tín hiệu proxy**, không phải xác suất lỗi thật. Điểm tối đa 1.0. Nếu được triển khai trong tương lai, tham khảo các công thức dưới đây.

### Overload (tham khảo)

$$\text{score} = 0.6 \times I(\text{Apparent\_Power\_S} > P99.5) + 0.2 \times I(PF\_rule < 0.70) + 0.2 \times I(z_{usage} > 3.0)$$

> Với logic AND, cả hai điều kiện kích hoạt phải đúng → **score tối thiểu thực tế = 0.8**. Thang đo hiệu dụng: **[0.8, 1.0]**.

### Idling (tham khảo)

$$\text{score} = 0.40 \times I(P > \text{Median}_{context}) + 0.45 \times I(PF\_rule < 0.50) + 0.15 \times I(\text{Duration} \ge 1h)$$

> **Lý do trọng số:** `PF_rule < 0.50` nhận 0.45 vì là tín hiệu vật lý mạnh nhất và khó giả mạo nhất. Khi PF_rule = P/S = 0.50, thành phần tác dụng chỉ chiếm 50% tải biểu kiến; thành phần phản kháng Q/S = √(1 − 0.50²) ≈ 0.87 — tức gần 87% tải biểu kiến là phản kháng, cho thấy hiệu quả sử dụng điện rất thấp. Ngưỡng này rất khắt khe, hiếm xảy ra trong vận hành bình thường. Score tối thiểu khi nhãn được gán (trước post-processing duration): **0.85**.

### Leakage Drift (tham khảo)

$$\text{score} = 0.25 \times I(\text{rolling\_28d} \ge 5\%) + 0.25 \times I(PF\_rule < 0.50) + 0.20 \times I(\text{Volatility} > P95) + 0.20 \times I(\text{Reactive\_Ratio\_OOB}) + 0.10 \times I(\text{Duration} \ge 1h)$$

> **Lý do trọng số:** `rolling_28d_increase` và `PF_rule < 0.50` đồng hạng 0.25 vì cả hai đều là tín hiệu cốt lõi. `Volatility` và `Reactive_Ratio` đồng hạng 0.20 vì là điều kiện phụ. `Duration` nhận 0.10 như bộ lọc nhiễu. Score tối thiểu khi nhãn được gán: **0.35** (chỉ rolling + 1 sub-condition + duration); score đầy đủ: **1.00**.

**Thang đo tổng quát (nếu triển khai):** High (0.75–1.00) | Medium (0.40–0.74) | Low (0.10–0.39) | None (0.00).

---

## 10. Output Schema

> **[I7 — v2.5] Schema được tái cấu trúc thành 3 phần riêng biệt. Không liệt kê cột optional như required current output.**

### 10.1. A. Current Gold Persistent Label Columns

Đây là các cột label được materialize trong Gold table hiện tại. Các cột đánh dấu `No` ở cột Nullable phải được kiểm tra assertion sau pipeline.

| Cột | Dtype | Range / Values | Nullable | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | datetime64[ns] | 2018-01-01 00:00 → 2018-12-31 23:45 | No | Index chính, bước 15 phút |
| `Suspected_Idling` | int8 | {0, 1} | No | Sau duration filter (≥ 4 dòng); idle-waste behavior |
| `Suspected_Overload` | int8 | {0, 1} | No | Point anomaly; high-stress proxy signal |
| `Suspected_Leakage_Drift` | int8 | {0, 1} | No | Sau duration filter (≥ 4 dòng); energy inefficiency drift |
| `anomaly_any` | int8 | {0, 1} | No | OR union sau khi áp duration filter |
| `dominant_label` | str | {"Normal", "Suspected_Idling", "Suspected_Overload", "Suspected_Leakage_Drift", "Excluded"} | No | Nhãn thắng theo thứ tự ưu tiên |
| `label_reason` | str | Free text, parseable | No | Điều kiện kích hoạt dưới dạng chuỗi có thể parse |
| `is_proxy_label` | bool | {True} | No | Dataset-level flag: luôn True trên toàn bộ dataset, kể cả dòng `Normal`. Nhắc nhở mọi cột label (`Suspected_Idling`, `Suspected_Leakage_Drift`, `Suspected_Overload`, `anomaly_any`, `dominant_label`) đều có nguồn gốc từ rule-based proxy labeling, không phải ground truth. |
| `baseline_warning` | bool | {True, False} | No | Audit flag: True nếu context baseline dùng fallback (n<10 hoặc std=0 trong nhóm). Không phải lỗi dữ liệu hoặc cờ loại trừ — các dòng được gán nhãn bình thường. Downstream analyst có thể lọc cờ này. |
| `night_simplified_baseline_warning` | bool | {True, False} | No | True nếu `baseline_level=3` AND `Hour ∈ {0–5}` |

### 10.2. B. Optional Diagnostic / Future Columns

Các cột này có thể được materialize để audit hoặc debug, nhưng **không thuộc danh sách output bắt buộc** của Gold table.

> **Note:** `baseline_level` may be computed internally to produce `baseline_warning` and `night_simplified_baseline_warning`; it does not have to be materialized as a persistent column if the warning flags are persisted.

| Cột | Dtype | Range / Values | Ghi chú |
| :--- | :--- | :--- | :--- |
| `confidence_score` | float32 | [0.0, 1.0] | Optional / Future Extension — xem Mục 9. 0.0 nếu `anomaly_any = 0` hoặc `Excluded`. |
| `confidence_band` | str | {"High", "Medium", "Low", "None"} | Derived từ `confidence_score` nếu được triển khai. |
| `baseline_level` | int8 | {1, 2, 3} | Cấp fallback: 1=full context, 2=hour-only, 3=simplified. |
| `pf_clipped` | bool | {True, False} | True nếu PF gốc > 1.0 và đã được clip. |
| `anomaly_idling_point` | int8 | {0, 1} | Point-level flag trước duration filter (diagnostic). |
| `anomaly_overload_point` | int8 | {0, 1} | Point-level flag (diagnostic). |
| `anomaly_leakage_point` | int8 | {0, 1} | Point-level flag trước duration filter (diagnostic). |

### 10.3. C. Event-Level Aggregation Schema

| Cột | Dtype | Range / Values | Nullable | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | str | "EVT-{YYYYMMDD}-{seq:04d}" | No | Unique per event |
| `event_label` | str | Xem `dominant_label` | No | Nhãn thống nhất cho toàn sự kiện |
| `start_time` | datetime64[ns] | — | No | Timestamp đầu tiên |
| `end_time` | datetime64[ns] | — | No | Timestamp cuối cùng |
| `duration_minutes` | int16 | ≥ 15 | No | Bội số của 15 |
| `avg_usage_kwh` | float32 | ≥ 0 | No | — |
| `max_apparent_power_s` | float32 | ≥ 0 | No | `Apparent_Power_S` max trong sự kiện |
| `avg_pf_rule` | float32 | [0.0, 1.0] | No | Mean của `PF_rule` |
| `dominant_load_type` | str | {"Light_Load", "Medium_Load", "Maximum_Load"} | No | Mode của `Load_Type` trong sự kiện |
| `label_reason` | str | Free text | No | Tổng hợp từ row-level |
| `row_count` | int16 | ≥ 1 | No | Số dòng trong sự kiện |
| `has_night_warning` | bool | {True, False} | No | True nếu bất kỳ dòng nào có `night_simplified_baseline_warning = True` |

### 10.4. Data Quality Rules (trước khi gán nhãn)

> **[G3 — v2.3] PF clip thay vì hard exclude:**
> Khi tính `PF_derived_abs` nội bộ để audit, nếu `PF_derived_abs > 1.0` thường do sai số floating point. Phản ứng phù hợp:
> - Nếu `PF_derived_abs ∈ (1.0, 1.0 + 1e-4]`: **clip về 1.0** và bật `pf_clipped = True`. Log warning.
> - Nếu `PF_derived_abs > 1.0 + 1e-4` (vi phạm nghiêm trọng, > 1.0001): **exclude** — gán `dominant_label = "Excluded"`.
>
> **Lưu ý:** PF rule chính (`PF_rule = Lagging_Current_Power_Factor / 100`) từ dataset gốc không cần clip vì giá trị đo đã nằm trong [0, 100]%.

> **[G4 — v2.3] Night simplified baseline — warning flag, không phải hard filter:**
> Khi `baseline_level = 3` AND `Hour ∈ {0, 1, 2, 3, 4, 5}`, hàng **không bị exclude**. Thay vào đó, bật `night_simplified_baseline_warning = True`. Downstream analyst có thể lọc cờ này để sensitivity analysis. Hard exclude bị loại bỏ vì chưa có empirical evidence về tỷ lệ false positive thực tế của nhóm này.

**Hard Filters (exclude hoàn toàn):**

| Filter | Điều kiện | Lý do |
| :--- | :--- | :--- |
| Zero-power rows | `Usage_kWh` == 0 AND `Apparent_Power_S` == 0 | Thiết bị tắt hoàn toàn |
| Negative power | `Usage_kWh` < 0 | Lỗi đo lường hoặc đảo chiều — cần kiểm tra riêng |
| PF severe violation | `PF_derived_abs` > 1.0001 (nếu có tính nội bộ) | Vi phạm vật lý nghiêm trọng — không thể là sai số số học |

Các hàng bị exclude giữ `dominant_label = "Excluded"`, không tính vào `anomaly_any`, không đưa vào GAN training.

---

## 11. Implementation Order

> **[G6 — v2.3] Thứ tự bắt buộc để tránh dependency error. Các bước có đánh dấu dependency không thể hoán đổi vị trí.**

| Bước | Hành động | Dependency |
| :---: | :--- | :--- |
| 1 | **Compute physical features:** `Q_net`, `Apparent_Power_S`, `PF_rule = Lagging_Current_Power_Factor / 100`. (Tùy chọn nội bộ: `PF_derived_abs`, `Reactive_Power_Ratio`, `Power_Factor_Volatility`.) | Raw data |
| 2 | **Compute context baselines & percentiles:** P99.5, P95, [P5,P95], Median theo grouping. Ghi `baseline_level`, `baseline_warning`. | Bước 1 |
| 3 | **Compute rolling 28-day Apparent_Power_S trend** cho Leakage Drift condition. | Bước 1 |
| 4 | **Apply hard data-quality filters:** zero-power, negative power, PF severe violation → `dominant_label = "Excluded"`. Clip PF nhẹ nếu có tính `PF_derived_abs`, bật `pf_clipped`. | Bước 1 |
| 5 | **Compute point-level rule flags** cho tất cả hàng không bị Excluded: `flag_overload`, `flag_idling_point`, `flag_leakage_point`. Bật `night_simplified_baseline_warning` khi phù hợp. | Bước 2, 3, 4 |
| 6 | **Apply duration post-processing** cho Idling và Leakage Drift: chỉ giữ flags trên chuỗi ≥ 4 dòng liên tiếp. Overload giữ point-level. | Bước 5 |
| 7 | **Resolve conflicts by priority:** Overload > Idling > Leakage Drift → gán `dominant_label`. | Bước 6 |
| 8 | **Generate output columns:** `Suspected_Idling`, `Suspected_Overload`, `Suspected_Leakage_Drift`, `anomaly_any`, `dominant_label`, `label_reason`, `is_proxy_label`, `baseline_warning`, `night_simplified_baseline_warning`. Kiểm tra `anomaly_any` rate vs `WARNING_THRESHOLD`. | Bước 7 |
| 9 | **Aggregate event-level table** từ consecutive rows có cùng `dominant_label`. | Bước 8 |
| 10 | **Run validation checklist** (Mục 12). | Bước 8, 9 |

---

## 12. Validation Checklist

> **[G7 — v2.3] Báo cáo bắt buộc sau mỗi lần chạy pipeline gán nhãn. Checklist này chứng minh guideline được thực thi đúng và kết quả có thể kiểm toán.**

### 12.1. Label Distribution Report

- [ ] Số mẫu và tỷ lệ của từng `dominant_label` (bao gồm `Excluded`).
- [ ] So sánh với phân rã tham chiếu quan sát được ở Mục 7. Nếu lệch > 2x, ghi lý do — lệch không có nghĩa là sai, dataset khác có thể có phân phối khác.
- [ ] `anomaly_any` rate vs `WARNING_THRESHOLD`. Log warning nếu vượt.

### 12.2. Cross-tabulations

- [ ] `dominant_label × Load_Type` — kiểm tra Idling chỉ xuất hiện trong Light\_Load; Overload tập trung ở Maximum\_Load.
- [ ] `dominant_label × Hour` — kiểm tra phân phối theo giờ có hợp lý về mặt vận hành.
- [ ] `dominant_label × WeekStatus` — kiểm tra Idling không tập trung bất thường vào một nhóm `WeekStatus` nếu không có lý do từ rule hoặc dữ liệu (rule v2.5 không bắt buộc Weekday, nên phân phối theo WeekStatus là kết quả data-driven, không phải artifact của rule).
- [ ] `dominant_label × confidence_band` — nếu confidence_score được triển khai; kiểm tra Overload chủ yếu ở High band [0.8, 1.0].

### 12.3. Baseline Quality Report

- [ ] Phân phối `baseline_level` (1/2/3): tỷ lệ `baseline_level = 3` không nên vượt 5% tổng dữ liệu.
- [ ] Số hàng có `baseline_warning = True`.
- [ ] Số hàng có `night_simplified_baseline_warning = True` và phân bố theo nhãn.
- [ ] Số hàng có `pf_clipped = True` và giá trị PF gốc trước khi clip (nếu có tính `PF_derived_abs`).

### 12.4. Event-level Report

- [ ] Số sự kiện (event count) theo `event_label`.
- [ ] Phân phối `duration_minutes` theo nhãn (min, median, max, P95).
- [ ] Top 5 sự kiện dài nhất theo từng nhãn (kèm `start_time`, `avg_pf_rule`, `avg_confidence_score` nếu có).
- [ ] Số sự kiện có `has_night_warning = True`.

### 12.5. Overlap & Integrity Report

- [ ] Số hàng vi phạm nhiều quy tắc trước khi áp priority (overlap trước resolution).
- [ ] Xác nhận không có `anomaly_any = 1` trong các hàng `dominant_label = "Excluded"`.
- [ ] Xác nhận `is_proxy_label = True` trên toàn bộ dataset.
- [ ] Nếu confidence_score được triển khai: xác nhận `confidence_score = 0.0` cho tất cả hàng `dominant_label = "Normal"` hoặc `"Excluded"`.

### 12.6. Correlation Sanity Check

- [ ] **Mutual information (MI) giữa `dominant_label` và `Load_Type`** — báo cáo giá trị thực tế. Không áp ngưỡng cứng vì MI cao một phần là hệ quả hợp lý của rule: Idling bắt buộc `Light_Load`, Overload tự nhiên tập trung ở `Maximum_Load`. Nếu MI cao, giải thích: (i) bao nhiêu phần đến từ rule design (expected); (ii) bao nhiêu phần vượt mức expected (cần kiểm tra). Flag nếu MI vượt 0.05 mà không giải thích được qua rule logic.
- [ ] Correlation MAE giữa real anomaly rows và GAN synthetic rows (nếu GAN được chạy).

---

## 13. Cảnh báo và Hạn chế (Limitations)

1. **Weak/Proxy Labels:** Mọi nhãn đều là weak/proxy label (`is_proxy_label = True`). Không dùng như ground truth cho quyết định vận hành. Không phải SCADA-confirmed.
2. **Circular leakage risk:** Không dùng `anomaly_any` hoặc `dominant_label` như feature đầu vào cho mô hình dự báo `Usage_kWh` cùng timestamp — xem Mục 1 (safe vs unsafe uses).
3. **"Leakage" ≠ Insulation Leakage:** Xem Mục 4. `Suspected_Leakage_Drift` đo energy inefficiency drift, không phải rò rỉ điện vật lý hay lỗi cách điện (not physical leakage, not insulation failure).
4. **"Idling" ≠ Machine Shutdown:** Xem Mục 4 và 6.2. `Suspected_Idling` = idle-waste behavior (tiêu thụ cao + PF thấp), không phải ngừng hoạt động.
5. **Ngữ cảnh Cục bộ:** Baseline và percentiles được fit trên dữ liệu Gwangyang 2018. Áp dụng cho nguồn khác phải fit lại toàn bộ.
6. **Mục đích Downstream:** Tối ưu cho phân tích offline. Không áp dụng cho ngắt mạch tự động thời gian thực (real-time trip/SCADA decisions).
7. **Ablation caveat:** Mô hình phân loại `anomaly_any` dùng trực tiếp các biến rule-defining (`Usage_kWh`, `Apparent_Power_S`, `Lagging_Current_Power_Factor`, `Load_Type`) có nguy cơ chỉ học lại labeling rules. Báo cáo ablation phải bao gồm cấu hình loại bỏ các biến này.
8. **Simplified baseline bias:** `baseline_level = 3` giảm precision ban đêm — xem Mục 5.2 và theo dõi `night_simplified_baseline_warning`.
9. **Synthetic data scope:** GAN data chỉ dùng cho thử nghiệm cân bằng, không dùng như bằng chứng lỗi thật.
10. **Non-ground-truth:** Toàn bộ nhãn là weak/proxy label. Không diễn giải là confirmed equipment fault, SCADA trip, hoặc real-time operational alert.
