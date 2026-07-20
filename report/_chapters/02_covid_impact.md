# Chapter 2 — Cú sốc COVID: Tác động Ngoại sinh lên Điểm thi

← [01 Data](01_data_overview.md) | → [03 Urban/Rural](03_urban_rural.md)

---

## 2.1 Bối cảnh

| Năm | Tình trạng dịch |
|-----|----------------|
| 2021 | Đợt dịch Delta — lockdown TP.HCM kéo dài 4 tháng; học online toàn quốc |
| 2022 | Hậu COVID — học online kéo dài H1; trường mở cửa lại H2 |
| 2024 | Baseline bình thường — 2 năm sau COVID |

COVID là **cú sốc ngoại sinh** (exogenous shock): không phụ thuộc vào năng lực học sinh, tác động lên toàn bộ hệ thống cùng lúc. Phù hợp để phân tích nhân quả.

---

## 2.2 Điểm trung bình 3 môn chính theo năm

| Môn | 2021 (COVID) | 2022 (Hậu) | 2024 (Bình thường) | Δ (2021→2024) |
|-----|-------------|-----------|-------------------|--------------|
| **Toán** | 6.615 | 6.466 | 6.447 | −0.168 |
| **Ngữ văn** | 6.471 | 6.508 | 7.231 | **+0.760** |
| **Ngoại ngữ** | 5.852 | 5.158 | 5.522 | −0.330 |

> 📌 **Insight:** Điểm Toán KHÔNG phục hồi về mức 2021 dù đã 3 năm. Ngữ văn tăng mạnh (+0.76) — có thể do thay đổi cấu trúc đề thi 2024. Ngoại ngữ vẫn thấp hơn 2021.

---

## 2.3 Phân phối điểm theo band (Toán)

| Band | 2021 | 2022 | 2024 |
|------|------|------|------|
| < 5 (Trượt) | 17.4% | 18.9% | 17.5% |
| 5–6.5 (TB) | 27.9% | 29.6% | 27.6% |
| 6.5–8 (Khá) | 28.8% | 30.6% | 35.9% |
| ≥ 8 (Giỏi) | **25.9%** | 21.8% | **19.0%** |

> 📌 Tỷ lệ đạt giỏi (≥8) giảm dần từ 25.9% → 19.0%. Cho thấy COVID làm tổn hại tầng **học sinh khá-giỏi** nhiều hơn học sinh trung bình.

---

## 2.4 Ngoại ngữ — môn bị ảnh hưởng nặng nhất

| Chỉ số | 2021 | 2022 | 2024 |
|--------|------|------|------|
| Điểm TB | 5.852 | **5.158** | 5.522 |
| % dưới 5 | 40.1% | **51.4%** | 42.5% |
| % ≥ 8 | 24.3% | **12.1%** | 14.6% |

**Lý giải nhân quả:** Học ngoại ngữ phụ thuộc môi trường giao tiếp và thực hành. Học online cắt đứt hoàn toàn khả năng luyện nghe-nói. Đây là loại kỹ năng không thể bù đắp qua tự học văn bản.

---

## 2.5 Difference-in-Differences: Đô thị vs Nông thôn (2021→2024)

|  | 2021 | 2024 | Δ |
|--|------|------|---|
| Đô thị lớn (HN, HCM) | 7.048 | 6.853 | **−0.195** |
| Đô thị vừa | 6.716 | 6.538 | −0.178 |
| Tỉnh lẻ/Nông thôn | 6.498 | 6.341 | **−0.157** |

**DiD estimate (Đô thị lớn vs Nông thôn): −0.038**

```
DiD = (−0.195) − (−0.157) = −0.038
```

> 📌 **Phát hiện ngược chiều kỳ vọng:** Đô thị giảm *nhiều hơn* nông thôn. Giải thích: TP.HCM chịu lockdown nghiêm trọng nhất (4 tháng 2021), kéo tụt điểm đô thị lớn. Hiệu ứng trường chuyên tại đô thị không đủ bù đắp mất mát do lockdown.

---

## 2.6 Kiểm định thống kê

**Mann-Whitney U test** — Toán 2021 vs 2024 (sample 50K mỗi nhóm):
- p-value = **1.19 × 10⁻⁹³**
- mean_2021 = 6.615, mean_2024 = 6.447
- Sự khác biệt **có ý nghĩa thống kê cao**, dù magnitude nhỏ (~0.17 điểm)

---

## 2.7 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| COVID có làm giảm điểm thi không? | **Có** — giảm 0.17 điểm Toán, 0.33 điểm Ngoại ngữ |
| Môn nào bị ảnh hưởng nặng nhất? | **Ngoại ngữ** — phụ thuộc thực hành, không thể tự học bù online |
| Điểm có phục hồi về baseline chưa? | **Chưa** — đến 2024 vẫn thấp hơn 2021 |
| Đô thị hay nông thôn bị ảnh hưởng hơn? | **Đô thị** — do lockdown TP.HCM kéo dài |

> 📊 Xem: `fig1_covid_mean_scores.png` · `fig2_covid_kde_toan.png` · `fig3_did_covid_urban_rural.png`

← [01 Data](01_data_overview.md) | → [03 Urban/Rural](03_urban_rural.md)
