# \MultiAgentSystemsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**BindAppsMasMasIdBindAppsPost**](MultiAgentSystemsAPI.md#BindAppsMasMasIdBindAppsPost) | **Post** /mas/{mas_id}/bind_apps | Bind Apps
[**CreateMasMasPut**](MultiAgentSystemsAPI.md#CreateMasMasPut) | **Put** /mas | Create Mas
[**DeleteMasMasMasIdDelete**](MultiAgentSystemsAPI.md#DeleteMasMasMasIdDelete) | **Delete** /mas/{mas_id} | Delete Mas
[**GetAllMasMasGet**](MultiAgentSystemsAPI.md#GetAllMasMasGet) | **Get** /mas | Get All Mas
[**GetMasAppsMasMasIdAppsGet**](MultiAgentSystemsAPI.md#GetMasAppsMasMasIdAppsGet) | **Get** /mas/{mas_id}/apps | Get Mas Apps
[**GetMasByIdMasMasIdGet**](MultiAgentSystemsAPI.md#GetMasByIdMasMasIdGet) | **Get** /mas/{mas_id} | Get Mas By Id
[**UpdateMasMasMasIdPost**](MultiAgentSystemsAPI.md#UpdateMasMasMasIdPost) | **Post** /mas/{mas_id} | Update Mas



## BindAppsMasMasIdBindAppsPost

> BindAppsMasMasIdBindAppsPost(ctx, masId).MultiAgentSystemAppsBindingRequest(multiAgentSystemAppsBindingRequest).Execute()

Bind Apps



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
	masId := "masId_example" // string | 
	multiAgentSystemAppsBindingRequest := *openapiclient.NewMultiAgentSystemAppsBindingRequest([]string{"AppIds_example"}) // MultiAgentSystemAppsBindingRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.MultiAgentSystemsAPI.BindAppsMasMasIdBindAppsPost(context.Background(), masId).MultiAgentSystemAppsBindingRequest(multiAgentSystemAppsBindingRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.BindAppsMasMasIdBindAppsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiBindAppsMasMasIdBindAppsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **multiAgentSystemAppsBindingRequest** | [**MultiAgentSystemAppsBindingRequest**](MultiAgentSystemAppsBindingRequest.md) |  | 

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateMasMasPut

> MultiAgentSystem CreateMasMasPut(ctx).MultiAgentSystemCreateRequest(multiAgentSystemCreateRequest).Execute()

Create Mas



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
	multiAgentSystemCreateRequest := *openapiclient.NewMultiAgentSystemCreateRequest("Name_example") // MultiAgentSystemCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiAgentSystemsAPI.CreateMasMasPut(context.Background()).MultiAgentSystemCreateRequest(multiAgentSystemCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.CreateMasMasPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateMasMasPut`: MultiAgentSystem
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.CreateMasMasPut`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateMasMasPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multiAgentSystemCreateRequest** | [**MultiAgentSystemCreateRequest**](MultiAgentSystemCreateRequest.md) |  | 

### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteMasMasMasIdDelete

> interface{} DeleteMasMasMasIdDelete(ctx, masId).Execute()

Delete Mas



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
	masId := "masId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiAgentSystemsAPI.DeleteMasMasMasIdDelete(context.Background(), masId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.DeleteMasMasMasIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteMasMasMasIdDelete`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.DeleteMasMasMasIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteMasMasMasIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAllMasMasGet

> []MultiAgentSystem GetAllMasMasGet(ctx).Execute()

Get All Mas



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
	resp, r, err := apiClient.MultiAgentSystemsAPI.GetAllMasMasGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.GetAllMasMasGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAllMasMasGet`: []MultiAgentSystem
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.GetAllMasMasGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAllMasMasGetRequest struct via the builder pattern


### Return type

[**[]MultiAgentSystem**](MultiAgentSystem.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetMasAppsMasMasIdAppsGet

> []AppViewModel GetMasAppsMasMasIdAppsGet(ctx, masId).Execute()

Get Mas Apps



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
	masId := "masId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiAgentSystemsAPI.GetMasAppsMasMasIdAppsGet(context.Background(), masId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.GetMasAppsMasMasIdAppsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetMasAppsMasMasIdAppsGet`: []AppViewModel
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.GetMasAppsMasMasIdAppsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetMasAppsMasMasIdAppsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**[]AppViewModel**](AppViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetMasByIdMasMasIdGet

> MultiAgentSystem GetMasByIdMasMasIdGet(ctx, masId).Execute()

Get Mas By Id



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
	masId := "masId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiAgentSystemsAPI.GetMasByIdMasMasIdGet(context.Background(), masId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.GetMasByIdMasMasIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetMasByIdMasMasIdGet`: MultiAgentSystem
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.GetMasByIdMasMasIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetMasByIdMasMasIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateMasMasMasIdPost

> MultiAgentSystem UpdateMasMasMasIdPost(ctx, masId).MultiAgentSystemUpdateRequest(multiAgentSystemUpdateRequest).Execute()

Update Mas



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
	masId := "masId_example" // string | 
	multiAgentSystemUpdateRequest := *openapiclient.NewMultiAgentSystemUpdateRequest("Name_example") // MultiAgentSystemUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiAgentSystemsAPI.UpdateMasMasMasIdPost(context.Background(), masId).MultiAgentSystemUpdateRequest(multiAgentSystemUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiAgentSystemsAPI.UpdateMasMasMasIdPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateMasMasMasIdPost`: MultiAgentSystem
	fmt.Fprintf(os.Stdout, "Response from `MultiAgentSystemsAPI.UpdateMasMasMasIdPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateMasMasMasIdPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **multiAgentSystemUpdateRequest** | [**MultiAgentSystemUpdateRequest**](MultiAgentSystemUpdateRequest.md) |  | 

### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

