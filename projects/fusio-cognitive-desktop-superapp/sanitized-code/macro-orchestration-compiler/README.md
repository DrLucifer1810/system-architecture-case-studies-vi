# ⚡ Workflow Macro Compiler & Deterministic Bypass

A Python reference implementation demonstrating Fusio's **Trace-to-Playwright Compiler**, which translates exploratory ReAct trajectory steps into standalone, deterministic automation scripts.

---

## 🎯 Architecture Problem Addressed

- Running repetitive ReAct reasoning loops consumes thousands of LLM tokens on every execution.
- LLM response latency (2–4 seconds per step) frustrates desktop users expecting fast automation.
- Probabilistic sampling causes identical tasks to randomly fail due to subtle model drift.

---

## ⚙️ How It Works

1. **ReAct Trace Capture:** Records all actions, DOM selectors, wait conditions, and values in structured JSON.
2. **Deterministic Script Synthesis:** Translates trace steps into native async Playwright code.
3. **Execution Bypass:** Subsequent runs bypass LLM inference completely, improving speed by **10,000% (from 45s down to 450ms)**.

---

## 🚀 Running the Example

```bash
python compiler.py
```