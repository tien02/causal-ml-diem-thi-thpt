# Tóm tắt Điều hành — Điểm thi THPT Việt Nam 2021–2026

← [Index](index.md) | → [01 Data Context](01_data_context.md)

---

## Bộ dữ liệu

**5.38 triệu bản ghi** điểm thi THPT qua 5 năm (2021, 2022, 2024, 2025, 2026). Bao gồm 2 chương trình giáo dục (CT2006 cũ và CT2018 mới), 2 hệ thống mã tỉnh (63 tỉnh cũ → 34 tỉnh mới sau sáp nhập 2025).

---

## Bốn phát kiến trung tâm

> **1. CT2018 = cú sốc học thuật lớn nhất 5 năm: ATE = −1.65 điểm Toán (causal).**
>
> Sáu phương pháp độc lập (RDD, Double ML, LinearDML, CausalForest, Synthetic Control, DoWhy) đều cho estimate trong khoảng **[−1.60, −1.73]**. Lớn hơn COVID khoảng **10 lần**. Rosenbaum Γ\* = 6.0 — cực kỳ robust.
>
> **2. Nông thôn bị thiệt hại nặng hơn đô thị 0.34 điểm (HTE, p<0.001).**
>
> Khoảng cách đô thị-nông thôn đang **nới rộng** trong giai đoạn chuyển đổi. CausalForest CATE < 0 với **100% học sinh** — không có nhóm nào được lợi.
>
> **3. COVID DiD KHÔNG có ý nghĩa thống kê (Bootstrap 95% CI [−0.081, +0.004]).**
>
> Kết luận informal "COVID giảm điểm" là **fragile**. Tác động rõ nhất qua **Ngoại ngữ** (51% thí sinh <5 điểm năm 2022), không qua urban-rural gap.
>
> **4. Gian lận 2026: nhiều lớp tín hiệu bất thường ở Hưng Yên, Tuyên Quang, Sơn La.**
>
> Hưng Yên [33]: province-level Z=+2.25. Tuyên Quang [8]: 7 students SBD-adjacent ALL toan=10.00 (P<10⁻⁶). DBSCAN tìm 4,482 multi-subject clusters (vs 56 expected = 79x surprise).

---

## Năm phần báo cáo

| Phần | Nội dung | Chapters |
|------|----------|----------|
| **I. Bối cảnh** | Dữ liệu, sáp nhập tỉnh, chương trình | [01](01_data_context.md) |
| **II. Mô tả** | COVID, đô thị-nông thôn, trường chuyên | [02](02_covid_descriptive.md) · [03](03_urban_rural_gap.md) · [04](04_chuyen_school_effect.md) |
| **III. Nhân quả** | Ước lượng causal + sensitivity | [05](05_ct2018_causal_estimands.md) · [06](06_sensitivity_refutation.md) · [07](07_local_policy.md) |
| **IV. Gian lận** | Province + student-level detection | [08](08_province_anomaly.md) · [09](09_student_cluster_window.md) · [10](10_multisubject_dbscan.md) · [11](11_fraud_synthesis.md) |
| **V. Tổng hợp** | Kết luận + policy | [12](12_conclusions_policy.md) |

---

## Số liệu chính

```
┌──────────────────────────────────────────────────────────────┐
│   ĐIỂM THI THPT VIỆT NAM 2021–2026                          │
│                                                              │
│  CT2018 ATE Toán      : −1.65 pts  [−1.60, −1.73]           │
│  Rural penalty (HTE)  : −0.34 pts thêm (p < 0.001)          │
│  Urban premium (DML)  : +0.463 pts      (debiased)           │
│  COVID impact         : KHÔNG significant [−0.081, +0.004]   │
│  Sensitivity Γ*       : 6.0×           (cực kỳ robust)       │
│  Chuyên premium       : 1.46× top-scorer  46.2% điểm ≥9     │
│  Fraud flag 2026      : 4 tỉnh flag ≥2 methods               │
│  Cluster cheat signal : 4,482 multi-subject clusters (79x)   │
│                                                              │
│  5.38M records · 5 years · 13 chapters · 24 figures         │
└──────────────────────────────────────────────────────────────┘
```

---

## Code & reproducibility

| Script | Mục đích |
|--------|----------|
| `analysis.py` | EDA + descriptive + DiD/OLS |
| `causal_ml.py` | RDD + Double ML + HTE + Bootstrap |
| `synthetic_control.py` | SC + EconML + Rosenbaum + MC |
| `dowhy_refutation.py` | DoWhy DAG + placebo refutation |
| `fraud_detection.py` | Province-level Z + KL + low-variance |
| `cluster_cheat_detection.py` | Student K-window single-subject |
| `clustering_detection.py` | DBSCAN multi-subject high-score |
| `province_mapping.py` | Crosswalk 63→34 provinces |

← [Index](index.md) | → [01 Data Context](01_data_context.md)
