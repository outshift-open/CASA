package internal

import (
	"bytes"
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"strings"

	authapi "github.com/cisco-eti/identity-auth-server/sdk/go"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	"k8s.io/client-go/util/jsonpath"
)

const (
	traceParentHeader = "traceparent"
)

type InboundExtAuthService struct {
	namespace     string
	authSrvClient AuthServerClient
	k8sService    KubernetesService
}

func NewInboundExtAuthService(
	namespace string,
	authSrvClient AuthServerClient,
	k8sService KubernetesService,
) *InboundExtAuthService {
	return &InboundExtAuthService{
		namespace:     namespace,
		authSrvClient: authSrvClient,
		k8sService:    k8sService,
	}
}

func (s *InboundExtAuthService) Check(ctx context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Failed to parse the traceparent header", "err", err)
			return nil, err
		}

		// Step 1. get the trace ID
		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("", "traceID", traceID)

		// Step 2. get the service name
		host := httpReq.Host

		slog.Info("", "App host", host)

		// Step 3.
		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByAppHost(ctx, s.namespace, host)
		if err != nil {
			slog.Error(fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for host %s", host), "err", err)
			return nil, fmt.Errorf("inbound: unable to get Kubernetes MultiAgentSystem resource for host %s: %w", host, err)
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			// Step 4.
			storedToken, err := s.authSrvClient.LoadTokenFromCache(ctx, s.namespace, traceID, appSpec.UrlHost, appSpec.Type)
			if err != nil {
				slog.Error(fmt.Sprintf("Unable to fetch cached tokens for host %s with trace id %s", host, traceID), "err", err)
				return nil, fmt.Errorf("inbound: unable to fetch cached tokens for host %s with trace id %s: %w", host, traceID, err)
			}

			if storedToken != nil {
				slog.Info(fmt.Sprintf("Found cached token for host %s with trace id %s", host, traceID))
			}

			// The app host must be configured correctly by the user for this to work
			if appSpec.Type == authapi.AGENT {
				slog.Info("Checking Agent call", "app", appSpec)

				if storedToken != nil && storedToken.AccessToken != "" {
					slog.Info("Validating agent token")

					return s.validateToken(ctx, storedToken.AccessToken, []string{})
				}

				// TODO: only to when it comes to CLIENT
				if appSpec.GetPromptFieldJsonPath() != "" {
					// Step 9.1
					jp := jsonpath.New("")
					err := jp.Parse(appSpec.GetPromptFieldJsonPath())
					if err != nil {
						slog.Error("Error parsing the prompt JSON path", "err", err)
						return nil, fmt.Errorf("inbound: unable to parse prompt JSON path: %w", err)
					}

					var body any
					err = json.Unmarshal([]byte(httpReq.Body), &body)
					if err != nil {
						slog.Error("Failed to unmarshal the HTTP request body", "err", err)
						return nil, fmt.Errorf("inbound: unable to unmarshal the HTTP request body: %w", err)
					}

					var buf bytes.Buffer
					err = jp.Execute(&buf, body)
					if err != nil {
						slog.Error("Failed to find the prompt using the JSON path", "err", err)
						return nil, fmt.Errorf("inbound: unable to find the prompt with the JSON path: %w", err)
					}

					userInputID, err := s.authSrvClient.CreateUserInput(ctx, appSpec.GetAppId(), buf.String(), traceID)
					if err != nil {
						return nil, fmt.Errorf("inbound: unable to create user input during Check: %w", err)
					}

					slog.Info(fmt.Sprintf("User input %s created for trace_id %s", userInputID, traceID))

					clientCreds, err := s.k8sService.GetAppCredentials(ctx, appSpec.GetAppId())
					if err != nil {
						slog.Error(fmt.Sprintf("Failed to fetch client credentials for app %s", appSpec.GetAppId()), "err", err)
						return nil, fmt.Errorf("unable to fetch client credentials for app %s: %w", appSpec.GetAppId(), err)
					}

					if clientCreds == nil {
						slog.Warn(fmt.Sprintf("No client credentials for app %s", appSpec.GetAppId()))
						return s.deny(), nil
					}

					// Step 9.2
					accessToken, err := s.authSrvClient.Token(
						ctx,
						appSpec.GetAppId(),
						clientCreds.ClientID,
						clientCreds.ClientSecret,
						userInputID,
					)
					if err != nil {
						return nil, fmt.Errorf("inbound: unable to generate token: %w", err)
					}

					slog.Info("Access token generated", "token", accessToken)

					err = s.authSrvClient.StoreTokenInCache(
						ctx,
						s.namespace,
						traceID,
						appSpec.GetUrlHost(),
						appSpec.GetType(),
						accessToken,
					)
					if err != nil {
						return nil, fmt.Errorf("inbound: unable to store token: %w", err)
					}

					break
				}
			} else if appSpec.Type == authapi.MCP_SERVER {
				slog.Info("Checking MCP server call", "app", appSpec)
				if httpReq.Body == "" {
					continue
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err)
					return nil, fmt.Errorf("inbound: unable to get MCP tool name from request: %w", err)
				}

				if toolName == "" {
					continue
				}

				if storedToken == nil || storedToken.AccessToken == "" {
					return s.deny(), nil
				}

				slog.Info("Validating tool call", "tool", toolName)

				return s.validateToken(ctx, storedToken.AccessToken, []string{toolName})
			}
		}
	}

	return s.allow(), nil
}

func (s *InboundExtAuthService) validateToken(ctx context.Context, token string, tools []string) (*authv3.CheckResponse, error) {
	introspectResp, err := s.authSrvClient.Introspect(ctx, token, tools)
	if err != nil {
		slog.Error("Failed to call token introspection endpoint", "err", err)
		return nil, fmt.Errorf("inbound: unable to call token introspection endpoint: %w", err)
	}

	if introspectResp == nil || !introspectResp.Active {
		return s.deny(), nil
	}

	return s.allow(), nil
}

func (s *InboundExtAuthService) allow() *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}
}

func (s *InboundExtAuthService) deny() *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_DeniedResponse{
			DeniedResponse: &authv3.DeniedHttpResponse{},
		},
		Status: &status.Status{Code: int32(codes.Unauthenticated)},
	}
}
