# \TracesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetTracesTraceGet**](TracesAPI.md#GetTracesTraceGet) | **Get** /trace | Get Traces
[**TraceLlmCallEnd**](TracesAPI.md#TraceLlmCallEnd) | **Post** /trace/llm/call_end | Trace Llm Call End
[**TraceLlmCallStart**](TracesAPI.md#TraceLlmCallStart) | **Post** /trace/llm/call_start | Trace Llm Call Start



## GetTracesTraceGet

> interface{} GetTracesTraceGet(ctx).Page(page).PageSize(pageSize).MasId(masId).All(all).Execute()

Get Traces



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
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 20)
	masId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |  (optional)
	all := true // bool |  (optional) (default to false)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TracesAPI.GetTracesTraceGet(context.Background()).Page(page).PageSize(pageSize).MasId(masId).All(all).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TracesAPI.GetTracesTraceGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetTracesTraceGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TracesAPI.GetTracesTraceGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetTracesTraceGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 20]
 **masId** | **string** |  | 
 **all** | **bool** |  | [default to false]

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


## TraceLlmCallEnd

> LLMCallEndedEvent TraceLlmCallEnd(ctx).LLMCallEndedRequest(lLMCallEndedRequest).Execute()

Trace Llm Call End



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
	lLMCallEndedRequest := *openapiclient.NewLLMCallEndedRequest("CallId_example", "Response_example") // LLMCallEndedRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TracesAPI.TraceLlmCallEnd(context.Background()).LLMCallEndedRequest(lLMCallEndedRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TracesAPI.TraceLlmCallEnd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TraceLlmCallEnd`: LLMCallEndedEvent
	fmt.Fprintf(os.Stdout, "Response from `TracesAPI.TraceLlmCallEnd`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiTraceLlmCallEndRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lLMCallEndedRequest** | [**LLMCallEndedRequest**](LLMCallEndedRequest.md) |  | 

### Return type

[**LLMCallEndedEvent**](LLMCallEndedEvent.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TraceLlmCallStart

> LLMCallStartedEvent TraceLlmCallStart(ctx).LLMCallStartedRequest(lLMCallStartedRequest).Execute()

Trace Llm Call Start



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
	lLMCallStartedRequest := *openapiclient.NewLLMCallStartedRequest("CallId_example", "Prompt_example") // LLMCallStartedRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TracesAPI.TraceLlmCallStart(context.Background()).LLMCallStartedRequest(lLMCallStartedRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TracesAPI.TraceLlmCallStart``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TraceLlmCallStart`: LLMCallStartedEvent
	fmt.Fprintf(os.Stdout, "Response from `TracesAPI.TraceLlmCallStart`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiTraceLlmCallStartRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lLMCallStartedRequest** | [**LLMCallStartedRequest**](LLMCallStartedRequest.md) |  | 

### Return type

[**LLMCallStartedEvent**](LLMCallStartedEvent.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

