# Chapter 1 — Bối cảnh Dữ liệu, Sáp nhập Tỉnh & Chương trình

← [00 Summary](00_executive_summary.md) | → [02 COVID](02_covid_descriptive.md)

---

## 1.1 Nguồn dữ liệu

| Năm | Số thí sinh | Ghi chú |
|-----|-------------|---------|
| 2021 | 988,013 | Có cột `Cum_thi` = mã tỉnh trực tiếp |
| 2022 | 995,441 | Mã tỉnh = 2 chữ số đầu SBD |
| 2024 | 1,061,605 | Tương tự 2022 |
| 2025 CT2006 | 22,090 | **Chương trình CŨ** — nhóm cuối (lưu ban/thi lại) |
| 2025 CT2018 | 1,131,136 | **Chương trình MỚI** — năm đầu tiên |
| 2026 | 1,208,863 | CT2018 năm thứ 2 |
| **Tổng** | **5,385,058** | |

> Năm 2023 không có trong bộ dữ liệu.

### Điểm trung bình quốc gia theo năm

| Năm | Toán | Ngữ văn | Ngoại ngữ | Vật lý | Hóa học | Sinh học | Lịch sử | Địa lý | GDCD/KTPL |
|-----|------|---------|-----------|--------|---------|---------|---------|--------|-----------|
| 2021 | 6.615 | 6.471 | 5.852 | 6.566 | 6.630 | 5.516 | 4.973 | 6.956 | 8.376 |
| 2022 | 6.466 | 6.508 | 5.158 | 6.724 | 6.704 | 5.019 | 6.344 | 6.678 | 8.033 |
| 2024 | 6.447 | 7.231 | 5.522 | 6.667 | 6.681 | 6.284 | 6.570 | 7.194 | 8.157 |
| 2025 CT2018 | **4.783** | 7.002 | 5.406 | 6.985 | 6.065 | 5.778 | 6.519 | 6.628 | 7.691 |
| 2026 | 5.652 | 6.497 | 5.093 | 5.559 | 6.284 | 5.837 | 6.190 | 5.101 | **5.023** |

> ⚠️ Toán 2025 = 4.783: sốc chương trình mới. GDCD 2026 = 5.023 do đổi sang môn KTPL hoàn toàn khác.

---

## 1.2 Phân loại biến

### Tier đô thị

| Tier | Tỉnh/Thành |
|------|-----------|
| Đô thị lớn | Hà Nội (01), TP.HCM (79 sau sáp nhập / 02 cũ) |
| Đô thị vừa | Hải Phòng (31), Đà Nẵng (48), Huế (46), Cần Thơ (92) |
| Tỉnh lẻ/Nông thôn | còn lại |

### Tỉnh chuyên mạnh (proxy)

> Hà Nội · TP.HCM · Nam Định · Nghệ An · Hà Tĩnh · Hải Phòng · Quảng Ninh · Thanh Hóa

### Tỉnh miễn phí thi

> Hà Nội (01) · TP.HCM (02/79) · Hải Phòng (03/31)

---

## 1.3 Sáp nhập Tỉnh 2025 — Vấn đề dữ liệu Critical

Đầu năm 2025, Việt Nam thực hiện sáp nhập hành chính lớn nhất kể từ 1975: **63 tỉnh → 34 tỉnh**. Kỳ thi 2026 là kỳ đầu tiên dùng hệ thống mã mới.

```
2022 data: codes ['01', '02', ... '63', '64']  → 63 tỉnh
2026 data: codes ['01', '04', '08', ... '91', '92', '96']  → 34 tỉnh
```

Codes như `66, 68, 75, 79, 80, 86, 91, 92` **không tồn tại** trong hệ cũ. Mapping naïve → sai hoàn toàn.

### Crosswalk 63 → 34 (file `province_mapping.py`)

| Mã mới 2026 | Tỉnh mới | Các tỉnh cũ |
|-------------|---------|-------------|
| **01** | Hà Nội | Hà Nội (1) |
| **37** | Ninh Bình (merged) | Hà Nam (22) + Thái Bình (25) + Nam Định (26) + Ninh Bình (27) |
| **40** | Nghệ An (merged) | Nghệ An (29) + Hà Tĩnh (30) |
| **75** | Đồng Nai (merged) | Kon Tum (41) + Bình Phước (46) + Đồng Nai (48) + Tây Ninh (49) + Bà Rịa-VT (63) |
| **79** | TP.HCM (merged) | TP.HCM (2) + Bình Dương (47) |
| **92** | Cần Thơ (merged) | Cần Thơ (58) + Hậu Giang (59) + Sóc Trăng (60) + Bạc Liêu (61) |
| **14** | Sơn La (merged) | Sơn La (14) + **Hòa Bình (16)** ⚠️ |
| **4** | Cao Bằng (merged) | **Hà Giang (5)** ⚠️ + Cao Bằng (6) + Bắc Kạn (11) |

> ⚠️ Các tỉnh gian lận 2018 (Hà Giang, Hòa Bình) đã bị hấp thụ vào đơn vị mới.

### Hệ quả phân tích

| Vấn đề | Mức độ | Giải pháp |
|--------|--------|-----------|
| Province code mismatch 2026 | CRITICAL | ✅ Crosswalk `OLD_TO_NEW_2026` |
| Urban tier sai cho 2026 | HIGH | ✅ `urban_tier_2026()` |
| Heatmap mixed codes | HIGH | ✅ `province_harmonized` |
| **Aggregate bias** | MEDIUM | ⚠️ Documented, không fix được |

**Aggregate bias example:** Thái Bình (7.26 Toán 2024) + Hà Nam (~6.3) → Ninh Bình [37] mean 2026 = 6.265, che spread ~0.96 điểm. Sơn La [14] che spread lớn nhất: 1.76 điểm (Hòa Bình cao + Sơn La thấp).

---

## 1.4 Hai chương trình giáo dục: CT2006 → CT2018

| Năm | Sự kiện |
|-----|---------|
| 2024 | Năm cuối cùng hoàn toàn CT2006 |
| 2025 | **Năm chuyển tiếp:** 22K HS CT2006 + 1.13M HS CT2018 |
| 2026 | Năm đầu tiên **hoàn toàn** CT2018 |

**Natural experiment sạch nhất (Chapter 5 dùng):** Năm 2025 có 2 nhóm thi **cùng năm, cùng kỳ** nhưng khác chương trình — loại bỏ yếu tố thời gian.

### So sánh baseline: CT2006-2024 vs CT2018-2026

| Môn | 2024 (CT2006) | 2026 (CT2018) | Δ |
|-----|--------------|--------------|---|
| **Toán** | 6.447 | 5.652 | **−0.796** |
| **Ngữ văn** | 7.231 | 6.497 | **−0.734** |
| **Vật lý** | 6.667 | 5.559 | **−1.108** |
| Hóa học | 6.681 | 6.284 | −0.396 |
| Sinh học | 6.284 | 5.837 | −0.447 |
| Ngoại ngữ | 5.522 | 5.093 | −0.429 |
| Lịch sử | 6.570 | 6.190 | −0.380 |
| **Địa lý** | 7.194 | 5.101 | **−2.093** |
| **GDCD→KTPL** | 8.157 | 5.023 | **−3.133** ⚠️ |

> ⚠️ GDCD→KTPL không phản ánh năng lực — 2 môn khác nhau hoàn toàn.

### Phục hồi năm 2 (CT2018)

| Band Toán | 2024 CT2006 | 2025 CT2018 (năm 1) | 2026 CT2018 (năm 2) |
|-----------|-------------|---------------------|---------------------|
| < 5 (Trượt) | 17.5% | **56.4%** | **38.0%** |
| 5–6.5 (TB) | 27.6% | 26.2% | 25.6% |
| 6.5–8 (Khá) | 35.9% | 12.0% | 20.8% |
| ≥ 8 (Giỏi) | 19.0% | 5.5% | 15.6% |

> 📌 Năm 2 cải thiện đáng kể (+0.87 điểm Toán) — vẫn thấp hơn CT2006 ~0.8 điểm. Phân tích causal chi tiết: [Chapter 5](05_ct2018_causal_estimands.md).

---

## 1.5 Phương pháp phân tích (tổng quan)

| Lớp | Phương pháp | Chapter |
|-----|-------------|---------|
| Descriptive | DiD, OLS, Mann-Whitney U, KDE | 2, 3, 4 |
| Causal estimation | RDD, Double ML, HTE, CausalForestDML, SC, DoWhy | 5 |
| Sensitivity | Bootstrap, Rosenbaum Bounds, Monte Carlo, Placebo | 6 |
| Anomaly detection | Z-score, KL divergence, low-variance | 8 |
| Cluster detection | K-window (single-subject), DBSCAN (multi-subject) | 9, 10 |

> 📊 Xem: `fig10_heatmap_province_year.png` (đã harmonized) · `figA_curriculum_2024_vs_2026.png`

← [00 Summary](00_executive_summary.md) | → [02 COVID](02_covid_descriptive.md)
