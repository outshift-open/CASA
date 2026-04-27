---
id: install-control-plane
sidebar_position: 2
title: Install Control Plane
---

# Install the CASA Control Plane

The CASA control plane is installed via the `casa-control-plane` Helm chart located at `deployments/helm/casa-control-plane/`.

## Basic Installation

```bash
helm install casa deployments/helm/casa-control-plane \
  --namespace casa-control-plane \
  --create-namespace
```

Wait for all pods to be ready:

```bash
kubectl -n casa-control-plane wait --for=condition=ready pod --all --timeout=300s
```

Expected pods:

```
NAME                              READY   STATUS  
casa-auth-service-...              1/1     Running  
casa-ui-explorer-...               1/1     Running  
casa-keycloak-...                  1/1     Running  
casa-postgres-auth-...             1/1     Running  
casa-postgres-keycloak-...         1/1     Running  
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

The Makefile uses `HELM_RELEASE=casa` and `HELM_NAMESPACE=casa-control-plane` by default. Override with:

```bash
make helm-install HELM_RELEASE=my-casa HELM_NAMESPACE=my-namespace
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
    domainPrefix: "casa-auth"

uiExplorer:
  ingress:
    enabled: true
    className: "nginx"
    apiDomainName: "internal.example.com"
    domainPrefix: "casa"

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
helm install casa deployments/helm/casa-control-plane \
  --namespace casa-control-plane \
  --create-namespace \
  -f values-prod.yaml
```

## Verify the Installation

Check the auth service health:

```bash
kubectl -n casa-control-plane port-forward svc/casa-auth-service 8000:8000 &
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

Access the UI:

```bash
kubectl -n casa-control-plane port-forward svc/casa-ui-explorer 8080:80 &
# Open http://localhost:8080 in your browser
```

## Apply CRDs

CRDs are included in the Helm chart and installed automatically. Verify they are present:

```bash
kubectl get crd | grep casa.io
# multiagentsystems.casa.io
# casapolicies.casa.io
```

## Next Step

[Install the Demo MAS →](demo-mas.md)

Or if you're deploying your own MAS, go to [Concepts — Multi-Agent Systems](/concepts/mas).
