---
id: upgrade
sidebar_position: 2
title: Upgrade
---

# Upgrade

Guidelines for upgrading CASA components.

## Upgrading the Control Plane Chart

Before upgrading, check the release notes for breaking changes.

```bash
# Dry-run to preview changes
helm upgrade casa deployments/helm/casa-control-plane \
  --namespace casa-control-plane \
  --dry-run

# Upgrade
helm upgrade casa deployments/helm/casa-control-plane \
  --namespace casa-control-plane

# Or using the Makefile
make helm-upgrade
```

Rolling upgrades are safe for the auth service (stateless). Keycloak and PostgreSQL upgrades may require additional care.

## Upgrading CRDs

CRDs are not automatically upgraded by `helm upgrade`. Apply them manually:

```bash
kubectl apply -f deployments/helm/casa-control-plane/crds/
```

For `v1alpha1` → stable version upgrades:
- Check if fields have been removed or renamed
- Update existing CRD resources before applying the new CRD schema
- The `authorizationServer` field is transitional and will be removed in a future version

## Upgrading Sidecars (Istio mode)

The ext-authz middleware is bundled in the `casa-control-plane` chart and upgrades automatically with `helm upgrade`. After a control plane upgrade, trigger a rolling restart of your MAS workloads so Istio re-injects with the latest configuration:

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
kubectl -n casa-control-plane logs deploy/casa-auth-service | grep -i "migration\|alembic"
```

## Rolling Back

```bash
# Roll back to the previous chart version
helm rollback casa --namespace casa-control-plane

# Or to a specific revision
helm history casa --namespace casa-control-plane
helm rollback casa 3 --namespace casa-control-plane
```

CRD rollbacks are not supported by Helm. If you need to roll back CRD schema changes, apply the previous CRD manifests manually.

## Zero-Downtime Considerations

- **Auth service**: Stateless, rolling update is safe. Token cache (30s TTL) absorbs brief unavailability.
- **Keycloak**: Single replica by default — there will be a brief downtime during pod restart. Scale to 2+ replicas for zero-downtime.
- **PostgreSQL**: Single replica by default — backup before upgrading.
- **Sidecars**: Do not restart all MAS pods simultaneously. Use rolling restarts.
