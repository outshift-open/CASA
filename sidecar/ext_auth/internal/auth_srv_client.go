package internal

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"

	identitysdk "github.com/cisco-eti/identity-auth-server/sdk/go"
)

type AuthServerClient interface {
	GetK8SMultiAgentSystemByAppHost(ctx context.Context, namespace, appHost string) (*identitysdk.K8sMultiAgentSystemCRDViewModel, error)
	GetK8SMultiAgentSystemByWorkloadName(ctx context.Context, namespace, appWorkload string) (*identitysdk.K8sMultiAgentSystemCRDViewModel, error)
	LoadTokenFromCache(ctx context.Context, namespace, traceID, appHost string, appType identitysdk.AppType, tool *string) (*identitysdk.TokenResponse, error)
	StoreTokenInCache(ctx context.Context, namespace, traceID, appHost string, appType identitysdk.AppType, token string, tool *string) error
	CreateUserInput(ctx context.Context, appID, prompt, tag string) (string, error)
	Token(ctx context.Context, appID, clientID, clientSecret, userInputID string) (string, error)
	ExchangeToken(ctx context.Context, appID, clientID, clientSecret, subjectToken, mcpServerURL string, tools []string) (string, error)
	Introspect(ctx context.Context, token string, tools []string) (*identitysdk.TokenIntrospectResponse, error)
	StoreLLMCallMapping(ctx context.Context, namespace, callID, traceID, token string) (*identitysdk.K8sLlmCallMapping, error)
}

type authServerClient struct {
	authSrvClient *identitysdk.APIClient
}

func NewAuthServerClient(authSrvClient *identitysdk.APIClient) AuthServerClient {
	return &authServerClient{
		authSrvClient: authSrvClient,
	}
}

func (c *authServerClient) GetK8SMultiAgentSystemByAppHost(
	ctx context.Context,
	namespace string,
	appHost string,
) (*identitysdk.K8sMultiAgentSystemCRDViewModel, error) {
	resp, r, err := c.authSrvClient.KubernetesResourcesAPI.GetK8sMasByAppHost(ctx, namespace).AppHost(appHost).Execute()
	if err != nil {
		c.logError("Error calling `KubernetesResourcesAPI.GetK8sMasByAppHost`", err, r)
		return nil, fmt.Errorf("unable to fetch K8S MAS: %w", err)
	}

	return resp, nil
}

func (c *authServerClient) GetK8SMultiAgentSystemByWorkloadName(
	ctx context.Context,
	namespace string,
	appWorkload string,
) (*identitysdk.K8sMultiAgentSystemCRDViewModel, error) {
	resp, r, err := c.authSrvClient.KubernetesResourcesAPI.GetK8sMasByAppWorkload(ctx, namespace).AppWorkload(appWorkload).Execute()
	if err != nil {
		c.logError("Error calling `KubernetesResourcesAPI.GetK8SMultiAgentSystemByWorkloadName`", err, r)
		return nil, fmt.Errorf("unable to fetch K8S MAS: %w", err)
	}

	return resp, nil
}

func (c *authServerClient) LoadTokenFromCache(
	ctx context.Context,
	namespace string,
	traceID string,
	appHost string,
	appType identitysdk.AppType,
	tool *string,
) (*identitysdk.TokenResponse, error) {
	resp, r, err := c.authSrvClient.KubernetesResourcesAPI.
		CacheLoadToken(ctx, namespace).
		CacheTokenLoadRequest(identitysdk.CacheTokenLoadRequest{
			TraceId: traceID,
			AppHost: appHost,
			AppType: appType,
			Tool:    *identitysdk.NewNullableString(tool),
		}).
		Execute()
	if err != nil {
		if r != nil && r.StatusCode == http.StatusNotFound {
			return nil, nil
		}

		c.logError("Error when calling `KubernetesResourcesAPI.LoadTokenFromCache`", err, r)
		return nil, fmt.Errorf("unable to load cached token: %w", err)
	}

	return resp, nil
}

func (c *authServerClient) StoreTokenInCache(
	ctx context.Context,
	namespace string,
	traceID string,
	appHost string,
	appType identitysdk.AppType,
	token string,
	tool *string,
) error {
	_, r, err := c.authSrvClient.KubernetesResourcesAPI.
		CacheStoreToken(ctx, namespace).
		CacheTokenStoreRequest(identitysdk.CacheTokenStoreRequest{
			TraceId:     traceID,
			AppHost:     appHost,
			AppType:     appType,
			AccessToken: token,
			Tool:        *identitysdk.NewNullableString(tool),
		}).
		Execute()
	if err != nil {
		c.logError("Error when calling `KubernetesResourcesAPI.StoreTokenInCache`", err, r)
		return fmt.Errorf("unable to store token in cache: %w", err)
	}

	return nil
}

func (c *authServerClient) CreateUserInput(ctx context.Context, appID, prompt, tag string) (string, error) {
	resp, r, err := c.authSrvClient.UserInputsAPI.
		CreateUserInput(ctx).
		CreateUserInputRequest(identitysdk.CreateUserInputRequest{
			AppId:  appID,
			Prompt: prompt,
			Tag:    *identitysdk.NewNullableString(&tag),
		}).
		Execute()
	if err != nil {
		c.logError("Error when calling `UserInputsAPI.CreateUserInput`", err, r)
		return "", fmt.Errorf("unable to create user input: %w", err)
	}

	return resp.GetId(), nil
}

func (c *authServerClient) Token(ctx context.Context, appID, clientID, clientSecret, userInputID string) (string, error) {
	resp, r, err := c.authSrvClient.AuthorizationServerAPI.Token(ctx, appID).
		ClientId(clientID).
		ClientSecret(clientSecret).
		UserInputId(userInputID).
		Execute()
	if err != nil {
		c.logError("Error when calling `AuthorizationServerAPI.Token`", err, r)
		return "", fmt.Errorf("unable to generate token: %w", err)
	}

	return resp.GetAccessToken(), nil
}

func (c *authServerClient) ExchangeToken(
	ctx context.Context,
	appID, clientID, clientSecret, subjectToken string,
	mcpServerURL string,
	tools []string,
) (string, error) {
	slog.Info("[TOKEN EXCHANGE]", "client_id", clientID, "client_secret", clientSecret, "subject_token", subjectToken, "mcp_server_url", mcpServerURL, "tools", tools)
	resp, r, err := c.authSrvClient.AuthorizationServerAPI.TokenExchange(ctx, appID).
		ClientId(clientID).
		ClientSecret(clientSecret).
		SubjectToken(subjectToken).
		SubjectTokenType("urn:ietf:params:oauth:token-type:access_token").
		McpServerUrl(mcpServerURL).
		Tools(tools).
		Execute()
	if err != nil {
		c.logError("Error when calling `AuthorizationServerAPI.TokenExchange`", err, r)
		return "", fmt.Errorf("unable to do token exchange: %w", err)
	}

	return resp.GetAccessToken(), nil
}

func (c *authServerClient) Introspect(ctx context.Context, token string, tools []string) (*identitysdk.TokenIntrospectResponse, error) {
	resp, r, err := c.authSrvClient.AuthorizationServerAPI.Introspect(ctx).Token(token).Tools(tools).Execute()
	if err != nil {
		c.logError("Error when calling `AuthorizationServerAPI.Introspect`", err, r)
		return nil, fmt.Errorf("unable to introspect the token: %w", err)
	}

	return resp, nil
}

func (c *authServerClient) StoreLLMCallMapping(
	ctx context.Context,
	namespace string,
	callID string,
	traceID string,
	token string,
) (*identitysdk.K8sLlmCallMapping, error) {
	resp, r, err := c.authSrvClient.KubernetesResourcesAPI.
		CacheStoreLlmCallMapping(ctx, namespace).
		LlmCallMappingStoreRequest(identitysdk.LlmCallMappingStoreRequest{
			Id:      callID,
			TraceId: traceID,
			Token:   token,
		}).
		Execute()
	if err != nil {
		c.logError("Error when calling `AuthorizationServerAPI.StoreLLMCallMapping`", err, r)
		return nil, fmt.Errorf("unable to store the LLM call mapping: %w", err)
	}

	return resp, nil
}

func (c *authServerClient) logError(msg string, err error, r *http.Response) {
	var statusCode int
	if r != nil {
		statusCode = r.StatusCode
	}

	slog.Error(msg, "err", err, "http.status", statusCode, "http.response", r)
}
