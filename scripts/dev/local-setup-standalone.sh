#!/usr/bin/env bash
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# local-setup-standalone.sh — Self-contained minikube bootstrap for CASA demo
# No external files required — all helm values are inlined.
# Usage:
#   bash scripts/dev/local-setup-standalone.sh          # install / upgrade
#   bash scripts/dev/local-setup-standalone.sh reset    # wipe data and reinstall
#
# Prerequisites: minikube, istioctl, helm, kubectl, docker, crane
#   brew install minikube istioctl helm kubectl crane
#
# Required env vars (export before running):
#   CASA_LLM_HOST       OpenAI-compatible API hostname (e.g. litellm.example.com)
#   CASA_LLM_API_KEY    API key for the LLM service
#
# Optional env vars:
#   CASA_LLM_MODEL_ID   LLM model for auth checks (default: bedrock/global.anthropic.claude-sonnet-4-6)
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — set these before running
# ---------------------------------------------------------------------------
: "${CASA_LLM_HOST:?CASA_LLM_HOST must be set (e.g. litellm.example.com)}"
: "${CASA_LLM_API_KEY:?CASA_LLM_API_KEY must be set}"

CASA_LLM_MODEL_ID="${CASA_LLM_MODEL_ID:-bedrock/global.anthropic.claude-sonnet-4-6}"

CASA_LLM_API_BASE_URL="http://${CASA_LLM_HOST}"

NAMESPACE="casa-dev"

log() {
    echo ""
    echo "==> $*"
}

# ---------------------------------------------------------------------------
# Reset mode: wipe helm releases + PVCs then continue with fresh install
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "reset" ]]; then
    log "Reset — stripping MAS finalizers to unblock deletion"
    kubectl get multiagentsystems.casa.io -n "$NAMESPACE" -o name 2>/dev/null |
        xargs -I{} kubectl patch {} -n "$NAMESPACE" --type=json \
            -p='[{"op":"remove","path":"/metadata/finalizers"}]' 2>/dev/null || true

    log "Reset — uninstalling helm releases"
    helm uninstall casa-demo -n "$NAMESPACE" 2>/dev/null || true
    helm uninstall casa-dev -n "$NAMESPACE" 2>/dev/null || true

    log "Reset — deleting PVCs"
    kubectl delete pvc --all -n "$NAMESPACE" 2>/dev/null || true

    log "Reset — done, continuing with fresh install…"
fi

# ---------------------------------------------------------------------------
# 1. Start Minikube
# ---------------------------------------------------------------------------
log "Step 1 — Start Minikube"
if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    echo "    minikube already running, skipping start"
else
    minikube start \
        --driver=docker \
        --memory=7168 \
        --cpus=6 \
        --addons=registry,ingress
fi

minikube addons enable registry 2>/dev/null || true
minikube addons enable ingress 2>/dev/null || true

log "Step 1 — Port-forward in-cluster registry (localhost:5000)"
pkill -f "kubectl port-forward.*kube-system.*svc/registry" 2>/dev/null || true
kubectl port-forward -n kube-system svc/registry 5000:80 &
sleep 2

# ---------------------------------------------------------------------------
# 2. Install Istio
# ---------------------------------------------------------------------------
log "Step 2 — Install Istio (minimal profile)"
istioctl install --set profile=minimal -y

# ---------------------------------------------------------------------------
# 3. Create namespace
# ---------------------------------------------------------------------------
log "Step 3 — Create namespace $NAMESPACE"
kubectl create namespace "$NAMESPACE" 2>/dev/null || echo "    namespace already exists"
kubectl label namespace "$NAMESPACE" istio-injection=enabled --overwrite

# ---------------------------------------------------------------------------
# 4. Build Docker images
# ---------------------------------------------------------------------------
log "Step 4 — Point shell at minikube Docker daemon"
eval "$(minikube docker-env)"

log "Step 4 — Build control plane images"
docker build -f deployments/docker/Dockerfile -t casa-auth-server:local .
docker build -f deployments/docker/Dockerfile.keycloak -t casa-auth-server-keycloak:local deployments/docker
docker build -f deployments/docker/Dockerfile.operator -t casa-operator:local .
docker build --no-cache -f deployments/docker/Dockerfile.ui \
    --build-arg VITE_API_BASE_URL=http://api.casa.outshift.ai \
    -t casa-auth-server-ui:local .
docker build -f deployments/docker/Dockerfile.extauth -t ext-auth-service:local .

log "Step 4 — Build demo images"
docker build -f demo/src/agent-safe/Dockerfile -t demo-agent-safe:local demo/src/agent-safe
docker build -f demo/src/agent-compromised/Dockerfile -t demo-agent-compromised:local demo/src/agent-compromised
docker build -f demo/src/mcp/Dockerfile -t demo-mcp:local demo/src/mcp
docker build -f demo/src/chat-ui/Dockerfile -t demo-chat-ui:local demo/src/chat-ui

log "Step 4 — Build and push WasmPlugin OCI images"
docker build -f sidecar/llm_proxy/Dockerfile -t llm-proxy:local sidecar/llm_proxy
docker build -f sidecar/traceparent_injector/Dockerfile -t traceparent-injector:local sidecar/traceparent_injector

docker save llm-proxy:local -o /tmp/llm-proxy.tar
docker save traceparent-injector:local -o /tmp/traceparent-injector.tar
crane push --insecure /tmp/llm-proxy.tar localhost:5000/llm-proxy:local
crane push --insecure /tmp/traceparent-injector.tar localhost:5000/traceparent-injector:local
rm /tmp/llm-proxy.tar /tmp/traceparent-injector.tar

# ---------------------------------------------------------------------------
# 5. Deploy control plane
# ---------------------------------------------------------------------------
log "Step 5 — Add helm repositories"
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts 2>/dev/null || true
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts 2>/dev/null || true
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

log "Step 5 — Build helm dependencies"
helm dependency build deployments/helm/sidecar
helm dependency build deployments/helm/casa-runtime

log "Step 5 — Install/upgrade casa-runtime (includes sidecar subchart)"
helm upgrade --install casa-dev \
    deployments/helm/casa-runtime \
    -n "$NAMESPACE" \
    --create-namespace \
    --set authService.image.repository=casa-auth-server \
    --set authService.image.tag=local \
    --set authService.image.pullPolicy=Never \
    --set authService.database.password=postgres \
    --set authService.idp.adminPassword=admin \
    --set "authService.openai.llmApiBaseUrl=${CASA_LLM_API_BASE_URL}" \
    --set "authService.openai.llmApiKey=${CASA_LLM_API_KEY}" \
    --set "authService.openai.modelId=${CASA_LLM_MODEL_ID}" \
    --set authService.externalSecrets.enabled=false \
    --set uiExplorer.image.repository=casa-auth-server-ui \
    --set uiExplorer.image.tag=local \
    --set uiExplorer.image.pullPolicy=Never \
    --set uiExplorer.ingress.enabled=true \
    --set uiExplorer.ingress.className=nginx \
    --set uiExplorer.ingress.apiDomainName=casa.outshift.ai \
    --set uiExplorer.ingress.domainPrefix=explorer \
    --set uiExplorer.nginx.apiProxyEnabled=false \
    --set authService.ingress.enabled=true \
    --set authService.ingress.className=nginx \
    --set authService.ingress.apiDomainName=casa.outshift.ai \
    --set authService.ingress.domainPrefix=api \
    --set keycloak.image.repository=casa-auth-server-keycloak \
    --set keycloak.image.tag=local \
    --set keycloak.image.pullPolicy=Never \
    --set keycloak.hostname=localhost \
    --set keycloak.hostnamePort=8080 \
    --set operator.image.repository=casa-operator \
    --set operator.image.tag=local \
    --set operator.image.pullPolicy=Never \
    --set postgresAuth.persistence.storageClass="" \
    --set postgresKeycloak.persistence.storageClass="" \
    --set sidecar.enabled=true \
    --set sidecar.authServerHost="" \
    --set sidecar.image.repository=ext-auth-service \
    --set sidecar.image.tag=local \
    --set sidecar.image.pullPolicy=Never \
    --set sidecar.llm_proxy.image.repository=registry.kube-system.svc.cluster.local/llm-proxy \
    --set sidecar.llm_proxy.image.tag=local \
    --set sidecar.llm_proxy.image.pullPolicy=IfNotPresent \
    --set sidecar.traceparent_injector.image.repository=registry.kube-system.svc.cluster.local/traceparent-injector \
    --set sidecar.traceparent_injector.image.tag=local \
    --set sidecar.traceparent_injector.image.pullPolicy=IfNotPresent

# ---------------------------------------------------------------------------
# Wait for control plane pods to be ready
# ---------------------------------------------------------------------------
log "Waiting for control plane pods to be Ready (timeout 10 min)…"
kubectl wait pod \
    --for=condition=Ready \
    --selector='app.kubernetes.io/instance=casa-dev' \
    -n "$NAMESPACE" \
    --timeout=600s

# ---------------------------------------------------------------------------
# 6. Deploy demo agents
# ---------------------------------------------------------------------------
log "Step 6 — Install/upgrade demo agents"
helm upgrade --install casa-demo \
    demo/helm \
    -n "$NAMESPACE" \
    --set agentSafe.replicas=1 \
    --set agentSafe.serviceName=demo-agent-safe \
    --set agentSafe.servicePort=8082 \
    --set agentSafe.docker.registry="" \
    --set agentSafe.docker.image=demo-agent-safe \
    --set agentSafe.tagversion=local \
    --set 'agentSafe.mcp_server_url=http://casa-demo-mcp:3000/mcp' \
    --set agentCompromised.replicas=1 \
    --set agentCompromised.serviceName=demo-agent-compromised \
    --set agentCompromised.servicePort=8082 \
    --set agentCompromised.docker.registry="" \
    --set agentCompromised.docker.image=demo-agent-compromised \
    --set agentCompromised.tagversion=local \
    --set 'agentCompromised.mcp_server_url=http://casa-demo-mcp:3000/mcp' \
    --set mcp.replicas=1 \
    --set mcp.serviceName=casa-demo-mcp \
    --set mcp.servicePort=3000 \
    --set mcp.docker.registry="" \
    --set mcp.docker.image=demo-mcp \
    --set mcp.tagversion=local \
    --set 'chatUis[0].name=safe' \
    --set 'chatUis[0].docker.registry=' \
    --set 'chatUis[0].docker.image=demo-chat-ui' \
    --set 'chatUis[0].tagversion=local' \
    --set 'chatUis[0].agentUrl=/safe-agent' \
    --set 'chatUis[0].ingress.enabled=true' \
    --set 'chatUis[0].ingress.className=nginx' \
    --set 'chatUis[0].ingress.apiDomainName=casa.outshift.ai' \
    --set 'chatUis[0].ingress.domainPrefix=chat-safe' \
    --set 'chatUis[1].name=compromised' \
    --set 'chatUis[1].docker.registry=' \
    --set 'chatUis[1].docker.image=demo-chat-ui' \
    --set 'chatUis[1].tagversion=local' \
    --set 'chatUis[1].agentUrl=/compromised-agent' \
    --set 'chatUis[1].ingress.enabled=true' \
    --set 'chatUis[1].ingress.className=nginx' \
    --set 'chatUis[1].ingress.apiDomainName=casa.outshift.ai' \
    --set 'chatUis[1].ingress.domainPrefix=chat-compromised' \
    --set "llmCredentials.apiBaseUrl=${CASA_LLM_API_BASE_URL}" \
    --set "llmCredentials.apiKey=${CASA_LLM_API_KEY}" \
    --set 'masSafe.name=CASA Demo Safe' \
    --set 'masSafe.enabledToolChecks[0]=DETERMINISTIC_TOOL_SELECTED' \
    --set 'masSafe.enabledToolChecks[1]=DETERMINISTIC_LLM_SELECTED_TOOLS' \
    --set 'masSafe.enabledToolChecks[2]=AI_POWERED_TOOL_MATCH' \
    --set "masSafe.llm_host=${CASA_LLM_HOST}" \
    --set 'masCompromised.name=CASA Demo Compromised' \
    --set 'masCompromised.enabledToolChecks[0]=DETERMINISTIC_TOOL_SELECTED' \
    --set 'masCompromised.enabledToolChecks[1]=DETERMINISTIC_LLM_SELECTED_TOOLS' \
    --set 'masCompromised.enabledToolChecks[2]=AI_POWERED_TOOL_MATCH' \
    --set "masCompromised.llm_host=${CASA_LLM_HOST}"

log "Step 6 — Patching chat-ui ingress annotations"
kubectl annotate ingress \
    casa-demo-chat-ui-safe \
    casa-demo-chat-ui-compromised \
    -n "$NAMESPACE" \
    "nginx.ingress.kubernetes.io/ssl-redirect=false" \
    "nginx.ingress.kubernetes.io/proxy-buffering=off" \
    "nginx.ingress.kubernetes.io/proxy-buffer-size=128k" \
    "nginx.ingress.kubernetes.io/proxy-read-timeout=300" \
    "nginx.ingress.kubernetes.io/proxy-send-timeout=300" \
    --overwrite

# ---------------------------------------------------------------------------
# 7. Verify
# ---------------------------------------------------------------------------
log "Step 7 — Pod status"
kubectl get pods -n "$NAMESPACE"

log "Step 7 — MultiAgentSystem status"
kubectl get multiagentsystems.casa.io -n "$NAMESPACE" 2>/dev/null || echo "    (no MAS resources yet)"

# ---------------------------------------------------------------------------
# Wait for all pods to be ready
# ---------------------------------------------------------------------------
log "Waiting for all pods to be Ready (timeout 5 min)…"
kubectl wait pod \
    --for=condition=Ready \
    --all \
    -n "$NAMESPACE" \
    --timeout=300s

# ---------------------------------------------------------------------------
# 8. Port-forwards
# ---------------------------------------------------------------------------
log "Step 8 — Starting port-forwards"

# Cache sudo credentials upfront (needed for port 80 binding)
sudo -v

pkill -f "kubectl port-forward.*$NAMESPACE" 2>/dev/null || true
sudo pkill -f "kubectl port-forward.*ingress-nginx" 2>/dev/null || true
sleep 1

kubectl port-forward -n "$NAMESPACE" svc/casa-dev-auth-service 8000:8000 &
kubectl port-forward -n "$NAMESPACE" svc/casa-dev-postgres-auth 5432:5432 &
kubectl port-forward -n "$NAMESPACE" svc/casa-dev-keycloak 8080:8080 &
kubectl port-forward -n "$NAMESPACE" svc/jaeger 16686:16686 &

# nginx ingress controller — exposes all 3 UIs on port 80 (requires sudo on macOS)
sudo -n kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 80:80 &

log "Step 8 — Updating /etc/hosts for ingress hostnames"
HOSTS_LINE="127.0.0.1  explorer.casa.outshift.ai api.casa.outshift.ai chat-safe.casa.outshift.ai chat-compromised.casa.outshift.ai"
if grep -q "casa.outshift.ai" /etc/hosts; then
    sudo sed -i '' '/casa\.outshift\.ai/d' /etc/hosts
fi
echo "$HOSTS_LINE" | sudo -n tee -a /etc/hosts >/dev/null
echo "    /etc/hosts updated"

echo ""
echo "Port-forwards started (background jobs):"
echo "  Auth server API   → http://localhost:8000"
echo "  Keycloak          → http://localhost:8080"
echo "  Jaeger traces     → http://localhost:16686"
echo ""
echo "UIs available via nginx ingress:"
echo "  Explorer UI       → http://explorer.casa.outshift.ai"
echo "  Auth API          → http://api.casa.outshift.ai"
echo "  Safe chat UI      → http://chat-safe.casa.outshift.ai"
echo "  Compromised UI    → http://chat-compromised.casa.outshift.ai"
echo ""
echo "Done. Run 'jobs' to see background port-forwards."
