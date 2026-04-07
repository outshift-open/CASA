package main

import (
	"context"
	"encoding/hex"
	"log/slog"

	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
)

const (
	traceParentHeader = "traceparent"
)

type InboundExtAuthService struct{}

func (s *InboundExtAuthService) Check(_ context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	slog.Info("Received a new HTTP INBOUND request")

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			// TODO: log err
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		// what do i need?
		// - traceID
		// - in service
		// - out service
		// - if client service then input schema to parse the prompt

		md := attrs.GetMetadataContext()
		rmd := attrs.GetRouteMetadataContext()
		src := attrs.GetSource()
		dst := attrs.GetDestination()
		slog.Info(
			"[IN]",
			"method", httpReq.Method,
			"host", httpReq.Host,
			"path", httpReq.Path,
			"metadata", md.String(),
			"route_metadata", rmd.String(),
			"src_service", src.Service,
			"src_labels", src.Labels,
			"dst_service", dst.Service,
			"dst_labels", dst.Labels,
			"trace_id", traceID,
			"headers", headers,
		)
	}

	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}, nil
}
