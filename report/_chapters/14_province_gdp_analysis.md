# Chapter 14 — Kinh Tế Tỉnh (GRDP) và Kết Quả Thi

← [13 Monte Carlo](13_monte_carlo_adaptation_2025_2026.md)

---

## 14.1 Dữ liệu và Phương pháp

**Nguồn GRDP:** Tổng cục Thống kê (GSO) — GRDP bình quân đầu người 2022 theo giá hiện hành (triệu VND/người/năm), 63 tỉnh thành.

**Lý do chọn 2022:** Năm gần nhất có đủ dữ liệu 63 tỉnh; khoảng cách xếp hạng tỉnh ổn định qua các năm (thứ hạng không đổi đáng kể 2020–2024).

**Phạm vi phân tích:** 3 năm thi (2021, 2022, 2024); môn Toán là biến kết quả chính.

**Hai metric kết quả:**
- `mean_toan`: điểm trung bình — đo năng lực học sinh đại trà
- `pct_9plus`: tỉ lệ điểm ≥ 9 — đo mật độ học sinh xuất sắc (phục vụ phân tích tuyển sinh ĐH top)

---

## 14.2 Tổng quan GRDP 63 tỉnh

| Chỉ số | Giá trị |
|--------|---------|
| Min | 33.54 triệu VND (Hà Giang) |
| Median | ~66 triệu VND |
| Max | 335.47 triệu VND (Bà Rịa–Vũng Tàu) |
| Tỉ lệ max/min | **10×** |

Phân phối lệch phải mạnh — Bà Rịa–Vũng Tàu là outlier do kinh tế dầu khí. Phép biến đổi log phù hợp hơn cho hồi quy.

---

## 14.3 Tương quan GRDP × Điểm trung bình Toán

| Năm | r(GRDP, mean) | r(log GRDP, mean) |
|-----|---------------|-------------------|
| 2021 | 0.162 | **0.268** |
| 2022 | 0.154 | **0.263** |
| 2024 | 0.116 | **0.231** |

**Hai phát hiện:**

1. **Log-linear fit tốt hơn tuyến tính** — phù hợp giả thuyết marginal return giảm dần: đồng tiền giáo dục ở tỉnh nghèo có tác động lớn hơn tỉnh giàu.

2. **Correlation suy giảm theo năm** (0.268 → 0.231 trong 3 năm) — bất bình đẳng giáo dục theo kinh tế đang thu hẹp, nhưng chậm.

---

## 14.4 Tương quan GRDP × Tỉ lệ 9+ Toán

| Năm | r(GRDP, pct9) | r(log GRDP, pct9) |
|-----|---------------|-------------------|
| 2021 | 0.110 | 0.187 |
| 2022 | 0.101 | 0.174 |
| 2024 | 0.093 | **0.166** |

Khi dùng metric 9+, correlation **giảm thêm ~30%** so với mean. GRDP hầu như không giải thích được phân bố học sinh xuất sắc.

---

## 14.5 Phân tích Tứ phân vị GRDP (2024)

| Nhóm GRDP | % điểm 9+ Toán | Min | Max |
|-----------|----------------|-----|-----|
| Q1 (nghèo, <54tr) | 0.63% | 0.17% | 2.09% |
| Q2 (54–67tr) | 0.91% | 0.24% | 2.26% |
| Q3 (67–88tr) | 0.98% | 0.21% | 2.50% |
| Q4 (giàu, >88tr) | 0.97% | 0.23% | 1.94% |

**Phát hiện cốt lõi: Q3 ≈ Q4.** Vượt ngưỡng thu nhập trung bình (~67 triệu VND) là đủ điều kiện — giàu thêm không tạo ra thêm học sinh đạt 9+ Toán. Đây là hiệu ứng **ngưỡng bão hòa**, không phải quan hệ tuyến tính.

---

## 14.6 Hồi quy Cấp tỉnh: GRDP, Chuyên, Gian lận

```
pct_9plus = β₀ + β₁·log_GRDP + β₂·chuyen + β₃·fraud + ε
```

| Biến | Hệ số | p-value | Kết luận |
|------|-------|---------|---------|
| Hằng số | 0.169 | 0.818 | — |
| `log_grdp` | **+0.143** | **0.400** | ❌ Không có ý nghĩa thống kê |
| `chuyen` | **+0.755** | **0.001** | ✅ Có ý nghĩa mạnh |
| `fraud` | +0.047 | 0.889 | ❌ Không có ý nghĩa thống kê |
| **R²** | **0.189** | — | — |

Sau khi kiểm soát biến chuyên, GRDP **mất hẳn significance** (p=0.40). Signal kinh tế trong metric 9+ được hấp thụ hoàn toàn bởi hệ thống trường chuyên — các tỉnh giàu có nhiều trường chuyên hơn, nhưng đó là kênh truyền dẫn, không phải tác động trực tiếp của thu nhập.

So sánh với kết quả Chapter 3 (urban_tier regression trên mean_toan, p < 0.001): GRDP liên tục (continuous) kém dự báo hơn tier đô thị (categorical) khi xét top performer.

---

## 14.7 Phân tích Phần dư — Overperform / Underperform

### Tỉnh vượt kỳ vọng kinh tế

| Tỉnh | GRDP (tr VND) | % 9+ thực tế | Phần dư | Chuyên |
|------|---------------|--------------|---------|--------|
| Bắc Giang | 82 | **2.50%** | +1.61 | Không |
| Thái Bình | 60 | 2.26% | +1.44 | Không |
| Đắk Nông | 60 | 2.21% | +1.39 | Không |
| Nam Định | 49 | 2.09% | +1.31 | Có |
| Ninh Bình | 81 | 2.07% | +1.18 | Không |
| Hòa Bình | 65 | 1.86% | +1.02 | Không |

**Bắc Giang dẫn đầu cả nước** về tỉ lệ 9+ dù GRDP trung bình thấp (82 triệu). Cụm Đồng bằng Bắc Bộ (Thái Bình, Nam Định, Ninh Bình) có văn hóa học tập đặc thù — áp lực thi cử cao, gia đình đầu tư mạnh vào giáo dục bất kể thu nhập. **Đắk Nông** (#3 toàn quốc) là anomaly Tây Nguyên cần điều tra thêm.

### Tỉnh thấp hơn kỳ vọng kinh tế

| Tỉnh | GRDP (tr VND) | % 9+ thực tế | Phần dư |
|------|---------------|--------------|---------|
| TP.HCM (cụm 2) | 158 | 0.23% | −0.82 |
| Cần Thơ | 86 | 0.21% | −0.70 |
| Bà Rịa–Vũng Tàu | 335 | 0.53% | −0.69 |
| Hậu Giang | 67 | 0.24% | −0.61 |
| Bình Dương | 165 | 0.49% | −0.57 |

Cluster công nghiệp và tài nguyên underperform đồng loạt: dân số lao động nhập cư cao, học sinh không ổn định cư trú. **Bà Rịa–Vũng Tàu** (GRDP cao nhất cả nước, 335 triệu) chỉ đạt 0.53% — thể hiện rõ "lời nguyền tài nguyên" trong giáo dục.

---

## 14.8 Tỉnh Gian lận 2018: Confounding Kinh tế

| Tỉnh | GRDP (tr VND) | % 9+ Toán (2024) | Phần dư |
|------|---------------|------------------|---------|
| Hà Giang | 33.5 (thấp nhất VN) | 0.17% | −0.53 |
| Sơn La | 48.6 | 0.28% | −0.44 |
| Hòa Bình | 64.7 | **1.86%** | **+1.02** |

**Hà Giang và Sơn La:** double disadvantage — vừa nghèo nhất, vừa có legacy gian lận 2018. Không thể tách biệt hai hiệu ứng trong cross-section đơn thuần; cần DiD hoặc synthetic control với baseline trước 2018 (xem Chapter 10).

**Hòa Bình là ngoại lệ:** dù là tỉnh gian lận 2018, đến 2024 đạt pct_9+ cao nhất trong nhóm và overperform so với GRDP. Phản ánh giám sát nghiêm ngặt sau scandal và/hoặc cấu trúc dân số thuận lợi hơn so với Hà Giang và Sơn La.

---

## 14.9 Tổng hợp So sánh Metric

| Phát hiện | Metric mean | Metric 9+ |
|-----------|:-----------:|:---------:|
| Correlation với GRDP | Yếu (r≈0.12–0.16) | Rất yếu (r≈0.09–0.11) |
| Log-linear fit tốt hơn tuyến tính | ✅ | ✅ |
| Trend giảm 2021→2024 | ✅ | ✅ |
| GRDP significant sau kiểm soát chuyên | ✅ (p<0.001) | ❌ (p=0.40) |
| Hiệu ứng ngưỡng bão hòa Q3≈Q4 | Không rõ | ✅ Rõ ràng |

**Metric 9+ tốt hơn mean để đánh giá bất bình đẳng giáo dục cấp cao** — nó loại bỏ nhiễu từ điểm đại trà và phơi bày rõ hơn vai trò của vốn xã hội so với vốn kinh tế.

---

## 14.10 Hàm ý Chính sách

**1. Không phân bổ ngân sách giáo dục theo GDP tỉnh.** Tỉnh GRDP cao không tự động có kết quả tốt hơn. Công thức phân bổ nên dựa vào kết quả học tập và nhu cầu thực tế.

**2. Mở rộng hệ thống trường chuyên ở tỉnh nghèo** có thể hiệu quả hơn trợ cấp thu nhập cho hộ gia đình — chuyên là kênh truyền dẫn mạnh nhất (coef +0.755, p=0.001).

**3. Nghiên cứu và nhân rộng mô hình Đồng bằng Bắc Bộ.** Bắc Giang, Thái Bình, Nam Định đạt kết quả vượt trội bất kể kinh tế — vốn xã hội và văn hóa học tập là tài sản có thể chuyển giao thông qua chính sách.

**4. Chính sách đặc thù cho tỉnh công nghiệp nhập cư** (Bình Dương, Đồng Nai, Bà Rịa–VT): ổn định học sinh, giáo dục dành cho con em lao động nhập cư, trợ cấp học phí hướng đến nhóm này thay vì toàn tỉnh.

---

*Dữ liệu GRDP: GSO Vietnam 2022 via Wikipedia VI. Dữ liệu thi: Bộ GD&ĐT 2021–2024.*
