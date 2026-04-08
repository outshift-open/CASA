# \ScopesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateScopeScopesPost**](ScopesAPI.md#CreateScopeScopesPost) | **Post** /scopes | Create Scope
[**DeleteScopeScopesScopeIdDelete**](ScopesAPI.md#DeleteScopeScopesScopeIdDelete) | **Delete** /scopes/{scope_id} | Delete Scope
[**GetScopeScopesScopeIdGet**](ScopesAPI.md#GetScopeScopesScopeIdGet) | **Get** /scopes/{scope_id} | Get Scope
[**GetScopesScopesGet**](ScopesAPI.md#GetScopesScopesGet) | **Get** /scopes | Get Scopes
[**UpdateScopeScopesScopeIdPut**](ScopesAPI.md#UpdateScopeScopesScopeIdPut) | **Put** /scopes/{scope_id} | Update Scope



## CreateScopeScopesPost

> ScopeViewModel CreateScopeScopesPost(ctx).ScopeCreateRequest(scopeCreateRequest).Execute()

Create Scope



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/cisco-eti/identity-auth-server/sdk/go"
)

func main() {
	scopeCreateRequest := *openapiclient.NewScopeCreateRequest("Name_example", "MasId_example") // ScopeCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScopesAPI.CreateScopeScopesPost(context.Background()).ScopeCreateRequest(scopeCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScopesAPI.CreateScopeScopesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateScopeScopesPost`: ScopeViewModel
	fmt.Fprintf(os.Stdout, "Response from `ScopesAPI.CreateScopeScopesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateScopeScopesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scopeCreateRequest** | [**ScopeCreateRequest**](ScopeCreateRequest.md) |  | 

### Return type

[**ScopeViewModel**](ScopeViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteScopeScopesScopeIdDelete

> map[string]interface{} DeleteScopeScopesScopeIdDelete(ctx, scopeId).Execute()

Delete Scope



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/cisco-eti/identity-auth-server/sdk/go"
)

func main() {
	scopeId := "scopeId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScopesAPI.DeleteScopeScopesScopeIdDelete(context.Background(), scopeId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScopesAPI.DeleteScopeScopesScopeIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteScopeScopesScopeIdDelete`: map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `ScopesAPI.DeleteScopeScopesScopeIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**scopeId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteScopeScopesScopeIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


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


## GetScopeScopesScopeIdGet

> ScopeViewModel GetScopeScopesScopeIdGet(ctx, scopeId).Execute()

Get Scope



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/cisco-eti/identity-auth-server/sdk/go"
)

func main() {
	scopeId := "scopeId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScopesAPI.GetScopeScopesScopeIdGet(context.Background(), scopeId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScopesAPI.GetScopeScopesScopeIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetScopeScopesScopeIdGet`: ScopeViewModel
	fmt.Fprintf(os.Stdout, "Response from `ScopesAPI.GetScopeScopesScopeIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**scopeId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetScopeScopesScopeIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**ScopeViewModel**](ScopeViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetScopesScopesGet

> []ScopeViewModel GetScopesScopesGet(ctx).Execute()

Get Scopes



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/cisco-eti/identity-auth-server/sdk/go"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScopesAPI.GetScopesScopesGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScopesAPI.GetScopesScopesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetScopesScopesGet`: []ScopeViewModel
	fmt.Fprintf(os.Stdout, "Response from `ScopesAPI.GetScopesScopesGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetScopesScopesGetRequest struct via the builder pattern


### Return type

[**[]ScopeViewModel**](ScopeViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateScopeScopesScopeIdPut

> ScopeViewModel UpdateScopeScopesScopeIdPut(ctx, scopeId).ScopeUpdateRequest(scopeUpdateRequest).Execute()

Update Scope



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/cisco-eti/identity-auth-server/sdk/go"
)

func main() {
	scopeId := "scopeId_example" // string | 
	scopeUpdateRequest := *openapiclient.NewScopeUpdateRequest("Name_example") // ScopeUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScopesAPI.UpdateScopeScopesScopeIdPut(context.Background(), scopeId).ScopeUpdateRequest(scopeUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScopesAPI.UpdateScopeScopesScopeIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateScopeScopesScopeIdPut`: ScopeViewModel
	fmt.Fprintf(os.Stdout, "Response from `ScopesAPI.UpdateScopeScopesScopeIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**scopeId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateScopeScopesScopeIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **scopeUpdateRequest** | [**ScopeUpdateRequest**](ScopeUpdateRequest.md) |  | 

### Return type

[**ScopeViewModel**](ScopeViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

