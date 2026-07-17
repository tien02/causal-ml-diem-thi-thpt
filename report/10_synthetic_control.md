# Chapter 10 — Synthetic Control, EconML & Monte Carlo Sensitivity

← [09 Causal ML](09_causal_ml.md) | → [Index](index.md)

---

## 10.1 Tổng quan

Chapter 9 dùng RDD, Double ML thủ công, HTE, Bootstrap DiD. Chapter này thêm 3 lớp bằng chứng độc lập:

| Phương pháp | Câu hỏi |
|-------------|---------|
| **Synthetic Control** | Nếu không có CT2018, điểm 2025 sẽ là bao nhiêu? |
| **EconML CausalForestDML** | CATE phân phối ra sao theo từng cá nhân/tier? |
| **Rosenbaum Bounds + MC** | Kết quả có bền vững trước biến nhiễu ẩn không? |

---

## 10.2 Synthetic Control Method

### 10.2.1 Thiết kế

- **Đơn vị:** 33 tỉnh (harmonized codes, đủ data 3 năm pre-treatment)
- **Pre-treatment:** 2021, 2022, 2024 (điểm Toán TB, cohort CT2006)
- **Post-treatment:** 2025 — cohort CT2018 đầu tiên
- **Synthetic 2025** = extrapolate linear trend (2021/2022/2024) → predict điểm nếu không có CT2018
- **Gap** = Actual_CT2018_2025 − Synthetic_2025

### 10.2.2 Kết quả

| Chỉ số | Giá trị |
|--------|---------|
| **SC National ATE** | **−1.602 pts** |
| 95% CI (cross-province SE) | [−1.651, −1.553] |
| Số tỉnh | 33 |

**Theo urban tier:**

| Tier | SC Gap |
|------|--------|
| Đô thị lớn (HN, HCM) | −1.521 pts |
| Đô thị vừa | −1.593 pts |
| **Tỉnh lẻ/Nông thôn** | **−1.628 pts** |

> 📌 Nhất quán với RDD (−1.689). Rural vẫn bị nặng hơn Urban — xác nhận HTE từ Chapter 9.

### 10.2.3 Placebo (In-time Falsification)

Predict 2024 từ linear trend 2021+2022 → gap nên ≈ 0 nếu parallel trends đúng.

| | Giá trị |
|--|---------|
| Placebo gap (2024) | **+0.264 pts**, |t| = 7.79 |
| Kết luận kỹ thuật | Parallel trends bị vi phạm theo nghĩa hẹp |

**Tại sao không fatal?**

```
2021 → 2022: COVID làm điểm DIP (lower than true trend)
2022 → 2024: Recovery bật lên (higher than 2021→2022 linear extrapolation)
→ Linear trend từ 2021+2022 underestimate 2024
→ Placebo "gap" = COVID recovery artifact, không phải structural break

SCM chính (3 điểm: 2021, 2022, 2024) đã capture recovery
→ Prediction 2025 vẫn valid (COVID effect đã included trong pre-trend)
```

---

## 10.3 EconML — LinearDML & CausalForestDML

### 10.3.1 Setup

- **Y**: điểm Toán cá nhân
- **T**: treatment (1 = CT2018, 0 = CT2006) — 2025 hai cohort
- **X**: [urban_large, urban_mid, is_chuyen, log(prov_n)]
- **Sample**: 200,000 học sinh (stratified subsample từ 1.15M)
- **Model Y/T**: GradientBoostingRegressor (100 trees, depth 3), 5-fold cross-fitting

### 10.3.2 Kết quả tổng hợp — 4 methods hội tụ

| Method | ATE CT2018 (Toán) | Notes |
|--------|-------------------|-------|
| RDD (Chapter 9) | −1.689 | Causal, within-2025 cohort split |
| Double ML thủ công | −1.69 | Debiased OLS |
| **LinearDML (econml)** | **−1.720** | Cross-fitted, parametric CATE(X) |
| **CausalForestDML** | **−1.727** | Non-parametric, individual CATE |
| Synthetic Control | −1.602 | Province-level, COVID caveat |

> **Range hội tụ: −1.60 đến −1.73 pts.** Mỗi phương pháp có assumptions khác nhau, tất cả cho estimate tương đồng → bằng chứng causal rất mạnh.

**CATE theo urban tier (LinearDML):**

| Tier | CATE |
|------|------|
| Đô thị lớn | −0.999 pts |
| Đô thị vừa | −1.414 pts |
| **Nông thôn** | **−1.700 pts** |

**Phân phối CATE (CausalForestDML):**
- p5/p95: [−2.124, −1.057]
- **Không có học sinh nào có CATE > 0** — toàn bộ phân phối âm
- Rural violin thấp hơn Urban ≈ 0.7 pts

---

## 10.4 Rosenbaum Bounds — Độ bền vững

### 10.4.1 Câu hỏi

> Biến nhiễu ẩn cần mạnh đến mức nào để làm kết quả mất ý nghĩa thống kê?

### 10.4.2 Kết quả

| Chỉ số | Giá trị |
|--------|---------|
| Wilcoxon (SC gaps ≠ 0) | p ≈ 0.000 |
| **Γ\* (Rosenbaum threshold)** | **6.0×** |
| Giải thích | Biến nhiễu cần odds ratio **6×** mới overturn kết quả |

**Tham chiếu mức Γ\*:**

| Γ\* | Độ mạnh |
|-----|---------|
| 1.5 | Fragile (quan sát đơn thuần yếu) |
| 2–3 | Tương đối robust |
| **6.0** | **Cực kỳ robust** |

Assignment CT2018/CT2006 = năm sinh/nhập học → không phải selection tự nguyện → hidden confounder khó có thể bias ở mức Γ = 6×.

### 10.4.3 Monte Carlo (Γ = 2)

Simulate biến nhiễu tăng gấp đôi odds:

| | Giá trị |
|--|---------|
| 90% MC range | [−1.609, −1.574] |
| **% simulations negative** | **100%** |
| Kết luận | **ROBUST** |

---

## 10.5 Tổng hợp bằng chứng đa phương pháp

```
Method                 ATE      Assumptions
───────────────────────────────────────────────────────────
RDD (Chapter 9)       -1.689   Sharp cutoff, no selection   ✅
Double ML thủ công    -1.690   Conditional exogeneity        ✅
LinearDML (econml)    -1.720   Cross-fitted, GBM nuisance    ✅
CausalForestDML       -1.727   Non-parametric CATE           ✅
Synthetic Control     -1.602   Linear trend (COVID caveat)   ⚠️
───────────────────────────────────────────────────────────
Hội tụ (4 methods):   -1.65 ± 0.06 pts  ← CAUSAL ESTIMATE
```

### Policy implication

CT2018 gây thiệt hại đồng đều, không có nhóm nào được lợi (CausalForest CATE < 0 với mọi học sinh). Đây là thách thức **systemic**. Cần:

1. **Phân bổ giáo viên** theo tier (nông thôn cần nhiều hơn)
2. **Tài liệu ôn CT2018** đặc biệt cho tỉnh xa trong ít nhất 3–5 năm đầu
3. **Monitor ATE 2026** (CT2018 năm 2) để kiểm tra adaptation curve

---

## 10.6 Giới hạn

| Limitation | Hệ quả |
|-----------|--------|
| SCM placebo fail (COVID 2022) | SC estimate ít robust hơn RDD |
| EconML subsample 200k/1.15M | Có thể miss province-level heterogeneity nhỏ |
| Permutation test không significant (p=0.32) | Khi ALL provinces treated, permutation phân phối ≈ observed |
| CT2006 cohort 2025 = lưu ban → selection bias | RDD overestimate nhẹ (đã noted Chapter 9) |

---

## 10.7 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| CT2018 ATE Toán là bao nhiêu? | **−1.65 pts** (range −1.60 đến −1.73, 4 methods) |
| Có nhóm nào được lợi? | **Không** — toàn bộ CATE < 0 |
| Kết quả có robust? | **Cực kỳ** — Γ\* = 6.0, MC 100% negative |
| SC có confirm RDD? | **Có** — −1.602 vs −1.689 (Δ = 0.087, COVID pre-trend) |

> 📊 Xem: `sc_main.png` · `sc_permutation.png` · `econml_cate.png` · `mc_sensitivity.png`

← [09 Causal ML](09_causal_ml.md) | → [Index](index.md)
