# 🏛️ Kiến Trúc: Tổng Quan Hệ Thống & Phân Rã Dịch Vụ

## 1. Phân Tách Nghiệp Vụ & Ranh Giới Dịch Vụ

Hệ thống được thiết kế theo mô hình kiến trúc microservices hướng miền (Domain-Driven Microservices), triển khai chủ yếu bằng **ngôn ngữ Go (Golang)** nhằm tối đa hóa khả năng xử lý đồng thời, giảm thiểu độ trễ và giữ cho mức tiêu thụ tài nguyên máy chủ ở mức tối ưu nhất.

```mermaid
classDiagram
    class CoreAPIService {
        +XacThucNguoiDung(credentials)
        +KiemTraPhienLamViec(token)
        +QuanLyHanNgachDoanhNghiep(tenantId)
        +LuuTru: MySQL 8.0 (ACID)
    }

    class MarketingService {
        +BienDichQuyTrinhChienDich(blueprint)
        +LapLichBatchTacVu(tasks)
        +KiemToanLichSuChay(runId)
        +LuuTru: MongoDB 6.0 (Documents)
    }

    class ChatbotService {
        +XuLyWebhookDaKenh(provider, payload)
        +ThucThiAgentGoiCongCu(history, tools)
        +TruyVanTriThucVector(prompt)
        +LuuTru: MongoDB + Vector Store
    }

    class TaskOrchestrator {
        +KiemTraTacVuChoXuLy()
        +CapPhepLeaseChoWorker(workerId, taskId)
        +GiamSatNhipTimWorker()
        +LuuTru: Redis (Streams + Locks)
    }

    CoreAPIService <--> TaskOrchestrator : Kiểm tra Token & Hạn ngạch
    MarketingService --> TaskOrchestrator : Đẩy Pipeline thực thi
    ChatbotService --> TaskOrchestrator : Kích hoạt Luồng tự động hóa
```

### Danh Mục & Trách Nhiệm Từng Dịch Vụ:

| Tên Dịch Vụ | Ngôn Ngữ Chính | Động Cơ Lưu Trữ | Vai Trò & Nhiệm Vụ |
| :--- | :--- | :--- | :--- |
| **`svc-core-api`** | Go 1.22 | **MySQL 8.0** | Quản lý danh tính người dùng, phân quyền RBAC, cơ cấu tổ chức doanh nghiệp, hạn mức đăng ký thanh toán và bảng thu hồi token. |
| **`svc-business-marketing`** | Go 1.22 | **MongoDB 6.0** | Lưu trữ schema động cho các chiến dịch tiếp thị, đồ thị node tự động hóa, mẫu chiến dịch và lịch sử kiểm toán thực thi. |
| **`svc-business-chatbot`** | Go 1.22 | **MongoDB + Redis** | Tiếp nhận webhook thông lượng cao từ các kênh đối tác (Facebook Messenger, Telegram Bot), gọi công cụ LLM Tool Calling, lưu trữ vector tri thức RAG. |
| **`orchestrator-go`** | Go 1.22 | **Redis (In-Memory)** | Dịch vụ điều phối phi trạng thái (Stateless), cấp phát hợp đồng tác vụ (Lease), theo dõi nhịp tim worker và thu hồi tác vụ chết (Dead-letter recovery). |
| **`wkr-marketing`** | Python 3.11 | SQLite / Bộ nhớ cục bộ | Tiến trình thực thi tự động hóa độc lập sử dụng Playwright, điều hướng proxy và vượt cơ chế chống bot fingerprint. |

---

## 2. Chiến Lược Lưu Trữ Đa Hình (Polyglot Persistence)

Một hệ cơ sở dữ liệu đơn lẻ không thể vừa đảm bảo tính toàn vẹn giao dịch tài chính (ACID), vừa hỗ trợ đồ thị node động biến đổi liên tục, vừa xử lý hàng chục nghìn thao tác điều phối tác vụ với độ trễ micro-giây. Hệ thống áp dụng **Chiến lược Lưu trữ Đa hình**:

```mermaid
flowchart LR
    subgraph CoSoDuLieu["Chiến Lược Lưu Trữ Chuyên Biệt"]
        MYSQL[("MySQL 8.0\nCơ sở Dữ liệu Quan hệ")]
        MONGO[("MongoDB 6.0\nCơ sở Dữ liệu Tài liệu")]
        REDIS[("Redis 7.2\nLưu trữ Trong Bộ nhớ")]
    end

    subgraph NghiepVu["Nghiệp Vụ Sử Dụng"]
        U1["Doanh nghiệp, Người dùng, Hóa đơn\n• Ràng buộc ACID nghiêm ngặt\n• Toàn vẹn tham chiếu quan hệ"]
        U2["Quy trình Động, Đồ thị Node, Nhật ký\n• Schema đa hình linh hoạt\n• Thông lượng ghi cao"]
        U3["Hàng đợi Luồng, Khóa Phân tán\n• Đọc/Ghi dưới 1 mili-giây\n• Pub/Sub & Streaming"]
    end

    U1 --> MYSQL
    U2 --> MONGO
    U3 --> REDIS
```

### Tại Sao Dùng Redis Streams Thay Vì Kafka/RabbitMQ Nặng Nề?
1. **Tiết Kiệm Tài Nguyên Hạ Tầng:** Hệ thống được thiết kế để vận hành tốt trên các cụm K3s gọn nhẹ. Việc duy trì một cụm Kafka + ZooKeeper/KRaft sẽ ngốn hàng gigabyte RAM chỉ cho trạng thái nhàn rỗi.
2. **Khả Năng Phân Nhóm Tiêu Thụ Toàn Diện:** Redis Streams cung cấp đầy đủ Consumer Groups, danh sách chờ xác nhận (PEL) và lệnh xác nhận nguyên tử (`XACK`), đáp ứng trọn vẹn yêu cầu vận hành mà không cần hạ tầng phức tạp.
3. **Thống Nhất Khóa & Hàng Đợi:** Sử dụng chung Redis cho cả khóa phân tán (`SET NX EX`) và hàng đợi sự kiện giúp loại bỏ sự phức tạp của cơ chế Two-Phase Commit giữa các dịch vụ.

---

## 3. Vòng Đời Xử Lý Yêu Cầu (End-to-End Sequence)

```mermaid
sequenceDiagram
    autonumber
    actor User as Khách Hàng / Trình Duyệt
    participant Edge as Cloudflare Pages (_middleware.ts)
    participant Core as svc-core-api (Go)
    participant Mkt as svc-business-marketing (Go)
    participant Redis as Redis (Streams & Lock)
    participant Orch as orchestrator-go
    participant MQTT as MQTT Broker (EMQX)
    participant Worker as wkr-marketing (Desktop)

    User->>Edge: POST /api/v1/campaigns/trigger
    Note over Edge: Tầng Biên xác thực JWT & lọc header nội bộ
    Edge->>Mkt: Chuyển tiếp yêu cầu đã chuẩn hóa
    Mkt->>Core: Kiểm tra hạn ngạch của doanh nghiệp
    Core-->>Mkt: Hạn ngạch hợp lệ (200 OK)
    Mkt->>Redis: XADD stream:tasks {task_id, payload, lease_duration}
    Mkt-->>User: 202 Accepted {run_id: "run_xyz"}

    Orch->>Redis: XREADGROUP GROUP orch_workers
    Redis-->>Orch: Trả về gói tác vụ
    Orch->>Redis: Lấy Khóa Lease (worker_id, task_id, TTL: 60s)
    Orch->>MQTT: Đẩy lệnh vào topic `worker/{id}/cmd`
    MQTT->>Worker: Giao tác vụ qua kết nối TCP liên tục
    
    loop Mỗi 20 giây trong lúc thực thi
        Worker->>MQTT: Gửi nhịp tim `worker/{id}/heartbeat`
        MQTT->>Orch: Chuyển tiếp nhịp tim
        Orch->>Redis: Gia hạn khóa Lease Lock (+60s)
    end

    Worker->>MQTT: Báo cáo sự kiện Hoàn tất tác vụ
    MQTT->>Orch: Chuyển tiếp kết quả
    Orch->>Redis: XACK stream:tasks + Giải phóng Khóa Lease
    Orch->>Redis: XADD stream:events {status: "COMPLETED"}
```