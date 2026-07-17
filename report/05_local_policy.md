# Chapter 5 — Tác động Chính sách Địa phương

← [04 Chuyên](04_chuyen_school.md) | → [06 Chương trình](06_curriculum_2018.md)

---

## 5.1 Bối cảnh chính sách

Một số tỉnh/thành đã ban hành chính sách **miễn phí lệ phí thi** cho thí sinh:

| Tỉnh | Chính sách | Năm áp dụng |
|------|-----------|------------|
| Hà Nội (01) | Miễn toàn bộ lệ phí thi | Nhiều năm |
| TP.HCM (02) | Miễn toàn bộ lệ phí thi | Nhiều năm |
| Hải Phòng (03) | Miễn/hỗ trợ lệ phí | Nhiều năm |

**Hypothesis ban đầu:** Miễn phí → nhiều học sinh yếu tham dự hơn → kéo điểm TB xuống + tăng variance.

---

## 5.2 Kết quả: Điểm Toán theo nhóm (2022 & 2024)

### Năm 2022

| Nhóm | N | Toán TB | Std | % < 5 | % ≥ 8 |
|------|---|---------|-----|-------|-------|
| Tỉnh miễn phí (HN, HCM, HP) | 202,170 | **6.904** | 1.521 | 11.6% | **29.1%** |
| Tỉnh đóng phí | 780,556 | 6.353 | 1.695 | 20.9% | 20.0% |
| **Gap** | | **+0.551** | **−0.174** | **−9.3%** | **+9.1%** |

### Năm 2024

| Nhóm | N | Toán TB | Std | % < 5 | % ≥ 8 |
|------|---|---------|-----|-------|-------|
| Tỉnh miễn phí | 218,445 | **6.846** | 1.438 | 11.0% | **26.1%** |
| Tỉnh đóng phí | 827,168 | 6.342 | 1.570 | 19.2% | 17.1% |
| **Gap** | | **+0.504** | **−0.132** | **−8.2%** | **+9.0%** |

---

## 5.3 Bác bỏ hypothesis ban đầu

Hypothesis "miễn phí kéo nhiều học sinh yếu vào" **KHÔNG được xác nhận**:

| Dự đoán từ hypothesis | Thực tế quan sát |
|----------------------|-----------------|
| Std tỉnh miễn phí CAO hơn | Std tỉnh miễn phí **THẤP hơn** (1.438 vs 1.570) |
| % dưới 5 tỉnh miễn phí CAO hơn | % dưới 5 tỉnh miễn phí **THẤP hơn** (11% vs 19%) |
| Điểm TB tỉnh miễn phí thấp hơn | Điểm TB tỉnh miễn phí **CAO hơn** (+0.504) |

---

## 5.4 Confounding: Hiệu ứng đô thị

**Vấn đề nhân quả:** Ba tỉnh miễn phí (HN, HCM, HP) đều là **đô thị lớn** — không thể tách "tác động miễn phí" khỏi "tác động đô thị".

```
Điểm cao ~ Miễn phí thi
         ← Đô thị lớn (confounder chính)
                ↙          ↘
         Miễn phí thi     Điểm cao
```

**Kết luận:** Với dữ liệu hiện có, **không thể xác định** liệu miễn phí thi có tác động nhân quả hay không. Toàn bộ gap (+0.504) có thể giải thích bởi hiệu ứng đô thị.

---

## 5.5 Gap HN+HCM vs Toàn quốc qua các năm

| Năm | Toán TB cả nước | HN + HCM TB | Gap | Xu hướng |
|-----|----------------|------------|-----|----------|
| 2021 | 6.615 | 7.048 | +0.432 | — |
| 2022 | 6.466 | 6.902 | +0.436 | ↑ tăng nhẹ |
| 2024 | 6.447 | 6.853 | +0.406 | ↓ giảm nhẹ |
| 2025 | 4.783 | 5.265 | +0.482 | ↑ tăng (sốc CT mới) |
| 2026 | 5.652 | 6.164 | +0.512 | ↑ tiếp tục tăng |

> 📌 Gap lớn nhất trong giai đoạn chuyển đổi chương trình (2025–2026): **HN+HCM thích nghi với chương trình mới nhanh hơn** tỉnh thường. Đây là bằng chứng gián tiếp cho thấy tài nguyên đô thị (thầy giỏi, tài liệu, gia sư) giúp điều chỉnh nhanh hơn.

---

## 5.6 Đề xuất để cải thiện nhân quả

Để tách được tác động chính sách cần:
1. **Synthetic Control Method** — dùng tỉnh không miễn phí làm "counterfactual" tổng hợp
2. **Panel DiD** — so sánh trước/sau khi từng tỉnh áp dụng chính sách
3. **IV approach** — dùng ngân sách giáo dục tỉnh làm instrumental variable
4. **Dữ liệu bổ sung** — tỷ lệ tham dự thi theo năm, GDP tỉnh, chi tiêu GD/học sinh

---

## 5.7 Kết luận

| Câu hỏi | Trả lời |
|---------|---------|
| Tỉnh miễn phí có điểm cao hơn không? | **Có** — +0.504 điểm Toán |
| Do miễn phí gây ra không? | **Không xác định được** — confounded bởi hiệu ứng đô thị |
| Gap có tăng theo thời gian không? | **Có** — đặc biệt tăng trong giai đoạn đổi chương trình |
| Cần gì để có causal estimate? | Synthetic control hoặc panel DiD với biến động chính sách |

> 📊 Xem: `fig8_fee_exemption_effect.png` · `fig9_hn_hcm_gap_trend.png`

← [04 Chuyên](04_chuyen_school.md) | → [06 Chương trình](06_curriculum_2018.md)
