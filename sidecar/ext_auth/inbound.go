package main

import (
	"context"
	"encoding/hex"
	"log/slog"

	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

const (
	traceParentHeader = "traceparent"
)

type InboundExtAuthService struct{}

func (s *InboundExtAuthService) Check(_ context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Error create K8S InCluster config", "err", err)
			return nil, err
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("", "traceID", traceID)

		// host := httpReq.Host

		config, err := rest.InClusterConfig()
		if err != nil {
			slog.Error("Error create K8S InCluster config", "err", err)
			return nil, err
		}

		clientset, err := kubernetes.NewForConfig(config)
		if err != nil {
			slog.Error("Error create K8S client", "err", err)
			return nil, err
		}

		_, err = clientset.CoreV1().Pods("zta-sidecar").List(context.Background(), metav1.ListOptions{})
		if err != nil {
			slog.Error("Error getting PODs", "err", err)
			return nil, err
		}

		// slog.Info("Fetched PODs", "pods", pods)

		dynClient, err := dynamic.NewForConfig(config)
		if err != nil {
			slog.Error("Error create K8S dynamic client", "err", err)
			return nil, err
		}

		gvr := schema.GroupVersionResource{
			Group:    "zta.io",
			Version:  "v1",
			Resource: "multiagentsystems",
		}

		obj, err := dynClient.Resource(gvr).Namespace("zta-sidecar").List(context.Background(), metav1.ListOptions{})
		if err != nil {
			slog.Error("Error listing MAS CRDs", "err", err)
			return nil, err
		}

		for _, item := range obj.Items {
			slog.Info("MAS CRD", "name", item.GetName(), "crd", item)
		}

		// what do i need?
		// - traceID
		// - in service
		// - out service
		// - if client service then input schema to parse the prompt
	}

	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}, nil
}
