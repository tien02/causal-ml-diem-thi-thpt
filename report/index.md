# Phân tích Nhân quả — Điểm thi THPT Việt Nam (2021–2026)

> **Dữ liệu:** 5.38 triệu bản ghi · 5 năm (2021, 2022, 2024, 2025, 2026)
> **Phương pháp:** DiD, OLS, Mann-Whitney U, KDE · RDD, Double ML, HTE, Bootstrap, Anomaly Detection · Synthetic Control, CausalForestDML, Rosenbaum Bounds · DoWhy DAG, Refutation Tests

---

## Mục lục

| # | Chủ đề | File |
|---|--------|------|
| 0 | Tóm tắt Điều hành | [_chapters/00_executive_summary.md](_chapters/00_executive_summary.md) |
| 1 | Bối cảnh Dữ liệu & Sáp nhập Tỉnh | [_chapters/01_data_context.md](_chapters/01_data_context.md) |
| 2 | Cú sốc COVID — Tác động ngoại sinh | [_chapters/02_covid_impact.md](_chapters/02_covid_impact.md) |
| 3 | Khoảng cách Đô thị / Nông thôn | [_chapters/03_urban_rural.md](_chapters/03_urban_rural.md) |
| 4 | Hiệu ứng Trường Chuyên | [_chapters/04_chuyen_school.md](_chapters/04_chuyen_school.md) |
| 5 | Tác động Chính sách Địa phương | [_chapters/05_local_policy.md](_chapters/05_local_policy.md) |
| 6 | Chương trình 2018 — Có giúp điểm tốt hơn? | [_chapters/06_curriculum_2018.md](_chapters/06_curriculum_2018.md) |
| 7 | Sáp nhập Tỉnh 2025 — Tác động dữ liệu | [_chapters/07_province_merger.md](_chapters/07_province_merger.md) |
| 8 | Phát hiện Gian lận — Anomaly Detection 2026 | [_chapters/08_fraud_detection.md](_chapters/08_fraud_detection.md) |
| 9 | Causal ML — RDD, Double ML, HTE, Bootstrap | [_chapters/09_causal_ml.md](_chapters/09_causal_ml.md) |
| 10 | Synthetic Control, EconML & Monte Carlo Sensitivity | [_chapters/10_synthetic_control.md](_chapters/10_synthetic_control.md) |
| 11 | Kết luận Tổng hợp & Hàm ý Chính sách | [_chapters/11_conclusions.md](_chapters/11_conclusions.md) |
| 12 | Clustering Cheat Detection — K-Window & DBSCAN 2026 | [_chapters/12_clustering_fraud_detection.md](_chapters/12_clustering_fraud_detection.md) |

---

## 5 Insight lớn nhất

1. **CT2018 = −1.69 pts Toán causal** (RDD) — cú sốc lớn hơn COVID × 10.
2. **Rural bị CT2018 nặng hơn Urban 0.34 pts** (HTE, p<0.001) — khoảng cách đô thị-nông thôn gia tốc.
3. **Urban premium thực = +0.463 pts** (Double ML) — OLS underestimate do chuyên tỉnh suppress effect.
4. **Hưng Yên [33] fraud flag 2026** — Z=+2.25, vượt trend khi toàn quốc sụt, n=42k.
5. **COVID DiD không significant** — Bootstrap 95% CI [−0.081, +0.004]; kết quả Chapter 2 fragile.
6. **COVID hại ngoại ngữ nhất** — 51% thí sinh dưới 5 điểm năm 2022; phục hồi chậm nhất.
7. **Thái Bình đứng đầu Toán** (7.262) — nay merged vào Ninh Bình [37], tỉnh #1 hệ mới.
8. **Trường chuyên = 1.46× top-scorer factory** — 31.7% thí sinh, đóng góp 46.2% điểm Toán ≥ 9.
9. **4 methods hội tụ: CT2018 ATE = −1.65 ± 0.06 pts** — RDD/DML/CausalForest/SC đều cho −1.60 đến −1.73.
10. **Rosenbaum Γ\* = 6.0** — cần biến nhiễu ẩn mạnh gấp 6× mới overturn; Monte Carlo 100% negative dưới Γ=2.
11. **DoWhy ATE = −1.675, placebo p=0.98** — 5 methods [−1.60, −1.73] nhất quán; placebo shuffle → −0.002 xác nhận effect thật.

---

## Figures

| File | Nội dung |
|------|----------|
| `fig1_covid_mean_scores.png` | Điểm TB 3 môn chính theo năm |
| `fig2_covid_kde_toan.png` | KDE Toán: 2021 vs 2022 vs 2024 |
| `fig3_did_covid_urban_rural.png` | DiD phục hồi đô thị/nông thôn |
| `fig4_urban_rural_2024.png` | KDE 3 môn theo tier đô thị |
| `fig5_province_ranking_2024.png` | Ranking tỉnh theo Toán TB |
| `fig6_chuyen_top_scorer_rate.png` | % thí sinh ≥ 9 Toán theo tỉnh |
| `fig7_chuyen_score_dist.png` | KDE: tỉnh chuyên mạnh vs tỉnh khác |
| `fig8_fee_exemption_effect.png` | Phân phối: tỉnh miễn phí vs đóng phí |
| `fig9_hn_hcm_gap_trend.png` | Trend gap HN+HCM vs toàn quốc |
| `fig10_heatmap_province_year.png` | Heatmap tỉnh × năm |
| `figA_curriculum_2024_vs_2026.png` | CT2006-2024 vs CT2018-2026 theo môn |
| `figB_curriculum_toan_kde.png` | KDE Toán 4 nhóm (2 chương trình × 2 năm) |
| `figC_delta_heatmap_province_subject.png` | Delta điểm (2026−2024) theo tỉnh × môn |
| `sc_main.png` | SC trajectory quốc gia + province-level gaps |
| `sc_permutation.png` | Permutation distribution (p=0.32, all-treated caveat) |
| `econml_cate.png` | CausalForest CATE distribution + violin by urban tier |
| `mc_sensitivity.png` | Rosenbaum bounds + Monte Carlo Γ=2 sensitivity |
| `dowhy_dag.png` | Causal DAG: CT2018 → Toán, backdoor criterion |
| `dowhy_refutation.png` | Refutation tests: placebo PASS, subset PASS |
