package main

import (
	"context"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"net/url"
	"strings"

	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
)

const (
	traceParentHeader = "traceparent"
)

type InboundExtAuthService struct {
	k8sDynClient *dynamic.DynamicClient
	k8sNamespace string
}

func NewInboundExtAuthService(
	k8sDynClient *dynamic.DynamicClient,
	k8sNamespace string,
) *InboundExtAuthService {
	return &InboundExtAuthService{
		k8sDynClient: k8sDynClient,
		k8sNamespace: k8sNamespace,
	}
}

func (s *InboundExtAuthService) Check(_ context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	/*
		Flow:
			- get trace id
			- get service name
			- fetch its config from the MAS CRD
			- get the JWT from the backend using the tuple (trace_id, service_name, service_type)
			- does it have a JWT?
			- yes -> validate it based on the service type (agent, mcp)
			- if invalid return 403
			- if MCP without JWT -> return 403
			- if it's an agent/client without JWT
				- take the prompt and create a mapping between the trace ID and the prompt (user_input_id)
				- call /token and store the token
	*/

	ctx := context.Background()
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Error create K8S InCluster config", "err", err)
			return nil, err
		}

		// get the trace ID
		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("", "traceID", traceID)

		// get the service name
		host := httpReq.Host
		slog.Info("", "serviceName", host)

		// fetch the list of MAS CRs
		gvr := schema.GroupVersionResource{
			Group:    "zta.io",
			Version:  "v1",
			Resource: "multiagentsystems",
		}

		resource, err := s.k8sDynClient.
			Resource(gvr).
			Namespace(s.k8sNamespace).
			List(ctx, metav1.ListOptions{})
		if err != nil {
			slog.Error("Error listing MAS CRDs", "err", err)
			return nil, err
		}

		if len(resource.Items) == 0 {
			slog.Error("no MultiAgentSystem resource found")
			return nil, errors.New("no MultiAgentSystem resource found")
		}

		// get the first one in the list
		masDef := resource.Items[0]

		apps, _, _ := unstructured.NestedSlice(masDef.Object, "spec", "apps")
		for _, payload := range apps {
			appMap, ok := payload.(map[string]any)
			if ok {
				app, err := NewAppFromMap(appMap)
				if err != nil {
					return nil, fmt.Errorf("unable to create App: %w", err)
				}

				baseURL, err := url.Parse(app.BaseURL)
				if err != nil {
					return nil, fmt.Errorf("unable to parse App base URL: %w", err)
				}

				if strings.EqualFold(host, baseURL.Host) {
					slog.Info("Found App config", "app", appMap)
				}
			}
		}
	}

	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}, nil
}
