# 🖥️ Local Server: Trung Tâm Dữ Liệu Thu Nhỏ Bare-Metal Kubernetes Tại Tầng Biên

[![Lĩnh vực](https://img.shields.io/badge/L%C4%A9nh%20v%E1%BB%B1c-Edge%20Computing%20%7C%20Bare--Metal%20Kubernetes-0284c7?style=flat-square)](https://github.com/DrLucifer1810)
[![Điều phối K8s](https://img.shields.io/badge/%C4%90i%E1%BB%81u%20ph%E1%BB%91i-K3d%20%7C%20K3s%20%7C%20Docker%20Registry-10b981?style=flat-square)](https://github.com/DrLucifer1810)
[![Mạng & Bảo mật](https://img.shields.io/badge/M%E1%BA%A1ng-Cloudflare%20Tunnel%20%7C%20Dual--WAN%204G%20Failover-8b5cf6?style=flat-square)](https://github.com/DrLucifer1810)
[![Phần cứng & Điện](https://img.shields.io/badge/Ph%E1%BA%A7n%20c%E1%BB%A9ng-Intel%2035W%20TDP%20%7C%20LiFePO4%20EPS%2014h-f59e0b?style=flat-square)](https://github.com/DrLucifer1810)

> **Tổng quan Case Study**: Dự án `local-server` đại diện cho một kiến trúc trung tâm dữ liệu thu nhỏ (Edge Micro-Datacenter) tự chủ hoàn toàn. Hệ thống điều phối toàn bộ cụm backend Tadagram/Biztada—bao gồm **10 microservices container hóa**, **4 động cơ cơ sở dữ liệu đa hình**, và **cổng đảo ngược Ingress tầng biên**—chạy bare-metal trên một máy tính Mini PC tiết kiệm điện với khả năng chịu lỗi mạng và nguồn điện 24/7.

---

## 📊 Các Chỉ Số Vận Hành Cốt Lõi

- **Mật Độ Tải Cao:** Vận hành trơn tru **10 microservices sản xuất** + **4 hệ cơ sở dữ liệu** (MySQL 8.0, MongoDB 6.0, Redis 7.0, Mosquitto MQTT) trên duy nhất một máy trạm Mini PC **16GB RAM / 35W TDP**.
- **Tiết Kiệm Chi Phí 99.5%:** Cắt giảm chi phí hạ tầng từ **$420/tháng** (thuê cụm Kubernetes trên AWS/DigitalOcean) xuống chỉ còn khoảng **~50.000 VNĐ (~$1.80)/tháng tiền điện**.
- **Dự Phòng Mạng Hai Kênh (Dual-WAN 4G Failover):** Router cân bằng tải tự động chuyển đổi từ mạng Cáp quang chính sang SIM 4G dự phòng trong vòng **3–5 giây**; đường hầm Cloudflare Tunnel tự động kết nối lại tức thì mà không cần can thiệp cấu hình IP.
- **Dự Phòng Điện 14 Tiếng (EPS Mode):** Trạm điện di động 512Wh pin LiFePO4 hoạt động ở chế độ EPS (< **30ms chuyển mạch**), đảm bảo máy chủ và mạng hoạt động liên tục không gián đoạn ngay cả khi mất điện lưới kéo dài.
- **Bảo Mật Zero-Trust:** **Không mở bất kỳ cổng port nào trên router**; toàn bộ lưu lượng được điều hướng qua đường hầm Cloudflare Zero Trust bảo mật.

---

## 🏛️ Sơ Đồ Kiến Trúc Toàn Cảnh (Master Blueprint)

```mermaid
graph TD
    %% Internet & Security Layer
    subgraph External_Network ["🌐 Mạng Internet & Tầng Bảo Mật Biên"]
        User["📱 Người Dùng Web / Mobile / Telegram Mini App"]
        CF_Pages["Cloudflare Pages (Lưu trữ Frontend)"]
        CF_Tunnel["🔒 Cloudflare Zero Trust Tunnel (Tiến trình cloudflared)"]
        User -->|HTTPS Frontend| CF_Pages
        User -->|HTTPS API Requests| CF_Tunnel
    end

    %% Edge Machine Layer
    subgraph BareMetal_Node ["⚡ Máy Chủ Biên Cục Bộ (Ubuntu Server 22.04 LTS / K3d Cluster)"]
        
        %% Ingress Layer
        subgraph Ingress_Layer ["🚪 Tầng Điều Hướng Ingress & LoadBalancer"]
            Traefik["Traefik / NGINX Ingress Controller (Cổng 80/443)"]
            CF_Tunnel -->|Chuyển tiếp HTTP Loopback:80| Traefik
        end

        %% Core Backend Microservices
        subgraph Core_Services ["🧠 Nhóm Dịch Vụ Cốt Lõi"]
            Orch["1. orchestrator (Go/Python)\nQuản lý Lease & Đăng ký Worker"]
            CoreAPI["2. svc-core-api (Go)\nDanh tính, Hạn mức & Xác thực"]
            Sidecar["3. telegram-sidecar (Rust)\nĐộng cơ Phiên MTProto"]
            Obs["4. svc-observability (Go)\nThu thập Log & Prometheus"]
        end

        %% Business Microservices
        subgraph Business_Services ["💼 Nhóm Dịch Vụ Nghiệp Vụ"]
            Chatbot["5. svc-business-chatbot (Go)\nWebhook Đa Kênh"]
            BizCRM["6. svc-business-crm (Go)\nĐồng Bộ CRM Doanh Nghiệp"]
            BiztadaCRM["7. svc-biztada-crm (Node/Go)\nNền Tảng Dữ Liệu Khách Hàng"]
            Mktg["8. svc-business-marketing (Go)\nQuy Trình Chiến Dịch Tiếp Thị"]
            AI["9. svc-ai-controller (Python)\nĐiều Phối Model & Prompt AI"]
            Credit["10. svc-tada-credit (Go)\nSổ Cái Thanh Toán & Ví"]
        end

        %% Routing
        Traefik -->|orchestrator.tadagram.com| Orch
        Traefik -->|core.tadagram.com| CoreAPI
        Traefik -->|business-chatbot.tadagram.com| Chatbot
        Traefik -->|business-crm.tadagram.com| BizCRM
        Traefik -->|biztada-crm.tadagram.com| BiztadaCRM
        Traefik -->|business-marketing.tadagram.com| Mktg
        Traefik -->|ai-controller.tadagram.com| AI
        Traefik -->|observability.tadagram.com| Obs
        Traefik -->|tada-credit.tadagram.com| Credit

        %% Data Persistence Layer
        subgraph Data_Layer ["💾 Tầng Cơ Sở Dữ Liệu Đa Hình (Namespace: database & tadagram)"]
            MySQL[("🐬 MySQL 8.0\nPersistent Volume (20GB)\nNgười dùng, Hóa đơn, Phiên")]
            Mongo[("🍃 MongoDB 6.0\nPersistent Volume (20GB)\nWorkflows, Khách hàng, Log")]
            Redis[("⚡ Redis 7.0\nTrạng Thái Bộ Nhớ\nTask Streams & Khóa Lease")]
            MQTT[("📡 Mosquitto MQTT\nPersistent Volume (5GB)\nKênh Điều Khiển Worker")]
        end

        CoreAPI --> MySQL
        CoreAPI --> Redis
        BizCRM --> MySQL
        Chatbot --> MySQL
        Chatbot --> MQTT
        Mktg --> Mongo
        Orch --> Mongo
        Orch --> Redis
    end

    %% Physical Infrastructure Layer
    subgraph Physical_Hardware ["🔋 Hạ Tầng Phần Cứng & Dự Phòng Thực Tế"]
        MINI_PC["HP / Dell Mini PC (i5-6500T, 16GB RAM, 256GB NVMe)"]
        ROUTER["Router Cân Bằng Tải Dual-WAN (Cáp Quang + SIM 4G Backup)"]
        POWER["Trạm Điện 512Wh LiFePO4 (Chế độ EPS < 30ms)"]
        
        POWER -.->|Điện Sin Chuẩn 220V (Dự phòng 14 tiếng)| MINI_PC
        POWER -.->|Nguồn Dự Phòng| ROUTER
        ROUTER -.->|Cáp Mạng LAN Gigabit (Không dùng Wi-Fi)| MINI_PC
    end
```

---

## 📑 Danh Mục Tài Liệu Kiến Trúc Chuyên Sâu

1. [**Tổng Quan Kiến Trúc & Cụm Microservices (`architecture/01-system-overview.md`)**](./architecture/01-system-overview.md)  
   Bản vẽ chi tiết 10 Docker Microservices, 4 cơ sở dữ liệu đa hình, phân chia Namespace Kubernetes và cấu hình lưu trữ PVC.

2. [**Bảo Mật Tầng Biên & Cổng Ingress Cloudflare Tunnel (`architecture/02-zero-trust-edge-ingress.md`)**](./architecture/02-zero-trust-edge-ingress.md)  
   Cơ chế công khai dịch vụ ra internet qua HTTPS mà không cần mở bất kỳ cổng port nào trên router hay mua IP tĩnh.

3. [**Quy Trình Khởi Tạo Cụm 6 Giai Đoạn Chuẩn Xác (`architecture/03-deterministic-bootstrap.md`)**](./architecture/03-deterministic-bootstrap.md)  
   Thứ tự phụ thuộc khởi tạo từ máy trắng (Clean Slate), vòng lặp kiểm tra sức khỏe socket DB và khôi phục hơn 45,000 bản ghi dữ liệu mẫu.

4. [**Quản Trị Cụm Kubernetes Từ Xa An Toàn (`architecture/04-remote-k8s-management.md`)**](./architecture/04-remote-k8s-management.md)  
   Quản trị viên thực thi lệnh `kubectl` an toàn qua mạng riêng ảo WireGuard/Tailscale và Cloudflare Access mà không phơi cổng 6443 ra ngoài.

---

## 🔬 Nghiên Cứu Sâu & Đột Phá Kỹ Thuật

- [**Kỹ Nghệ Phần Cứng, Mạng Dual-WAN 4G & Dự Phòng Điện 14 Tiếng (`deep-dives/01-hardware-power-failover.md`)**](./deep-dives/01-hardware-power-failover.md)  
  Lựa chọn phần cứng tiêu thụ điện 35W, router tự chuyển SIM 4G trong 3 giây và trạm điện pin LiFePO4 hoạt động liên tục 24/7.
- [**Bài Toán Kinh Tế & Đo Tải: Cloud Managed K8s vs. Bare-Metal (`deep-dives/02-cost-and-resource-profiling.md`)**](./deep-dives/02-cost-and-resource-profiling.md)  
  So sánh chi phí thực tế $420/tháng của đám mây so với $1.80/tháng của máy chủ biên nội bộ, kèm đối soát IOPS ổ cứng.
- [**Tự Động Hóa Khôi Phục Dữ Liệu & Nạp Seed Ban Đầu (`deep-dives/03-database-restoration-automation.md`)**](./deep-dives/03-database-restoration-automation.md)  
  Bộ giám sát vòng lặp thăm dò socket ngăn chặn tình trạng ghi đè hỏng cơ sở dữ liệu trong quá trình khởi tạo K8s.

---

## 💻 Mã Nguồn Mẫu Chuẩn Hóa (Sanitized Reference Implementations)

- [`../sanitized-code/k3d-bootstrap-orchestrator/`](../sanitized-code/k3d-bootstrap-orchestrator/): Kịch bản tự động hóa khởi tạo cụm K3d và gắn kết Local Container Registry nội bộ.
- [`../sanitized-code/cloudflared-tunnel-ingress/`](../sanitized-code/cloudflared-tunnel-ingress/): File cấu hình Kubernetes triển khai Daemon Cloudflare Tunnel và Ingress Traefik.
- [`../sanitized-code/db-health-probe-watchdog/`](../sanitized-code/db-health-probe-watchdog/): Script Python thăm dò kết nối socket cơ sở dữ liệu trước khi nạp dữ liệu di chuyển.
