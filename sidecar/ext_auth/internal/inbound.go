// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package internal

import (
	"bytes"
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"strings"

	authapi "github.com/outshift-open/identity-auth-server/sdk/go"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"github.com/google/uuid"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc/codes"
	"k8s.io/client-go/util/jsonpath"
)

const (
	traceParentHeader = "traceparent"
	inCtxField        = "INBOUND"
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

	checkID := uuid.NewString()

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Failed to parse the traceparent header", CheckCtxField, inCtxField, "err", err, CheckIdField, checkID)

			return s.deny(), nil
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		host := httpReq.Host

		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByAppHost(ctx, s.namespace, host)
		if err != nil {
			slog.Error(
				fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for host %s", host),
				CheckCtxField,
				inCtxField,
				TraceIdField,
				traceID,
				"host",
				host,
				"err",
				err,
				CheckIdField,
				checkID,
			)

			return s.deny(), nil
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			// The app host must be configured correctly by the user for this to work
			switch appSpec.Type {
			case authapi.AGENT:
				slog.Info("Checking Agent call", CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)

				existingAccessToken, err := s.loadStoredToken(ctx, headers, traceID, appSpec.UrlHost, appSpec.Type, nil)
				if err != nil {
					return s.deny(), nil
				}

				if existingAccessToken != "" {
					slog.Info("Validating access token for Agent", CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)

					return s.validateToken(ctx, existingAccessToken, []string{}, traceID)
				}

				if appSpec.GetPromptFieldJsonPath() != "" {
					jp := jsonpath.New("")
					err := jp.Parse(appSpec.GetPromptFieldJsonPath())
					if err != nil {
						slog.Error("Error parsing the prompt JSON path", "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
						return s.deny(), nil
					}

					var body any
					err = json.Unmarshal([]byte(httpReq.Body), &body)
					if err != nil {
						slog.Error("Failed to unmarshal the HTTP request body", "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
						return s.deny(), nil
					}

					var buf bytes.Buffer
					err = jp.Execute(&buf, body)
					if err != nil {
						slog.Error("Failed to find the prompt using the JSON path", "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
						return s.deny(), nil
					}

					userInputID, err := s.authSrvClient.CreateUserInput(ctx, appSpec.GetAppId(), buf.String(), traceID)
					if err != nil {
						return s.deny(), nil
					}

					slog.Info(fmt.Sprintf("User input %s created for trace_id %s", userInputID, traceID), CheckIdField, checkID)

					clientCreds, err := s.k8sService.GetAppCredentials(ctx, appSpec.GetAppId())
					if err != nil {
						slog.Error(fmt.Sprintf("Failed to fetch client credentials for app %s", appSpec.GetAppId()), "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
						return s.deny(), nil
					}

					if clientCreds == nil {
						slog.Warn(fmt.Sprintf("No client credentials for app %s", appSpec.GetAppId()), CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
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
						return s.deny(), nil
					}

					slog.Info("Access token generated", "token", accessToken, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)

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
						return s.deny(), nil
					}

					return s.allow(), nil
				}
			case authapi.MCP_SERVER:
				slog.Info("Checking MCP server call", CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, "method", httpReq.Method, "path", httpReq.Path, CheckIdField, checkID)
				if httpReq.Body == "" {
					return s.allow(), nil
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)
					return s.deny(), nil
				}

				if toolName == "" {
					return s.allow(), nil
				}

				existingAccessToken, err := s.loadStoredToken(ctx, headers, traceID, appSpec.UrlHost, appSpec.Type, &toolName)
				if err != nil {
					return s.deny(), nil
				}

				if existingAccessToken == "" {
					return s.deny(), nil
				}

				slog.Info("Validating tool call", "tool", toolName, CheckCtxField, inCtxField, TraceIdField, traceID, "host", host, CheckIdField, checkID)

				return s.validateToken(ctx, existingAccessToken, []string{toolName}, traceID)
			}
		}
	}

	slog.Info("Call allowed", CheckCtxField, outCtxField, CheckIdField, checkID)
	return s.allow(), nil
}

func (s *InboundExtAuthService) loadStoredToken(
	ctx context.Context,
	headers map[string]string,
	traceID, appHost string,
	appType authapi.AppType,
	tool *string,
) (string, error) {
	slog.Info("Loading stored token", CheckCtxField, inCtxField, TraceIdField, traceID, "host", appHost, "tool", DerefStr(tool))

	// Check first in the headers
	if authHeader, ok := headers["authorization"]; ok {
		if strings.HasPrefix(authHeader, "Bearer ") {
			slog.Info("Found access token in HTTP header", CheckCtxField, inCtxField, TraceIdField, traceID, "host", appHost)
			return strings.ReplaceAll(authHeader, "Bearer ", ""), nil
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
		slog.Error("Failed to call token introspection endpoint", "err", err, CheckCtxField, inCtxField, TraceIdField, traceID, "tools", tools)

		return s.deny(), nil
	}

	if introspectResp == nil || !introspectResp.Active {
		slog.Info("Call denied, token not active", CheckCtxField, inCtxField, TraceIdField, traceID, "tools", tools)

		return s.deny(), nil
	}

	slog.Info("Call allowed", CheckCtxField, inCtxField, TraceIdField, traceID, "tools", tools)

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
