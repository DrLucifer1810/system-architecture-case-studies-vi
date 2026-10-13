# 🧠 Fusio: Node Nhận Thức Phi Tập Trung & Desktop SuperApp

[![Lĩnh vực](https://img.shields.io/badge/L%C4%A9nh%20v%E1%BB%B1c-Cognitive%20Desktop%20%7C%20Autonomous%20Multi--Agent-6366f1?style=flat-square)](https://github.com/DrLucifer1810)
[![Môi trường Lõi](https://img.shields.io/badge/M%C3%B4i%20tr%C6%B0%E1%BB%9Dng-Rust%20(Tauri%20v2)%20%7C%20Python%203.11%20%7C%20React%2018-0ea5e9?style=flat-square)](https://github.com/DrLucifer1810)
[![Giao thức & P2P](https://img.shields.io/badge/Giao%20th%E1%BB%A9c-Telegram%20MTProto%20%7C%20P2P%20Gossip%20Consensus%20%7C%20MCP-10b981?style=flat-square)](https://github.com/DrLucifer1810)
[![Bộ nhớ](https://img.shields.io/badge/B%E1%BB%99%20nh%E1%BB%9B-SQLite%20WAL%20Blackboard%20%7C%20State%20Graph-f59e0b?style=flat-square)](https://github.com/DrLucifer1810)

> **Tổng quan Case Study**: Fusio là một Desktop SuperApp cấp doanh nghiệp và là một node nhận thức phi tập trung (Decentralized Cognitive Node). Ứng dụng kết hợp nhân hệ điều hành hiệu năng cao viết bằng **Rust (Tauri v2)** với **Bộ não AI Python (Python Brain)** và giao diện **React 18** để cung cấp khả năng tự động hóa Multi-Agent tự thích nghi, chia sẻ kỹ năng ngang hàng P2P, truyền dữ liệu nhị phân Telegram MTProto bản địa, và biên dịch Macro tự động.

---

## 📊 Các Chỉ Số Kiến Trúc Đột Phá

- **Truy Xuất Trạng Thái Độ Trễ 0ms:** Đạt **độ trễ 0ms** nhờ Bảng Đen Phiên Làm Việc (Session Blackboard) chạy SQLite chế độ WAL, loại bỏ hoàn toàn các file JSON sidecar dễ xung đột.
- **Tăng Tốc 10,000% Bằng Trình Biên Dịch Macro:** Bộ biên dịch Macro tự động dịch lịch sử ReAct thành script Playwright độc lập, **bỏ qua hoàn toàn việc gọi LLM** ở các lần chạy sau, tăng tốc độ thực thi lên gấp 100 lần.
- **Truyền Tệp Lớn 2GB–4GB:** Động cơ Telegram MTProto (TDLib) viết bằng Rust bản địa xử lý mượt mà các file video và tệp sao lưu lớn từ **2GB đến 4GB** mà **không gây nghẽn Python GIL hay rò rỉ RAM**.
- **Chống Vòng Lặp Ảo Giác Bằng Trạm Overwatch:** Loại bỏ hoàn toàn vòng lặp đẻ nhánh vô tận của Agent mà không cần dùng đến các giới hạn `max_depth` cứng nhắc bóp nghẹt tư duy AI.
- **Node Phi Tập Trung P2P:** Tích hợp Symbio Node chạy giao thức P2P Gossip Sub, đồng thuận phi tập trung và kinh tế chia sẻ kỹ năng Skill Dossier với token FWNC.

---

## 🏛️ Sơ Đồ Kiến Trúc Toàn Cảnh (Topology)

```mermaid
flowchart TB
    subgraph UI_Layer["Tầng Giao Diện Người Dùng (React 18 + TypeScript + Zustand)"]
        UI_MAIN["Cửa Sổ Desktop SuperApp\n• Giao diện Chat phong cách Telegram\n• Trực quan hóa Dynamic DAG thời gian thực\n• Khung Ngữ Cảnh & Xem Trực Tiếp Stream"]
        UI_INTERCEPT["Middleware Chặn Nhận Thức\n(Tương tác xin ý kiến Người Dùng)"]
    end

    subgraph Rust_Kernel["Nhân Hệ Điều Hành Bản Địa & Mạng Lưới (Tauri v2 / Rust)"]
        TAURI_IPC["Cầu Nối IPC Zero-Copy Cực Nhanh"]
        TG_MTPROTO["Động Cơ MTProto Telegram Bản Địa\n• Mã hóa cấp Byte AES-IGE / RSA\n• Truyền file đa phương tiện 2GB-4GB\n• Điều khiển Custom Bot chạy ngầm"]
        SYMBIO_NODE["Lõi P2P Symbio Node\n• Động cơ Giao thức P2P Gossip\n• Đồng thuận & Lưu trữ Khối Chuỗi\n• Thưởng Thực thi Mù (Blind Execution)"]
        MCP_SERVER["Model Context Protocol (MCP)\nTrạm Máy Chủ & Quản Trị Công Cụ"]
        WATCHDOG["Giám Sát Vòng Đời Tiến Trình Con\n(Khởi chạy & Theo dõi Python Brain)"]
    end

    subgraph Python_Brain["Tiến Trình Con Bộ Não Nhận Thức (Python 3.11)"]
        ROUTER["Bộ Điều Hướng Nhận Thức & Phân Loại Ý Định\n• Phân loại trực tiếp bằng LLM\n• Rẽ nhánh Tán gẫu vs Thực thi Tác vụ"]
        
        subgraph OrchestrationEngine["Đồ Thị Trạng Thái Động (Dynamic Macro DAG)"]
            STATE_GRAPH["Giám Sát Đồ Thị Trạng Thái\n(Mô hình Dynamic DAG như LangGraph)"]
            ZERO_SHOT["Zero-Shot Discovery (Node 0)\n(Tự động cào tài liệu khi nhận lệnh mù)"]
            AQC["Kiểm Soát Chất Lượng Động (AQC)\n(Ép tiêu chuẩn đánh giá từng Node)"]
            OVERWATCH["Trạm Giám Sát Nhận Thức (Overwatch)\n(Chặn vòng lặp ảo giác đẻ nhánh)"]
        end

        subgraph MemoryVault["Kho Lưu Trữ Trí Nhớ & Học Tập Thống Nhất"]
            BLACKBOARD["Bảng Đen Phiên (SQLite WAL Blackboard)\n• Bộ nhớ làm việc Scoped KV\n• Cây Quỹ đạo Phiên (Session Tree)"]
            MACRO_COMPILER["Bộ Biên Dịch Macro Quy Trình\n(Dịch ReAct sang Playwright trực tiếp)"]
            DOSSIER["Động Cơ Cẩm Nang Kỹ Năng (Dossier)\n(Hợp nhất tri thức & Tải từ GitHub)"]
        end
    end

    subgraph DecentralizedMesh["Mạng Lưới Ngang Hàng P2P & Thế Giới Bên Ngoài"]
        P2P_PEERS["Mạng Lưới Node P2P (Gossip / Symbio)"]
        TG_SERVERS["Trung Tâm Dữ Liệu Telegram (MTProto)"]
        LLM_APIS["Nhà Cung Cấp LLM (Gemini, Claude, GPT)"]
    end

    UI_MAIN <--> UI_INTERCEPT
    UI_INTERCEPT <-->|Sự kiện Tauri IPC| TAURI_IPC

    TAURI_IPC <--> TG_MTPROTO
    TAURI_IPC <--> SYMBIO_NODE
    TAURI_IPC <--> MCP_SERVER
    WATCHDOG -->|Khởi chạy & Giám sát nhịp tim| Python_Brain

    TAURI_IPC <==>|Luồng IPC Hai Chiều (JSON-RPC / stdio)| ROUTER
    ROUTER --> STATE_GRAPH
    STATE_GRAPH --> ZERO_SHOT
    STATE_GRAPH --> AQC
    STATE_GRAPH --> OVERWATCH

    STATE_GRAPH <--> BLACKBOARD
    STATE_GRAPH <--> MACRO_COMPILER
    STATE_GRAPH <--> DOSSIER

    SYMBIO_NODE <==>|P2P Gossip (LibP2P/TCP)| P2P_PEERS
    TG_MTPROTO <==>|Socket Nhị Phân TLS MTProto| TG_SERVERS
    Python_Brain <==>|HTTPS Bất Đồng Bộ| LLM_APIS
```

---

## 📑 Danh Mục Tài Liệu Kiến Trúc Chuyên Sâu

1. [**Kiến Trúc Lai Ghép Tauri (Rust) & Python Brain (`architecture/01-system-overview.md`)**](./architecture/01-system-overview.md)  
   Lý do kết hợp Rust và Python, ranh giới phân định trách nhiệm, triệt tiêu nghẽn GIL khi chạy MTProto nhị phân và đường ống IPC Zero-Copy.

2. [**Đồ Thị Trạng Thái Động (Dynamic DAG) & Kiểm Soát Chất Lượng AQC (`architecture/02-cognitive-orchestration-dag.md`)**](./architecture/02-cognitive-orchestration-dag.md)  
   Cơ chế Zero-Shot Discovery (Node 0), tự động ép tiêu chuẩn đánh giá `evaluation_criteria` ở từng bước và vòng lặp tự sửa lỗi (Self-healing).

3. [**Bảng Đen Phiên (Session Blackboard) & Bộ Nhớ Scoped WAL (`architecture/03-session-blackboard-memory.md`)**](./architecture/03-session-blackboard-memory.md)  
   Cơ sở dữ liệu SQLite WAL thay thế hoàn toàn file JSON sidecar, hỗ trợ cây tiến trình đẻ nhánh và chia sẻ dữ liệu với độ trễ 0ms.

4. [**Node Ngang Hàng P2P Symbio & Cổng Kết Nối MCP (`architecture/04-p2p-symbio-node-and-mcp.md`)**](./architecture/04-p2p-symbio-node-and-mcp.md)  
   Giao thức đồng thuận P2P Gossip, thị trường chia sẻ cẩm nang kỹ năng trả phí bản quyền (FWNC), và ảo hóa công cụ bằng giao thức MCP trong Rust.

---

## 🔬 Nghiên Cứu Sâu & Đột Phá Kỹ Thuật

- [**Trạm Giám Sát Overwatch Chống Ảo Giác (`deep-dives/01-hallucination-overwatch.md`)**](./deep-dives/01-hallucination-overwatch.md)  
  Cách giám sát ngữ nghĩa trong cửa sổ trượt 15 bước để chặn đứng vòng lặp đẻ nhánh mà không bóp nghẹt độ sâu tư duy của AI.
- [**Biên Dịch Macro Tự Động (Tăng Tốc 10,000%) (`deep-dives/02-macro-compiler-bypass.md`)**](./deep-dives/02-macro-compiler-bypass.md)  
  Chuyển đổi lịch sử ReAct tốn kém thành script Playwright chạy nội bộ trong 420ms, loại bỏ 100% token ở các lần chạy sau.
- [**Cô Lập Tiến Trình & Vượt Qua Rào Cản Python GIL (`deep-dives/03-rust-python-ipc-performance.md`)**](./deep-dives/03-rust-python-ipc-performance.md)  
  Đẩy toàn bộ mã hóa MTProto và upload video 4GB sang tiến trình Rust đa luồng, giải phóng tài nguyên CPU cho bộ não AI.

---

## 💻 Mã Nguồn Mẫu Chuẩn Hóa (Sanitized Reference Implementations)

- [`../sanitized-code/rust-mcp-ipc-gateway/`](../sanitized-code/rust-mcp-ipc-gateway/): Module Rust định tuyến IPC bất đồng bộ và ảo hóa công cụ Model Context Protocol (MCP).
- [`../sanitized-code/python-cognitive-blackboard/`](../sanitized-code/python-cognitive-blackboard/): Module Python Bảng Đen SQLite WAL quản lý biến Scoped KV và cây quỹ đạo rẽ nhánh.
- [`../sanitized-code/macro-orchestration-compiler/`](../sanitized-code/macro-orchestration-compiler/): Trình biên dịch ReAct sang Playwright script chạy trực tiếp không tốn token.
