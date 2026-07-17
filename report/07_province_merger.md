# Chapter 7 — Sáp nhập Tỉnh 2025: Tác động đến Dữ liệu & Phân tích

← [06 Curriculum](06_curriculum_2018.md) | → [08 Fraud](08_fraud_detection.md)

---

## 7.1 Bối cảnh

Đầu năm 2025, Việt Nam thực hiện sáp nhập hành chính lớn nhất kể từ 1975:

| Trước (đến 2025) | Sau (từ 2026) |
|-----------------|--------------|
| 63 tỉnh/thành | **34 tỉnh/thành** |
| Mã SBD thi: 01–64 (tuần tự) | Mã SBD thi: **mã hành chính chính thức** |

Kỳ thi 2026 là kỳ đầu tiên dùng hệ thống mã mới — toàn bộ dữ liệu tỉnh từ 2021–2025 **không thể so sánh trực tiếp** với 2026 nếu không có crosswalk.

---

## 7.2 Vấn đề dữ liệu phát hiện

```
2022 data: codes ['01', '02', '03', ... '63', '64']  → 63 tỉnh
2026 data: codes ['01', '04', '08', ... '91', '92', '96']  → 34 tỉnh
```

Codes như `66, 68, 75, 79, 80, 86, 91, 92` **không tồn tại** trong hệ cũ. Mapping naïve → sai hoàn toàn.

---

## 7.3 Crosswalk 63 → 34 tỉnh

File `province_mapping.py` xây crosswalk đầy đủ. Các merger tiêu biểu:

| Mã mới 2026 | Tỉnh mới | Các tỉnh cũ (mã exam cũ) |
|-------------|---------|--------------------------|
| **01** | Hà Nội | Hà Nội (1) |
| **37** | Ninh Bình (merged) | Hà Nam (22) + Thái Bình (25) + Nam Định (26) + Ninh Bình (27) |
| **40** | Nghệ An (merged) | Nghệ An (29) + Hà Tĩnh (30) |
| **75** | Đồng Nai (merged) | Kon Tum (41) + Bình Phước (46) + Đồng Nai (48) + Tây Ninh (49) + Bà Rịa-VT (63) |
| **79** | TP.HCM (merged) | TP.HCM (2) + Bình Dương (47) |
| **92** | Cần Thơ (merged) | Cần Thơ (58) + Hậu Giang (59) + Sóc Trăng (60) + Bạc Liêu (61) |
| **14** | Sơn La (merged) | Sơn La (14) + **Hòa Bình (16)** ⚠️ |
| **4** | Cao Bằng (merged) | **Hà Giang (5)** ⚠️ + Cao Bằng (6) + Bắc Kạn (11) |

> ⚠️ Các tỉnh gian lận 2018 (Hà Giang, Hòa Bình) đã bị hấp thụ vào đơn vị mới.

---

## 7.4 Ảnh hưởng đến phân tích

### 7.4.1 So sánh theo tỉnh 2024 vs 2026 — không hợp lệ trực tiếp

| Tỉnh cũ 2024 | n (2024) | Tỉnh mới 2026 | n (2026) |
|-------------|---------|--------------|---------|
| Thái Bình #1 Toán | 21,653 | Ninh Bình merged [37] | 47,818 |
| Nam Định | 22,403 | (merged vào 37) | — |
| Ninh Bình | 11,594 | (merged vào 37) | — |
| Hà Nam | 9,447 | (merged vào 37) | — |

Tỉnh [37] năm 2026 đứng **#1 Toán toàn quốc** (6.265) — nhưng đây là trung bình của 4 tỉnh cũ, không phải Ninh Bình đơn lẻ.

### 7.4.2 Urban tier bị pha loãng

| Đơn vị | Thành phần | Hệ quả |
|--------|-----------|--------|
| TP.HCM [79] 2026 | TP.HCM cũ + Bình Dương | Mean thấp hơn do pha loãng với tỉnh công nghiệp |
| Hải Phòng [31] 2026 | Hải Phòng + Hưng Yên + Hải Dương | Urban T2 bị pha loãng với 2 tỉnh nông thôn |

### 7.4.3 Confounder đồng thời với CT2018

Năm 2026 xảy ra **đồng thời** hai thay đổi lớn:
- Chương trình mới CT2018 (năm 2)
- Hệ thống tỉnh mới (34 đơn vị)

Không thể tách riêng effect nếu không harmonize dữ liệu.

---

## 7.5 Giải pháp: Province Harmonization

`analysis.py` đã được cập nhật — thêm cột `province_harmonized` cho mọi năm:

```python
# 2021–2025: map old code → new 2026 admin code
df['province_harmonized'] = df['province'].map(OLD_TO_NEW_2026)

# 2026: already in new codes
df['province_harmonized'] = df['province'].astype('Int64')
```

FIG 10 heatmap và cross-year analysis dùng `province_harmonized` → đơn vị địa lý nhất quán.

---

## 7.6 Aggregate Bias — Heterogeneity bị che giấu

Sáp nhập tỉnh tạo ra **aggregate bias**: trung bình tỉnh mới che giấu bất bình đẳng nội tỉnh.

| Tỉnh mới | Tỉnh cũ mạnh nhất | Tỉnh cũ yếu nhất | Spread bị che |
|---------|-----------------|----------------|--------------|
| Ninh Bình [37] | Thái Bình (7.26) | Hà Nam (~6.3) | ~0.96 điểm |
| Sơn La [14] ⚠️ | Hòa Bình (~7.0 năm 2024) | Sơn La (~5.24) | ~1.76 điểm |
| Đồng Nai [75] | Đồng Nai (~6.3) | Kon Tum (~5.3) | ~1.0 điểm |

> 📌 **Sơn La [14] đặc biệt:** Hòa Bình (tỉnh điểm cao, fraud 2018) gộp với Sơn La (tỉnh thấp nhất). Mean 2026 = 4.245 — thấp nhất toàn quốc, che giấu bất đồng đều nội tỉnh lớn nhất.

---

## 7.7 Kết luận

| Vấn đề | Mức độ | Đã xử lý |
|--------|--------|----------|
| Province code mismatch 2026 | **CRITICAL** | ✅ Crosswalk 63→34 |
| Urban tier sai cho 2026 | HIGH | ✅ `urban_tier_2026()` |
| HN+HCM detection sai | HIGH | ✅ `{1,79}` thay `{1,2}` |
| FIG 10 heatmap mixed codes | HIGH | ✅ `province_harmonized` |
| Aggregate bias | MEDIUM | ⚠️ Documented, không fix được |
| Fraud signal diluted | MEDIUM | ⚠️ Xem Chapter 8 |

> 📊 Xem: `fig10_heatmap_province_year.png` (đã harmonized)

← [06 Curriculum](06_curriculum_2018.md) | → [08 Fraud](08_fraud_detection.md)
