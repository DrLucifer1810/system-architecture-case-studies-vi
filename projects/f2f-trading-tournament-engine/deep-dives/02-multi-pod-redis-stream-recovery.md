# 🔬 Nghiên Cứu Sâu Kỹ Thuật 02: Phục Hồi Sự Kiện Theo Ngữ Cảnh Qua Redis Streams (XADD/XREVRANGE)

## 1. Giải Pháp Chống Đứt Gãy Dữ Liệu Cho Thiết Bị Di Động

Trong giao dịch tài chính, việc mất một thông báo vào lệnh có thể khiến đấu thủ đưa ra quyết định sai lầm.

Thay vì bắt client phải query lại toàn bộ cơ sở dữ liệu MySQL khi kết nối lại (gây sập DB khi hàng nghìn người cùng rớt mạng lúc cao điểm), F2F Arena sử dụng **Redis Streams Phân Vùng Theo Ngữ Cảnh**:
- Các Stream được chia nhỏ theo `match_events:{id}` và `tournament_events:{id}`.
- Khi kết nối lại, client chỉ cần gửi kèm `last_event_id` cuối cùng nhận được, pod sẽ gọi `XREVRANGE` để bắn luồng bù đắp trong chưa đầy 15 mili-giây.

---

## 2. Chiến Lược Dọn Dẹp RAM & Tối Ưu Bộ Nhớ
- **Cắt Stream Tự Động (Stream Capping):** Dùng `maxlen=100, approximate=True` để giới hạn bộ nhớ Stream ở độ phức tạp O(1).
- **Hết Hạn Tự Động (TTL):** Mỗi khi có sự kiện mới, Stream được gia hạn thêm 300 giây (5 phút). Khi trận đấu kết thúc, toàn bộ dữ liệu tự hủy để giải phóng RAM cho Redis.
- **Lọc Sự Kiện Rác:** Các sự kiện cập nhật số người xem hay chat đều không được đưa vào Stream phục hồi.
