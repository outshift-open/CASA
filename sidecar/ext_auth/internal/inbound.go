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
	inFilterLogCtx    = "INBOUND"
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
			slog.Error("Failed to parse the traceparent header", "context", inFilterLogCtx, "err", err)
			// return nil, err
			return s.deny(), nil
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		slog.Info("[IN]", "traceID", traceID)

		host := httpReq.Host

		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByAppHost(ctx, s.namespace, host)
		if err != nil {
			slog.Error(
				fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for host %s", host),
				"context",
				inFilterLogCtx,
				"trace_id",
				traceID,
				"host",
				host,
				"err",
				err,
			)
			// return nil, fmt.Errorf("inbound: unable to get Kubernetes MultiAgentSystem resource for host %s: %w", host, err)
			return s.deny(), nil
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			// var existingAccessToken string

			// slog.Info("[IN]", "headers", headers)

			// if authHeader, ok := headers["authorization"]; ok {
			// 	if strings.HasPrefix(authHeader, "Bearer ") {
			// 		slog.Info("Found access token in HTTP header", "context", inFilterLogCtx, "trace_id", traceID, "host", host)
			// 		existingAccessToken = strings.Replace(authHeader, "Bearer ", "", -1)
			// 	}
			// }

			// The app host must be configured correctly by the user for this to work
			switch appSpec.Type {
			case authapi.AGENT:
				slog.Info("Checking Agent call", "context", inFilterLogCtx, "trace_id", traceID, "host", host)

				// if existingAccessToken == "" {

				// }
				slog.Info("Loading stored token", "context", inFilterLogCtx, "trace_id", traceID, "host", host)
				existingAccessToken, err := s.loadStoredToken(ctx, headers, traceID, appSpec.UrlHost, appSpec.Type, nil)
				if err != nil {
					return s.deny(), nil
				}

				if existingAccessToken != "" {
					slog.Info("Validating access token for Agent", "context", inFilterLogCtx, "trace_id", traceID, "host", host)

					return s.validateToken(ctx, existingAccessToken, []string{}, traceID)
				}

				// TODO: only to when it comes to CLIENT
				if appSpec.GetPromptFieldJsonPath() != "" {
					jp := jsonpath.New("")
					err := jp.Parse(appSpec.GetPromptFieldJsonPath())
					if err != nil {
						slog.Error("Error parsing the prompt JSON path", "err", err, "context", inFilterLogCtx, "trace_id", traceID, "host", host)
						// return nil, fmt.Errorf("inbound: unable to parse prompt JSON path: %w", err)
						return s.deny(), nil
					}

					var body any
					err = json.Unmarshal([]byte(httpReq.Body), &body)
					if err != nil {
						slog.Error("Failed to unmarshal the HTTP request body", "err", err, "context", inFilterLogCtx, "trace_id", traceID, "host", host)
						// return nil, fmt.Errorf("inbound: unable to unmarshal the HTTP request body: %w", err)
						return s.deny(), nil
					}

					var buf bytes.Buffer
					err = jp.Execute(&buf, body)
					if err != nil {
						slog.Error("Failed to find the prompt using the JSON path", "err", err, "context", inFilterLogCtx, "trace_id", traceID, "host", host)
						// return nil, fmt.Errorf("inbound: unable to find the prompt with the JSON path: %w", err)
						return s.deny(), nil
					}

					userInputID, err := s.authSrvClient.CreateUserInput(ctx, appSpec.GetAppId(), buf.String(), traceID)
					if err != nil {
						// return nil, fmt.Errorf("inbound: unable to create user input during Check: %w", err)
						return s.deny(), nil
					}

					slog.Info(fmt.Sprintf("User input %s created for trace_id %s", userInputID, traceID))

					clientCreds, err := s.k8sService.GetAppCredentials(ctx, appSpec.GetAppId())
					if err != nil {
						slog.Error(fmt.Sprintf("Failed to fetch client credentials for app %s", appSpec.GetAppId()), "err", err, "context", inFilterLogCtx, "trace_id", traceID, "host", host)
						// return nil, fmt.Errorf("unable to fetch client credentials for app %s: %w", appSpec.GetAppId(), err)
						return s.deny(), nil
					}

					if clientCreds == nil {
						slog.Warn(fmt.Sprintf("No client credentials for app %s", appSpec.GetAppId()), "context", inFilterLogCtx, "trace_id", traceID, "host", host)
						return s.deny(), nil
					}

					accessToken, err := s.authSrvClient.Token(
						ctx,
						appSpec.GetAppId(),
						clientCreds.ClientID,
						clientCreds.ClientSecret,
						userInputID,
					)
					if err != nil {
						// return nil, fmt.Errorf("inbound: unable to generate token: %w", err)
						return s.deny(), nil
					}

					slog.Info("Access token generated", "token", accessToken, "context", inFilterLogCtx, "trace_id", traceID, "host", host)

					err = s.authSrvClient.StoreTokenInCache(
						ctx,
						s.namespace,
						traceID,
						appSpec.GetUrlHost(),
						appSpec.GetType(),
						accessToken,
						nil,
					)
					if err != nil {
						// return nil, fmt.Errorf("inbound: unable to store token: %w", err)
						return s.deny(), nil
					}

					return s.allow(), nil
				}
			case authapi.MCP_SERVER:
				slog.Info("Checking MCP server call", "context", inFilterLogCtx, "trace_id", traceID, "host", host, "method", httpReq.Method, "path", httpReq.Path)
				if httpReq.Body == "" {
					return s.allow(), nil
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err, "context", inFilterLogCtx, "trace_id", traceID, "host", host)
					// return nil, fmt.Errorf("inbound: unable to get MCP tool name from request: %w", err)
					return s.deny(), nil
				}

				if toolName == "" {
					return s.allow(), nil
				}

				// if existingAccessToken == "" {

				// }

				slog.Info("Loading stored token", "context", inFilterLogCtx, "trace_id", traceID, "host", host)
				existingAccessToken, err := s.loadStoredToken(ctx, headers, traceID, appSpec.UrlHost, appSpec.Type, &toolName)
				if err != nil {
					return s.deny(), nil
				}

				if existingAccessToken == "" {
					return s.deny(), nil
				}

				slog.Info("Validating tool call", "tool", toolName, "context", inFilterLogCtx, "trace_id", traceID, "host", host)

				return s.validateToken(ctx, existingAccessToken, []string{toolName}, traceID)
			}
		}
	}

	slog.Info("Call allowed", "context", outFilterLogCtx)
	return s.allow(), nil
}

func (s *InboundExtAuthService) loadStoredToken(
	ctx context.Context,
	headers map[string]string,
	traceID, appHost string,
	appType authapi.AppType,
	tool *string,
) (string, error) {
	// Check first in the headers
	if authHeader, ok := headers["authorization"]; ok {
		if strings.HasPrefix(authHeader, "Bearer ") {
			slog.Info("Found access token in HTTP header", "context", inFilterLogCtx, "trace_id", traceID, "host", appHost)
			return strings.Replace(authHeader, "Bearer ", "", -1), nil
		}
	}

	// Get it from the cache
	storedToken, err := s.authSrvClient.LoadTokenFromCache(ctx, s.namespace, traceID, appHost, appType, tool)
	if err != nil {
		slog.Error(fmt.Sprintf("Unable to fetch cached tokens for host %s with trace id %s", appHost, traceID), "err", err)
		return "", fmt.Errorf("inbound: unable to fetch cached tokens for host %s with trace id %s: %w", appHost, traceID, err)
	}

	if storedToken != nil && storedToken.AccessToken != "" {
		slog.Info(fmt.Sprintf("Found cached token for host %s with trace id %s", appHost, traceID))
		return storedToken.AccessToken, nil
	}

	return "", nil
}

func (s *InboundExtAuthService) validateToken(ctx context.Context, token string, tools []string, traceID string) (*authv3.CheckResponse, error) {
	introspectResp, err := s.authSrvClient.Introspect(ctx, token, tools)
	if err != nil {
		slog.Error("Failed to call token introspection endpoint", "err", err, "context", inFilterLogCtx, "trace_id", traceID, "tools", tools)
		// return nil, fmt.Errorf("inbound: unable to call token introspection endpoint: %w", err)
		slog.Info("Call denied", "context", inFilterLogCtx, "trace_id", traceID, "tools", tools)
		return s.deny(), nil
	}

	if introspectResp == nil || !introspectResp.Active {
		slog.Info("Call denied, token not active", "context", inFilterLogCtx, "trace_id", traceID, "tools", tools)
		return s.deny(), nil
	}

	slog.Info("Call allowed", "context", inFilterLogCtx, "trace_id", traceID, "tools", tools)
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
