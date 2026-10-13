# ⚙️ K3d Bootstrap Orchestrator

A shell automation script demonstrating deterministic clean-slate setup of an on-premises **K3d Kubernetes Cluster** bound to an internal, air-gapped **Local Container Registry**.

---

## 🎯 Architecture Problem Addressed

- External image registries (Docker Hub, GitHub Packages) introduce rate limits and fail if the edge node is offline or during WAN failover.
- Manual cluster setup leads to configuration drift across multiple bare-metal machines.
- This script guarantees idempotent cluster creation with local registry binding.

---

## 🚀 Execution

```bash
chmod +x bootstrap_cluster.sh
./bootstrap_cluster.sh
```