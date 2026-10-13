# 📐 Tài Liệu Kiến Trúc 03: Ma Trận Radar 6 Chiều & Tỷ Lệ Sửa Đổi Mã (Semantic Edit Ratio)

## 1. Khung Đánh Giá Năng Lực Chuẩn Doanh Nghiệp

Thay vì đánh giá lập trình viên bằng số lượng commit hay số dòng code (LOC) - những chỉ số vô nghĩa trong thời đại AI, MyDNA đo lường **Độ sâu nhận thức, Kỹ năng làm chủ công cụ AI và Tính kỷ luật công nghệ**.

Khung đánh giá kết hợp hai mô hình giáo dục và phát triển kỹ năng uy tín nhất thế giới:
1. **Thang đo Bloom (Bloom's Revised Taxonomy):** Đi từ mức độ tư duy thấp (Ghi nhớ / Copy mù quáng) lên các mức độ làm chủ (Ứng dụng / Phân tích / Đánh giá phản biện / Sáng tạo).
2. **Mô hình tiếp thu kỹ năng Dreyfus (Dreyfus Model):** Nhận diện hành vi từ người mới bắt đầu (Novice - tin tưởng tuyệt đối vào AI) đến chuyên gia (Proficient/Expert - chủ động phát hiện và sửa lỗi ảo giác của mô hình).

```mermaid
radar-chart
    title "Ma Trận Năng Lực Lập Trình Viên 6 Chiều"
    "Competence (Năng Lực)" : 88
    "Discipline (Kỷ Luật)" : 92
    "Creativity (Sáng Tạo)" : 78
    "Critical Thinking (Phản Biện)" : 90
    "Collaboration (Làm Việc Nhóm)" : 85
    "AI Token Efficiency (Hiệu Suất Token)" : 94
```

---

## 2. Định Nghĩa Toán Học Về Tỷ Lệ Sửa Đổi (Semantic Edit Ratio)

Hành vi của lập trình viên sau khi nhận kết quả từ AI phản ánh trực tiếp năng lực chuyên môn của họ. Nếu người dùng nhận code từ AI và lưu ngay mà không sửa một ký tự nào, họ có thể đang rơi vào bẫy **Mù Ảo Giác Thụ Động (Passive Hallucination Blindness)**. Ngược lại, nếu họ xóa sạch và viết lại toàn bộ, câu prompt ban đầu đã thất bại hoàn toàn.

MyDNA tính toán **Tỷ Lệ Sửa Đổi ($\mathcal{E}$)** dựa trên thuật toán so khớp dòng mã Myers Diff (`similar` crate):

$$\mathcal{E} = rac{\Delta_{	ext{thêm}} + \Delta_{	ext{xóa}}}{\Delta_{	ext{thêm}} + \Delta_{	ext{xóa}} + \Delta_{	ext{giữ nguyên}}}$$

Ý nghĩa các khoảng giá trị:
- $\mathcal{E} = 0.0$: Chấp nhận 100% nguyên văn từ AI (Không chỉnh sửa).
- $0.0 < \mathcal{E} \le 0.5$: Chuyên gia tinh chỉnh (sửa lại tên biến, chuẩn hóa convention dự án, bổ sung xử lý lỗi biên).
- $0.5 < \mathcal{E} < 1.0$: Tái cấu trúc lớn (phát hiện lỗi logic của AI, sửa thuật toán).
- $\mathcal{E} = 1.0$: Vứt bỏ hoàn toàn code AI để tự viết lại (lãng phí 100% chi phí token).

```rust
pub fn calculate_edit_ratio(ai_output: &str, final_user_output: &str) -> f64 {
    if ai_output.is_empty() {
        return 1.0;
    }

    let diff = TextDiff::from_lines(ai_output, final_user_output);
    let mut total_lines = 0;
    let mut changed_lines = 0;

    for change in diff.iter_all_changes() {
        total_lines += 1;
        match change.tag() {
            ChangeTag::Delete | ChangeTag::Insert => changed_lines += 1,
            ChangeTag::Equal => {}
        }
    }

    if total_lines == 0 {
        return 0.0;
    }

    (changed_lines as f64) / (total_lines as f64)
}
```

---

## 3. Gom Cụm Phiên Làm Việc (Sessionization Logic)

Tiến trình nền tự động liên kết các sự kiện rời rạc thành một phiên làm việc có ý nghĩa:
1. **Điểm bắt đầu:** Phát hiện sự kiện `CLIPBOARD_COPY` từ một cửa sổ ứng dụng AI (ChatGPT, Gemini, Cursor AI panel).
2. **Ngữ cảnh phiên:** Ghi nhận đoạn code AI vừa sinh ra và đánh dấu mốc thời gian bắt đầu.
3. **Điểm kết thúc:** Người dùng nhấn Lưu file trong IDE (`FILE_SAVED`) hoặc gửi văn bản hoàn chỉnh.
4. **Tính điểm:** Đo lường Edit Ratio, ước tính chi phí token ($pprox rac{	ext{độ dài}}{4}$), và chuyển prompt đánh giá cho LLM.
