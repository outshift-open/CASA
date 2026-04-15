package internal

import (
	"context"
	"encoding/base64"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"net/url"
	"strings"

	api "github.com/cisco-eti/identity-auth-server/sdk/go"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
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

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("[OUT] Failed to parse the traceparent header", "err", err)
			return nil, err
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("[OUT]", "trace_id", traceID)

		host := httpReq.Host

		// TODO: this is not always reliable,
		// x-envoy-peer-metadata could be configured to not be present
		peerMetadata, err := s.decodePeerMetadata(httpReq.Headers["x-envoy-peer-metadata"])
		if err != nil {
			slog.Error("Failed to decode peer metadata", "err", err)
			return nil, fmt.Errorf("outbound: unable to decode peer metadata: %w", err)
		}

		callerWorkloadName, found, err := unstructured.NestedString(peerMetadata, "WORKLOAD_NAME")
		if err != nil {
			slog.Error("Failed to get workload name from peer metadata", "err", err)
			return nil, fmt.Errorf("unable to get workload name from peer metadata: %w", err)
		}

		if !found {
			return nil, errors.New("unable to find WORKLOAD_NAME in peer metadata")
		}

		slog.Info(fmt.Sprintf("Caller workload name = %s", callerWorkloadName))

		// TODO: use the workload name of the caller to fetch the MAS, because MCP servers can be shared between MASes
		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByAppHost(ctx, s.namespace, host)
		if err != nil {
			slog.Error(fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for host %s", host), "err", err)
			return nil, fmt.Errorf("outbound: unable to get Kubernetes MultiAgentSystem resource for host %s: %w", host, err)
		}

		var callerToken string

		// get stored JWT of the caller
		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(callerWorkloadName, appSpec.GetKubernetesWorkloadName()) {
				continue
			}

			token, err := s.authSrvClient.LoadTokenFromCache(ctx, s.namespace, traceID, appSpec.UrlHost, appSpec.Type)
			if err != nil {
				slog.Error(fmt.Sprintf("Unable to fetch cached tokens for host %s with trace id %s", appSpec.UrlHost, traceID), "err", err)
				return nil, fmt.Errorf("outbound: unable to fetch cached tokens for host %s with trace id %s: %w", appSpec.UrlHost, traceID, err)
			}

			if token == nil || token.AccessToken == "" {
				return s.deny(), nil
			}

			callerToken = token.AccessToken
			break
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			var err error
			var accessToken string

			if appSpec.GetType() == api.AGENT {
				clientCreds, err := s.getClientCredentials(ctx, appSpec.GetAppId())
				if err != nil {
					return nil, err
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
					"",
					nil,
				)
				if err != nil {
					return nil, fmt.Errorf("outbound: unable to exchange token for agent: %w", err)
				}

				if accessToken == "" {
					return s.deny(), nil
				}
			} else if appSpec.GetType() == api.MCP_SERVER {
				if httpReq.Body == "" {
					return s.allow(), nil
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err)
					return nil, fmt.Errorf("outbound: unable to get MCP tool name from request: %w", err)
				}

				if toolName == "" {
					return s.allow(), nil
				}

				mcpURL, err := url.Parse(fmt.Sprintf("%s://%s", appSpec.UrlScheme, appSpec.UrlHost))
				if err != nil {
					slog.Error("Failed to construct MCP server URL", "err", err)
					return nil, fmt.Errorf("unable to construct MCP server URL: %w", err)
				}

				clientCreds, err := s.getClientCredentials(ctx, appSpec.GetAppId())
				if err != nil {
					return nil, err
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
					return nil, fmt.Errorf("outbound: unable to exchange token for agent: %w", err)
				}

				if accessToken == "" {
					return s.deny(), nil
				}
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
				)
				if err != nil {
					return nil, fmt.Errorf("outbound: unable to store token: %w", err)
				}

				return s.allow(), nil
			}
		}
	}

	return s.allow(), nil
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

func (*OutboundExtAuthService) allow() *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
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
