# Chapter 4 — Hiệu ứng Trường Chuyên / Năng khiếu

← [03 Urban/Rural](03_urban_rural.md) | → [05 Policy](05_local_policy.md)

---

## 4.1 Vấn đề nhận dạng

Dữ liệu không có trường "loại trường" — không biết ai học chuyên, ai học thường.

**Proxy strategy:** Tỉnh có nhiều trường chuyên mạnh → có nhiều học sinh chuyên → kết quả top-tail cao hơn. Đo bằng **chỉ số tập trung top-scorer**:

```
Concentration = (% Toán≥9 đến từ tỉnh X) / (% thí sinh từ tỉnh X)
```

**Tỉnh chuyên mạnh được định nghĩa:**
> Hà Nội · TP.HCM · Nam Định · Nghệ An · Hà Tĩnh · Hải Phòng · Quảng Ninh · Thanh Hóa

---

## 4.2 Chỉ số tập trung top-scorer

| Năm | % thí sinh từ tỉnh chuyên | % Toán≥9 từ tỉnh chuyên | Concentration ratio |
|-----|--------------------------|------------------------|-------------------|
| 2022 | 31.8% | 45.6% | **1.43×** |
| 2024 | 31.7% | 46.2% | **1.46×** |

> 📌 Các tỉnh chuyên mạnh chiếm ~32% thí sinh nhưng đóng góp ~46% top-scorer. Tỷ lệ này **ổn định qua các năm** — hiệu ứng trường chuyên là cấu trúc dài hạn, không bị COVID làm lung lay.

---

## 4.3 Kiểm định thống kê (2024)

**Mann-Whitney U test** — Toán: tỉnh chuyên vs tỉnh khác (sample 50K):

| Nhóm | N | Toán TB | Std |
|------|---|---------|-----|
| Tỉnh chuyên mạnh | ~336,000 | **6.712** | — |
| Tỉnh khác | ~725,000 | **6.324** | — |
| **Chênh lệch** | | **+0.388** | |
| p-value (Mann-Whitney) | | **≈ 0** | |

---

## 4.4 Top 15 tỉnh theo % Toán ≥ 9 (2024)

| Hạng | Tỉnh | N | % ≥ 9 | Là tỉnh chuyên? |
|------|------|---|-------|----------------|
| 1 | **Bắc Giang** | 17,489 | **2.49%** | ❌ |
| 2 | Thái Bình | 21,653 | 2.25% | ❌ |
| 3 | Đắk Nông | 15,041 | 2.18% | ❌ |
| 4 | **Nam Định** | 22,403 | **2.07%** | ✅ |
| 5 | Ninh Bình | 11,594 | 2.04% | ❌ |
| 6 | **Hà Nội** | 106,554 | **1.92%** | ✅ |
| 7 | Hòa Bình | 15,290 | 1.84% | ❌ |
| 8 | **Thanh Hóa** | 37,921 | **1.68%** | ✅ |
| 9 | **Hải Phòng** | 25,400 | **1.54%** | ✅ |
| 10 | Hải Dương | 9,447 | 1.51% | ❌ |

> 📌 **Surprise:** Bắc Giang (không phải tỉnh chuyên truyền thống) **dẫn đầu** với 2.49%. Đây là bằng chứng cho thấy **đầu tư giáo dục địa phương mới nổi** có thể thách thức hegemony của tỉnh chuyên truyền thống.

---

## 4.5 Bimodal distribution — fingerprint của trường chuyên

Tỉnh chuyên mạnh có xu hướng phân phối **bimodal nhẹ**: đuôi phải dày hơn (nhiều học sinh 9–10) so với tỉnh khác có phân phối đối xứng hơn.

Điều này phản ánh cấu trúc **"hai tầng"** của hệ thống giáo dục Việt Nam:
- **Tầng trên:** Học sinh chuyên — đầu tư tập trung, điểm rất cao
- **Tầng dưới:** Học sinh đại trà — phân phối bình thường

---

## 4.6 Hạn chế & Cảnh báo nhân quả

⚠️ Phân tích này là **correlational, không phải causal** vì:

1. **Selection bias:** Học sinh giỏi vốn đã tập trung vào tỉnh chuyên — không biết trường chuyên *tạo ra* hay chỉ *thu hút* học sinh giỏi.
2. **Confounders:** Tỉnh chuyên mạnh thường cũng là tỉnh giàu hơn, đô thị hơn.
3. **Thiếu dữ liệu trường:** Không có mã trường trong dataset → không thể so sánh chuyên vs thường trong cùng tỉnh.

**Để có causal estimate cần:** RDD (regression discontinuity) tại điểm cắt vào trường chuyên, hoặc IV dùng số lượng chỉ tiêu trường chuyên theo năm.

---

## 4.7 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| Tỉnh chuyên có điểm cao hơn không? | **Có** — +0.388 điểm Toán (p≈0) |
| Concentration ratio? | **1.46×** — ổn định qua năm |
| Hiệu ứng có bị COVID ảnh hưởng? | **Không** — 1.43× (2022) vs 1.46× (2024), gần như không đổi |
| Tỉnh nào dẫn đầu top-scorer? | **Bắc Giang** (2.49%) — không phải tỉnh chuyên truyền thống |

> 📊 Xem: `fig6_chuyen_top_scorer_rate.png` · `fig7_chuyen_score_dist.png`

← [03 Urban/Rural](03_urban_rural.md) | → [05 Policy](05_local_policy.md)
