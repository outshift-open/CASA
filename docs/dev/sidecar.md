# Preparing the environemnt

You can use the comn-dev-use2-1 eks cluster.

## 0. Create your own namespace that is not "zta-sidecar"!

```sh
$ kubectl create ns YOUR_NAMESPACE_HERE
```

## 1. Enable Istio Sidecar for your namespace

```sh
$ kubectl label namespace YOUR_NAMESPACE_HERE istio-injection=enabled
```

## 2. Deploy MAS

First generate an OpenAI4o token and put it here `demo/k8s/helm/values.yaml`

```sh
$ cd demo/k8s/helm
$ helm install zta-mas -f values.yaml . --namespace YOUR_NAMESPACE_HERE
```

## 3. Deploy Our Custom Ext-Auth Filter

Before deploying, go to `ext_authz_middleware/helm/ext-authz-middleware/crds/extauth_filter.yaml` and fix `ext-authz-middleware.zta-sidecar.svc.cluster.local` at the end of the file with what the comment says.

After that, you can deploy the middleware:

```sh
$ cd ext_authz_middleware/helm/ext-authz-middleware/
$ helm install ext-authz-middleware -f values.yaml . --namespace YOUR_NAMESPACE_HERE
```

## 4. Deploy Otel Collector & Jaeger

```sh
$ cd ext_authz_middleware/helm/otel-collector
$ helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
$ helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
$ helm install jaeger jaegertracing/jaeger -f jaeger.yaml --namespace YOUR_NAMESPACE_HERE
$ helm install otel-collector open-telemetry/opentelemetry-collector -f otel.yaml --namespace YOUR_NAMESPACE_HERE --set image.repository="otel/opentelemetry-collector-k8s"
```

## 5. Use OBI instead of Grafana Beyla (IGNORE THIS STEP, THE CONFIG IS STILL NOT FINISHED)

```sh
$ cd ext_authz_middleware/helm/obi
$ helm install obi open-telemetry/opentelemetry-ebpf-instrumentation -f values.yaml --namespace YOUR_NAMESPACE_HERE
```

## A way to test this

```sh
$ kubectl -n zta-sidecar exec -it $(kubectl -n zta-sidecar get pods -o custom-columns=NAME:.metadata.name --no-headers | grep ext-authz-middleware) -- wget -qO- \
  --header 'content-type: application/json' \
  --post-data '{"content": "Get the account summary and scheduled payments"}' \
  http://zta-demo-agent:8082/chat
```

# TODO:

We can first create two custom Go middlewares instead of one to handle INBOUND HTTP requests and OUTBOUND HTTP requests, one middleware for each filter (for now I only have one as you can see here `ext_authz_middleware/helm/ext-authz-middleware/crds/extauth_filter.yaml`).

## For the INBOUND logic:

In the method `Check()` located in the file `ext_authz_middleware/main.go` we need to add this flow:

1. Get the trace ID from the header `traceparent` ([RFC](https://www.w3.org/TR/trace-context/)), the format of this header is `{VERSION}-{TRACE_ID}-{SPAN_ID}-{FLAGS}`, so we can simply spit the string by `-` and take the second value in the array.

### If it's the first request from a user

1. Do token generation if it's the first time request from the user (this is equivalent to a client app), we call our zta-auth-server to create a user input (we need to add an endpoint, or you can simply call `/token` and then parse the returned JWT to get the user input ID)
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
