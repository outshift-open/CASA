---
id: troubleshooting
sidebar_position: 1
title: Troubleshooting
---

# Troubleshooting

Common issues and how to resolve them.

## Runtime Issues

### Auth service pod is not starting

**Symptoms:** `casa-auth-service` pod in `Pending` or `CrashLoopBackOff` state

**Check:**

```bash
kubectl -n casa-runtime describe pod -l app=casa-auth-service
kubectl -n casa-runtime logs -l app=casa-auth-service --previous
```

**Common causes:**

| Cause | Fix |
|---|---|
| PostgreSQL not ready | Wait for `casa-postgres-auth` pod to be ready, then restart the auth service pod |
| Wrong database credentials | Check `authService.database.password` in values matches the actual postgres password |
| Keycloak not ready | Check `casa-keycloak` pod status; auth service will retry but may crash first |

### Keycloak pod is not starting

```bash
kubectl -n casa-runtime logs -l app=casa-keycloak
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
kubectl -n casa-runtime logs deploy/casa-auth-service | tail -50
```

---

## Sidecar Issues

### Requests are blocked with 403

The sidecar is failing-closed. Possible causes:

1. **Token introspection failing** — runtime unreachable

   ```bash
   # Check if auth service is accessible from the sidecar
   kubectl exec -n your-mas-namespace deploy/your-agent -c istio-proxy -- \
     curl -s http://casa-auth-service.casa-runtime.svc.cluster.local:8000/health
   ```

2. **Token expired** — token TTL is 5 minutes; if the request is older, get a fresh token

3. **Wrong scope** — the token scope doesn't match the operation. Check the denial reason in auth service logs:

   ```bash
   kubectl -n casa-runtime logs deploy/casa-auth-service | grep "DENY\|denied\|403"
   ```

4. **Tool check failure** — a deterministic or semantic check rejected the token exchange. Check:

   ```bash
   kubectl -n casa-runtime logs deploy/casa-auth-service | grep "tool_check"
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

## Network Policy Issues (Cilium mode — coming soon)

### Traffic being dropped unexpectedly

Use the **Explorer UI** to inspect flow verdicts and token denials:

```bash
kubectl -n casa-runtime port-forward svc/casa-ui-explorer 8080:80
# Open http://localhost:8080 → Traces
```

### Policy not created from CASAPolicy CRD

```bash
# Check CASAPolicy status
kubectl describe casap your-policy-name -n your-mas-namespace

# Look for error in status.message
kubectl get casap your-policy-name -n your-mas-namespace -o jsonpath='{.status.message}'
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
kubectl -n casa-runtime get pods
kubectl -n casa-runtime get events --sort-by=.lastTimestamp | tail -20

# Auth service logs
kubectl -n casa-runtime logs deploy/casa-auth-service -f

# All MAS resources
kubectl get mas --all-namespaces
kubectl get casap --all-namespaces

# Helm release status
helm status casa --namespace casa-runtime
helm history casa --namespace casa-runtime
```
