# 🚀 Biztada: Mạng Lưới Tự Động Hóa Phân Tán & AI CRM Thời Gian Thực

[![Lĩnh vực](https://img.shields.io/badge/L%C4%A9nh%20v%E1%BB%B1c-Enterprise%20Automation%20%7C%20Distributed%20Systems-0284c7?style=flat-square)](https://github.com/DrLucifer1810)
[![Backend](https://img.shields.io/badge/Backend-Go%20%7C%20Python%20%7C%20Redis%20Streams-10b981?style=flat-square)](https://github.com/DrLucifer1810)
[![Edge & Messaging](https://img.shields.io/badge/Edge%20%26%20Messaging-Cloudflare%20Pages%20Functions%20%7C%20MQTT-8b5cf6?style=flat-square)](https://github.com/DrLucifer1810)
[![Hạ tầng](https://img.shields.io/badge/H%E1%BA%A1%20t%E1%BA%A7ng-K3s%20%7C%20Docker%20%7C%20PyInstaller-f59e0b?style=flat-square)](https://github.com/DrLucifer1810)

> **Tổng quan Case Study**: Biztada là nền tảng tự động hóa tiếp thị đa kênh, nền tảng dữ liệu khách hàng (CDP) và CRM trí tuệ nhân tạo thời gian thực cấp doanh nghiệp. Tài liệu này đặc tả chi tiết kiến trúc kỹ thuật được xây dựng để điều phối ổn định hàng nghìn worker tự động hóa trình duyệt hoạt động sau tường lửa doanh nghiệp và mạng NAT gia đình.

---

## 📊 Quy Mô Triển Khai & Chỉ Số Thực Tế

- **Quy mô Worker:** Điều phối **1,000+** worker node đồng thời trải rộng trên cả máy chủ Linux đám mây lẫn máy tính để bàn của khách hàng.
- **Độ trễ Điều phối:** Độ trễ gửi lệnh đạt dưới **50ms** từ API trung tâm tới các máy worker thông qua giao thức MQTT liên tục.
- **Độ tin cậy Mạng:** Đạt **99.9%** khả năng kết nối cho các node sau NAT nhờ cơ chế tự động chuyển đổi đường hầm kép (Cloudflare Quick Tunnel + Localtunnel).
- **Tính toàn vẹn Dữ liệu:** **0 trường hợp trùng lặp tác vụ** nhờ cơ chế khóa phân tán Redis Lease và thu hồi danh sách chờ (Pending Entry List - PEL) nguyên tử.
- **Tối ưu Tài nguyên:** Các microservice viết bằng Go duy trì mức tiêu thụ RAM cực thấp (< **45MB** khi rảnh, < **120MB** khi tải tối đa).

---

## 🏛️ Sơ Đồ Kiến Trúc Toàn Cảnh (C4 Topology)

```mermaid
flowchart TB
    subgraph Clients["Tầng Khách Hàng & Kênh Truy Cập"]
        TG_USER["Người dùng Telegram / Mini App"]
        WEB_USER["Giao diện Quản trị Web Portal"]
        EXT["Tiện ích Chrome Extension"]
    end

    subgraph Edge["Tầng Biên Mạng (Cloudflare Edge)"]
        CF_INGRESS["Cloudflare Pages Functions\n(_middleware.ts)"]
        CF_AUTH["Xác thực Token tại Biên\n& Điều hướng Proxy"]
    end

    subgraph CoreBackend["Cụm Microservices Lõi (K3s / Go)"]
        SVC_CORE["svc-core-api (Go)\n• Vòng đời Phiên & Xác thực\n• Tài khoản Doanh nghiệp & Quota\n• MySQL (Quan hệ ACID)"]
        SVC_MKT["svc-business-marketing (Go)\n• Bản thiết kế Chiến dịch\n• Lập lịch Pipeline Tác vụ\n• MongoDB (Tài liệu Động)"]
        SVC_CHAT["svc-business-chatbot (Go)\n• Tiếp nhận Webhook Đa kênh\n• Gọi Công cụ LLM Nhiều lượt\n• Truy xuất Vector Tri thức"]
    end

    subgraph StateBroker["Trạng Thái Chia Sẻ & Luồng Sự Kiện (Stateless Cluster)"]
        REDIS_STREAM["Redis Streams\n• task-events\n• worker-heartbeats\n• execution-logs"]
        REDIS_LOCK["Redis Distributed Lock\n& Quản lý Lease"]
        MQTT_BROKER["MQTT Broker (EMQX)\n• Kênh Điều khiển Hai chiều\n• Bus Lệnh Độ trễ Thấp"]
    end

    subgraph Orchestration["Điều Phối & Phân Bổ Tác Vụ"]
        ORCH["orchestrator-go\n• Quản lý Hạn ngạch Worker\n• Giám sát Nhịp tim Watchdog\n• Thu hồi Dead-Letter Queue"]
    end

    subgraph WorkerFleet["Mạng Lưới Worker Phân Tán (Cloud & Desktop)"]
        subgraph CloudWorker["Worker Máy Chủ Cloud Linux"]
            WKR_CLOUD["wkr-marketing (Python/Playwright)\nTrang trại Trình duyệt Headless"]
        end
        subgraph EdgeWorker["Máy Trạm Khách Hàng (Sau NAT)"]
            WKR_EDGE["Tiến trình Đóng gói PyInstaller\nTự động hóa Playwright + Live Stream"]
            TUNNEL["Đường Hầm Đảo Ngược Động\n(Cloudflare / Fallback)"]
        end
    end

    Clients --> CF_INGRESS
    CF_INGRESS --> CF_AUTH
    CF_AUTH -->|Đường dẫn tương đối nội bộ| SVC_CORE
    CF_AUTH -->|Đường dẫn tương đối nội bộ| SVC_MKT
    CF_AUTH -->|Đường dẫn tương đối nội bộ| SVC_CHAT

    SVC_MKT -->|Đẩy tác vụ| REDIS_STREAM
    SVC_CHAT -->|Đẩy sự kiện| REDIS_STREAM

    ORCH -->|Tiêu thụ & Cấp Lease| REDIS_STREAM
    ORCH <-->|Giữ/Gia hạn Lease Lock| REDIS_LOCK
    ORCH -->|Bắn lệnh điều khiển| MQTT_BROKER

    MQTT_BROKER <-->|Kết nối điều khiển TCP liên tục| WKR_CLOUD
    MQTT_BROKER <-->|Kết nối điều khiển TCP liên tục| WKR_EDGE

    WKR_EDGE -.->|Mở luồng stream theo yêu cầu| TUNNEL
    TUNNEL -.->|Stream HTTPS đảo ngược| WEB_USER
```

---

## 📑 Danh Mục Tài Liệu Kiến Trúc Chuyên Sâu

1. [**Toàn Cảnh Hệ Thống & Microservices (`architecture/01-system-overview.md`)**](./architecture/01-system-overview.md)  
   Phân rã ranh giới nghiệp vụ dịch vụ, chiến lược lưu trữ dữ liệu đa hình Polyglot (MySQL + MongoDB + Redis), và hợp đồng giao tiếp nội bộ.

2. [**Mạng Lưới Worker Hai Kênh & Vượt Rào Cản NAT (`architecture/02-dual-channel-worker-mesh.md`)**](./architecture/02-dual-channel-worker-mesh.md)  
   Giải pháp giao tiếp hai chiều ổn định với các máy tính để bàn của khách hàng nằm sau router gia đình mà không cần mở cổng port hay mua IP tĩnh.

3. [**Điều Phối Tác Vụ Theo Hướng Sự Kiện & Worker Lease (`architecture/03-event-driven-orchestration.md`)**](./architecture/03-event-driven-orchestration.md)  
   Phân tích nhóm tiêu thụ Redis Streams Consumer Groups, giao thức nhịp tim gia hạn khóa tự động và cơ chế Dead-Letter Queue (DLQ).

4. [**Bảo Mật Tầng Biên & Xác Thực Zero-Trust (`architecture/04-edge-security-and-auth.md`)**](./architecture/04-edge-security-and-auth.md)  
   Thiết kế tầng đảo ngược Proxy tại Cloudflare Pages Functions và kiến trúc Sidecar cho xác thực Telegram MTProto.

---

## 🔬 Nghiên Cứu Nghẽn Cổ Chai & Tối Ưu Thực Chiến

- [**Nghẽn Cổ Chai & Tối Ưu Vận Hành (`deep-dives/01-bottlenecks-and-optimizations.md`)**](./deep-dives/01-bottlenecks-and-optimizations.md)  
  Phân tích 3 sự cố sản xuất lớn: Rò rỉ RAM Chromium, nghẽn hạn ngạch đường hầm tunnel và lệch pha trạng thái cụm.
- [**Kiểm Thử Tải & Đánh Giá Tài Nguyên (`deep-dives/02-scalability-and-metrics.md`)**](./deep-dives/02-scalability-and-metrics.md)  
  Số liệu thông lượng, so sánh dấu chân bộ nhớ Go vs Python, và đường cong mở rộng kết nối.
- [**Đóng Gói Desktop, DevOps & Khả Năng Giám Sát (`deep-dives/03-devops-and-packaging.md`)**](./deep-dives/03-devops-and-packaging.md)  
  Đóng gói ứng dụng desktop không phụ thuộc môi trường bằng PyInstaller + Playwright, điều phối K3s Kubernetes và chuẩn hóa Log Trace.

---

## 💻 Mã Nguồn Mẫu Chuẩn Hóa (Sanitized Reference Implementations)

Các module mã nguồn đã được tách rời độc lập, bảo mật và chạy thật:

- [`../sanitized-code/go-worker-lease-dispatcher/`](../sanitized-code/go-worker-lease-dispatcher/): Triển khai Go tiêu thụ Redis Streams với cơ chế cấp lease nguyên tử và hủy ngữ cảnh an toàn.
- [`../sanitized-code/python-resilient-tunnel-manager/`](../sanitized-code/python-resilient-tunnel-manager/): Triển khai Python quản lý đường hầm đảo ngược tự động thăm dò sức khỏe và dự phòng đa nhà cung cấp.
- [`../sanitized-code/edge-api-gateway/`](../sanitized-code/edge-api-gateway/): Middleware Cloudflare Pages Functions bằng TypeScript trung chuyển đường dẫn và lọc tiêu đề bảo mật.
