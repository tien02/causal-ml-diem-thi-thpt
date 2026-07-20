# Chapter 1 — Tổng quan Dữ liệu & Phương pháp

← [Index](index.md) | → [02 COVID](02_covid_impact.md)

---

## 1.1 Nguồn dữ liệu

| Năm | Số thí sinh | Ghi chú |
|-----|-------------|---------|
| 2021 | 988,013 | Có cột `Cum_thi` = mã tỉnh trực tiếp |
| 2022 | 995,441 | Mã tỉnh = 2 chữ số đầu SBD |
| 2024 | 1,061,605 | Tương tự 2022 |
| 2025 CT2006 | 22,090 | **Chương trình CŨ** — nhóm cuối cùng (lưu ban/thi lại) |
| 2025 CT2018 | 1,131,136 | **Chương trình MỚI** — năm đầu tiên |
| 2026 | 1,208,863 | Chương trình mới — năm thứ 2 |
| **Tổng** | **5,385,058** | |

> Năm 2023 không có trong bộ dữ liệu.

---

## 1.2 Phân loại biến

### Tier đô thị

| Tier | Tỉnh/Thành |
|------|-----------|
| Đô thị lớn | Hà Nội (01), TP.HCM (02) |
| Đô thị vừa | Hải Phòng (03), Đà Nẵng (04), Huế (33), Cần Thơ (58) |
| Tỉnh lẻ/Nông thôn | 58 tỉnh còn lại |

### Tỉnh chuyên mạnh (proxy)

Dựa trên lịch sử kết quả thi HSG quốc gia:
> Hà Nội · TP.HCM · Nam Định · Nghệ An · Hà Tĩnh · Hải Phòng · Quảng Ninh · Thanh Hóa

### Tỉnh miễn phí thi

> Hà Nội (01) · TP.HCM (02) · Hải Phòng (03)

---

## 1.3 Phương pháp

**Difference-in-Differences (DiD)**
```
DiD = (Đô thị_2024 − Đô thị_2021) − (Nông thôn_2024 − Nông thôn_2021)
```

**OLS Regression**
```
Điểm_Toán = β₀ + β₁·urban_large + β₂·urban_mid + ε
```

**Chỉ số tập trung top-scorer**
```
Concentration = (% điểm≥9 từ tỉnh X) / (% thí sinh từ tỉnh X)
```
> Nếu > 1: tỉnh X sản xuất top-scorer nhiều hơn tỷ trọng dân số thi.

---

## 1.4 Điểm trung bình quốc gia theo năm

| Năm | N | Toán | Ngữ văn | Ngoại ngữ | Vật lý | Hóa học | Sinh học | Lịch sử | Địa lý | GDCD |
|-----|---|------|---------|-----------|--------|---------|---------|---------|--------|------|
| 2021 | 988K | 6.615 | 6.471 | 5.852 | 6.566 | 6.630 | 5.516 | 4.973 | 6.956 | 8.376 |
| 2022 | 995K | 6.466 | 6.508 | 5.158 | 6.724 | 6.704 | 5.019 | 6.344 | 6.678 | 8.033 |
| 2024 | 1.06M | 6.447 | 7.231 | 5.522 | 6.667 | 6.681 | 6.284 | 6.570 | 7.194 | 8.157 |
| 2025 CT2018 | 1.13M | **4.783** | 7.002 | 5.406 | 6.985 | 6.065 | 5.778 | 6.519 | 6.628 | 7.691 |
| 2026 | 1.21M | 5.652 | 6.497 | 5.093 | 5.559 | 6.284 | 5.837 | 6.190 | 5.101 | **5.023** |

> ⚠️ Toán 2025 = 4.783: sốc chương trình mới. GDCD 2026 = 5.023 do đổi sang môn KTPL hoàn toàn khác.

← [Index](index.md) | → [02 COVID](02_covid_impact.md)
