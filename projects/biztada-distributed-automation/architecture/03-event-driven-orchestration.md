# ⚡ Kiến Trúc: Điều Phối Tác Vụ Hướng Sự Kiện & Worker Lease Phân Tán

## 1. Tổng Quan Về Kiến Trúc Điều Phối Tác Vụ

Các tác vụ tự động hóa kéo dài (chẳng hạn như cào dữ liệu nhiều trang web hoặc gửi tin nhắn hàng loạt theo đợt) đặt ra những thách thức mà các endpoint REST đồng bộ thông thường không thể giải quyết:
- Tác vụ có thể kéo dài từ vài phút đến hàng giờ.
- Máy tính của worker có thể bị mất mạng, sập nguồn hoặc hết RAM bất ngờ.
- Nếu tác vụ thất bại giữa chừng, hệ thống phải tự động thử lại an toàn mà không thực hiện trùng lặp những hành động đã hoàn tất trước đó, hoặc đẩy vào hàng đợi lỗi Dead-Letter Queue (DLQ).

Biztada xây dựng một **Hệ Thống Điều Phối Tác Vụ Hướng Sự Kiện** bằng Go trên nền tảng **Redis Streams** và **Hợp Đồng Khóa Phân Tán (Atomic Distributed Leases)**.

---

## 2. Cấu Trúc Redis Streams & Nhóm Tiêu Thụ (Consumer Groups)

```mermaid
flowchart LR
    subgraph NhaXuatBan["Dịch Vụ Phát Tác Vụ"]
        P1["svc-business-marketing"]
        P2["svc-business-chatbot"]
    end

    subgraph RedisStream["Redis Stream: stream:tasks"]
        M1["Tác vụ #1001"]
        M2["Tác vụ #1002"]
        M3["Tác vụ #1003"]
    end

    subgraph NhomTieuThu["Nhóm Tiêu Thụ: cg:task-orchestrators"]
        C1["Orchestrator Tiến Trình 1"]
        C2["Orchestrator Tiến Trình 2"]
    end

    subgraph PEL["Danh Sách Chờ Xác Nhận (PEL)"]
        PEL1["Tác vụ #1001 (Đang gán Inst 1, Rảnh: 40s)"]
        PEL2["Tác vụ #1002 (Đang gán Inst 2, Rảnh: 120s - QUÁ HẠN!)"]
    end

    subgraph QuetDon["Tiến Trình Quét Dọn Tự Động"]
        SWEEP["XAUTOCLAIM / XCLAIM Watchdog"]
    end

    P1 -->|XADD| RedisStream
    P2 -->|XADD| RedisStream
    RedisStream -->|XREADGROUP| C1
    RedisStream -->|XREADGROUP| C2
    C1 -.->|Theo dõi trong| PEL
    C2 -.->|Theo dõi trong| PEL
    SWEEP -->|Kiểm tra tin nhắn quá hạn| PEL
    SWEEP -->|Thu hồi tác vụ chết| C1
```

---

## 3. Giao Thức Worker Lease Phân Tán

Để ngăn chặn tình trạng hai worker cùng lúc thao tác vào một tài khoản mạng xã hội (dễ dẫn đến việc tài khoản bị khóa do hành vi spam bất thường), mọi tác vụ đều bắt buộc phải có một **Distributed Lease**:

```mermaid
sequenceDiagram
    autonumber
    participant Orch as orchestrator-go
    participant Redis as Máy Chủ Redis
    participant Worker as Máy Trạm Worker

    Orch->>Redis: XREADGROUP GROUP cg:tasks Orch-1 COUNT 1
    Redis-->>Orch: Tác vụ {ID: "1001", Payload: {...}}

    Note over Orch,Redis: Nhận Khóa Phân Tán (Distributed Lease)
    Orch->>Redis: SET lock:account:acc_889 "orch-1" NX EX 120
    alt Khóa thất bại (Một worker khác đang nắm giữ tài khoản)
        Redis-->>Orch: Trả về NIL
        Orch->>Redis: Tạm hoãn xác nhận, đẩy tác vụ vào luồng backoff
    else Khóa thành công
        Redis-->>Orch: Trả về OK
        Orch->>Worker: Giao lệnh tác vụ qua MQTT
    end

    loop Nhịp Tim Duy Trì Của Worker (Mỗi 30s)
        Worker->>Orch: Nhịp tim {task_id: "1001", status: "running"}
        Note over Orch,Redis: Chạy Lua Script Nguyên Tử Để Gia Hạn Lease
        Orch->>Redis: EVALSHA renew_script (Kiểm tra đúng chủ == "orch-1" & EX 120)
        Redis-->>Orch: Gia hạn thành công OK
    end

    Worker->>Orch: Tác vụ hoàn tất {status: "success"}
    Orch->>Redis: DEL lock:account:acc_889
    Orch->>Redis: XACK stream:tasks cg:tasks "1001"
    Orch->>Redis: XDEL stream:tasks "1001"
```

### Script Lua Gia Hạn Nguyên Tử:
Để đảm bảo rằng một worker bị nghẽn mạng đã hết hạn lease không vô tình gia hạn hoặc xóa nhầm lease vừa được cấp cho một worker khác, toàn bộ thao tác gia hạn và giải phóng khóa đều chạy qua Lua script:

```lua
-- Lua Script Gia Hạn Khóa Nguyên Tử
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("expire", KEYS[1], ARGV[2])
else
    return 0
end
```

---

## 4. Cơ Chế Tự Phục Hồi Khi Sập Nguồn & Hàng Đợi Lỗi (DLQ)

Khi một tiến trình worker hoặc orchestrator bị tắt đột ngột:
1. Tin nhắn vẫn nằm trong **Pending Entries List (PEL)** mà chưa nhận được lệnh `XACK`.
2. Một goroutine nền chạy định kỳ mỗi 30 giây thực hiện lệnh `XPENDING stream:tasks cg:tasks`.
3. Bất kỳ tác vụ nào có thời gian không phản hồi vượt quá ngưỡng an toàn (`> 60 giây`) sẽ được tự động thu hồi bằng lệnh `XAUTOCLAIM`.
4. Nếu số lần thử lại vượt quá ngưỡng tối đa (`retry_count >= 3`), tác vụ sẽ được chuyển sang hàng đợi lỗi riêng biệt `stream:tasks:dlq` và kích hoạt chuông cảnh báo tới quản trị viên.