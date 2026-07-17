# Chapter 8 — Phát hiện Gian lận: Anomaly Detection 2026

← [07 Merger](07_province_merger.md) | → [09 Causal ML](09_causal_ml.md)

---

## 8.1 Bối cảnh

Việt Nam có hai vụ gian lận thi cử lớn:

| Năm | Tỉnh bị phát hiện | Hình thức |
|-----|-------------------|-----------|
| **2018** | Hà Giang, Sơn La, Hòa Bình | Cán bộ sửa điểm hàng loạt trong file máy tính |
| **2026** | Đang điều tra | Chưa công bố chính thức |

> **Vấn đề:** Nếu có gian lận 2026, điểm bị inflate → mọi analysis dùng 2026 bị nhiễu. Cần phát hiện thống kê trước khi tin dùng.

---

## 8.2 Phương pháp: 3-Signal Detection

### Signal 1 — Trend Z-score
Với mỗi tỉnh (harmonized codes):
1. Fit linear regression: `mean_toan ~ year` trên 2021/2022/2024
2. Predict expected 2026 score
3. Z-score residuals: `Z = (actual - predicted) / std_residual`
4. Flag: `Z > 2.0` (inflation)

### Signal 2 — KL Divergence
So sánh shape phân phối điểm tỉnh năm 2026 vs 2024 (re-weighted về tỉnh mới).
KL cao + shift dương = phân phối thay đổi bất thường theo hướng thuận lợi.

### Signal 3 — Low Variance
Gian lận tập trung sửa điểm → làm phẳng phân phối → std bất thường thấp.
Flag: std Z-score `< −2.0`

---

## 8.3 Kết quả

### Flag đầy đủ (≥ 2/3 signals)

| Tỉnh | Code | Actual | Expected | Residual | Z | KL | Verdict |
|------|------|--------|----------|----------|---|----|---------|
| **Hưng Yên (merged)** | **33** | **5.988** | **5.602** | **+0.386** | **+2.25** | cao | ⚠️ **FRAUD FLAG** |

- n = **42,860** — không phải sampling noise
- Signal 1 kích hoạt: Z = +2.25 > 2.0
- Signal 2 kích hoạt: KL divergence trên 75th percentile
- **Điểm đặc biệt:** Toàn quốc 2026 sụt dưới trend do CT2018. Hưng Yên ngược chiều — đây là anomaly mạnh.

### 2018 Fraud-adjacent (theo dõi)

| Tỉnh | Code | Z | Actual | Expected | Nhận xét |
|------|------|---|--------|----------|---------|
| Cao Bằng merged | 4 | +1.59 | 4.765 | 4.702 | Dưới threshold, bao gồm Hà Giang cũ |
| **Sơn La merged** | **14** | **−2.67** | **4.245** | **6.256** | **Anomaly âm lớn nhất** |

> 📌 **Sơn La [14] Z = −2.67 âm:** Không phải gian lận tăng điểm — điểm sụt rất mạnh so với trend. Hai khả năng: (1) CT2018 đánh nặng nhất vào tỉnh miền núi nghèo; (2) Sau scandal 2018, coi thi cực kỳ nghiêm → trend 2021-2024 có thể vẫn còn bị inflate nhẹ, 2026 phản ánh điểm thực.

### Elevated risk (dưới threshold)

| Tỉnh | Code | Z |
|------|------|---|
| Cà Mau | 96 | +1.60 |
| Cao Bằng merged | 4 | +1.59 |

---

## 8.4 Pattern toàn quốc

```
Phần lớn tỉnh 2026: điểm DƯỚI trend 2021-2024
─────────────────────────────────────────────
Lý do: CT2018 khó hơn + toán không bắt buộc
→ Cohort tự chọn thi toán = năng lực cao hơn TB
→ Nhưng đề khó → mean vẫn thấp hơn trend

Hưng Yên VƯỢT trend trong bối cảnh sụt chung
→ Anomaly mạnh hơn nhiều so với giá trị tuyệt đối
```

### Phân phối Z-scores toàn quốc

| Range Z | Số tỉnh | Ý nghĩa |
|---------|---------|---------|
| Z > +2.0 | **1** (Hưng Yên) | Potential inflation |
| +1.0 < Z ≤ +2.0 | 2 | Elevated, watch |
| −1.0 ≤ Z ≤ +1.0 | 25 | Normal |
| −2.0 ≤ Z < −1.0 | 5 | Below trend |
| Z < −2.0 | **1** (Sơn La) | Strongest negative anomaly |

---

## 8.5 Giới hạn

| Limitation | Hệ quả |
|-----------|--------|
| Chỉ 3 data points để fit trend | CI rộng, Z=2 có thể quá lỏng |
| Toán không bắt buộc CT2018 → selection bias | Expected score khó ước tính |
| Crosswalk có thể sai một số tỉnh | Aggregate mean bị nhiễu |
| KL divergence nhạy với sample size | Tỉnh nhỏ có KL cao tự nhiên |

**Khuyến nghị:** Đối chiếu với dữ liệu điều tra chính thức + microdata SBD pattern.

---

## 8.6 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| Có tỉnh nào bị flag 2026 không? | **Có — Hưng Yên [33]**: Z=+2.25, KL cao, n=42k |
| Tỉnh fraud 2018 có tái phạm không? | **Không rõ** — Hà Giang merged vào [4] (Z=+1.59, borderline); Sơn La [14] âm mạnh (Z=−2.67) |
| 2026 data dùng được cho causal analysis? | **Được** — nhưng loại Hưng Yên [33] khỏi province-level analysis; cảnh báo Sơn La [14] |

> 📊 Xem: `fraud_z_scores.png` · `fraud_scatter.png`

← [07 Merger](07_province_merger.md) | → [09 Causal ML](09_causal_ml.md)
