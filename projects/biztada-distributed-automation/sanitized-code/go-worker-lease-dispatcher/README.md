# 📦 Go Worker Lease Dispatcher

A production-grade, sanitized Go reference implementation demonstrating how to consume messages from **Redis Streams** with **Distributed Lease Management** and **Heartbeat Renewal**.

---

## 🎯 Architecture Problem Addressed

In distributed task execution, multiple workers consume from a central queue. If a worker picks up a job for a tenant or account, two critical race conditions arise:
1. **Concurrency Conflict:** Another worker might simultaneously process a second task for the same account, triggering platform rate-limits or corrupting state.
2. **Crash Disconnection:** If the leased worker crashes midway through execution, the job must not remain locked forever, nor should another worker prematurely steal it while execution is legitimately still ongoing.

---

## ⚙️ How It Works

1. **Redis Streams Consumer Group (`XREADGROUP`):** Reads tasks reliably.
2. **Distributed Lease (`SET NX EX`):** Obtains an exclusive lock on the account identifier before executing the job.
3. **Heartbeat Routine (`Ticker + Lua`):** Atomically extends the lease TTL every 20 seconds while execution is active. If the owner token does not match (lease expired and acquired by someone else), the worker cancels its context immediately.
4. **Acknowledgement (`XACK`):** Acknowledges the message only upon successful completion.

---

## 🚀 Running Tests

```bash
go test -v ./...
```