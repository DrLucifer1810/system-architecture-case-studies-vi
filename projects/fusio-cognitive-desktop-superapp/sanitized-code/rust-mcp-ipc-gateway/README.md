# 🦀 Rust MCP & IPC Gateway Engine

A production-grade, sanitized Rust reference implementation demonstrating **Model Context Protocol (MCP)** tool virtualization and framed asynchronous IPC messaging.

---

## 🎯 Architecture Problem Addressed

In a hybrid desktop AI application:
- Spawning Python or Node.js tool runners for basic filesystem or OS operations introduces heavy subprocess overhead and memory bloat.
- Multiple local client processes (e.g. background sync workers, local chat UIs, external IDE plugins) need unified access to virtualized tools.
- Native desktop security requires strict sandboxing and parameter schema enforcement before invoking system operations.

---

## ⚙️ How It Works

1. **Structured IPC Envelopes:** Standardizes framed bidirectional JSON messages between the UI host and external cognitive runtimes.
2. **Dynamic Tool Registry:** Registers async tool handlers with input JSON-Schema validation.
3. **Thread-Safe Concurrent Dispatch:** Uses `tokio::sync::RwLock` to enable concurrent read queries and zero-lock execution of stateless tool calls.

---

## 🚀 Running Tests

```bash
cargo test
```