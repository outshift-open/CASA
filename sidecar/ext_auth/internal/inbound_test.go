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

package internal_test

import (
	"fmt"
	"testing"

	identitysdk "github.com/outshift-open/CASA/sdk/go"
	"github.com/outshift-open/CASA/sidecar/ext_auth/internal"
	"github.com/outshift-open/CASA/sidecar/ext_auth/internal/mocks"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc/codes"
)

func TestInboundCheck_should_generate_token_for_agent(t *testing.T) {
	t.Parallel()

	host := uuid.NewString()
	namespace := uuid.NewString()
	appID := uuid.NewString()
	traceID := "4bf92f3577b34da6a3ce929d0e0e4736"
	accessToken := uuid.NewString()
	pfJsonPath := "{.content}"
	clientCreds := &internal.AppClientCredential{
		ClientID:     uuid.NewString(),
		ClientSecret: uuid.NewString(),
	}
	userInputID := uuid.NewString()
	prompt := uuid.NewString()

	authSrvClient := mocks.NewAuthServerClient(t)
	authSrvClient.EXPECT().
		GetK8SMultiAgentSystemByAppHost(t.Context(), namespace, host).
		Return(&identitysdk.K8sMultiAgentSystemCRDViewModel{
			Namespace: namespace,
			AppSpecs: []identitysdk.K8sAppSpecViewModel{
				{
					Type:                identitysdk.AGENT,
					UrlHost:             host,
					AppId:               *identitysdk.NewNullableString(&appID),
					PromptFieldJsonPath: *identitysdk.NewNullableString(&pfJsonPath),
				},
			},
		}, nil)
	authSrvClient.EXPECT().
		LoadTokenFromCache(t.Context(), namespace, traceID, host, identitysdk.AGENT, mock.Anything).
		Return(nil, nil)
	authSrvClient.EXPECT().
		Token(t.Context(), appID, clientCreds.ClientID, clientCreds.ClientSecret, userInputID).
		Return(accessToken, nil)
	authSrvClient.EXPECT().CreateUserInput(t.Context(), appID, prompt, traceID).Return(userInputID, nil)
	authSrvClient.EXPECT().
		StoreTokenInCache(t.Context(), namespace, traceID, host, identitysdk.AGENT, accessToken, mock.Anything).
		Return(nil)

	k8sSrv := mocks.NewKubernetesService(t)
	k8sSrv.EXPECT().
		GetAppCredentials(t.Context(), mock.Anything).
		Return(clientCreds, nil)

	sut := internal.NewInboundExtAuthService(namespace, authSrvClient, k8sSrv)

	resp, err := sut.Check(t.Context(), &authv3.CheckRequest{
		Attributes: &authv3.AttributeContext{
			Request: &authv3.AttributeContext_Request{
				Http: &authv3.AttributeContext_HttpRequest{
					Headers: map[string]string{
						"traceparent": fmt.Sprintf("00-%s-00f067aa0ba902b7-01", traceID),
					},
					Host: host,
					Body: fmt.Sprintf(`{"content": "%s"}`, prompt),
				},
			},
		},
	})

	assert.NoError(t, err)
	assert.Equal(t, int32(codes.OK), resp.Status.Code)
}

func TestInboundCheck_MCP(t *testing.T) {
	t.Parallel()

	host := uuid.NewString()
	appID := uuid.NewString()
	namespace := uuid.NewString()
	traceID := "4bf92f3577b34da6a3ce929d0e0e4736"
	accessToken := uuid.NewString()

	authSrvClient := mocks.NewAuthServerClient(t)
	authSrvClient.EXPECT().
		GetK8SMultiAgentSystemByAppHost(t.Context(), namespace, host).
		Return(&identitysdk.K8sMultiAgentSystemCRDViewModel{
			Namespace: namespace,
			AppSpecs: []identitysdk.K8sAppSpecViewModel{
				{
					Type:    identitysdk.MCP_SERVER,
					UrlHost: host,
					AppId:   *identitysdk.NewNullableString(&appID),
				},
			},
		}, nil)
	authSrvClient.EXPECT().
		LoadTokenFromCache(t.Context(), namespace, traceID, host, identitysdk.MCP_SERVER, mock.Anything).
		Return(&identitysdk.TokenResponse{AccessToken: accessToken}, nil)
	authSrvClient.EXPECT().
		Introspect(t.Context(), accessToken, mock.Anything).
		Return(&identitysdk.TokenIntrospectResponse{Active: true}, nil)

	sut := internal.NewInboundExtAuthService(namespace, authSrvClient, nil)

	resp, err := sut.Check(t.Context(), &authv3.CheckRequest{
		Attributes: &authv3.AttributeContext{
			Request: &authv3.AttributeContext_Request{
				Http: &authv3.AttributeContext_HttpRequest{
					Headers: map[string]string{
						"traceparent": fmt.Sprintf("00-%s-00f067aa0ba902b7-01", traceID),
					},
					Host: host,
					Body: `{"method":"tools/call","params":{"name":"schedule_payment","arguments":{"from_account":"Primary Checking","amount":10000.0,"frequency":"Monthly","next_date":"2025-11-20","payee":"Charlie","description":"Ad hoc payment"}},"jsonrpc":"2.0","id":1}`,
				},
			},
		},
	})

	assert.NoError(t, err)
	assert.Equal(t, int32(codes.OK), resp.Status.Code)
}
