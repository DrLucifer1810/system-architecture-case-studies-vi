# 🔒 Cloudflare Tunnel Ingress Manifests

Production Kubernetes manifests demonstrating how to deploy an outbound **Cloudflare Zero Trust Tunnel Daemon (`cloudflared`)** inside the cluster and map incoming edge traffic to **Traefik Ingress** rules without opening any router ports.

---

## 🎯 Architecture Problem Addressed

- Eliminates incoming port forwarding (`80/443`) on edge routers.
- Keeps backend servers invisible to public port scanners.
- Enables instant reconnection when WAN links switch over backup 4G interfaces.

---

## 🚀 Deployment

```bash
kubectl create secret generic cloudflare-tunnel-token \
  --from-literal=token="<YOUR_TUNNEL_TOKEN>" \
  -n kube-system

kubectl apply -f cloudflared-daemon.yaml
kubectl apply -f ingress-routes.yaml
```