# 🧠 Session Blackboard Working Memory

A Python reference implementation of Fusio's **SQLite WAL Scoped Blackboard** and **Agent Session Tree**.

---

## 🎯 Architecture Problem Addressed

In multi-agent systems:
- Storing agent state and trajectories in raw `.json` sidecar files creates file-lock race conditions when parallel sub-agents execute concurrently.
- Passing full trajectories in LLM context windows rapidly exceeds token limits and increases costs.
- The Session Blackboard provides an indexed, crash-resilient working memory with microsecond read/write performance.

---

## ⚙️ How It Works

1. **SQLite WAL Mode (`PRAGMA journal_mode=WAL`):** Enables concurrent readers without blocking writes.
2. **Scoped Variable Inheritance:** Sub-agent branches inherit parent variables seamlessly with local overrides.
3. **Branching Trajectory Tree:** Tracks historical steps (`node_id`, `parent_id`, `role`, `content`) for post-execution auditing and dynamic error recovery.

---

## 🚀 Running the Example

```bash
python example_usage.py
```