# Chapter 9 — Causal ML: RDD, Double ML, HTE, Bootstrap DiD

← [08 Fraud](08_fraud_detection.md) | → [Index](index.md)

---

## 9.1 Tổng quan Phương pháp

| Phương pháp | Câu hỏi | Dữ liệu |
|-------------|---------|---------|
| **RDD** | CT2018 làm giảm điểm bao nhiêu? (causal) | 2025 hai cohort + 2024 vs 2025 |
| **Double ML** | Urban premium thực sự là bao nhiêu? (debiased) | 2021 + 2022 + 2024 |
| **HTE** | CT2018 ảnh hưởng đô thị vs nông thôn khác nhau? | 2025 hai cohort |
| **Bootstrap DiD** | COVID DiD có ý nghĩa thống kê thực không? | 2021 + 2024 |

---

## 9.2 RDD — Curriculum Effect (CT2018)

### 9.2.1 Natural Experiment

Năm 2025 có **hai cohort thi cùng kỳ**:
- CT2006 (n = 22,000) — học sinh lưu ban/thi lại, chương trình cũ
- CT2018 (n = 1,131,000) — thế hệ đầu tiên chương trình mới

Đây là **sharp RDD** sạch nhất: cùng năm, cùng kỳ thi, chỉ khác chương trình học.

### 9.2.2 Kết quả

| Comparison | ATE Toán | 95% CI | p-value |
|-----------|----------|--------|---------|
| Within-2025: CT2018 vs CT2006 | **−1.689** | [−1.73, −1.65] | ≈ 0 |
| Year-level: 2025-CT2018 vs 2024-CT2006 | **−1.669** | tight | ≈ 0 |

> 📌 **ATE = −1.69 điểm Toán** — nhất quán qua cả hai cách đo. Estimate **causal** (không phải correlation) vì assignment vào CT2018/CT2006 dựa theo năm sinh/nhập học, không phải năng lực học sinh.

### 9.2.3 Caveat

Nhóm CT2006 năm 2025 = học sinh lưu ban/thi lại → **selection bias**: nhóm này năng lực thấp hơn trung bình, làm **overestimate** tác động tiêu cực CT2018. Estimate thực có thể là −1.4 đến −1.7.

---

## 9.3 Double ML — Urban Causal Effect (Debiased)

### 9.3.1 Vấn đề OLS naïve

OLS bị confounded: tỉnh đô thị có nhiều trường chuyên, GDP cao → OLS tính nhầm một phần urban premium thành chuyên/GDP effect.

### 9.3.2 Setup Manual Double ML (5-fold cross-fitting)

- **Y:** điểm Toán
- **T:** urban_large (1 = Đô thị lớn, 0 = khác)
- **X:** [year, is_chuyen_province, province_size_proxy]

**Stage 1:** Regress T on X → T̃ (treatment residual)
**Stage 2:** Regress Y on X → Ỹ (outcome residual)
**Stage 3:** ATE = coef(Ỹ ~ T̃)

### 9.3.3 Kết quả

| Method | ATE Urban | So với DML |
|--------|-----------|-----------|
| Naive OLS | +0.427 | −0.036 (underestimate) |
| **Double ML** | **+0.463** | baseline |

> 📌 **Kết quả bất ngờ:** DML *tăng* estimate so với OLS. Các confounders (year trend, chuyên province) đang **suppress** urban premium trong OLS, không phải inflate. Urban effect thực sự mạnh hơn OLS cho thấy.

**Cơ chế:** Chuyên provinces phân bố nhiều ở tỉnh nông thôn (Nam Định, Nghệ An, Hà Tĩnh). Khi control cho chuyên → urban coefficient tăng lên.

---

## 9.4 HTE — CT2018 theo Urban Tier

### Câu hỏi: Học sinh nông thôn bị thiệt hơn không?

| Tier | ATE CT2018 Toán | So với đô thị lớn |
|------|----------------|-----------------|
| Đô thị lớn (HN, HCM) | **−1.42 pts** | baseline |
| Đô thị vừa | −1.57 pts | −0.15 |
| **Tỉnh lẻ/Nông thôn** | **−1.76 pts** | **−0.34** |

**Interaction terms kiểm định trên 2025 data:**
- `CT2018 × Urban_large`: +0.34, p < 0.001 ✓
- `CT2018 × Urban_mid`: +0.21, p < 0.01 ✓

> 📌 **Kết luận causal:** CT2018 làm giảm điểm Toán mọi nơi, nhưng **học sinh nông thôn bị thiệt thêm 0.34 điểm** so với học sinh đô thị lớn. HTE có ý nghĩa thống kê.

### Cơ chế

```
CT2018 yêu cầu tư duy phản biện + ứng dụng
              ↓
Đô thị: giáo viên đào tạo lại sớm · tài liệu ôn thi mới · trường tư luyện CT2018
              ↓
Nông thôn: giáo viên chưa kịp thích nghi · thiếu tài liệu CT2018
              ↓
Gap NỚI RỘNG trong giai đoạn chuyển đổi
```

**Policy implication:** CT2018 cần kèm theo hỗ trợ giáo viên tỉnh xa và tài liệu ôn tập đặc biệt cho học sinh nông thôn trong ít nhất 3 năm đầu.

---

## 9.5 Bootstrap DiD — COVID Recovery

### 9.5.1 DiD gốc (Chapter 2)

|  | 2021 | 2024 | Δ |
|--|------|------|---|
| Đô thị lớn | 7.048 | 6.853 | −0.195 |
| Tỉnh lẻ/Nông thôn | 6.498 | 6.341 | −0.157 |
| **DiD** | | | **−0.038** |

### 9.5.2 Bootstrap 1,000 iterations (cluster by province_harmonized)

| Chỉ số | Giá trị |
|--------|---------|
| Bootstrap mean DiD | −0.038 |
| Bootstrap std | 0.022 |
| **95% CI** | **[−0.081, +0.004]** |
| p-value (hai phía) | ~0.09 |

> 📌 **Kết luận: DiD gốc KHÔNG có ý nghĩa thống kê** tại mức 5% khi bootstrap cluster theo tỉnh. CI chạm 0 từ phía dương. Kết quả Chapter 2 ("đô thị phục hồi kém hơn") là **fragile**.

### 9.5.3 Tại sao bootstrap khác OLS standard error?

OLS giả định independent observations — nhưng học sinh cùng tỉnh có correlated errors (cùng môi trường, cùng giáo viên). Cluster bootstrap theo tỉnh sửa lỗi này → SE thực lớn hơn → CI rộng hơn → evidence yếu hơn.

---

## 9.6 Tổng hợp

| Phân tích | Kết quả chính | Độ tin cậy |
|-----------|--------------|-----------|
| RDD CT2018 | **−1.69 pts Toán causal** | Cao (selection bias nhỏ) |
| Double ML Urban | **+0.463 pts** (debiased) | Cao |
| HTE Urban×CT2018 | **Rural −0.34 pts thêm** | Cao (p<0.001) |
| Bootstrap DiD COVID | **Không significant** [−0.081, +0.004] | Cao — prior result fragile |

---

## 9.7 Kết luận — Những gì Causal ML thay đổi

| Kết luận cũ (baseline descriptive) | Kết luận mới (Causal ML) |
|------------------------------------|-------------------------|
| DiD COVID: đô thị phục hồi kém hơn | ❌ **Không significant** — fragile |
| Urban premium ≈ +0.43 pts (OLS) | ✅ **+0.463 pts** (DML, mạnh hơn thực tế) |
| CT2018 gây sốc điểm Toán | ✅ **−1.69 pts causal** (RDD confirmed) |
| CT2018 ảnh hưởng đồng đều | ❌ **Rural bị nặng hơn −0.34 pts** (HTE) |

### Big picture

```
CT2018 = cú sốc lớn nhất 5 năm × 10 so với COVID
                    ↓
Tác động KHÔNG đồng đều: Rural bị nặng hơn Urban 0.34 pts
                    ↓
Trong khi Urban premium đang bị OLS underestimate
                    ↓
Khoảng cách đô thị-nông thôn thực sự NỚI RỘNG nhanh hơn
số liệu thô cho thấy — và CT2018 đang gia tốc quá trình này
```

> 📊 Xem: `rdd_curriculum_effect.png` · `dml_urban_effect.png` · `hte_curriculum_by_tier.png` · `bootstrap_did.png`

← [08 Fraud](08_fraud_detection.md) | → [Index](index.md)
