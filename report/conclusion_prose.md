# Kết luận — Trả lời các câu hỏi nghiên cứu

*Tổng hợp tự nhiên, không phải bảng số liệu.*

---

## COVID có thực sự làm điểm thi tệ hơn không?

Câu trả lời ngắn gọn: **không chắc — và bằng chứng quá yếu để kết luận.**

Nhìn vào điểm trung bình, năm 2022 thấp hơn 2021 ở cả ba môn chính. Người ta dễ dàng kết luận ngay rằng COVID là thủ phạm. Nhưng khi áp dụng Difference-in-Differences với bootstrap cluster theo tỉnh, khoảng tin cậy 95% cho tác động của COVID rơi vào [−0.081, +0.004] — tức là ôm cả số 0. Về mặt thống kê, không thể loại trừ khả năng COVID không gây ra tác động gì lên điểm thi.

Điều đó không có nghĩa COVID hoàn toàn vô hại. COVID rõ ràng đánh vào **Ngoại ngữ** — năm 2022 có đến 51% thí sinh dưới 5 điểm môn này, tỷ lệ cao bất thường. Nhưng tác động lên Toán và Văn thì không đủ mạnh để vượt qua ngưỡng thống kê. Kết quả Chapter 2 nên được đọc với thái độ thận trọng: DiD point estimate âm, nhưng fragile.

---

## Học sinh thành phố học giỏi hơn nông thôn bao nhiêu?

**Khoảng 0.46 điểm Toán** — nhưng con số thực sự cao hơn những gì OLS thông thường cho thấy.

Nếu chỉ chạy hồi quy thẳng, urban premium trông như +0.43 pts. Nhưng có một vấn đề ẩn: các tỉnh nông thôn như Nam Định, Hà Tĩnh, Nghệ An lại có trường chuyên rất mạnh, kéo điểm nông thôn lên cao bất thường. Khi dùng Double ML để tách riêng hiệu ứng đô thị khỏi hiệu ứng trường chuyên, urban premium tăng lên **+0.463 pts** — OLS đang bị underestimate.

Quan trọng hơn, khoảng cách này không đứng yên. CT2018 đang nới rộng nó: thí sinh nông thôn bị ảnh hưởng thêm −0.34 pts so với thí sinh thành phố lớn do cùng một chương trình. Nếu không có can thiệp, chênh lệch đô thị-nông thôn sẽ tiếp tục tăng trong những năm đầu CT2018.

---

## Trường chuyên có thực sự tạo ra học sinh giỏi không?

**Có — nhưng cần phân biệt selection và treatment.**

Dữ liệu cho thấy các tỉnh có trường chuyên mạnh đóng góp 46.2% số thí sinh đạt Toán ≥ 9 dù chỉ chiếm 31.7% tổng số thí sinh — tỷ lệ sản xuất top-scorer gấp **1.46 lần** so với tỉnh không có chuyên mạnh.

Nhưng đây là correlation, không phải causal. Trường chuyên tuyển chọn học sinh giỏi từ đầu (selection bias). Để biết chuyên *dạy* tốt hơn hay chỉ *chọn* học sinh tốt hơn thì cần RDD hoặc lottery-based assignment — dữ liệu hiện tại chưa cho phép phân tách rõ. Kết luận an toàn nhất: trường chuyên là *nơi tập trung* top-scorer, chưa chắc là *nguyên nhân* tạo ra họ.

---

## Chính sách miễn học phí có làm điểm tốt hơn không?

**Không rõ — và rất khó kết luận nhân quả từ dữ liệu này.**

Hà Nội và TP.HCM — hai địa phương miễn học phí sớm nhất — cũng là hai thành phố có điểm cao nhất. Nhưng đây là confounding rõ ràng: hai thành phố này giàu hơn, có nhiều trường chuyên hơn, giáo viên tốt hơn. Khi nhìn phân phối điểm theo nhóm tỉnh miễn phí vs. đóng phí, chênh lệch gần như hoàn toàn bị giải thích bởi urban tier và chuyên school effect, không phải policy.

Để đánh giá được policy này cần một natural experiment rõ ràng hơn — ví dụ một tỉnh bắt đầu miễn phí giữa giai đoạn nghiên cứu. Dữ liệu hiện tại không có đủ variation sạch để làm điều đó.

---

## Chương trình 2018 có giúp học sinh học tốt hơn không?

**Không — ngược lại, nó gây ra cú sốc lớn nhất trong 5 năm.**

Đây là câu hỏi trung tâm và cũng là phát hiện quan trọng nhất của toàn bộ nghiên cứu.

Năm 2025, lần đầu tiên có hai cohort thi cùng một kỳ thi THPT: một nhóm học CT2006 (chương trình cũ) và một nhóm học CT2018 (chương trình mới). Đây là một natural experiment gần như lý tưởng — cùng năm, cùng đề thi, chỉ khác chương trình học.

Kết quả: **nhóm CT2018 thấp hơn CT2006 trung bình 1.65 điểm Toán**. Không phải 0.1, không phải 0.5 — mà 1.65 điểm trên thang 10. Đây là cú sốc lớn hơn COVID khoảng 10 lần về độ lớn.

Điều đáng chú ý là con số này nhất quán qua **6 phương pháp độc lập**: RDD cho −1.689, Double ML cho −1.690, LinearDML cho −1.720, CausalForest cho −1.727, Synthetic Control cho −1.602, DoWhy cho −1.675. Khi sáu cách tiếp cận với giả định khác nhau đều ra kết quả trong khoảng [−1.60, −1.73], đây không còn là artefact thống kê nữa. Đây là tín hiệu thực.

Phân tích độ bền vững (Rosenbaum Bounds) cho thấy cần một biến nhiễu ẩn mạnh **gấp 6 lần** mới đủ sức đảo ngược kết quả — ngưỡng cực kỳ cao với dữ liệu quan sát. Placebo test của DoWhy cho ATE → −0.002 (p = 0.98), xác nhận effect không phải ngẫu nhiên.

Cơ chế khả dĩ: CT2018 yêu cầu tư duy phản biện và ứng dụng thực tế, trong khi hệ thống luyện thi và giáo viên — đặc biệt ở nông thôn — vẫn đang dạy theo kiểu học thuộc lòng của CT2006. Học sinh chưa được chuẩn bị, và điểm phản ánh điều đó.

---

## Sáp nhập tỉnh 2025 ảnh hưởng đến nghiên cứu như thế nào?

**Tạo ra lỗi dữ liệu nghiêm trọng nếu không xử lý đúng.**

Từ năm 2026, Việt Nam dùng mã tỉnh theo hệ thống 34 tỉnh mới (sáp nhập từ 63 tỉnh cũ). Mã SBD của thí sinh 2026 bắt đầu bằng mã tỉnh mới — nếu dùng crosswalk cũ để gán urban tier hay tên tỉnh, sẽ ra kết quả sai hoặc "Unknown".

Ví dụ cụ thể: Thái Bình và Nam Định — hai tỉnh đứng đầu và thứ nhì về điểm Toán trong hệ thống cũ — nay sáp nhập vào Ninh Bình [mã 37]. Nếu so sánh thẳng 2026 vs. 2024 mà không harmonize, "Ninh Bình 2026" trông như tỉnh mới xuất hiện với điểm rất cao, trong khi thực ra nó là tổng hợp của ba tỉnh cũ với spread lên đến 1.76 điểm. Vấn đề này đã được xử lý trong `province_mapping.py` qua crosswalk `OLD_TO_NEW_2026`, nhưng nó nhắc nhở rằng bất kỳ so sánh tỉnh-level nào giữa 2024 và 2026 đều cần thực hiện cẩn thận.

---

## Có gian lận thi năm 2026 không?

**Hưng Yên [mã 33] có dấu hiệu thống kê đáng ngờ — nhưng chưa đủ để kết luận gian lận.**

Năm 2026, toàn quốc điểm Toán trung bình giảm do CT2018. Hầu hết tỉnh đều giảm. Trong bối cảnh đó, Hưng Yên với 42,860 thí sinh lại tăng điểm — Z-score vượt trend là +2.25, tức là xác suất xảy ra ngẫu nhiên dưới 1.2%. Không chỉ vậy, phân phối điểm của Hưng Yên cũng có KL divergence cao so với các tỉnh tương đồng.

Tuy nhiên, phát hiện thống kê không phải bằng chứng gian lận. Có thể có các giải thích khác: tỉnh có chính sách ôn thi đặc biệt, giáo viên adapt CT2018 sớm hơn, hay đơn giản là sampling variability. Kết luận đúng đắn là: **cần điều tra thêm bằng microdata và dữ liệu thanh tra**. Thống kê chỉ raise red flag, không phán xét.

---

## Nhìn lại toàn bộ: điều gì quan trọng nhất?

Ba năm trước, nếu ai hỏi "điều gì ảnh hưởng nhất đến điểm thi THPT Việt Nam?", câu trả lời trực quan có thể là COVID, hoặc khoảng cách giàu nghèo, hoặc trường chuyên. Nghiên cứu này cho kết quả khác hẳn.

**CT2018 là tác nhân lớn nhất** — lớn hơn COVID, lớn hơn urban premium, lớn hơn bất cứ chính sách địa phương nào trong giai đoạn 2021–2026. Và nó ảnh hưởng không đều: nông thôn chịu nặng hơn thành phố, tạo ra một vòng xoáy mà nếu không có can thiệp sẽ tiếp tục nới rộng khoảng cách vốn đã tồn tại.

Điều này không có nghĩa CT2018 là chương trình xấu. Tư duy phản biện và ứng dụng thực tế là hướng đi đúng về dài hạn. Nhưng trong ngắn hạn, hệ thống giáo viên và tài liệu chưa kịp adapt — và học sinh đang trả giá cho khoảng cách đó.

Ưu tiên cấp bách nhất không phải là thay chương trình, mà là **đưa nguồn lực hỗ trợ đến đúng nơi cần nhất**: giáo viên nông thôn, tài liệu CT2018 phù hợp, và theo dõi liên tục để biết adaptation curve đang đi theo hướng nào trong những năm tiếp theo.

---

*← [11 Kết luận tổng hợp](11_conclusions.md) | [Index](index.md)*
