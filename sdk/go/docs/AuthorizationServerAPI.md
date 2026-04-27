# \AuthorizationServerAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AppMetadata**](AuthorizationServerAPI.md#AppMetadata) | **Get** /{app_id}/oauth2/client-metadata.json | App Metadata
[**HealthCheckHealthGet**](AuthorizationServerAPI.md#HealthCheckHealthGet) | **Get** /health | Health Check
[**Introspect**](AuthorizationServerAPI.md#Introspect) | **Post** /oauth2/introspect | Introspect
[**Token**](AuthorizationServerAPI.md#Token) | **Post** /{app_id}/oauth2/token | Token
[**TokenExchange**](AuthorizationServerAPI.md#TokenExchange) | **Post** /{app_id}/oauth2/token_exchange | Token Exchange



## AppMetadata

> AppMetadataResponse AppMetadata(ctx, appId).Execute()

App Metadata



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/identity-auth-server/sdk/go"
)

func main() {
	appId := "appId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationServerAPI.AppMetadata(context.Background(), appId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationServerAPI.AppMetadata``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AppMetadata`: AppMetadataResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationServerAPI.AppMetadata`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiAppMetadataRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**AppMetadataResponse**](AppMetadataResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## HealthCheckHealthGet

> map[string]interface{} HealthCheckHealthGet(ctx).Execute()

Health Check



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/identity-auth-server/sdk/go"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationServerAPI.HealthCheckHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationServerAPI.HealthCheckHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `HealthCheckHealthGet`: map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationServerAPI.HealthCheckHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiHealthCheckHealthGetRequest struct via the builder pattern


### Return type

**map[string]interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## Introspect

> TokenIntrospectResponse Introspect(ctx).Token(token).Tools(tools).Execute()

Introspect



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/identity-auth-server/sdk/go"
)

func main() {
	token := "token_example" // string | 
	tools := []string{"Inner_example"} // []string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationServerAPI.Introspect(context.Background()).Token(token).Tools(tools).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationServerAPI.Introspect``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `Introspect`: TokenIntrospectResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationServerAPI.Introspect`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiIntrospectRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **string** |  | 
 **tools** | **[]string** |  | 

### Return type

[**TokenIntrospectResponse**](TokenIntrospectResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/x-www-form-urlencoded
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## Token

> TokenResponse Token(ctx, appId).ClientId(clientId).ClientSecret(clientSecret).UserInput(userInput).UserInputId(userInputId).Execute()

Token



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/identity-auth-server/sdk/go"
)

func main() {
	appId := "appId_example" // string | 
	clientId := "clientId_example" // string | 
	clientSecret := "clientSecret_example" // string | 
	userInput := "userInput_example" // string |  (optional)
	userInputId := "userInputId_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationServerAPI.Token(context.Background(), appId).ClientId(clientId).ClientSecret(clientSecret).UserInput(userInput).UserInputId(userInputId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationServerAPI.Token``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `Token`: TokenResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationServerAPI.Token`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **clientId** | **string** |  | 
 **clientSecret** | **string** |  | 
 **userInput** | **string** |  | 
 **userInputId** | **string** |  | 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/x-www-form-urlencoded
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TokenExchange

> TokenResponse TokenExchange(ctx, appId).ClientId(clientId).ClientSecret(clientSecret).SubjectToken(subjectToken).SubjectTokenType(subjectTokenType).Scope(scope).McpServerUrl(mcpServerUrl).Tools(tools).Execute()

Token Exchange



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/identity-auth-server/sdk/go"
)

func main() {
	appId := "appId_example" // string | 
	clientId := "clientId_example" // string | 
	clientSecret := "clientSecret_example" // string | 
	subjectToken := "subjectToken_example" // string | 
	subjectTokenType := "subjectTokenType_example" // string | 
	scope := "scope_example" // string |  (optional)
	mcpServerUrl := "mcpServerUrl_example" // string |  (optional)
	tools := []string{"Inner_example"} // []string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationServerAPI.TokenExchange(context.Background(), appId).ClientId(clientId).ClientSecret(clientSecret).SubjectToken(subjectToken).SubjectTokenType(subjectTokenType).Scope(scope).McpServerUrl(mcpServerUrl).Tools(tools).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationServerAPI.TokenExchange``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TokenExchange`: TokenResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationServerAPI.TokenExchange`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTokenExchangeRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **clientId** | **string** |  | 
 **clientSecret** | **string** |  | 
 **subjectToken** | **string** |  | 
 **subjectTokenType** | **string** |  | 
 **scope** | **string** |  | 
 **mcpServerUrl** | **string** |  | 
 **tools** | **[]string** |  | 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/x-www-form-urlencoded
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

