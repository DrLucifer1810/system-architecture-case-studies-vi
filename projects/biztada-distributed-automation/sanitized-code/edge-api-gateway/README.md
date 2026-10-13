# 🛡️ Edge Reverse Proxy Middleware (Cloudflare Pages Functions)

A TypeScript reference implementation demonstrating **Zero-Trust Edge Routing**, **Hop-by-Hop Header Sanitization**, and **Internal Route Canonicalization** on Cloudflare Pages Functions.

---

## 🎯 Architecture Problem Addressed

- Direct communication from web browsers or mobile apps to backend origin servers exposes internal cluster IPs and load balancers to DDoS attacks.
- Cross-Origin Resource Sharing (CORS) preflights create avoidable network latency.
- Internal microservices must be able to trust that requests originated from verified edge routes rather than spoofed direct HTTP calls.

---

## ⚙️ How It Works

1. **Path-Based Service Routing:** Dispatches `/api/v1/marketing/*` and `/api/v1/core/*` to their corresponding cluster endpoints while keeping frontend URLs relative.
2. **Hop-by-Hop Header Stripping:** Cleans client headers to prevent smuggling.
3. **Edge Secret Injection:** Injects mutual trust secrets (`X-Edge-Auth-Secret`) verified by upstream origin ingress controllers.
4. **CORS Elimination:** By sharing origin with frontend static assets, all CORS pre-flight overhead is eliminated.