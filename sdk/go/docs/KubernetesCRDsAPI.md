# \KubernetesCRDsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateMasCrd**](KubernetesCRDsAPI.md#CreateMasCrd) | **Post** /k8s/namespaces/{namespace}/mas | Create Mas Crd
[**CreatePolicyCrd**](KubernetesCRDsAPI.md#CreatePolicyCrd) | **Post** /k8s/namespaces/{namespace}/policies | Create Policy Crd
[**DeleteMasCrd**](KubernetesCRDsAPI.md#DeleteMasCrd) | **Delete** /k8s/namespaces/{namespace}/mas/{name} | Delete Mas Crd
[**DeletePolicyCrd**](KubernetesCRDsAPI.md#DeletePolicyCrd) | **Delete** /k8s/namespaces/{namespace}/policies/{name} | Delete Policy Crd



## CreateMasCrd

> MultiAgentSystemCRD CreateMasCrd(ctx, namespace).MASCreateRequest(mASCreateRequest).Execute()

Create Mas Crd



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
	mASCreateRequest := *openapiclient.NewMASCreateRequest(*openapiclient.NewMultiAgentSystemMetadata("Name_example", "Namespace_example"), *openapiclient.NewMultiAgentSystemSpec("Name_example")) // MASCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.CreateMasCrd(context.Background(), namespace).MASCreateRequest(mASCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.CreateMasCrd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateMasCrd`: MultiAgentSystemCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.CreateMasCrd`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCreateMasCrdRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **mASCreateRequest** | [**MASCreateRequest**](MASCreateRequest.md) |  | 

### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreatePolicyCrd

> CASAPolicyCRD CreatePolicyCrd(ctx, namespace).CASAPolicyCreateRequest(cASAPolicyCreateRequest).Execute()

Create Policy Crd



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
	cASAPolicyCreateRequest := *openapiclient.NewCASAPolicyCreateRequest(*openapiclient.NewMultiAgentSystemMetadata("Name_example", "Namespace_example"), *openapiclient.NewCASAPolicySpec(*openapiclient.NewCASAPolicyTargetRef("Kind_example", "Name_example"))) // CASAPolicyCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.CreatePolicyCrd(context.Background(), namespace).CASAPolicyCreateRequest(cASAPolicyCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.CreatePolicyCrd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreatePolicyCrd`: CASAPolicyCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.CreatePolicyCrd`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCreatePolicyCrdRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cASAPolicyCreateRequest** | [**CASAPolicyCreateRequest**](CASAPolicyCreateRequest.md) |  | 

### Return type

[**CASAPolicyCRD**](CASAPolicyCRD.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteMasCrd

> DeleteMasCrd(ctx, namespace, name).Execute()

Delete Mas Crd



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
	name := "name_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.KubernetesCRDsAPI.DeleteMasCrd(context.Background(), namespace, name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.DeleteMasCrd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteMasCrdRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeletePolicyCrd

> DeletePolicyCrd(ctx, namespace, name).Execute()

Delete Policy Crd



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
	name := "name_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.KubernetesCRDsAPI.DeletePolicyCrd(context.Background(), namespace, name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.DeletePolicyCrd``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeletePolicyCrdRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

