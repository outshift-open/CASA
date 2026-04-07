---
id: install-control-plane
sidebar_position: 2
title: Install Control Plane
---

# Install the ZTA Control Plane

The ZTA control plane is installed via the `zta-control-plane` Helm chart located at `deployments/k8s/helm/zta-control-plane/`.

## Basic Installation

```bash
helm install zta deployments/k8s/helm/zta-control-plane \
  --namespace zta-control-plane \
  --create-namespace
```

Wait for all pods to be ready:

```bash
kubectl -n zta-control-plane wait --for=condition=ready pod --all --timeout=300s
```

Expected pods:

```
NAME                              READY   STATUS  
zta-auth-service-...              1/1     Running  
zta-ui-explorer-...               1/1     Running  
zta-keycloak-...                  1/1     Running  
zta-postgres-auth-...             1/1     Running  
zta-postgres-keycloak-...         1/1     Running  
```

## Using the Makefile

```bash
# Install
make helm-install

# Upgrade
make helm-upgrade

# Uninstall
make helm-uninstall
```

The Makefile uses `HELM_RELEASE=zta` and `HELM_NAMESPACE=zta-control-plane` by default. Override with:

```bash
make helm-install HELM_RELEASE=my-zta HELM_NAMESPACE=my-namespace
```

## Production Configuration

For production deployments, override the default passwords and configure ingress. Create a custom values file:

```yaml
# values-prod.yaml
authService:
  replicaCount: 3
  database:
    host: "postgres.internal.example.com"
    password: "CHANGE_ME"
  idp:
    serverUrl: "https://keycloak.internal.example.com"
    adminPassword: "CHANGE_ME"
  ingress:
    enabled: true
    className: "nginx"
    apiDomainName: "internal.example.com"
    domainPrefix: "zta-auth"

uiExplorer:
  ingress:
    enabled: true
    className: "nginx"
    apiDomainName: "internal.example.com"
    domainPrefix: "zta"

postgresAuth:
  enabled: false   # Use external PostgreSQL

postgresKeycloak:
  enabled: false   # Use external PostgreSQL

keycloak:
  admin:
    password: "CHANGE_ME"
  hostname: "keycloak.internal.example.com"
  hostnamePort: 443
  ingress:
    enabled: true
    className: "nginx"
    apiDomainName: "internal.example.com"
    domainPrefix: "keycloak"
```

Install with the custom values:

```bash
helm install zta deployments/k8s/helm/zta-control-plane \
  --namespace zta-control-plane \
  --create-namespace \
  -f values-prod.yaml
```

## Verify the Installation

Check the auth service health:

```bash
kubectl -n zta-control-plane port-forward svc/zta-auth-service 8000:8000 &
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

Access the UI:

```bash
kubectl -n zta-control-plane port-forward svc/zta-ui-explorer 8080:80 &
# Open http://localhost:8080 in your browser
```

## Apply CRDs

CRDs are included in the Helm chart and installed automatically. Verify they are present:

```bash
kubectl get crd | grep zta.io
# multiagentsystems.zta.io
# ztapolicies.zta.io
```

## Next Step

[Install the Demo MAS →](demo-mas.md)

Or if you're deploying your own MAS, go to [Concepts — Multi-Agent Systems](/concepts/mas).
