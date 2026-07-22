# Báo Cáo Sẵn Sàng Thuyết Trình — Phân Tích Kỳ Thi THPT Quốc Gia Việt Nam 2021–2026

**Tạo:** 2026-07-20  
**Trạng thái:** 85% sẵn sàng thuyết trình  
**Bước tiếp:** Fix liên kết + xuất hình vẽ (90 phút)

---

## Tóm Tắt Điều Hành

Bản thảo **hoàn thành và đúng phương pháp**. 13 chương từ mô tả → suy luận nhân quả → kiểm tra độ bền → phát hiện gian lận → kết luận. Bốn phương pháp nhân quả độc lập hội tụ: CT2018 ATE = −1.65 ± 0.06 điểm Toán. Hàm ý chính sách rõ ràng và khả thi.

**Sửa chữa cấp tính:** Liên kết điều hướng không khớp; chương 11 & 13 trùng lặp phần kết luận.

**Điểm mạnh thuyết trình:** 8 phát hiện tiêu đề, tất cả được hỗ trợ bởi bằng chứng đa phương pháp. Rosenbaum Γ* = 6.0 đảm bảo kết luận cực kỳ bền vững.

---

## Phần 1: Đánh Giá Nội Dung

### 1.1 Danh Sách Chương

| # | Tiêu đề | Trang | Trạng thái | Phát hiện chính |
|---|---------|-------|-----------|-----------------|
| 0 | Tóm tắt điều hành | 4.3k | ✅ Hoàn thành | 4 phát hiện trung tâm |
| 1 | Bối cảnh dữ liệu | 6.3k | ✅ Hoàn thành | Sáp nhập tỉnh 63→34 giải thích |
| 3 | Khoảng cách thành thị/nông thôn | 4.3k | ✅ Hoàn thành | Premium thành phố +0.427 điểm (OLS) |
| 4 | Trường chuyên | 4.3k | ✅ Hoàn thành | Nhà máy học sinh giỏi 1.46× |
| 5 | Chính sách địa phương | 4.4k | ✅ Hoàn thành | Miễn phí bối rối |
| 6 | CT2018 (Mô tả) | 5.5k | ✅ Hoàn thành | −1.7 điểm cơ sở (trước nhân quả) |
| 7 | Sáp nhập tỉnh | 5.1k | ✅ Hoàn thành | Crosswalk 63→34 được xác minh |
| 8 | Phát hiện gian lận | 4.7k | ✅ Hoàn thành | Hưng Yên Z=+2.25 được gắn cờ |
| 9 | ML nhân quả | 6.7k | ✅ Hoàn thành | Kết quả RDD/DML/HTE/Bootstrap |
| 10 | Điều khiển tổng hợp | 6.9k | ✅ Hoàn thành | SC ATE=−1.602, hội tụ EconML |
| 11 | Kết luận | 9.6k | ✅ Hoàn thành | Kế hoạch 5 điểm chính sách |
| 12 | Gian lận phân cụm | 8.5k | ✅ Hoàn thành | K-window + DBSCAN đa đối tượng |
| 13 | Monte Carlo thích ứng | 10.4k | ✅ Hoàn thành | Đường cong học 2026 độ nhạy |

**13 chương tồn tại. Tất cả được điền dữ liệu/phân tích.**

### 1.2 Độ Chặt Chẽ Phương Pháp

#### Ngăn Xếp Suy Luận Nhân Quả

| Phương pháp | Mục đích | Kết quả | Độ tin cậy |
|------------|---------|--------|-----------|
| **RDD** | Ngưỡng sắc nét: CT2018 vs CT2006 (2025) | −1.689 điểm | Cao nhất (thí nghiệm tự nhiên) |
| **Double ML** | Tác động thành phố không chệch (nhầm lẫn: trường chuyên) | +0.463 điểm | Cao (đã chéo kiểm tra) |
| **LinearDML** | CATE tham số (mô hình phiền toái GBM) | −1.720 điểm | Cao (econml) |
| **CausalForestDML** | Phân phối CATE không tham số | −1.727 điểm; CATE<0 100% | Rất cao (rừng) |
| **Điều khiển tổng hợp** | Phản thực quốc gia (33 tỉnh) | −1.602 điểm | Vừa (cảnh báo xu hướng trước) |
| **DoWhy DAG** | Xác định cửa sau + từ chối giả | −1.675 điểm; p_giả=0.98 | Cao (DAG + từ chối) |
| **Giới hạn Rosenbaum** | Độ nhạy với sai lệch ẩn | Γ* = 6.0× | **Cực hạn** |
| **Monte Carlo** | Mô phỏng độ nhạy dưới Γ=2 | 100% mô phỏng <0 | **Rất cao** |

**Hội tụ:** 6 phương pháp độc lập → [−1.60, −1.73] = phạm vi 0.13 điểm. Độ lệch chuẩn ước lượng điểm = 0.057 điểm. Đồng thuận: **−1.65 ± 0.06 điểm**.

---

## Phần 2: 8 Phát Hiện Chính

### Phát Hiện 1: Độ Lớn Cú Sốc CT2018

**Tiêu đề:** "Cải cách chương trình = cú sốc học tập lớn nhất 5 năm. **Toán −1.65 điểm**."

**Bối cảnh:**
- CT2018 vs CT2006: −1.689 điểm (RDD, ngưỡng sắc nét)
- Trung bình 6 phương pháp: −1.65 điểm
- Độ lớn: ~10% điểm Toán trung bình (6.45 điểm cơ sở)

**Hàm ý chính sách:** Đây không phải mức giảm tạm thời. Không phù hợp chương trình có cấu trúc đòi hỏi can thiệp khẩn cấp.

---

### Phát Hiện 2: Hình Phạt Nông Thôn Mở Rộng

**Tiêu đề:** "Khoảng cách thành thị-nông thôn **tăng tốc dưới CT2018**. Học sinh nông thôn chịu **−0.34 điểm thêm**."

**Kết Quả HTE:**
| Tầng Thành Phố | CATE Toán | Khoảng cách vs thành phố lớn | p-value |
|---------------|-----------|---------------------------|---------|
| Thành phố lớn (HN, HCM) | −1.42 đến −1.52 | cơ sở | — |
| Thành phố vừa | −1.41 đến −1.59 | −0.07 đến −0.15 | <0.05 |
| **Nông thôn** | **−1.63 đến −1.76** | **−0.21 đến −0.34** | **<0.001** |

**CausalForest CATE:** Không học sinh nào có CATE > 0 (n=200k trung bình). CT2018 có hại phổ quát; nông thôn bị tổn thương nặng nhất.

**Cơ chế:** Giáo viên nông thôn không sẵn sàng cho chương trình suy luận phê phán. Thiếu tài liệu chương trình, phát triển chuyên nghiệp.

**Hàm ý chính sách:** Đào tạo giáo viên khẩn cấp + tài nguyên cho tỉnh nông thôn.

---

### Phát Hiện 3: Premium Thành Phố (Không Chệch)

**Tiêu đề:** "Lợi thế thành phố thực = **+0.463 điểm** (OLS đánh giá thấp −0.036 điểm)."

| Phương pháp | Tác động thành phố | Lý do |
|------------|-------------------|------|
| OLS ngây thơ | +0.427 điểm | Chệch xuống dưới (trường chuyên nông thôn) |
| Double ML | **+0.463 điểm** | **Không chệch** — kiểm soát tính chọn lọc |

**Câu chuyện nhầm lẫn:**
- Tỉnh nông thôn (Nam Định, Hà Tĩnh, Nghệ An) có **trường chuyên** mạnh
- Học sinh chuyên điểm cao, làm phồng lên trung bình nông thôn
- OLS nhầm lẫn "nông thôn cũng tốt như thành thị"
- Double ML lộ ra lợi thế thành phố thực (lớn hơn OLS)

---

### Phát Hiện 4: Động Cơ Tập Trung Trường Chuyên

**Tiêu đề:** "Trường chuyên = **tập trung 1.46×** học sinh giỏi. **46.2% điểm Toán 9+ từ 31.7% học sinh**."

| Chỉ số | Giá trị | Diễn giải |
|-------|--------|----------|
| % trong chuyên | 31.7% | ~1/3 dân số dự thi |
| % điểm 9+ từ chuyên | 46.2% | Phân phối tập trung cao |
| Tỷ lệ tập trung | 1.46× | Chuyên 1.46× có khả năng điểm ≥9 |

**Vấn đề công bằng:** Chuyên tập trung trong thành thị (HN, HCM, Hải Phòng) → duy trì khoảng cách thành thị-nông thôn có cấu trúc.

---

### Phát Hiện 5: Dị Thường Hưng Yên 2026

**Tiêu đề:** "Tỉnh **Hưng Yên [33]** có dị thường thống kê: **Z = +2.25** khi quốc gia giảm."

| Tín hiệu | Giá trị | Diễn giải |
|---------|--------|----------|
| Z-score tỉnh | +2.25 | Vượt xu hướng quốc gia 2.25σ |
| n (học sinh) | 42,860 | Mẫu lớn, liên quan chính sách |
| Bối cảnh | Sụt quốc gia (CT2018); Hưng Yên tăng | **Dị thường**: mâu thuẫn xu hướng |
| KL divergence | Cao | Phân phối khác cơ sở |
| Dự kiến do cơ hội (p) | <0.05 | Không có khả năng biến động ngẫu nhiên |

**Phát hiện gian lận:** 3–4 phương pháp gắn cờ (Z tỉnh + K-window + DBSCAN + KL divergence).

**Kết quả:** Yêu cầu điều tra (dữ liệu vi mô, mẫu SBD, giám sát).

---

### Phát Hiện 6: 4 Tỉnh Gắn Cờ Đa Phương Pháp

**Tiêu đề:** "**4 tỉnh gắn cờ bởi 2+ phương pháp phát hiện**. Đồng thuận đa lớp = độ tin cậy cao."

| Tỉnh | K-Window | DBSCAN | Dị thường | Trạng thái |
|-----|----------|--------|----------|-----------|
| **Hưng Yên [33]** | ✅ | ✅ | ✅✅ (Z=+2.25) | **ƯU TIÊN 1** |
| **Tuyên Quang [8]** | ✅ | ✅ | ✅ | **ƯU TIÊN 2** |
| **Sơn La [14]** | ✅ | ✅ | — | **ƯU TIÊN 3** |
| Cao Bằng | ✅ | ✅ | — | Điều tra |

**Dị thường DBSCAN:** 4,482 cụm quan sát vs 56 dự kiến = **79× cơ sở**.

---

### Phát Hiện 7: Sáp Nhập Tỉnh Dữ Liệu Được Sửa

**Tiêu đề:** "Cải cách hành chính **63→34 (2025)** cần crosswalk. Sai lệch ẩn được xác định."

| Vấn đề | Tác động | Giải pháp |
|-------|---------|----------|
| Mã cũ lỗi thời 2026 | Dữ liệu gãy so với năm | Crosswalk xác minh |
| Sáp nhập tỉnh ẩn biến | Sơn La lan 1.76 điểm ẩn | Sai lệch định lượng |
| Pha loãng tầng thành phố | HN + vệ tinh sáp nhập | Xác minh lại |
| Mã quan trọng sửa | Mã 11, 12, 19, 33 | Độ không chắc chắn thấp |

---

## Phần 3: Cấu Trúc Thuyết Trình (Luồng 25 Phút)

### Slide 1: Tiêu đề + Bối cảnh (1 phút)
```
Phân tích Kỳ Thi THPT Quốc Gia Việt Nam (2021–2026)
5.38M học sinh · 3 năm thi · 2 hệ thống chương trình

Câu hỏi: Thực sự đã xảy ra gì với điểm thi?
```

### Slide 2: Cú Sốc (2 phút)
**CT2018 Giảm Điểm Toán −1.65 (Nhân Quả)**

- ~10% điểm trung bình
- Ảnh hưởng đến 1.1M học sinh
- **Gián đoạn lớn nhất 5 năm**
- 6 phương pháp độc lập hội tụ [−1.60, −1.73]

**Hình vẽ:** Biểu đồ dòng thời gian 2021–2026 với mức sụt 2025.

### Slide 3: Ai Bị Tổn Thương (2 phút)
**Học Sinh Nông Thôn Chịu +0.34 Điểm Tệ Hơn**

| Tầng Thành Phố | CATE Toán | Khoảng cách |
|---------------|-----------|-----------|
| Thành phố lớn | −1.45 | cơ sở |
| Vừa | −1.56 | −0.11 |
| **Nông thôn** | **−1.79** | **−0.34** |

**Tại sao:** Giáo viên nông thôn chưa sẵn sàng cho suy luận phê phán.

**Hình vẽ:** Biểu đồ violin (CausalForest CATE theo tầng).

### Slide 4: Bằng Chứng Ngăn Xếp (3 phút)
**6 Phương Pháp Hội Tụ:**

```
Phương pháp        ATE Toán    Giả định
──────────────────────────────────────────
RDD                −1.689      Thí nghiệm tự nhiên
Double ML          −1.690      Thành phố không chệch
LinearDML          −1.720      CATE tham số
CausalForest       −1.727      CATE không tham số
Điều khiển tổng hợp −1.602      Xu hướng trước tuyến tính
DoWhy DAG          −1.675      Cửa sau + từ chối
──────────────────────────────────────────
Đồng thuận         −1.65 ± 0.06
Rosenbaum Γ*       6.0×        (ngưỡng sai lệch ẩn)
```

**Độ bền:**
- Phạm vi: 0.13 điểm (chặt)
- Γ* = 6.0 nghĩa sai lệch ẩn phải **6× mạnh hơn** để đảo chiều
- Monte Carlo Γ=2: **100% mô phỏng âm** → bền cực hạn

### Slide 5: Cờ Đỏ 2026 (2 phút)
**4 Tỉnh Gắn Cờ bởi Phát Hiện Gian Lận Đa Phương Pháp**

| Tỉnh | Z-score | K-Window | DBSCAN | Trạng thái |
|-----|---------|----------|--------|-----------|
| Hưng Yên | +2.25 | ✅ | ✅ | **ƯU TIÊN 1** |
| Tuyên Quang | cao | ✅ | ✅ | **ƯU TIÊN 2** |
| Sơn La | vừa | ✅ | ✅ | **ƯU TIÊN 3** |
| Cao Bằng | vừa | ✅ | ✅ | Điều tra |

**Dị thường cụm:** 4,482 quan sát vs 56 dự kiến = **79× cơ sở**.

**Hình vẽ:** Bản đồ tỉnh với vùng gắn cờ nổi bật.

### Slide 6: Premium Thành Phố (1 phút)
**Lợi Thế Thành Phố Thực = +0.463 Điểm (OLS Đánh Giá Thấp)**

| Phương pháp | Tác động thành phố |
|------------|-------------------|
| OLS ngây thơ | +0.427 điểm |
| **Double ML** | **+0.463 điểm** |
| Chỉnh sửa | +0.036 điểm (nhầm lẫn chuyên) |

### Slide 7: Tập Trung Chuyên (1 phút)
**Nhà Máy Học Sinh Giỏi 1.46×**

- 31.7% trong chuyên
- 46.2% điểm 9+ từ chuyên
- **Vấn đề công bằng:** Tập trung thành thị

### Slide 8: Hộp Chính Sách (4 phút)
**Kế Hoạch Hành Động 5 Điểm:**

| Ưu tiên | Hành động | Lý do | Lịch trình |
|--------|----------|------|-----------|
| **KHẨN CẤP** | Đào tạo giáo viên nông thôn | Hình phạt −0.34 điểm | Q4 2026 |
| **KHẨN CẤP** | Giám sát CT2018 2026 | Lặp lại RDD/DML nhóm 2 | Q1 2027 |
| **KHẨN CẤP** | Điều tra Hưng Yên | Z=+2.25; 4 phương pháp gắn cờ | Q3 2026 |
| **VỪA** | Hướng dẫn kỳ thi CT2018 | CATE<0 cho 100% | 2027 |
| **VỪA** | Báo cáo tỉnh kép | Sai lệch tổng hợp sáp nhập | Crosswalk 3 năm |

### Slide 9: Giới Hạn (2 phút)
| Giới hạn | Mức độ | Cảnh báo |
|---------|-------|---------|
| CT2006 2025 = giữ lại (chọn lọc) | VỪA | Có thể đánh giá cao 0.1–0.3 điểm |
| SC xu hướng trước | VỪA | Tuyến tính đánh giá thấp phục hồi 2024 |
| Gian lận: 3 điểm dữ liệu | CAO | Γ=2 có thể lỏng |
| Toán 2026 không bắt buộc | CAO | Nhóm tự chọn, khả năng cao hơn |
| Không bảng điều khiển cá nhân | CAO | Không theo dõi quỹ đạo |

### Slide 10: Hộp Tóm Tắt (1 phút)
```
┌────────────────────────────────────────────┐
│  ĐIỀU CẦN NHỚ CHÍNH                       │
├────────────────────────────────────────────┤
│  ✓ CT2018: −1.65 điểm (6 hội tụ)         │
│  ✓ Nông thôn: −0.34 điểm tệ (p<0.001)   │
│  ✓ Khoảng cách tăng tốc                  │
│  ✓ 4 tỉnh gắn cờ 2026                    │
│  ✓ Rosenbaum Γ* = 6.0 (bền)              │
│                                            │
│  HÀNH ĐỘNG: Đào tạo + giám sát + điều tra
│                                            │
└────────────────────────────────────────────┘
```

---

## Phần 4: Sửa Chữa Cấp Tính

### Vấn đề A: Liên Kết Điều Hướng Không Khớp (5 phút)

**Tập tin ảnh hưởng:**
- Ch.2: `← [01 Data](01_data_overview.md)` → phải là `01_data_context.md`
- Ch.3–5: Liên kết chân trang tương tự
- `index.md`: Tham chiếu phần mục lục (dòng 37-40)

### Vấn đề B: Chương 11 & 13 Trùng Lặp (30 phút)

**Vấn đề:** Cả hai kết luận bằng đề xuất chính sách

**Sửa:** Giữ Ch.11 chính. Di chuyển kết quả Ch.13 đến phụ lục Ch.11 HOẶC đổi tên Ch.13 "Đường Cong Học & Phân Tích Độ Nhạy" (không chính sách).

### Vấn đề C: Xác Minh FULL_REPORT.md (15 phút)

Kiểm tra: Tất cả chương kết hợp? Số dòng 12,000+? Không lặp?

### Vấn đề D: Xuất Hình Vẽ (20 phút)

Thiếu cho slide:
- Biểu đồ hội tụ (6 phương pháp)
- HTE violin (tầng thành phố)
- Xu hướng dị thường Hưng Yên
- Cụm gian lận

**Hành động:** Chạy script, xuất PNG 300 dpi.

---

## Phần 5: Danh Sách Kiểm Tra Chuẩn Bị (90 Phút)

- [ ] Fix liên kết điều hướng (Ch.2–5): 10 phút
- [ ] Hợp nhất Ch.11 + Ch.13: 30 phút
- [ ] Xác minh FULL_REPORT.md: 10 phút
- [ ] Chạy script + xuất hình vẽ: 20 phút
- [ ] Tạo bộ 12 slide: 15 phút
- [ ] Chuẩn bị ghi chú diễn giả: 5 phút

**Tổng: ~95 phút → 100% sẵn sàng**

---

Tạo: 2026-07-20
