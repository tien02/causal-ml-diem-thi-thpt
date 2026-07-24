# Phân tích Nhân quả — Điểm thi THPT Việt Nam (2021–2026)

> **Causal Inference on Vietnam National High School Exam Scores**
>
> 5.38 triệu bản ghi · 5 năm (2021, 2022, 2024, 2025, 2026) · 11 chương phân tích

---

## Kết quả chính

| Finding | Giá trị | Phương pháp |
|---------|---------|-------------|
| **CT2018 ATE Toán** | **−1.65 pts** [−1.60, −1.73] | RDD / DML / CausalForest / SC / DoWhy |
| Rural penalty (HTE) | −0.34 pts thêm | CausalForest, p < 0.001 |
| Urban premium | +0.463 pts (debiased) | Double ML |
| COVID impact | **Không significant** [−0.081, +0.004] | Bootstrap DiD |
| Sensitivity | Γ\* = **6.0×** | Rosenbaum Bounds |
| Fraud flag 2026 | Hưng Yên Z = +2.25 | Anomaly Detection |

> **4 phương pháp độc lập hội tụ: CT2018 = −1.65 ± 0.06 pts** — bằng chứng causal mạnh nhất trong bộ dữ liệu.

---

## Cấu trúc dự án

```
.
├── analysis.py              # DiD, OLS, KDE, Urban/Rural, Chuyên school, Province merger
├── causal_ml.py             # RDD, Double ML, HTE, Bootstrap
├── fraud_detection.py       # Anomaly detection 2026 (Z-score, KL divergence)
├── cluster_cheat_detection.py       # K-Window sliding (consecutive SBD, high scores)
├── clustering_detection.py          # DBSCAN multi-subject (spatial + score alignment)
├── synthetic_control.py     # Synthetic Control, EconML (LinearDML/CausalForestDML),
│                            #   Rosenbaum Bounds, Monte Carlo sensitivity
├── dowhy_refutation.py      # DoWhy DAG + refutation tests (placebo, RCC, subset)
├── province_mapping.py      # Crosswalk 63 → 34 tỉnh (sáp nhập 2025)
├── figures/                 # 35+ figures (git LFS)
└── report/                  # 12 chapters + FULL_REPORT.md
    ├── index.md
    └── _chapters/
        ├── 00_executive_summary.md
        ├── 01_data_context.md
        ├── ...
        ├── 11_conclusions.md
        ├── 12_clustering_fraud_detection.md
        └── FULL_REPORT.md
```

---

## Pipeline phân tích

```
Data (5.38M records)
    │
    ├── analysis.py
    │     ├── COVID DiD (2021→2022)            [Chapter 2]
    │     ├── Urban/Rural gap (KDE, OLS)        [Chapter 3]
    │     ├── Chuyên school effect              [Chapter 4]
    │     ├── Local policy (fee exemption)      [Chapter 5]
    │     ├── CT2018 descriptive                [Chapter 6]
    │     └── Province merger crosswalk         [Chapter 7]
    │
    ├── fraud_detection.py
    │     └── Z-score, KL divergence 2026       [Chapter 8]
    │
    ├── causal_ml.py
    │     ├── RDD (within-2025 cohort split)    [Chapter 9]
    │     ├── Double ML (5-fold, manual)
    │     ├── HTE by urban tier
    │     └── Bootstrap cluster DiD
    │
    ├── synthetic_control.py
    │     ├── SCM (33 provinces, pre: 2021/22/24)[Chapter 10]
    │     ├── LinearDML + CausalForestDML
    │     ├── Rosenbaum Bounds (Γ* = 6.0)
    │     └── Monte Carlo sensitivity (Γ = 2)
    │
    └── dowhy_refutation.py
          ├── Causal DAG (GML)                  [Chapter 11]
          ├── Backdoor identification
          └── Refutation: placebo / RCC / subset
```

---

## Yêu cầu & Hướng dẫn cài đặt

### ⚡ Cách nhanh nhất (0 effort)

```bash
./setup.sh          # Cài đặt dependencies + kiểm tra dữ liệu
python analysis.py  # Chạy phân tích
```

👉 **[SETUP.md](SETUP.md)** — Chi tiết đầy đủ (cài đặt, hướng dẫn, khắc phục sự cố)

**Dữ liệu:** Đặt file CSV vào `GraduationExamScoreProcessing/Results/<năm>/`. Nguồn: [tien02/GraduationExamScoreProcessing](https://github.com/tien02/GraduationExamScoreProcessing).

---

## Chạy phân tích

```bash
python analysis.py           # Descriptive + DiD + province mapping
python fraud_detection.py    # Anomaly detection 2026
python causal_ml.py          # RDD + Double ML + HTE
python synthetic_control.py  # SCM + EconML + sensitivity
python dowhy_refutation.py   # DoWhy DAG + refutation
```

Figures ghi vào `figures/`. Xem **[SETUP.md](SETUP.md)** để chi tiết về output mỗi script.

---

## CT2018 — 5 methods hội tụ

| Method | ATE Toán | Ghi chú |
|--------|----------|---------|
| RDD | −1.689 | Sharp cutoff, within-2025 cohort |
| Double ML (manual) | −1.690 | 5-fold cross-fitting |
| LinearDML (econml) | −1.720 | GBM nuisance, parametric CATE |
| CausalForestDML | −1.727 | Non-parametric CATE |
| Synthetic Control | −1.602 | 33 provinces, COVID pre-trend caveat |
| DoWhy (backdoor LR) | −1.675 | DAG identification |
| **Consensus** | **−1.65 ± 0.06** | Rosenbaum Γ\* = 6.0 |

### Heterogeneous Treatment Effects

| Urban Tier | CATE CT2018 |
|------------|-------------|
| Đô thị lớn (HN, HCM) | −1.42 đến −1.52 pts |
| Đô thị vừa | −1.41 đến −1.59 pts |
| **Tỉnh lẻ / Nông thôn** | **−1.63 đến −1.76 pts** |

Không có học sinh nào có CATE > 0 (CausalForest, n=200k).

---

## Hàm ý chính sách

1. **[KHẨN CẤP]** Tập huấn giáo viên nông thôn — CT2018 thêm −0.34 pts cho rural (p<0.001)
2. **[KHẨN CẤP]** Monitor ATE CT2018 năm 2026 — kiểm tra adaptation curve
3. **[KHẨN CẤP]** Điều tra Hưng Yên 2026 — Z=+2.25, n=42k, khi toàn quốc sụt
4. **[TRUNG BÌNH]** Phát hành bộ đề mẫu CT2018 — CATE < 0 với 100% học sinh
5. **[TRUNG BÌNH]** Báo cáo song song 34 đơn vị mới + crosswalk 63 đơn vị cũ

---

## Báo cáo

- **[report/index.md](report/index.md)** — Mục lục 12 chương
- **[report/_chapters/FULL_REPORT.md](report/_chapters/FULL_REPORT.md)** — Báo cáo tổng hợp toàn bộ

---

## Giới hạn

| Giới hạn | Mức |
|---------|-----|
| CT2006/2025 = lưu ban → selection bias | MEDIUM |
| SCM placebo fail do COVID 2022 dip | MEDIUM |
| Fraud detection: chỉ 3 data points | HIGH |
| Toán 2026 không bắt buộc → self-selected cohort | HIGH |
| Không có panel data cá nhân | HIGH |

---

*Dữ liệu thô không được bao gồm trong repo. Nguồn: [tien02/GraduationExamScoreProcessing](https://github.com/tien02/GraduationExamScoreProcessing)*
