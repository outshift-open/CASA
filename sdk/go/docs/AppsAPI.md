# \AppsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateAppAppsPost**](AppsAPI.md#CreateAppAppsPost) | **Post** /apps | Create App
[**DeleteAppAppsAppIdDelete**](AppsAPI.md#DeleteAppAppsAppIdDelete) | **Delete** /apps/{app_id} | Delete App
[**GetAppAppsAppIdGet**](AppsAPI.md#GetAppAppsAppIdGet) | **Get** /apps/{app_id} | Get App
[**GetAppsAppsGet**](AppsAPI.md#GetAppsAppsGet) | **Get** /apps | Get Apps
[**UpdateAppAppsAppIdPut**](AppsAPI.md#UpdateAppAppsAppIdPut) | **Put** /apps/{app_id} | Update App



## CreateAppAppsPost

> AppViewModel CreateAppAppsPost(ctx).AppRequest(appRequest).Execute()

Create App



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
	appRequest := *openapiclient.NewAppRequest(openapiclient.AppType("agent"), "Name_example", "BaseUrl_example", "MasId_example") // AppRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.CreateAppAppsPost(context.Background()).AppRequest(appRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.CreateAppAppsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAppAppsPost`: AppViewModel
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.CreateAppAppsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAppAppsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **appRequest** | [**AppRequest**](AppRequest.md) |  | 

### Return type

[**AppViewModel**](AppViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteAppAppsAppIdDelete

> map[string]interface{} DeleteAppAppsAppIdDelete(ctx, appId).Execute()

Delete App



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
	resp, r, err := apiClient.AppsAPI.DeleteAppAppsAppIdDelete(context.Background(), appId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.DeleteAppAppsAppIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteAppAppsAppIdDelete`: map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.DeleteAppAppsAppIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteAppAppsAppIdDeleteRequest struct via the builder pattern


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


## GetAppAppsAppIdGet

> AppViewModel GetAppAppsAppIdGet(ctx, appId).Execute()

Get App



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
	resp, r, err := apiClient.AppsAPI.GetAppAppsAppIdGet(context.Background(), appId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.GetAppAppsAppIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAppAppsAppIdGet`: AppViewModel
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.GetAppAppsAppIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetAppAppsAppIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**AppViewModel**](AppViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAppsAppsGet

> []AppViewModel GetAppsAppsGet(ctx).Execute()

Get Apps



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
	resp, r, err := apiClient.AppsAPI.GetAppsAppsGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.GetAppsAppsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAppsAppsGet`: []AppViewModel
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.GetAppsAppsGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAppsAppsGetRequest struct via the builder pattern


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


## UpdateAppAppsAppIdPut

> AppViewModel UpdateAppAppsAppIdPut(ctx, appId).AppRequest(appRequest).Execute()

Update App



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
	appRequest := *openapiclient.NewAppRequest(openapiclient.AppType("agent"), "Name_example", "BaseUrl_example", "MasId_example") // AppRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.UpdateAppAppsAppIdPut(context.Background(), appId).AppRequest(appRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.UpdateAppAppsAppIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateAppAppsAppIdPut`: AppViewModel
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.UpdateAppAppsAppIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**appId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateAppAppsAppIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **appRequest** | [**AppRequest**](AppRequest.md) |  | 

### Return type

[**AppViewModel**](AppViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

