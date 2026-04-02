---
id: troubleshooting
sidebar_position: 1
title: Troubleshooting
---

# Troubleshooting

Common issues and how to resolve them.

## Control Plane Issues

### Auth service pod is not starting

**Symptoms:** `zta-auth-service` pod in `Pending` or `CrashLoopBackOff` state

**Check:**

```bash
kubectl -n zta-control-plane describe pod -l app=zta-auth-service
kubectl -n zta-control-plane logs -l app=zta-auth-service --previous
```

**Common causes:**

| Cause | Fix |
|---|---|
| PostgreSQL not ready | Wait for `zta-postgres-auth` pod to be ready, then restart the auth service pod |
| Wrong database credentials | Check `authService.database.password` in values matches the actual postgres password |
| Keycloak not ready | Check `zta-keycloak` pod status; auth service will retry but may crash first |

### Keycloak pod is not starting

```bash
kubectl -n zta-control-plane logs -l app=zta-keycloak
```

Common issue: `postgres-keycloak` not ready. Keycloak waits for the database, but check for connection errors:

```
FATAL: password authentication failed for user "keycloak"
```

Check that `postgresKeycloak.password` and `keycloak.database.password` (if overridden) match.

### Auth service returns 500 on /health

```bash
curl -v http://localhost:8000/health
```

If the response is a 500, the auth service cannot connect to PostgreSQL or Keycloak. Check the pod logs:

```bash
kubectl -n zta-control-plane logs deploy/zta-auth-service | tail -50
```

---

## Sidecar Issues

### Requests are blocked with 403

The sidecar is failing-closed. Possible causes:

1. **Token introspection failing** — control plane unreachable

   ```bash
   # Check if auth service is accessible from the sidecar
   kubectl exec -n your-mas-namespace deploy/your-agent -c istio-proxy -- \
     curl -s http://zta-auth-service.zta-control-plane.svc.cluster.local:8000/health
   ```

2. **Token expired** — token TTL is 5 minutes; if the request is older, get a fresh token

3. **Wrong scope** — the token scope doesn't match the operation. Check the denial reason in auth service logs:

   ```bash
   kubectl -n zta-control-plane logs deploy/zta-auth-service | grep "DENY\|denied\|403"
   ```

4. **Tool check failure** — a deterministic or semantic check rejected the token exchange. Check:

   ```bash
   kubectl -n zta-control-plane logs deploy/zta-auth-service | grep "tool_check"
   ```

### Sidecar not injected

In Istio mode:

```bash
# Verify namespace is labeled
kubectl get namespace your-mas-namespace --show-labels | grep istio-injection

# Verify the pod has the sidecar
kubectl -n your-mas-namespace describe pod your-pod | grep istio-proxy
```

If the label is missing:

```bash
kubectl label namespace your-mas-namespace istio-injection=enabled
kubectl rollout restart deploy/your-deployment -n your-mas-namespace
```

---

## Network Policy Issues (Cilium mode)

### Traffic being dropped unexpectedly

```bash
# Check Hubble flow logs for drops
cilium hubble observe --namespace your-mas-namespace --verdict DROPPED

# Check which policy is dropping the traffic
cilium hubble observe --namespace your-mas-namespace --verdict DROPPED -o json | \
  jq '.flow.policy_match_reason'
```

### Policy not created from ZTAPolicy CRD

```bash
# Check ZTAPolicy status
kubectl describe ztap your-policy-name -n your-mas-namespace

# Look for error in status.message
kubectl get ztap your-policy-name -n your-mas-namespace -o jsonpath='{.status.message}'
```

---

## CRD Issues

### MultiAgentSystem stuck in Pending

```bash
kubectl describe mas your-mas-name -n your-mas-namespace
```

Check `status.message` for the reason. Common causes:
- One or more apps in `spec.apps` could not be reached at their `baseUrl`
- Keycloak realm creation failed

### MAS phase is Failed

```bash
kubectl get mas your-mas-name -n your-mas-namespace -o jsonpath='{.status.message}'
```

---

## Common Commands Reference

```bash
# Control plane status
kubectl -n zta-control-plane get pods
kubectl -n zta-control-plane get events --sort-by=.lastTimestamp | tail -20

# Auth service logs
kubectl -n zta-control-plane logs deploy/zta-auth-service -f

# All MAS resources
kubectl get mas --all-namespaces
kubectl get ztap --all-namespaces

# Helm release status
helm status zta --namespace zta-control-plane
helm history zta --namespace zta-control-plane
```
