---
id: control-plane-values
sidebar_position: 1
title: Control Plane Values
---

# Control Plane Helm Values

Reference for `deployments/helm/casa-control-plane/values.yaml`.

## Auth Service

```yaml
authService:
    image:
        repository: ghcr.io/outshift-open/casa-auth-server
        tag: latest
        pullPolicy: IfNotPresent
    replicaCount: 1
    service:
        type: ClusterIP
        port: 8000
    resources:
        requests:
            memory: "256Mi"
            cpu: "250m"
        limits:
            memory: "512Mi"
            cpu: "500m"
    ingress:
        enabled: false
        className: ""
        apiDomainName: ""
        domainPrefix: "auth"
        annotations: {}
    env:
        authServerUrl: "" # defaults to in-cluster URL
    database:
        host: "" # defaults to in-cluster postgres-auth
        port: 5432
        name: identity-platform
        username: postgres
        password: postgres # override in production
    idp:
        serverUrl: "" # defaults to in-cluster Keycloak
        adminUsername: admin
        adminPassword: admin # override in production
```

| Field                   | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `replicaCount`          | Number of auth service replicas. Stateless — safe to scale horizontally. |
| `ingress.enabled`       | Set to `true` to create an Ingress resource for external access.         |
| `ingress.apiDomainName` | Base domain for the Ingress (e.g. `internal.example.com`).               |
| `ingress.domainPrefix`  | Subdomain prefix (e.g. `auth` → `auth.internal.example.com`).            |
| `database.host`         | External PostgreSQL hostname. Leave empty to use the bundled instance.   |
| `idp.serverUrl`         | External Keycloak URL. Leave empty to use the bundled instance.          |

## UI Explorer

```yaml
uiExplorer:
    image:
        repository: ghcr.io/outshift-open/casa-auth-server-ui
        tag: latest
        pullPolicy: IfNotPresent
    replicaCount: 1
    service:
        type: ClusterIP
        port: 80
    ingress:
        enabled: false
        className: ""
        apiDomainName: ""
        domainPrefix: "casa"
        annotations: {}
    nginx:
        apiProxyEnabled: true
```

| Field                   | Description                                                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `nginx.apiProxyEnabled` | When `true`, Nginx proxies `/api/` requests to the auth service. The UI image must be built with `VITE_API_BASE_URL=/api`. |

## PostgreSQL (Auth)

```yaml
postgresAuth:
    image:
        repository: postgres
        tag: "15-alpine"
        pullPolicy: IfNotPresent
    persistence:
        enabled: true
        size: 1Gi
        storageClass: "" # uses cluster default StorageClass
    database: identity-platform
    username: postgres
    password: postgres # override in production
    resources:
        requests:
            memory: "256Mi"
            cpu: "100m"
        limits:
            memory: "512Mi"
            cpu: "250m"
```

Set `postgresAuth.enabled: false` (not a top-level chart field — configure via `authService.database.host`) to use an external PostgreSQL instance.

## PostgreSQL (Keycloak)

```yaml
postgresKeycloak:
    image:
        repository: postgres
        tag: "15-alpine"
    persistence:
        enabled: true
        size: 1Gi
        storageClass: ""
    database: keycloak
    username: keycloak
    password: keycloak # override in production
```

## Keycloak

```yaml
keycloak:
    image:
        repository: ghcr.io/outshift-open/casa-auth-server-keycloak
        tag: latest
        pullPolicy: IfNotPresent
    replicaCount: 1
    service:
        type: ClusterIP
        port: 8080
    admin:
        username: admin
        password: admin # override in production
    ingress:
        enabled: false
        className: ""
        apiDomainName: ""
        domainPrefix: "keycloak"
        annotations: {}
    hostname: localhost
    hostnamePort: 8080
```

| Field          | Description                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `hostname`     | Keycloak's public hostname (`KC_HOSTNAME`). Set to your actual domain when deploying behind an Ingress. |
| `hostnamePort` | Port Keycloak is accessible on externally (usually 443 for HTTPS behind ingress).                       |
