---
id: upgrade
sidebar_position: 2
title: Upgrade
---

# Upgrade

Guidelines for upgrading ZTA components.

## Upgrading the Control Plane Chart

Before upgrading, check the release notes for breaking changes.

```bash
# Dry-run to preview changes
helm upgrade zta deployments/k8s/helm/zta-control-plane \
  --namespace zta-control-plane \
  --dry-run

# Upgrade
helm upgrade zta deployments/k8s/helm/zta-control-plane \
  --namespace zta-control-plane

# Or using the Makefile
make helm-upgrade
```

Rolling upgrades are safe for the auth service (stateless). Keycloak and PostgreSQL upgrades may require additional care.

## Upgrading CRDs

CRDs are not automatically upgraded by `helm upgrade`. Apply them manually:

```bash
kubectl apply -f deployments/k8s/helm/zta-control-plane/crds/
```

For `v1alpha1` → stable version upgrades:
- Check if fields have been removed or renamed
- Update existing CRD resources before applying the new CRD schema
- The `authorizationServer` field is transitional and will be removed in a future version

## Upgrading Sidecars (Istio mode)

After a control plane upgrade, update the ext-authz middleware:

```bash
cd ext_authz_middleware/helm/ext-authz-middleware/
helm upgrade ext-authz-middleware -f values.yaml . --namespace your-mas-namespace
```

Then trigger a rolling restart of your MAS workloads so Istio re-injects with the latest configuration:

```bash
kubectl rollout restart deploy/your-agent -n your-mas-namespace
kubectl rollout restart deploy/your-mcp-server -n your-mas-namespace
```

## Upgrading Sidecars (Cilium mode — coming soon)

Update the mutating webhook by upgrading the control plane chart (the webhook is bundled). Then restart MAS workloads to get the new sidecar version:

```bash
kubectl rollout restart deploy/your-agent -n your-mas-namespace
```

## Database Migrations

The auth service applies database migrations automatically on startup using Alembic. During a rolling upgrade:

1. The new auth service version applies any pending migrations
2. Old replicas continue running on the previous schema (migrations are backwards-compatible)
3. After all replicas are updated, the migration is complete

If a migration fails:

```bash
kubectl -n zta-control-plane logs deploy/zta-auth-service | grep -i "migration\|alembic"
```

## Rolling Back

```bash
# Roll back to the previous chart version
helm rollback zta --namespace zta-control-plane

# Or to a specific revision
helm history zta --namespace zta-control-plane
helm rollback zta 3 --namespace zta-control-plane
```

CRD rollbacks are not supported by Helm. If you need to roll back CRD schema changes, apply the previous CRD manifests manually.

## Zero-Downtime Considerations

- **Auth service**: Stateless, rolling update is safe. Token cache (30s TTL) absorbs brief unavailability.
- **Keycloak**: Single replica by default — there will be a brief downtime during pod restart. Scale to 2+ replicas for zero-downtime.
- **PostgreSQL**: Single replica by default — backup before upgrading.
- **Sidecars**: Do not restart all MAS pods simultaneously. Use rolling restarts.
