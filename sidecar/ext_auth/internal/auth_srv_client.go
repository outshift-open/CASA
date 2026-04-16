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
	LoadTokenFromCache(ctx context.Context, namespace, traceID, appHost string, appType identitysdk.AppType, tool *string) (*identitysdk.TokenResponse, error)
	StoreTokenInCache(ctx context.Context, namespace, traceID, appHost string, appType identitysdk.AppType, token string, tool *string) error
	CreateUserInput(ctx context.Context, appID, prompt, tag string) (string, error)
	Token(ctx context.Context, appID, clientID, clientSecret, userInputID string) (string, error)
	ExchangeToken(ctx context.Context, appID, clientID, clientSecret, subjectToken, mcpServerURL string, tools []string) (string, error)
	Introspect(ctx context.Context, token string, tools []string) (*identitysdk.TokenIntrospectResponse, error)
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
	// TODO: KubernetesResourcesAPI.GetK8sMasByAppHost` err="3 is not a valid ToolCheckFlags"
	resp, r, err := c.authSrvClient.KubernetesResourcesAPI.GetK8sMasByAppHost(ctx, namespace).AppHost(appHost).Execute()
	if err != nil {
		slog.Error("Error calling `KubernetesResourcesAPI.GetK8sMasByAppHost`", "err", err, "http.response", r)
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
		if r.StatusCode == http.StatusNotFound {
			return nil, nil
		}

		slog.Error("Error when calling `KubernetesResourcesAPI.LoadTokenFromCache`", "err", err, "http.response", r)
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
		slog.Error("Error when calling `KubernetesResourcesAPI.StoreTokenInCache`", "err", err, "http.response", r)
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
		slog.Error("Error when calling `UserInputsAPI.CreateUserInput`", "err", err, "http.response", r)
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
		slog.Error("Error when calling `AuthorizationServerAPI.Token`", "err", err, "http.response", r)
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
	resp, r, err := c.authSrvClient.AuthorizationServerAPI.TokenExchange(ctx, appID).
		ClientId(clientID).
		ClientSecret(clientSecret).
		SubjectToken(subjectToken).
		SubjectTokenType("urn:ietf:params:oauth:token-type:access_token").
		McpServerUrl(mcpServerURL).
		Tools(tools).
		Execute()
	if err != nil {
		slog.Error("Error when calling `AuthorizationServerAPI.TokenExchange`", "err", err, "http.response", r)
		return "", fmt.Errorf("unable to do token exchange: %w", err)
	}

	return resp.GetAccessToken(), nil
}

func (c *authServerClient) Introspect(ctx context.Context, token string, tools []string) (*identitysdk.TokenIntrospectResponse, error) {
	resp, r, err := c.authSrvClient.AuthorizationServerAPI.Introspect(ctx).Token(token).Tools(tools).Execute()
	if err != nil {
		slog.Error("Error when calling `AuthorizationServerAPI.Introspect`", "err", err, "http.response", r)
		return nil, fmt.Errorf("unable to introspect the token: %w", err)
	}

	return resp, nil
}
