# 💰 Nghiên Cứu Sâu: Bài Toán Kinh Tế: Cloud Managed K8s vs. Bare-Metal Tầng Biên

Động lực cốt lõi khi thiết kế kiến trúc `local-server` bắt nguồn từ chi phí hạ tầng đám mây tăng phi mã trong giai đoạn phát triển và mở rộng sản phẩm.

---

## 1. So Sánh Chi Phí: Kubernetes Đám Mây vs. Máy Chủ Cục Bộ

Để vận hành 10 microservices container hóa và 4 hệ thống cơ sở dữ liệu trên các nhà cung cấp đám mây (như DigitalOcean DOKS hoặc AWS EKS):

### Chi Phí Hạ Tầng Đám Mây (Ước Tính Hàng Tháng):
- **Cụm Máy Chủ Kubernetes (Worker Nodes):** 3 node (4 vCPU, 8GB RAM mỗi node) = **$144 / tháng**
- **Cơ Sở Dữ Liệu MySQL Quản Trị:** 1 máy chủ MySQL (2 vCPU, 4GB RAM) = **$60 / tháng**
- **Cơ Sở Dữ Liệu MongoDB Quản Trị:** 1 máy chủ MongoDB Cluster = **$65 / tháng**
- **Redis & Hàng Đợi Quản Trị:** 1 máy chủ Redis Cluster = **$35 / tháng**
- **Cân Bằng Tải Đám Mây (Load Balancers):** 2 dịch vụ Cloud LoadBalancer = **$40 / tháng**
- **Ổ Cứng Ảo Hóa (Persistent Volumes):** 100GB NVMe Block Storage = **$20 / tháng**
- **Băng Thông Truyền Tải (Egress Bandwidth):** ~500GB dữ liệu đi ra ngoài = **$25 / tháng**
- **Tổng Chi Phí Đám Mây:** **~$389 đến $450+ mỗi tháng** *(Tương đương ~110.000.000 VNĐ đến 135.000.000 VNĐ / năm)*

---

### Chi Phí Hạ Tầng Bare-Metal Cục Bộ (Local Server):
- **Chi Phí Mua Sắm Phần Cứng Ban Đầu (CapEx - Chỉ Trả 1 Lần):**
  - Máy tính Mini PC (i5-6500T, 16GB RAM, 256GB NVMe): **~3.000.000 VNĐ (~$120)**
  - Router Cân Bằng Tải Dual-WAN + USB 4G: **~1.500.000 VNĐ (~$60)**
  - Trạm Điện Di Động EcoFlow 512Wh LiFePO4: **~6.000.000 VNĐ (~$240)**
  - Tổng Chi Phí Đầu Tư Ban Đầu: **~10.500.000 VNĐ (~$420)**
- **Chi Phí Vận Hành Định Kỳ Hàng Tháng (OpEx):**
  - Tiền Điện Tiêu Thụ: `30W * 24h * 30 ngày = 21.6 kWh` @ 2,500đ/kWh = **~54.000 VNĐ (~$2.10) / tháng**
  - Gói Cước SIM 4G Không Giới Hạn Dự Phòng: **~100.000 VNĐ (~$4.00) / tháng**
  - Đường Hầm Cloudflare Zero Trust: **0 VNĐ (Gói miễn phí)**
  - Tổng Chi Phí Định Kỳ Hàng Tháng: **~154.000 VNĐ (~$6.10) / tháng**

### Hiệu Quả Đầu Tư (ROI):
- **Tiết Kiệm Hàng Năm:** Tiết kiệm hơn **100.000.000 VNĐ (~$4,500 USD) mỗi năm**.
- **Thời Gian Hoàn Vốn Đầu Tư Phần Cứng:** **Chưa đầy 1.2 tháng**.

---

## 2. So Sánh Hiệu Năng Thực Tế: IOPS Ổ Cứng & Độ Trễ Giao Tiếp

Bên cạnh yếu tố tài chính, phần cứng bare-metal trực tiếp thường có hiệu năng vượt trội so với máy ảo chia sẻ trên đám mây:

| Chỉ Số Đánh Giá | Máy Ảo Đám Mây (DigitalOcean / AWS gp3) | Máy Chủ Bare-Metal Cục Bộ (NVMe Trực Tiếp) | Mức Độ Cải Thiện |
| :--- | :--- | :--- | :--- |
| **IOPS Đọc Ngẫu Nhiên** | ~3,000 IOPS (Bị bóp băng thông) | **~180,000 IOPS** | **Nhanh hơn 60 lần** |
| **Độ Trễ Ghi Cơ Sở Dữ Liệu** | 2.5 ms – 6.0 ms (Ổ cứng mạng EBS) | **0.15 ms – 0.35 ms (Giao tiếp PCIe NVMe)** | **Độ trễ thấp hơn 17 lần** |
| **Độ Trễ Giữa Các Dịch Vụ** | 0.8 ms – 2.0 ms (Cầu mạng ảo VPC) | **0.02 ms (Loopback nhân Linux)** | **Giao tiếp IPC nhanh hơn 40 lần** |
| **Ảnh Hưởng Bởi Máy Ảo Khác** | Cao (Tài nguyên CPU bị chia sẻ) | **Bằng 0 (Phần cứng độc quyền 100%)** | **Hiệu năng tất định tuyệt đối** |