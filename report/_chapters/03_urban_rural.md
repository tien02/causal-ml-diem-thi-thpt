# Chapter 3 — Khoảng cách Đô thị / Nông thôn

← [02 COVID](02_covid_impact.md) | → [04 Chuyên](04_chuyen_school.md)

---

## 3.1 Điểm trung bình theo tier đô thị (2024 + 2026)

| Tier | N | Toán TB | Ngữ văn | Ngoại ngữ | % Toán ≥ 9 |
|------|---|---------|---------|-----------|-----------|
| Đô thị lớn | 318,115 | **6.582** | — | — | **3.7%** |
| Đô thị vừa | 108,868 | 6.235 | — | — | 3.1% |
| Tỉnh lẻ/Nông thôn | 1,811,067 | **5.913** | — | — | **2.6%** |

**Khoảng cách đô thị lớn vs nông thôn: 0.669 điểm Toán** (~7% thang điểm).

---

## 3.2 OLS Regression — Định lượng hiệu ứng đô thị

```
Toán = 5.913 + 0.512·urban_large + 0.197·urban_mid + ε     (2024)
```

| Biến | Hệ số | p-value |
|------|-------|---------|
| Hằng số (nông thôn) | 5.913 | < 10⁻¹⁰⁰ |
| `urban_large` (HN, HCM) | **+0.512** | **≈ 0** |
| `urban_mid` (HP, ĐN, Huế, CT) | **+0.197** | **2.3 × 10⁻²⁰⁰** |
| **R²** | **0.016** | — |

> 📌 R² = 0.016 rất nhỏ — địa lý chỉ giải thích **1.6% phương sai** điểm. Phần lớn phương sai đến từ năng lực cá nhân, gia đình, trường học. Nhưng hệ số β có ý nghĩa nhân quả thực sự: **sinh ra ở đô thị lớn = +0.51 điểm Toán**, kiểm soát các yếu tố khác.

---

## 3.3 Ranking tỉnh theo Toán TB (2024)

### Top 15

| Hạng | Tỉnh/Thành | Điểm TB | % ≥ 9 | Ghi chú |
|------|-----------|---------|-------|---------|
| 1 | **Thái Bình** | **7.262** | 2.25% | ⭐ Surprise #1 |
| 2 | **Đắk Nông** | **7.132** | 2.18% | ⭐ Surprise #2 |
| 3 | Bắc Giang | 7.001 | 2.49% | |
| 4 | TP.HCM | 6.984 | 1.37% | |
| 5 | Hòa Bình | 6.950 | 1.84% | |
| 6 | Ninh Bình | 6.949 | 2.04% | |
| 7 | Nam Định | 6.906 | 2.07% | Tỉnh chuyên mạnh |
| 8 | Hải Dương | 6.894 | 1.51% | |
| 9 | Bến Tre | 6.889 | 0.91% | |
| 10 | Hải Phòng | 6.794 | 1.54% | |
| 11 | **Hà Nội** | **6.747** | **1.92%** | Thủ đô chỉ hạng 11 |

### Bottom 5

| Hạng | Tỉnh/Thành | Điểm TB | % ≥ 9 |
|------|-----------|---------|-------|
| 60 | Sơn La | 5.241 | 0.26% |
| 61 | Bắc Kạn | 5.330 | 0.22% |
| 62 | Cà Mau | 5.279 | 0.32% |
| 63 | Cao Bằng | 5.102 | 0.27% |
| 64 | **Hà Giang** | **4.585** | **0.16%** |

**Khoảng cách Thái Bình vs Hà Giang: 2.677 điểm Toán** — gần bằng 1/3 thang điểm.

---

## 3.4 Tại sao Thái Bình đứng đầu?

Thái Bình là tỉnh đồng bằng sông Hồng, **không phải đô thị lớn**, nhưng có:
- Mật độ dân số cao + văn hóa học tập truyền thống vùng đồng bằng Bắc Bộ
- Không có nhiều trường ĐH tại chỗ → áp lực thi cử cao hơn để thoát tỉnh
- Tương tự: Nam Định, Ninh Bình, Hà Nam đều vào top 10

> 📌 **Hypothesis:** Các tỉnh đồng bằng Bắc Bộ không có đô thị lớn nhưng có văn hóa học tập mạnh → điểm Toán cao hơn cả thành phố. Hiện tượng này không tìm thấy ở tỉnh miền Nam hay Tây Nguyên.

---

## 3.5 Gap đô thị–nông thôn theo năm

| Năm | Toán TB cả nước | HN + HCM | Gap |
|-----|----------------|----------|-----|
| 2021 | 6.615 | 7.048 | **+0.432** |
| 2022 | 6.466 | 6.902 | **+0.436** |
| 2024 | 6.447 | 6.853 | **+0.406** |
| 2025 | 4.783 | 5.265 | **+0.482** |
| 2026 | 5.652 | 6.164 | **+0.512** |

> 📌 Gap **nới rộng từ 0.432 → 0.512** qua 5 năm. Đặc biệt tăng mạnh trong 2025–2026 (năm chuyển đổi chương trình): đô thị thích nghi nhanh hơn nông thôn.

---

## 3.6 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| Đô thị có điểm cao hơn không? | **Có** — +0.51 điểm Toán (đô thị lớn), kiểm định p≈0 |
| Khoảng cách có tăng không? | **Có** — từ 0.432 (2021) lên 0.512 (2026) |
| Đô thị nào dẫn đầu? | **Thái Bình** — surprise! Không phải HN/HCM |
| Tỉnh nào tệ nhất? | **Hà Giang** — 4.585 điểm TB, vùng núi dân tộc thiểu số |

> 📊 Xem: `fig4_urban_rural_2024.png` · `fig5_province_ranking_2024.png` · `fig9_hn_hcm_gap_trend.png` · `fig10_heatmap_province_year.png`

← [02 COVID](02_covid_impact.md) | → [04 Chuyên](04_chuyen_school.md)
