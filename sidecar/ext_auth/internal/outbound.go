package internal

import (
	"context"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"log/slog"
	"net/url"
	"strings"
	"time"

	api "github.com/cisco-eti/identity-auth-server/sdk/go"
	corev3 "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"github.com/google/uuid"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
)

const (
	outFilterLogCtx = "OUTBOUND"
)

type OutboundExtAuthService struct {
	namespace     string
	authSrvClient AuthServerClient
	k8sService    KubernetesService
}

func NewOutboundExtAuthService(
	namespace string,
	authSrvClient AuthServerClient,
	k8sService KubernetesService,
) *OutboundExtAuthService {
	return &OutboundExtAuthService{
		namespace:     namespace,
		authSrvClient: authSrvClient,
		k8sService:    k8sService,
	}
}

func (s *OutboundExtAuthService) Check(ctx context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	start := time.Now()
	done := make(chan struct{})
	go func() {
		select {
		case <-ctx.Done():
			slog.Info("[CTX] authz ctx canceled", "after", time.Since(start), "err", ctx.Err())
		case <-done:
		}
	}()
	defer close(done)

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Failed to parse the traceparent header", "context", outFilterLogCtx, "err", err)
			return s.deny(), nil
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("[OUT]", "trace_id", traceID)

		host := httpReq.Host

		// TODO: this is not always reliable,
		// x-envoy-peer-metadata could be configured to not be present
		peerMetadata, err := s.decodePeerMetadata(httpReq.Headers["x-envoy-peer-metadata"])
		if err != nil {
			slog.Error("Failed to decode peer metadata", "context", outFilterLogCtx, "trace_id", traceID, "err", err)
			return s.deny(), nil
		}

		callerWorkloadName, found, err := unstructured.NestedString(peerMetadata, "WORKLOAD_NAME")
		if err != nil {
			slog.Error("Failed to get workload name from peer metadata", "context", outFilterLogCtx, "trace_id", traceID, "err", err)
			return s.deny(), nil
		}

		if !found {
			slog.Error("No workload found in peer metadata", "context", outFilterLogCtx, "trace_id", traceID)
			return s.deny(), nil
		}

		slog.Info(fmt.Sprintf("Host = %s, caller workload name = %s", host, callerWorkloadName), "context", outFilterLogCtx, "trace_id", traceID)

		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByWorkloadName(ctx, s.namespace, callerWorkloadName)
		if err != nil {
			slog.Error(
				fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for caller workload %s", callerWorkloadName),
				"context", outFilterLogCtx,
				"trace_id", traceID,
				"err", err,
			)

			return s.deny(), nil
		}

		var callerToken string

		// get stored JWT of the caller
		for _, appSpec := range masCRD.AppSpecs {
			slog.Info("Matching caller app", "context", outFilterLogCtx, "trace_id", traceID, "src_workload", callerWorkloadName, "workload", appSpec.GetKubernetesWorkloadName())
			if !strings.EqualFold(callerWorkloadName, appSpec.GetKubernetesWorkloadName()) {
				continue
			}

			token, err := s.authSrvClient.LoadTokenFromCache(ctx, s.namespace, traceID, appSpec.UrlHost, appSpec.Type, nil)
			if err != nil {
				slog.Error(fmt.Sprintf("Unable to fetch cached tokens for host %s with trace id %s", appSpec.UrlHost, traceID), "err", err)
				return s.deny(), nil
			}

			if token == nil || token.AccessToken == "" {
				slog.Info("Call denied, no access token found", "context", outFilterLogCtx, "trace_id", traceID)
				return s.deny(), nil
			}

			slog.Info(
				"Found cached access token",
				"context",
				outFilterLogCtx,
				"trace_id",
				traceID,
				"workload",
				appSpec.GetKubernetesWorkloadName(),
				"token",
				token.AccessToken,
			)

			callerToken = token.AccessToken
			break
		}

		if strings.EqualFold(host, masCRD.GetLlmHost()) {
			llmCallID := uuid.NewString()

			slog.Info(fmt.Sprintf("Generating x-litellm-call-id: %s", llmCallID), "context", outFilterLogCtx, "trace_id", traceID)

			_, err := s.authSrvClient.StoreLLMCallMapping(ctx, s.namespace, llmCallID, traceID, callerToken)
			if err != nil {
				return s.deny(), nil
			}

			return s.allowWithHeaders(map[string]string{"x-litellm-call-id": llmCallID}), nil
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			var err error
			var accessToken string
			var associatedTool *string

			if appSpec.GetType() == api.AGENT {
				clientCreds, err := s.getClientCredentials(ctx, appSpec.GetAppId())
				if err != nil {
					return s.deny(), nil
				}

				if clientCreds == nil {
					slog.Info("Call denied, no client credentials found", "context", outFilterLogCtx, "trace_id", traceID)
					return s.deny(), nil
				}

				accessToken, err = s.authSrvClient.ExchangeToken(
					ctx,
					appSpec.GetAppId(),
					clientCreds.ClientID,
					clientCreds.ClientSecret,
					callerToken,
					"",
					nil,
				)
				if err != nil {
					return s.deny(), nil
				}

				if accessToken == "" {
					slog.Info("Call defnied, access token is empty after token exchange [agent->agent]", "context", outFilterLogCtx, "trace_id", traceID)
					return s.deny(), nil
				}

				return s.allow(accessToken), nil
			} else if appSpec.GetType() == api.MCP_SERVER {
				slog.Info("Checking MCP server call", "context", outFilterLogCtx, "trace_id", traceID, "host", host, "method", httpReq.Method, "path", httpReq.Path)
				if httpReq.Body == "" {
					return s.allow(""), nil
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err)
					// return nil, fmt.Errorf("outbound: unable to get MCP tool name from request: %w", err)
					return s.deny(), nil
				}

				if toolName == "" {
					slog.Info("Call allowed, tool name is empty", "context", outFilterLogCtx, "trace_id", traceID)
					return s.allow(""), nil
				}

				slog.Info("Found tool name", "tool_name", toolName, "context", outFilterLogCtx, "trace_id", traceID)

				mcpURL, err := url.Parse(fmt.Sprintf("%s://%s/mcp", appSpec.UrlScheme, appSpec.UrlHost))
				if err != nil {
					slog.Error("Failed to construct MCP server URL", "context", outFilterLogCtx, "trace_id", traceID, "err", err)
					return s.deny(), nil
				}

				clientCreds, err := s.getClientCredentials(ctx, appSpec.GetAppId())
				if err != nil {
					return s.deny(), nil
				}

				if clientCreds == nil {
					return s.deny(), nil
				}

				accessToken, err = s.authSrvClient.ExchangeToken(
					ctx,
					appSpec.GetAppId(),
					clientCreds.ClientID,
					clientCreds.ClientSecret,
					callerToken,
					mcpURL.String(),
					[]string{toolName},
				)
				if err != nil {
					return s.deny(), nil
				}

				if accessToken == "" {
					slog.Info("Call defnied, access token is empty after token exchange [agent->MCP]", "context", outFilterLogCtx, "trace_id", traceID)
					return s.deny(), nil
				}

				associatedTool = &toolName
			}

			if accessToken != "" {
				slog.Info("Access token generated with token exchange", "token", accessToken)

				err = s.authSrvClient.StoreTokenInCache(
					ctx,
					s.namespace,
					traceID,
					appSpec.UrlHost,
					appSpec.GetType(),
					accessToken,
					associatedTool,
				)
				if err != nil {
					return s.deny(), nil
				}

				slog.Info("Call allowed", "context", outFilterLogCtx, "trace_id", traceID, "tool_name", associatedTool)
				return s.allow(accessToken), nil
			}
		}
	}

	slog.Info("Call allowed", "context", outFilterLogCtx)
	return s.allow(""), nil
}

func (*OutboundExtAuthService) decodePeerMetadata(v string) (map[string]any, error) {
	b, err := base64.StdEncoding.DecodeString(v)
	if err != nil {
		b, err = base64.RawStdEncoding.DecodeString(v)
		if err != nil {
			return nil, fmt.Errorf("failed to decode peer metadata base64: %w", err)
		}
	}

	var s structpb.Struct
	if err := proto.Unmarshal(b, &s); err != nil {
		return nil, fmt.Errorf("unable to unmarshal peer metadata protobuf: %w", err)
	}

	return s.AsMap(), nil
}

func (s *OutboundExtAuthService) allow(jwt string) *authv3.CheckResponse {
	if jwt != "" {
		return s.allowWithHeaders(map[string]string{"authorization": fmt.Sprintf("Bearer %s", jwt)})
	}

	return s.allowWithHeaders(map[string]string{})
}

func (*OutboundExtAuthService) allowWithHeaders(headers map[string]string) *authv3.CheckResponse {
	hvOptions := []*corev3.HeaderValueOption{}
	for k, v := range headers {
		hvOptions = append(hvOptions, &corev3.HeaderValueOption{
			Header: &corev3.HeaderValue{
				Key:   k,
				Value: v,
			},
		})
	}

	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{
				Headers: hvOptions,
			},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}
}

func (*OutboundExtAuthService) deny() *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_DeniedResponse{
			DeniedResponse: &authv3.DeniedHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.Unauthenticated)},
	}
}

func (s *OutboundExtAuthService) getClientCredentials(ctx context.Context, appID string) (*AppClientCredential, error) {
	clientCreds, err := s.k8sService.GetAppCredentials(ctx, appID)
	if err != nil {
		slog.Error(fmt.Sprintf("Failed to fetch client credentials for app %s", appID), "err", err)
		return nil, fmt.Errorf("unable to fetch client credentials for app %s: %w", appID, err)
	}

	if clientCreds == nil {
		slog.Warn(fmt.Sprintf("No client credentials for app %s", appID))
		return nil, nil
	}

	return clientCreds, nil
}
