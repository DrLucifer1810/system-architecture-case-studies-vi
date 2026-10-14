# ⚔️ F2F Trading Arena: Động Cơ Giải Đấu & Trận Đấu Giao Dịch Tài Chính Thời Gian Thực

[![Case Study Kiến Trúc](https://img.shields.io/badge/Ki%E1%BA%BFn%20tr%C3%BAc-Case%20Study%20S%E1%BA%A3n%20Xu%E1%BA%A5t-0ea5e9?style=flat-square)](https://github.com/DrLucifer1810/system-architecture-case-studies-vi)
[![Core: Python & Go](https://img.shields.io/badge/Core-FastAPI%20%7C%20Go%20%7C%20aiomysql-3b82f6?style=flat-square&logo=python)](https://fastapi.tiangolo.com/)
[![Trạng Thái: Redis Streams](https://img.shields.io/badge/Tr%E1%BA%A1ng%20th%C3%A1i-Redis%20Streams%20%7C%20PubSub-red?style=flat-square&logo=redis)](https://redis.io/)
[![Cụm: Kubernetes](https://img.shields.io/badge/C%E1%BB%A5m-Kubernetes%20Pods%20%7C%20APScheduler-326ce5?style=flat-square&logo=kubernetes)](https://kubernetes.io/)
[![Giấy Phép: MIT](https://img.shields.io/badge/Gi%E1%BA%A5y%20ph%C3%A9p-MIT-emerald?style=flat-square)](LICENSE)

[🌐 English Edition available at: system-architecture-case-studies](https://github.com/DrLucifer1810/system-architecture-case-studies/tree/main/projects/f2f-trading-tournament-engine)

---

## 📌 Tóm Tắt Dự Án

**F2F Arena (Face-to-Face Trading Arena)** là nền tảng phân tán hướng sự kiện (Event-Driven) chịu tải cao được thiết kế cho các **giải đấu giao dịch tài chính PvP đối kháng trực tiếp và giải đấu nhiều vòng quy mô lớn**.

Kết nối trực tiếp với các máy chủ giao dịch của sàn môi giới (MetaTrader MT4/MT5 và cổng thanh khoản), F2F Arena điều phối môi trường thi đấu cạnh tranh thời gian thực: cấp phát tài khoản giao dịch tự động, kiểm soát phân nhánh giải đấu (bracket), tính toán thời gian vòng đấu tự động, theo dõi PnL/Equity theo thời gian thực và phát sóng bảng xếp hạng WebSocket tức thì qua cụm Kubernetes đa pod.

Khác với các nền tảng e-sports thông thường, giải đấu tài chính đòi hỏi các tiêu chuẩn kỹ thuật phi chức năng khắt khe:
- **Quản lý Bể Tài Khoản Sàn (Account Pooling) & Cô Lập Mật Khẩu:** Tự động xuất và thu hồi tài khoản MetaTrader cho người chơi trong vài trăm mili-giây, khôi phục số dư tự động sau trận đấu.
- **Phục Hồi Sự Kiện Không Thất Thoát (Zero-Loss State):** Trader dùng thiết bị di động (kể cả Telegram Mini App) liên tục bị rớt mạng khi chuyển 4G; đường ống Redis Streams lưu trữ và phát lại toàn bộ sự kiện đã bỏ lỡ ngay khi kết nối lại.
- **Tính Toán Lịch Trình Vòng Đấu Tất Định:** Phân nhánh giải đấu (Vòng tích điểm Points chuyển sang Vòng loại trực tiếp Knockout) tự động tính toán thời gian theo chuẩn UTC mà không cần quản trị viên can thiệp thủ công.

---

## 🏛️ Sơ Đồ Kiến Trúc Tổng Thể

```mermaid
flowchart TB
    subgraph Client_Layer ["📱 Phân Tầng Ứng Dụng Client"]
        WebTrader["React 18 Trader WebApp<br/>(Phòng Đấu Trực Tiếp / Biểu Đồ Nến)"]
        TgMiniApp["Telegram Mini App<br/>(Xác Thực JWT / Đăng Ký 1-Chạm)"]
        AdminCRM["Bảng Điều Khiển Quản Trị & CRM<br/>(Vite / React / TypeScript / Lucide)"]
    end

    subgraph Ingress_Layer ["🛡️ Cổng Vào & API Gateway"]
        APIGW["Cụm Ingress FastAPI<br/>(Uvicorn ASGI / Vòng Lặp Asyncio)"]
        AuthModule["Bộ Xác Thực Telegram & JWT<br/>(HMAC-SHA256 / PyJWT)"]
    end

    subgraph Core_Services ["⚙️ Dịch Vụ Cốt Lõi Phân Tán (K8s Pods)"]
        TournamentSvc["Quản Lý Giải Đấu<br/>(Vòng Points & Phân Nhánh Knockout)"]
        MatchSvc["Động Cơ Trận Đấu 1v1 PvP<br/>(Phòng Chờ & Trận Đấu Sống)"]
        AccountPool["Cầu Nối Bể Tài Khoản Sàn<br/>(Cấp Phát & Đặt Lại MT4/MT5)"]
        Scheduler["Tiến Trình Định Thời APScheduler<br/>(Chuyển Vòng Tự Động)"]
    end

    subgraph State_And_Message ["⚡ Nền Tảng Trạng Thái & Hàng Đợi Sự Kiện"]
        RedisPubSub["Redis Pub/Sub<br/>(Phát Sóng WebSocket Đa Pod)"]
        RedisStreams["Redis Streams (XADD/XREVRANGE)<br/>(Phục Hồi Sự Kiện Theo Ngữ Cảnh)"]
        LBQueue["Hàng Đợi Công Việc (queue:lb:match_assignments)<br/>(Cân Bằng Tải Bot Giao Dịch)"]
        MySQL[("Bể Kết Nối Async MySQL (aiomysql)<br/>(tournaments, matches, accounts)")]
    end

    subgraph Trading_Infrastructure ["📈 Hạ Tầng Giao Dịch Sàn Môi Giới"]
        BrokerLB["Bộ Cân Bằng Tải Máy Chủ Giao Dịch<br/>(Cụm Tiến Trình Daemon Python)"]
        MTBridge["Cầu Nối MetaTrader 4/5<br/>(Quét Lệnh Sống, Vốn & Sụt Giảm Tài Khoản)"]
    end

    WebTrader & TgMiniApp --> APIGW
    AdminCRM --> APIGW
    APIGW --> AuthModule
    AuthModule --> TournamentSvc & MatchSvc & AccountPool

    TournamentSvc --> Scheduler
    Scheduler --> MySQL
    MatchSvc --> MySQL
    AccountPool --> MySQL

    MatchSvc --> LBQueue
    LBQueue --> BrokerLB
    BrokerLB --> MTBridge
    MTBridge --> BrokerLB
    BrokerLB --> RedisPubSub

    MatchSvc --> RedisStreams
    RedisStreams --> APIGW
    RedisPubSub --> APIGW
    APIGW <==>|"Luồng WebSocket Giao Dịch Sống"| WebTrader
```

---

## 📁 Mục Lục Tài Liệu Kỹ Thuật

```text
projects/f2f-trading-tournament-engine/
├── README.md                                 # Bản Đặc Tả Kiến Trúc Tổng Thể (Hiện tại)
├── architecture/
│   ├── 01-system-overview.md                 # Kiến trúc bất đồng bộ thông lượng cao & Cụm Pod K8s
│   ├── 02-distributed-matchmaking-engine.md  # Vòng Points, Nhánh Knockout & Động cơ Ghép Cặp
│   ├── 03-broker-account-pool-bridge.md      # Bể tài khoản MetaTrader, hàng đợi cân bằng tải & đặt lại vốn
│   └── 04-realtime-websocket-event-recovery.md# WebSocket đa pod & Redis Streams phục hồi sự kiện không mất mát
├── deep-dives/
│   ├── 01-round-timing-and-bracket-fairness.md# Tính toán thời gian vòng đấu tự động & công thức phân hạng
│   ├── 02-multi-pod-redis-stream-recovery.md # Phục hồi sự kiện theo ngữ cảnh qua Redis Streams (XADD/XREVRANGE)
│   └── 03-trading-loadbalancer-dispatch.md   # Phân phối tải bot giám sát tài khoản sàn và cô lập mật khẩu
└── sanitized-code/
    ├── fastapi-match-event-recovery/         # Mã nguồn Python Async Redis Streams Event Recovery kèm test
    ├── go-bracket-matchmaker/                # Mã nguồn Go sinh nhánh đấu giải đấu Knockout kèm test
    └── broker-account-pool-dispatcher/       # Mã nguồn Python điều phối hàng đợi tài khoản kèm test
```

---

## ⚡ Chỉ Số Vận Hành & Cam Kết SLA Thực Chiến

| Chỉ Số Vận Hành | Cam Kết SLA / Thực Tế Đo Đạc | Lựa Chọn Thiết Kế Kiến Trúc |
| :--- | :--- | :--- |
| **Độ Trễ Phân Bổ Trận Đấu** | `< 250 ms` | Đẩy hàng đợi Redis bất đồng bộ (`queue:lb:match_assignments`) |
| **Tần Suất Cập Nhật PnL** | `1000 ms / nhịp` | Ghép kênh Redis Pub/Sub vào luồng WebSocket ASGI |
| **Thời Gian Phục Hồi Khi Mất Mạng** | `< 15 ms phát lại` | Redis Streams theo ngữ cảnh (`XREVRANGE` giới hạn 100 bản ghi) |
| **Cấp Phát Tài Khoản Sàn** | `O(1) Khóa Nguyên Tử` | Giao dịch MySQL với máy trạng thái tài khoản |
| **Khả Năng Mở Rộng Pod** | Mở rộng ngang trên K8s | Các pod FastAPI phi trạng thái định danh qua `POD_ID` |
| **Chịu Lỗi Giải Đấu** | Không mất mát trạng thái | Lưu trữ bền vững MySQL + vòng lặp tự phục hồi APScheduler |
