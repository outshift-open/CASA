package internal_test

import (
	"fmt"
	"testing"

	identitysdk "github.com/cisco-eti/identity-auth-server/sdk/go"
	"github.com/cisco-eti/identity-auth-server/sidecar/ext_auth/internal"
	"github.com/cisco-eti/identity-auth-server/sidecar/ext_auth/internal/mocks"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc/codes"
)

func TestOutbound(t *testing.T) {
	t.Parallel()

	agentAppHost := uuid.NewString()
	mcpHost := uuid.NewString()
	namespace := uuid.NewString()
	traceID := "4bf92f3577b34da6a3ce929d0e0e4736"
	agentAppID := uuid.NewString()
	mcpAppID := uuid.NewString()
	agentAccessToken := uuid.NewString()
	mcpAccessToken := uuid.NewString()
	agentWorkloadName := "zta-demo-agent"

	authSrvClient := mocks.NewAuthServerClient(t)
	authSrvClient.EXPECT().
		GetK8SMultiAgentSystemByAppHost(t.Context(), namespace, mock.Anything).
		Return(&identitysdk.K8sMultiAgentSystemCRDViewModel{
			Namespace: namespace,
			AppSpecs: []identitysdk.K8sAppSpecViewModel{
				{
					Type:                   identitysdk.AGENT,
					UrlHost:                agentAppHost,
					UrlScheme:              "http",
					AppId:                  *identitysdk.NewNullableString(&agentAppID),
					KubernetesWorkloadName: *identitysdk.NewNullableString(&agentWorkloadName),
				},
				{
					Type:      identitysdk.MCP_SERVER,
					UrlHost:   mcpHost,
					UrlScheme: "http",
					AppId:     *identitysdk.NewNullableString(&mcpAppID),
				},
			},
		}, nil)
	authSrvClient.EXPECT().
		LoadTokenFromCache(t.Context(), namespace, traceID, agentAppHost, identitysdk.AGENT, mock.Anything).
		Return(&identitysdk.TokenResponse{
			AccessToken: agentAccessToken,
		}, nil)
	authSrvClient.EXPECT().
		ExchangeToken(t.Context(), mcpAppID, mock.Anything, mock.Anything, agentAccessToken, fmt.Sprintf("http://%s/mcp", mcpHost), mock.Anything).
		Return(mcpAccessToken, nil)
	authSrvClient.EXPECT().StoreTokenInCache(t.Context(), namespace, traceID, mcpHost, identitysdk.MCP_SERVER, mcpAccessToken, mock.Anything).Return(nil)

	k8sSrv := mocks.NewKubernetesService(t)
	k8sSrv.EXPECT().
		GetAppCredentials(t.Context(), mock.Anything).
		Return(&internal.AppClientCredential{
			ClientID:     uuid.NewString(),
			ClientSecret: uuid.NewString(),
		}, nil)

	sut := internal.NewOutboundExtAuthService(namespace, authSrvClient, k8sSrv)

	resp, err := sut.Check(t.Context(), &authv3.CheckRequest{
		Attributes: &authv3.AttributeContext{
			Request: &authv3.AttributeContext_Request{
				Http: &authv3.AttributeContext_HttpRequest{
					Headers: map[string]string{
						"traceparent":           fmt.Sprintf("00-%s-00f067aa0ba902b7-01", traceID),
						"x-envoy-peer-metadata": "ChoKCkNMVVNURVJfSUQSDBoKS3ViZXJuZXRlcwqMAQoGTEFCRUxTEoEBKn8KFwoDYXBwEhAaDnp0YS1kZW1vLWFnZW50CjMKH3NlcnZpY2UuaXN0aW8uaW8vY2Fub25pY2FsLW5hbWUSEBoOenRhLWRlbW8tYWdlbnQKLwojc2VydmljZS5pc3Rpby5pby9jYW5vbmljYWwtcmV2aXNpb24SCBoGbGF0ZXN0CikKBE5BTUUSIRofenRhLWRlbW8tYWdlbnQtNTVjOWM2ZDk1Ny1zNWZncwoaCglOQU1FU1BBQ0USDRoLenRhLXNpZGVjYXIKVgoFT1dORVISTRpLa3ViZXJuZXRlczovL2FwaXMvYXBwcy92MS9uYW1lc3BhY2VzL3p0YS1zaWRlY2FyL2RlcGxveW1lbnRzL3p0YS1kZW1vLWFnZW50CiEKDVdPUktMT0FEX05BTUUSEBoOenRhLWRlbW8tYWdlbnQ=",
					},
					Host: mcpHost,
					Body: `{"method":"tools/call","params":{"name":"schedule_payment","arguments":{"from_account":"Primary Checking","amount":10000.0,"frequency":"Monthly","next_date":"2025-11-20","payee":"Charlie","description":"Ad hoc payment"}},"jsonrpc":"2.0","id":1}`,
				},
			},
		},
	})

	assert.NoError(t, err)
	assert.Equal(t, int32(codes.OK), resp.Status.Code)
}
