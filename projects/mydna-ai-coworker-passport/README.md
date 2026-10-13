# 🧬 Hồ Sơ Kiến Trúc MyDNA (Phiên Bản Tiếng Việt)

[![Ngôn ngữ: Tiếng Việt](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t-red?style=flat-square)](https://github.com/DrLucifer1810/system-architecture-case-studies/tree/main/projects/mydna-ai-coworker-passport)
[![English Edition](https://img.shields.io/badge/Language-English-blue?style=flat-square)](https://github.com/DrLucifer1810/system-architecture-case-studies/tree/main/projects/mydna-ai-coworker-passport)

## 📌 Tóm Tắt Điều Hành

**MyDNA** đại diện cho một bước nhảy vọt trong việc đánh giá năng lực lập trình viên và phân tích hiệu quả cộng tác giữa con người và trí tuệ nhân tạo (AI-Coworker Collaboration). Được xây dựng như một tiến trình ngầm (daemon) bảo vệ quyền riêng tư viết bằng Rust và Tauri v2, hệ thống thu thập thụ động các tín hiệu thao tác của nhà phát triển ở tầng hệ điều hành, làm sạch toàn bộ dữ liệu nhạy cảm ngay trên thiết bị và lập nên một **"Hộ Chiếu Kỹ Năng Thực Chiến"**.

Trong kỷ nguyên GenAI, các tổ chức công nghệ đối mặt với hai nguy cơ lớn:
1. **Ảo tưởng năng lực & Gian lận hồ sơ:** Khối lượng code sinh ra ồ ạt từ LLM có thể che giấu những lỗ hổng kiến thức nghiêm trọng và đưa vào dự án các rủi ro kiến trúc thảm khốc nếu người dùng chỉ copy/paste mù quáng.
2. **Lo ngại bị theo dõi & Xâm phạm quyền riêng tư:** Các phần mềm giám sát truyền thống thường ghi lại bàn phím (keylogger) hoặc chụp màn hình bừa bãi, vi phạm đạo đức và tạo ra lỗ hổng bảo mật rò rỉ dữ liệu khách hàng.

MyDNA giải quyết triệt để hai bài toán này thông qua **Kiến Trúc Thu Thập Tại Biên với Bộ Lọc Khử Dữ Liệu Riêng Tư (PIR)** và **Ma Trận Năng Lực Chuẩn Doanh Nghiệp 6 Chiều** dựa trên thang đo Bloom's Taxonomy và mô hình tiếp thu kỹ năng Dreyfus.

---

## 🏛️ Mục Lục Tài Liệu Kỹ Thuật

### 📐 Tài Liệu Thiết Kế Kiến Trúc
1. [**01. Động Cơ Telemetry Tầng OS & Hệ Sinh Thái Desktop Lai**](./architecture/01-system-overview.md)  
   Tích hợp Win32 API, theo dõi cửa sổ tích cực, Hook trợ năng COM UIAutomation và luồng ghi sự kiện SQLite an toàn.
2. [**02. Đường Ống Lọc & Che Giấu Dữ Liệu Nhạy Cảm (PIR) Phía Client**](./architecture/02-privacy-redaction-pipeline.md)  
   Bộ lọc Regex đơn thể (Singleton) hiệu năng cao, khử sạch API Key, Bearer Token, Email và thẻ tín dụng trước khi gửi prompt.
3. [**03. Ma Trận Radar 6 Chiều & Tỷ Lệ Sửa Đổi Mã (Semantic Edit Ratio)**](./architecture/03-evaluation-matrix-engine.md)  
   Phân tích phả hệ Myers Diff, công thức Edit Ratio toán học, phân loại hành vi nhận thức theo Bloom và hiệu suất sử dụng token.
4. [**04. Máy Chủ Nhúng Model Context Protocol (MCP) Chạy Trên Localhost**](./architecture/04-embedded-mcp-server.md)  
   Máy chủ Axum JSON-RPC 2.0 trên cổng 5050 cung cấp tài nguyên `/mcp/resources/user_dna` cho Cursor, Claude Desktop và Antigravity.

### 🔬 Nghiên Cứu Sâu Kỹ Thuật Thực Chiến
1. [**01. Phả Hệ Clipboard Win32 & Liên Kết Dòng Chảy Tiến Trình**](./deep-dives/01-win32-clipboard-lineage.md)  
   Cơ chế băm 64-bit qua `DefaultHasher`, theo dõi dòng chảy dữ liệu liên ứng dụng mà không lưu trữ nội dung nhạy cảm.
2. [**02. Hệ Thống Đa Agent Trích Xuất DNA Với YAML Tải Động**](./deep-dives/02-hot-reload-multi-agent-dna.md)  
   Kiến trúc prompt mô-đun hóa kiểu CrewAI, 3 Agent chuyên biệt (`CodeAnalyzer`, `CommunicationAnalyzer`, `CareerDiagnostic`) và cập nhật prompt không cần build lại app.
3. [**03. Đồng Hành Webview Ẩn Thay Thế Tự Động Hóa Trình Duyệt Playwright**](./deep-dives/03-headless-companion-ipc.md)  
   Tận dụng WebView2 có sẵn của hệ điều hành, IPC qua URL fragment hash (`#bzt-{KIND}-{stamp}`), loại bỏ gói Chromium 200MB và tránh bị chặn bot.

---

## 📊 Bảng Chỉ Số Kiến Trúc Trọng Yếu

| Phân Tầng | Công Nghệ | Vai Trò Chính | Chỉ Số SLA Thực Chiến |
| :--- | :--- | :--- | :--- |
| **OS Telemetry** | Rust (`windows-rs`, `windows-sys`) | Quét cửa sổ tích cực và PID ứng dụng | Độ trễ hook `< 2 ms` |
| **Clipboard Lineage** | `clipboard-win`, `DefaultHasher` | Truy vết dữ liệu qua mã băm 64-bit Hex | Không lưu văn bản thô vĩnh viễn |
| **Filesystem Watcher** | `notify` (Notify-rs) | Bắt sự kiện lưu tệp mã nguồn theo thời gian thực | Xử lý bất đồng bộ qua mpsc channel |
| **State Machine** | `rusqlite` (SQLite WAL) | Cơ sở dữ liệu nhúng giao dịch đơn tệp | Không cần cấu hình máy chủ |
| **Privacy Redaction** | `regex` kết hợp `OnceLock` | Khử sạch bí mật và dữ liệu định danh (PII) | Băng thông lọc `> 450 MB/s` |
| **Diff & Metrics** | `similar` (TextDiff) | Phân tích dòng code thêm/xóa/giữ nguyên | Edit Ratio tất định $0.0 - 1.0$ |
| **Agent Server** | `axum`, `tokio` (Cổng 5050) | Cổng MCP JSON-RPC 2.0 cho AI IDE ngoài | Phản hồi truy vấn `< 1.2 ms` |
| **Desktop UI** | Tauri v2, Chart.js, HTML5 | Biểu đồ Radar mạng nhện & hồ sơ cá nhân | Tận dụng WebView2 nhẹ của Windows |
