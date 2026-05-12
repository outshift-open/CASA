// Copyright 2026 Cisco Systems, Inc. and its affiliates
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
	"context"
	"encoding/base64"
	"encoding/hex"
	"errors"
	"fmt"
	"log/slog"
	"net/url"
	"slices"
	"strings"

	api "github.com/outshift-open/CASA/sdk/go"
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
	CheckCtxField = "context"
	CheckIdField  = "check_id"
	TraceIdField  = "trace_id"

	outCtxField = "OUTBOUND"
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
	checkID := uuid.NewString()

	if tpv, ok := headers[traceParentHeader]; ok {
		tp, err := ParseTraceParent(tpv)
		if err != nil {
			slog.Error("Failed to parse the traceparent header", CheckCtxField, outCtxField, "err", err, CheckIdField, checkID)
			return s.deny(), nil
		}

		traceID := hex.EncodeToString(tp.TraceID[:])
		host := httpReq.Host

		// TODO: this is not always reliable, x-envoy-peer-metadata could be configured to not be present
		peerMetadata, err := s.decodePeerMetadata(httpReq.Headers["x-envoy-peer-metadata"])
		if err != nil {
			slog.Error("Failed to decode peer metadata", CheckCtxField, outCtxField, TraceIdField, traceID, "err", err, CheckIdField, checkID)
			return s.deny(), nil
		}

		callerWorkloadName, found, err := unstructured.NestedString(peerMetadata, "WORKLOAD_NAME")
		if err != nil {
			slog.Error("Failed to get workload name from peer metadata", CheckCtxField, outCtxField, TraceIdField, traceID, "err", err, CheckIdField, checkID)
			return s.deny(), nil
		}

		if !found {
			slog.Error("No workload found in peer metadata", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
			return s.deny(), nil
		}

		slog.Info(fmt.Sprintf("Host = %s, caller workload name = %s", host, callerWorkloadName), CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)

		masCRD, err := s.authSrvClient.GetK8SMultiAgentSystemByWorkloadName(ctx, s.namespace, callerWorkloadName)
		if err != nil {
			slog.Error(
				fmt.Sprintf("Unable to get Kubernetes MultiAgentSystem resource for caller workload %s", callerWorkloadName),
				CheckCtxField, outCtxField,
				TraceIdField, traceID,
				"err", err,
				CheckIdField, checkID,
			)

			return s.deny(), nil
		}

		// Fetch CASAPolicy for the caller workload (nil = no policy configured, allow all)
		casaPolicy, err := s.authSrvClient.GetPolicyCRDByWorkload(ctx, s.namespace, callerWorkloadName)
		if err != nil {
			slog.Error("Failed to fetch CASAPolicy", CheckCtxField, outCtxField, TraceIdField, traceID, "workload", callerWorkloadName, "err", err, CheckIdField, checkID)
			return s.deny(), nil
		}

		if strings.EqualFold(host, masCRD.GetLlmHost()) {
			if casaPolicy != nil {
				llmEp := casaPolicy.Spec.LlmEndpoint.Get()
				if llmEp == nil {
					slog.Warn("CASAPolicy denies LLM call: no llmEndpoint configured", CheckCtxField, outCtxField, TraceIdField, traceID, "workload", callerWorkloadName, "host", host, CheckIdField, checkID)
					return s.deny(), nil
				}
				if !strings.EqualFold(host, llmEp.GetFqdn()) {
					slog.Warn("CASAPolicy denies LLM call: host not in llmEndpoint", CheckCtxField, outCtxField, TraceIdField, traceID, "workload", callerWorkloadName, "host", host, CheckIdField, checkID)
					return s.deny(), nil
				}
			}

			llmCallID := uuid.NewString()

			slog.Info(fmt.Sprintf("Generating x-litellm-call-id: %s", llmCallID), CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)

			callerToken, err := s.getCallerToken(ctx, masCRD, callerWorkloadName, traceID, checkID)
			if err != nil {
				return s.deny(), nil
			}

			_, err = s.authSrvClient.StoreLLMCallMapping(ctx, s.namespace, llmCallID, traceID, callerToken)
			if err != nil {
				return s.deny(), nil
			}

			return s.allowWithHeaders(map[string]string{"x-litellm-call-id": llmCallID}), nil
		}

		for _, appSpec := range masCRD.AppSpecs {
			if !strings.EqualFold(host, appSpec.UrlHost) {
				continue
			}

			if casaPolicy != nil {
				if err := checkCASAPolicy(casaPolicy, host, appSpec.GetType()); err != nil {
					slog.Warn("CASAPolicy denied outbound request", CheckCtxField, outCtxField, TraceIdField, traceID, "workload", callerWorkloadName, "host", host, "reason", err, CheckIdField, checkID)
					return s.deny(), nil
				}
			}

			var err error
			var accessToken string
			var associatedTool *string

			if appSpec.GetType() == api.AGENT {
				callerToken, err := s.getCallerToken(ctx, masCRD, callerWorkloadName, traceID, checkID)
				if err != nil {
					return s.deny(), nil
				}

				clientCreds, err := s.getClientCredentials(ctx, appSpec.GetAppId())
				if err != nil {
					return s.deny(), nil
				}

				if clientCreds == nil {
					slog.Info("Call denied, no client credentials found", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
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
					slog.Error("ExchangeToken failed", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID, "err", err)
					return s.deny(), nil
				}

				if accessToken == "" {
					slog.Info("Call defnied, access token is empty after token exchange [agent->agent]", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
					return s.deny(), nil
				}

				return s.allow(accessToken), nil
			} else if appSpec.GetType() == api.MCP_SERVER {
				slog.Info("Checking MCP server call", CheckCtxField, outCtxField, TraceIdField, traceID, "host", host, "method", httpReq.Method, "path", httpReq.Path, CheckIdField, checkID)
				if httpReq.Body == "" {
					return s.allow(""), nil
				}

				toolName, err := GetMCPToolFromRequest(httpReq.Body)
				if err != nil {
					slog.Error("Failed to get MCP tool name from request", "err", err, CheckIdField, checkID)
					return s.deny(), nil
				}

				if toolName == "" {
					slog.Info("Call allowed, tool name is empty", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
					return s.allow(""), nil
				}

				slog.Info("Found tool name", "tool_name", toolName, CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)

				callerToken, err := s.getCallerToken(ctx, masCRD, callerWorkloadName, traceID, checkID)
				if err != nil {
					return s.deny(), nil
				}

				mcpURL, err := url.Parse(fmt.Sprintf("%s://%s/mcp", appSpec.UrlScheme, appSpec.UrlHost))
				if err != nil {
					slog.Error("Failed to construct MCP server URL", CheckCtxField, outCtxField, TraceIdField, traceID, "err", err, CheckIdField, checkID)
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
					slog.Error("ExchangeToken failed", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID, "tool", toolName, "err", err)
					return s.deny(), nil
				}

				if accessToken == "" {
					slog.Info("Call defnied, access token is empty after token exchange [agent->MCP]", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
					return s.deny(), nil
				}

				associatedTool = &toolName
			}

			if accessToken != "" {
				slog.Info("Access token generated with token exchange", "token", accessToken, CheckIdField, checkID)

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

				slog.Info("Call allowed", CheckCtxField, outCtxField, TraceIdField, traceID, "tool_name", associatedTool, CheckIdField, checkID)
				return s.allow(accessToken), nil
			}
		}
	}

	slog.Info("Call allowed", CheckCtxField, outCtxField, CheckIdField, checkID)
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

func (s *OutboundExtAuthService) getCallerToken(
	ctx context.Context,
	masCRD *api.K8sMultiAgentSystemCRDViewModel,
	callerWorkloadName, traceID, checkID string,
) (string, error) {
	for _, appSpec := range masCRD.AppSpecs {
		slog.Info("Matching caller app", CheckCtxField, outCtxField, TraceIdField, traceID, "src_workload", callerWorkloadName, "workload", appSpec.GetKubernetesWorkloadName(), CheckIdField, checkID)
		if !strings.EqualFold(callerWorkloadName, appSpec.GetKubernetesWorkloadName()) {
			continue
		}

		token, err := s.authSrvClient.LoadTokenFromCache(ctx, s.namespace, traceID, appSpec.UrlHost, appSpec.Type, nil)
		if err != nil {
			slog.Error(fmt.Sprintf("Unable to fetch cached tokens for host %s with trace id %s", appSpec.UrlHost, traceID), "err", err, CheckIdField, checkID)
			return "", err
		}

		if token == nil || token.AccessToken == "" {
			slog.Info("Call denied, no access token found", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
			return "", errors.New("no access token found")
		}

		slog.Info(
			"Found cached access token",
			CheckCtxField,
			outCtxField,
			TraceIdField,
			traceID,
			"workload",
			appSpec.GetKubernetesWorkloadName(),
			"token",
			token.AccessToken,
			CheckIdField, checkID,
		)

		return token.AccessToken, nil
	}

	slog.Info("Call denied, no caller workload found", CheckCtxField, outCtxField, TraceIdField, traceID, CheckIdField, checkID)
	return "", errors.New("no caller workload found")
}

// checkCASAPolicy verifies that the outbound call is permitted by the caller's CASAPolicy.
// It checks that the destination host is in allowedEndpoints and the required protocol is in allowedProtocols.
func checkCASAPolicy(policy *api.CASAPolicyCRD, host string, appType api.AppType) error {
	// Map Envoy app type to CASAPolicy protocol string
	var requiredProtocol string
	switch appType {
	case api.MCP_SERVER:
		requiredProtocol = "mcp"
	case api.AGENT:
		requiredProtocol = "a2a"
	}

	if requiredProtocol != "" && !slices.Contains(policy.Spec.GetAllowedProtocols(), requiredProtocol) {
		return fmt.Errorf("protocol %q not in allowedProtocols %v", requiredProtocol, policy.Spec.GetAllowedProtocols())
	}

	// host may include port (e.g. "casa-demo-mcp:3000"); strip port for FQDN comparison
	hostWithoutPort := strings.SplitN(host, ":", 2)[0]
	for _, ep := range policy.Spec.GetAllowedEndpoints() {
		fqdn := fmt.Sprintf("%s.%s.svc.cluster.local", ep.GetName(), ep.GetNamespace())
		if strings.EqualFold(hostWithoutPort, fqdn) || strings.EqualFold(hostWithoutPort, ep.GetName()) {
			return nil
		}
	}
	return fmt.Errorf("host %q not in allowedEndpoints", host)
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
