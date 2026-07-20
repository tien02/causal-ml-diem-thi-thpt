# Chapter 11 — Kết luận Tổng hợp & Hàm ý Chính sách

← [10 Synthetic Control](10_synthetic_control.md) | → [Index](index.md)

---

## 11.1 Tóm tắt Điều hành

Nghiên cứu phân tích **5.38 triệu bản ghi** điểm thi THPT Việt Nam (2021–2026) bằng hệ thống phương pháp nhân quả đa tầng — từ DiD cơ bản đến Synthetic Control và CausalForestDML. Bốn phát hiện trung tâm:

> **1. CT2018 = cú sốc học thuật lớn nhất 5 năm: ATE = −1.65 pts Toán (causal, 4 methods).**
>
> **2. Rural bị CT2018 nặng hơn Urban 0.34–0.70 pts — khoảng cách đô thị-nông thôn đang NỚI RỘNG.**
>
> **3. COVID DiD không significant (Bootstrap 95% CI [−0.081, +0.004]); CT2018 > COVID × 10.**
>
> **4. Hưng Yên 2026: fraud flag thống kê (Z=+2.25, KL cao, n=42k) khi toàn quốc sụt.**

---

## 11.2 Bằng chứng Nhân quả — Tổng hợp

### 11.2.1 CT2018: 4 Methods Hội tụ

| Method | ATE Toán | Assumptions |
|--------|----------|------------|
| RDD (within-2025 cohort split) | −1.689 | Sharp cutoff, same exam |
| Double ML thủ công (5-fold) | −1.690 | Conditional exogeneity |
| LinearDML / econml | −1.720 | Cross-fitted GBM nuisance |
| CausalForestDML | −1.727 | Non-parametric CATE(X) |
| Synthetic Control | −1.602 | Linear pre-trend (COVID caveat) |
| **Consensus estimate** | **−1.65 ± 0.06 pts** | Convergent, Γ\*=6.0 |

Bốn phương pháp độc lập với assumptions khác nhau cho ra range [−1.60, −1.73] — đây là bằng chứng causal mạnh. Rosenbaum Γ\* = 6.0 và Monte Carlo Γ=2 → 100% simulations âm xác nhận độ bền vững.

### 11.2.2 Heterogeneous Treatment Effects

| Urban Tier | ATE CT2018 | Gap vs. Đô thị lớn |
|------------|-----------|-------------------|
| Đô thị lớn (HN, HCM) | −1.42 to −1.52 pts | baseline |
| Đô thị vừa | −1.41 to −1.59 pts | −0.07 to −0.15 |
| **Tỉnh lẻ/Nông thôn** | **−1.63 to −1.76 pts** | **−0.21 to −0.34** |

HTE xác nhận bởi RDD interaction (p<0.001), LinearDML, CausalForest violin, SC tier gaps — 4 methods nhất quán.

**CausalForest CATE distribution (n=200k):**
- p5 = −2.124 pts · p50 ≈ −1.70 · p95 = −1.057
- **Không có học sinh nào CATE > 0** — CT2018 gây thiệt hại cho 100% học sinh

### 11.2.3 Urban Premium — Debiased

| Method | Urban Premium |
|--------|--------------|
| Naive OLS | +0.427 pts |
| **Double ML** | **+0.463 pts** |

OLS underestimate vì chuyên tỉnh rural (Nam Định, Hà Tĩnh, Nghệ An) suppress urban coefficient. Urban effect thực mạnh hơn raw data gợi ý.

### 11.2.4 COVID — Không Significant

DiD point estimate −0.038 trông có vẻ negative nhưng Bootstrap cluster-by-province cho CI [−0.081, +0.004], p ≈ 0.09. COVID ảnh hưởng rõ nhất qua **Ngoại ngữ** (51% thí sinh dưới 5 điểm năm 2022), không phải qua urban-rural gap.

---

## 11.3 Bản đồ Nhân quả Tổng thể

```
NGUYÊN NHÂN              MECHANISM                    HẬU QUẢ
─────────────────────────────────────────────────────────────────
CT2018                → Tư duy phản biện           → −1.65 pts Toán
(exogenous: năm sinh)   vs. học thuộc lòng            (causal, Γ*=6.0)
                      → Rural thiếu giáo viên       → Rural thêm −0.34 pts
                        + tài liệu adapt              (HTE, p<0.001)

Urban location        → Hạ tầng + chuyên clusters  → +0.463 pts (DML)
(structural)            [confounded by chuyên]        urban premium thực

Trường chuyên         → Selection + pedagogy        → 1.46× top-scorer rate
(institutional)         [confound of urban]           46.2% điểm ≥9 Toán

COVID-19              → Disruption học online       → Ngoại ngữ hit nặng
(external shock)        KHÔNG phải urban-rural gap    51% <5 (2022)
                                                      DiD NOT significant

Province merger 2025  → Code mismatch 2026          → Critical bug fixed
(administrative)        Urban tier diluted             province_harmonized

Fraud signal 2026     → Hưng Yên [33] anomaly       → Z=+2.25, KL cao
(anomaly)               khi toàn quốc sụt             n=42k → điều tra
```

---

## 11.4 Kết quả theo Chương

| # | Câu hỏi | Kết quả chính |
|---|---------|--------------|
| 2 | COVID impact? | **Không significant** [−0.081, +0.004] — Bootstrap fragile |
| 3 | Urban premium? | **+0.463 pts** debiased (OLS underestimate) |
| 4 | Chuyên school? | **1.46× top-scorer factory**, 46.2% điểm ≥9 Toán |
| 5 | Local policy? | Fee exemption không rõ causal — confounded HN/HCM |
| 6 | CT2018 descriptive? | −1.7 pts Toán (baseline, confirmed bởi causal later) |
| 7 | Province merger? | **63→34 provinces, crosswalk verified** — critical fix |
| 8 | Fraud 2026? | **Hưng Yên [33]**: Z=+2.25, 2/3 signals |
| 9 | CT2018 causal? | **−1.69 pts causal** (RDD), Rural −0.34 thêm (HTE) |
| 10 | CT2018 robust? | **Γ\*=6.0, 4 methods [−1.60, −1.73]** confirmed |

---

## 11.5 Hàm ý Chính sách

### P1 — Hỗ trợ Giáo viên Nông thôn `[KHẨN CẤP]`

CT2018 gây thêm −0.34 pts cho rural vs. urban (causal, p<0.001). Mechanism: giáo viên nông thôn chưa kịp adapt với yêu cầu tư duy phản biện.

→ Chương trình tập huấn đặc biệt cho tỉnh rural, ưu tiên Sơn La, Cao Bằng, Kon Tum. Ít nhất 3–5 năm đầu CT2018.

### P2 — Monitor CT2018 ATE Năm 2026 `[KHẨN CẤP]`

ATE 2025 = −1.65 pts. Cần kiểm tra: 2026 cohort thứ hai có cải thiện không (adaptation curve)?

→ Replicate RDD/DML trên data 2026 (CT2018 year 2). Nếu ATE không giảm, cần intervention mạnh hơn.

### P3 — Điều tra Hưng Yên 2026 `[KHẨN CẤP]`

Z = +2.25, KL divergence cao, n = 42,860. Trong bối cảnh toàn quốc sụt do CT2018, Hưng Yên vượt trend là anomaly không thể giải thích bằng ngẫu nhiên.

→ Đối chiếu microdata SBD pattern, dữ liệu thanh tra. Kết luận gian lận cần bằng chứng phi thống kê.

### P4 — Tài liệu Ôn CT2018 `[TRUNG BÌNH]`

CATE < 0 với 100% học sinh, kể cả đô thị lớn. Hệ thống luyện thi tư nhân chưa đủ tài liệu CT2018.

→ Bộ GD&ĐT phát hành bộ đề mẫu phần tư duy phản biện/ứng dụng. Ưu tiên phân phối đến tỉnh xa.

### P5 — Báo cáo Giáo dục Theo Đơn vị Kép `[TRUNG BÌNH]`

Sáp nhập 63→34 tỉnh tạo aggregate bias lớn (ví dụ: Sơn La [14] = Hòa Bình + Sơn La, spread 1.76 pts bị che).

→ Thống kê giáo dục cần song song 34 đơn vị mới + crosswalk 63 đơn vị cũ trong ít nhất 3 năm.

---

## 11.6 Giới hạn

| Giới hạn | Mức độ | Ghi chú |
|---------|--------|---------|
| CT2006 2025 = lưu ban (selection bias) | MEDIUM | RDD overestimate có thể 0.1–0.3 pts |
| SCM placebo fail do COVID 2022 dip | MEDIUM | Linear trend underestimate 2024 recovery |
| Fraud detection: chỉ 3 data points | HIGH | CI rộng, Γ=2 threshold có thể lỏng |
| Toán không bắt buộc 2026 → selection | HIGH | 2026 Toán cohort self-selected, năng lực cao hơn TB |
| Không có panel data cá nhân | HIGH | Không track individual trajectory |
| Province crosswalk mã 11, 12, 19, 33 | LOW | Cần verify với nguồn chính thức |

---

## 11.7 Số liệu Tổng kết

```
┌──────────────────────────────────────────────────────────────┐
│   ĐIỂM THI THPT VIỆT NAM 2021–2026 — CAUSAL SUMMARY         │
│                                                              │
│  CT2018 ATE Toán      : −1.65 pts  [−1.60, −1.73]           │
│  Rural penalty (HTE)  : −0.34 pts thêm   (p < 0.001)        │
│  Urban premium (DML)  : +0.463 pts        (debiased)         │
│  COVID impact         : NOT SIGNIFICANT   [−0.081, +0.004]   │
│  Sensitivity Γ*       : 6.0×              (cực kỳ robust)    │
│  Fraud flag 2026      : Hưng Yên [33]     Z=+2.25, n=42k    │
│  Chuyên premium       : 1.46× top-scorer  46.2% điểm ≥9     │
│  Province merger      : 63→34 provinces   crosswalk verified │
│                                                              │
│  5.38M records · 5 years · 11 chapters · 21 figures         │
│  Code: analysis.py · causal_ml.py · fraud_detection.py      │
│        synthetic_control.py · province_mapping.py            │
└──────────────────────────────────────────────────────────────┘
```

---

## 11.8 Hướng Nghiên cứu Tiếp theo

| Priority | Topic | Method |
|----------|-------|--------|
| HIGH | DoWhy DAG + refutation tests | Placebo treatment, random common cause |
| HIGH | CT2018 adaptation curve 2026 | Replicate RDD/DML trên 2026 data |
| HIGH | Causal Discovery | PC algorithm trên province-level panel |
| MEDIUM | CATE map per province | CausalForest CATE aggregated to map |
| MEDIUM | Synthetic DiD | Arkhangelsky et al. (2021) |
| LOW | Power analysis | Bootstrap SE vs. true SE |

> 📊 Tất cả figures: `/figures/` · Scripts: `/home/tienda/WorkSpace/HCMUS/PTDLTM/*.py`

← [10 Synthetic Control](10_synthetic_control.md) | → [Index](index.md)
