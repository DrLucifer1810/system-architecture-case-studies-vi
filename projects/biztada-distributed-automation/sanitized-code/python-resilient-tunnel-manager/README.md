# 🐍 Resilient Dynamic Reverse Tunnel Manager

A Python module implementing dynamic reverse tunnel fallback across **Cloudflare Quick Tunnel** and **Localtunnel** with active external HTTP health probing.

---

## 🎯 Architecture Problem Addressed

Client desktop workers run behind residential NAT and strict router firewalls. When remote visual browser inspection or interactive streaming is requested:
- Standard port forwarding is unfeasible for non-technical users.
- A single tunnel provider (like Cloudflare Quick Tunnel) can encounter rate limits or temporary DNS resolution latency.
- Advertising an unverified URL to the central orchestrator leads to broken user sessions and timeout errors in the web UI.

---

## ⚙️ How It Works

1. **Autonomous Provider Spawning:** Spawns `cloudflared` to obtain an ephemeral `*.trycloudflare.com` URL.
2. **Pre-flight Health Probe:** Executes an external HTTP probe (`GET /health`) with strict timeout limits to verify global routing before advertising the URL.
3. **Automated Fallback:** If the primary provider fails 3 consecutive probes or is rate-limited, it automatically trips a circuit breaker and activates the secondary provider (`localtunnel` or custom relay).
4. **Clean Process Lifecycle:** Manages process trees to avoid orphan background network tunnels.

---

## 🚀 Running the Example

```bash
python example.py
```