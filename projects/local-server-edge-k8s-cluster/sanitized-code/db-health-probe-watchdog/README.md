# 🩺 Database Health Probe Watchdog

A lightweight Python probe script implementing TCP handshake checks and exponential backoff loops to verify that stateful database sockets are fully bound before initiating table migrations or high-volume BSON/SQL restores.

---

## 🎯 Architecture Problem Addressed

- Kubernetes pod `Running` status does not mean the internal database engine is ready for connections.
- Prevents database corruption caused by running restore scripts against uninitialized engines.

---

## 🚀 Execution

```bash
python watchdog.py
```