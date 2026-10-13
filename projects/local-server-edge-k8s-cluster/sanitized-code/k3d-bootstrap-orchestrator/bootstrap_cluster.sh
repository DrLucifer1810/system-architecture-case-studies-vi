#!/usr/bin/env bash
# ==============================================================================
# Deterministic K3d Edge Cluster Bootstrap Orchestrator
# Automates clean-slate teardown, local registry creation, and cluster binding.
# ==============================================================================

set -euo pipefail

CLUSTER_NAME="mycluster"
REGISTRY_NAME="myregistry.localhost"
REGISTRY_PORT="5000"

echo "=========================================================="
echo " Stage 0: Teardown & Clean-Slate Reset"
echo "=========================================================="
echo "Checking existing clusters..."
if k3d cluster list | grep -q "${CLUSTER_NAME}"; then
    echo "Deleting old cluster: ${CLUSTER_NAME}..."
    k3d cluster delete "${CLUSTER_NAME}"
fi

if k3d registry list | grep -q "${REGISTRY_NAME}"; then
    echo "Deleting old registry: ${REGISTRY_NAME}..."
    k3d registry delete "${REGISTRY_NAME}"
fi

echo "Pruning dangling docker volumes..."
docker system prune -f --volumes

echo "=========================================================="
echo " Stage 1: Initializing Local Registry & K3d Cluster"
echo "=========================================================="
echo "Creating local registry: ${REGISTRY_NAME}:${REGISTRY_PORT}..."
k3d registry create "${REGISTRY_NAME}" --port "${REGISTRY_PORT}"

echo "Creating K3d cluster: ${CLUSTER_NAME}..."
k3d cluster create "${CLUSTER_NAME}" \
    --registry-use "k3d-${REGISTRY_NAME}:${REGISTRY_PORT}" \
    -p "80:80@loadbalancer" \
    -p "443:443@loadbalancer" \
    --k3s-arg "--disable=traefik@server:0"

echo "Updating local kubeconfig..."
k3d kubeconfig merge "${CLUSTER_NAME}" --kubeconfig-switch-context

echo "=========================================================="
echo " Stage 1 Complete: Cluster & Registry Ready!"
echo " Nodes:"
kubectl get nodes
echo "=========================================================="