# \KubernetesResourcesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CacheLoadLlmCallMapping**](KubernetesResourcesAPI.md#CacheLoadLlmCallMapping) | **Get** /k8s/cache/load-llm-call-mapping/{call_id} | Load Llm Call Mapping
[**CacheLoadToken**](KubernetesResourcesAPI.md#CacheLoadToken) | **Post** /k8s/namespaces/{namespace}/cache/load-token | Load Token
[**CacheStoreLlmCallMapping**](KubernetesResourcesAPI.md#CacheStoreLlmCallMapping) | **Post** /k8s/namespaces/{namespace}/cache/store-llm-call-mapping | Store Llm Call Mapping
[**CacheStoreToken**](KubernetesResourcesAPI.md#CacheStoreToken) | **Post** /k8s/namespaces/{namespace}/cache/store-token | Store Token
[**GetK8sMasByAppHost**](KubernetesResourcesAPI.md#GetK8sMasByAppHost) | **Get** /k8s/namespaces/{namespace}/get_mas_by_app_host | Get K8S Mas By App Host
[**GetK8sMasByAppWorkload**](KubernetesResourcesAPI.md#GetK8sMasByAppWorkload) | **Get** /k8s/namespaces/{namespace}/get_mas_by_app_workload | Get K8S Mas By App Workload
[**K8sTraceLlmCallEnd**](KubernetesResourcesAPI.md#K8sTraceLlmCallEnd) | **Post** /k8s/trace/llm/call_end | K8S Trace Llm Call End



## CacheLoadLlmCallMapping

> K8sLlmCallMapping CacheLoadLlmCallMapping(ctx, callId).Execute()

Load Llm Call Mapping

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	callId := "callId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.CacheLoadLlmCallMapping(context.Background(), callId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.CacheLoadLlmCallMapping``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CacheLoadLlmCallMapping`: K8sLlmCallMapping
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.CacheLoadLlmCallMapping`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**callId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCacheLoadLlmCallMappingRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**K8sLlmCallMapping**](K8sLlmCallMapping.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CacheLoadToken

> TokenResponse CacheLoadToken(ctx, namespace).CacheTokenLoadRequest(cacheTokenLoadRequest).Execute()

Load Token

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	namespace := "namespace_example" // string | 
	cacheTokenLoadRequest := *openapiclient.NewCacheTokenLoadRequest("TraceId_example", "AppHost_example", openapiclient.AppType("agent")) // CacheTokenLoadRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.CacheLoadToken(context.Background(), namespace).CacheTokenLoadRequest(cacheTokenLoadRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.CacheLoadToken``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CacheLoadToken`: TokenResponse
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.CacheLoadToken`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCacheLoadTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cacheTokenLoadRequest** | [**CacheTokenLoadRequest**](CacheTokenLoadRequest.md) |  | 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CacheStoreLlmCallMapping

> K8sLlmCallMapping CacheStoreLlmCallMapping(ctx, namespace).LlmCallMappingStoreRequest(llmCallMappingStoreRequest).Execute()

Store Llm Call Mapping

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	namespace := "namespace_example" // string | 
	llmCallMappingStoreRequest := *openapiclient.NewLlmCallMappingStoreRequest("Id_example", "TraceId_example", "Token_example") // LlmCallMappingStoreRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.CacheStoreLlmCallMapping(context.Background(), namespace).LlmCallMappingStoreRequest(llmCallMappingStoreRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.CacheStoreLlmCallMapping``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CacheStoreLlmCallMapping`: K8sLlmCallMapping
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.CacheStoreLlmCallMapping`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCacheStoreLlmCallMappingRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **llmCallMappingStoreRequest** | [**LlmCallMappingStoreRequest**](LlmCallMappingStoreRequest.md) |  | 

### Return type

[**K8sLlmCallMapping**](K8sLlmCallMapping.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CacheStoreToken

> interface{} CacheStoreToken(ctx, namespace).CacheTokenStoreRequest(cacheTokenStoreRequest).Execute()

Store Token

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	namespace := "namespace_example" // string | 
	cacheTokenStoreRequest := *openapiclient.NewCacheTokenStoreRequest("TraceId_example", "AppHost_example", openapiclient.AppType("agent"), "AccessToken_example") // CacheTokenStoreRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.CacheStoreToken(context.Background(), namespace).CacheTokenStoreRequest(cacheTokenStoreRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.CacheStoreToken``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CacheStoreToken`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.CacheStoreToken`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCacheStoreTokenRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cacheTokenStoreRequest** | [**CacheTokenStoreRequest**](CacheTokenStoreRequest.md) |  | 

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetK8sMasByAppHost

> K8sMultiAgentSystemCRDViewModel GetK8sMasByAppHost(ctx, namespace).AppHost(appHost).Execute()

Get K8S Mas By App Host

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	namespace := "namespace_example" // string | 
	appHost := "appHost_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.GetK8sMasByAppHost(context.Background(), namespace).AppHost(appHost).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.GetK8sMasByAppHost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetK8sMasByAppHost`: K8sMultiAgentSystemCRDViewModel
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.GetK8sMasByAppHost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetK8sMasByAppHostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **appHost** | **string** |  | 

### Return type

[**K8sMultiAgentSystemCRDViewModel**](K8sMultiAgentSystemCRDViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetK8sMasByAppWorkload

> K8sMultiAgentSystemCRDViewModel GetK8sMasByAppWorkload(ctx, namespace).AppWorkload(appWorkload).Execute()

Get K8S Mas By App Workload

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	namespace := "namespace_example" // string | 
	appWorkload := "appWorkload_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.GetK8sMasByAppWorkload(context.Background(), namespace).AppWorkload(appWorkload).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.GetK8sMasByAppWorkload``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetK8sMasByAppWorkload`: K8sMultiAgentSystemCRDViewModel
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.GetK8sMasByAppWorkload`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetK8sMasByAppWorkloadRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **appWorkload** | **string** |  | 

### Return type

[**K8sMultiAgentSystemCRDViewModel**](K8sMultiAgentSystemCRDViewModel.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## K8sTraceLlmCallEnd

> LLMCallEndedEvent K8sTraceLlmCallEnd(ctx).LLMCallEndedKubernetesRequest(lLMCallEndedKubernetesRequest).Execute()

K8S Trace Llm Call End



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/outshift-open/CASA/sdk/go"
)

func main() {
	lLMCallEndedKubernetesRequest := *openapiclient.NewLLMCallEndedKubernetesRequest("CallId_example", "Response_example") // LLMCallEndedKubernetesRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesResourcesAPI.K8sTraceLlmCallEnd(context.Background()).LLMCallEndedKubernetesRequest(lLMCallEndedKubernetesRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesResourcesAPI.K8sTraceLlmCallEnd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `K8sTraceLlmCallEnd`: LLMCallEndedEvent
	fmt.Fprintf(os.Stdout, "Response from `KubernetesResourcesAPI.K8sTraceLlmCallEnd`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiK8sTraceLlmCallEndRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lLMCallEndedKubernetesRequest** | [**LLMCallEndedKubernetesRequest**](LLMCallEndedKubernetesRequest.md) |  | 

### Return type

[**LLMCallEndedEvent**](LLMCallEndedEvent.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

