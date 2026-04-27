# Preparing the environemnt

You can use the comn-dev-use2-1 eks cluster.

## 0. Create your own namespace that is not "casa-sidecar"!

```sh
$ kubectl create ns YOUR_NAMESPACE_HERE
```

## 1. Enable Istio Sidecar for your namespace

```sh
$ kubectl label namespace YOUR_NAMESPACE_HERE istio-injection=enabled
```

## 2. Deploy MAS

First generate an OpenAI4o token and put it here `demo/helm/values.yaml`

```sh
$ cd demo/helm
$ helm install casa-mas -f values.yaml . --namespace YOUR_NAMESPACE_HERE
```

## 3. Deploy Our Custom Ext-Auth Filter

The namespace is now templated automatically — no manual edits needed before deploying.

```sh
$ cd ext_authz_middleware/helm/ext-authz-middleware/
$ helm install ext-authz-middleware -f values.yaml . --namespace YOUR_NAMESPACE_HERE
```

## 4. Observability stack (OTel Collector + Jaeger + OBI)

All three are bundled as subcharts of `ext-authz-middleware` and deployed automatically in step 3. No separate install needed.

To disable any of them, set the relevant flag in `ext_authz_middleware/helm/ext-authz-middleware/values.yaml`:
- `otelcollector.enabled: false`
- `jaeger.jaeger.enabled: false`
- `obi.enabled: false`

Jaeger UI is available at `https://casa-jaeger.dev.outshift.ai` (requires DNS entry pointing to the nginx ingress ELB).

## A way to test this

```sh
$ kubectl -n casa-sidecar exec -it $(kubectl -n casa-sidecar get pods -o custom-columns=NAME:.metadata.name --no-headers | grep ext-authz-middleware) -- wget -qO- \
  --header 'content-type: application/json' \
  --post-data '{"content": "Get the account summary and scheduled payments"}' \
  http://casa-demo-agent:8082/chat
```

# TODO:

We can first create two custom Go middlewares instead of one to handle INBOUND HTTP requests and OUTBOUND HTTP requests, one middleware for each filter (for now I only have one as you can see here `ext_authz_middleware/helm/ext-authz-middleware/crds/extauth_filter.yaml`).

## For the INBOUND logic:

In the method `Check()` located in the file `ext_authz_middleware/main.go` we need to add this flow:

1. Get the trace ID from the header `traceparent` ([RFC](https://www.w3.org/TR/trace-context/)), the format of this header is `{VERSION}-{TRACE_ID}-{SPAN_ID}-{FLAGS}`, so we can simply spit the string by `-` and take the second value in the array.

### If it's the first request from a user

1. Do token generation if it's the first time request from the user (this is equivalent to a client app), we call our casa-auth-server to create a user input (we need to add an endpoint, or you can simply call `/token` and then parse the returned JWT to get the user input ID)
2. Store a mapping between the TRACE_ID and the USER_INPUT_ID (or the initial prompt), it can be found in the generated token (or you can store the token too)

### If not

1. Well in this case we do token validation (TBAC verification stuff)

## For the OUTBOUND logic:

I suppose it's simpler to have a separate middleware/Go program to handle the OUTBOUND HTTP requests. The logic is to:

1. Get the TRACE_ID from `traceparent`
2. Map it to the corresponding user_input_id
3. Do the token/token exchange logic
4. Create an Authorization header when returning the response, for example:
```go
...
HttpResponse: &authv3.CheckResponse_OkResponse{
  OkResponse: &authv3.OkHttpResponse{
    Headers: []*corev3.HeaderValueOption{
      {
        Header: &corev3.HeaderValue{
          Key: "Authorization",
          Value: "Bearer ...JWT...",
        },
      },
    },
  },
},
...
```

> **PS: For now parallel requests don't work because I didn't configure well OBI**
