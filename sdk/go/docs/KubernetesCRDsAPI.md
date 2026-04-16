# \KubernetesCRDsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateMasCrdK8sNamespacesNamespaceMasPost**](KubernetesCRDsAPI.md#CreateMasCrdK8sNamespacesNamespaceMasPost) | **Post** /k8s/namespaces/{namespace}/mas | Create Mas Crd
[**DeleteMasCrdK8sNamespacesNamespaceMasNameDelete**](KubernetesCRDsAPI.md#DeleteMasCrdK8sNamespacesNamespaceMasNameDelete) | **Delete** /k8s/namespaces/{namespace}/mas/{name} | Delete Mas Crd
[**GetMasCrdK8sNamespacesNamespaceMasMasIdGet**](KubernetesCRDsAPI.md#GetMasCrdK8sNamespacesNamespaceMasMasIdGet) | **Get** /k8s/namespaces/{namespace}/mas/{mas_id} | Get Mas Crd
[**ListAllMasCrdsK8sMasGet**](KubernetesCRDsAPI.md#ListAllMasCrdsK8sMasGet) | **Get** /k8s/mas | List All Mas Crds
[**ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet**](KubernetesCRDsAPI.md#ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet) | **Get** /k8s/namespaces/{namespace}/mas | List Mas Crds In Namespace
[**LivenessProbeK8sHealthzGet**](KubernetesCRDsAPI.md#LivenessProbeK8sHealthzGet) | **Get** /k8s/healthz | Liveness Probe
[**ReadinessProbeK8sReadyzGet**](KubernetesCRDsAPI.md#ReadinessProbeK8sReadyzGet) | **Get** /k8s/readyz | Readiness Probe
[**UpdateMasCrdK8sNamespacesNamespaceMasNamePut**](KubernetesCRDsAPI.md#UpdateMasCrdK8sNamespacesNamespaceMasNamePut) | **Put** /k8s/namespaces/{namespace}/mas/{name} | Update Mas Crd
[**UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch**](KubernetesCRDsAPI.md#UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch) | **Patch** /k8s/namespaces/{namespace}/mas/{name}/status | Update Mas Status
[**WatchAllMasK8sWatchMultiagentsystemsGet**](KubernetesCRDsAPI.md#WatchAllMasK8sWatchMultiagentsystemsGet) | **Get** /k8s/watch/multiagentsystems | Watch All Mas
[**WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet**](KubernetesCRDsAPI.md#WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet) | **Get** /k8s/watch/namespaces/{namespace}/multiagentsystems | Watch Mas In Namespace
[**WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet**](KubernetesCRDsAPI.md#WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet) | **Get** /k8s/watch/namespaces/{namespace}/ztapolicies | Watch Policies In Namespace



## CreateMasCrdK8sNamespacesNamespaceMasPost

> MultiAgentSystemCRD CreateMasCrdK8sNamespacesNamespaceMasPost(ctx, namespace).MASCreateRequest(mASCreateRequest).Execute()

Create Mas Crd



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
	namespace := "namespace_example" // string | 
	mASCreateRequest := *openapiclient.NewMASCreateRequest(*openapiclient.NewMultiAgentSystemMetadata("Name_example", "Namespace_example"), *openapiclient.NewMultiAgentSystemSpecInput("Name_example")) // MASCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.CreateMasCrdK8sNamespacesNamespaceMasPost(context.Background(), namespace).MASCreateRequest(mASCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.CreateMasCrdK8sNamespacesNamespaceMasPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateMasCrdK8sNamespacesNamespaceMasPost`: MultiAgentSystemCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.CreateMasCrdK8sNamespacesNamespaceMasPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCreateMasCrdK8sNamespacesNamespaceMasPostRequest struct via the builder pattern


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


## DeleteMasCrdK8sNamespacesNamespaceMasNameDelete

> DeleteMasCrdK8sNamespacesNamespaceMasNameDelete(ctx, namespace, name).Execute()

Delete Mas Crd



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
	namespace := "namespace_example" // string | 
	name := "name_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.KubernetesCRDsAPI.DeleteMasCrdK8sNamespacesNamespaceMasNameDelete(context.Background(), namespace, name).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.DeleteMasCrdK8sNamespacesNamespaceMasNameDelete``: %v\n", err)
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

Other parameters are passed through a pointer to a apiDeleteMasCrdK8sNamespacesNamespaceMasNameDeleteRequest struct via the builder pattern


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


## GetMasCrdK8sNamespacesNamespaceMasMasIdGet

> MultiAgentSystemCRD GetMasCrdK8sNamespacesNamespaceMasMasIdGet(ctx, namespace, masId).Execute()

Get Mas Crd



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
	namespace := "namespace_example" // string | 
	masId := "masId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.GetMasCrdK8sNamespacesNamespaceMasMasIdGet(context.Background(), namespace, masId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.GetMasCrdK8sNamespacesNamespaceMasMasIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetMasCrdK8sNamespacesNamespaceMasMasIdGet`: MultiAgentSystemCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.GetMasCrdK8sNamespacesNamespaceMasMasIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 
**masId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetMasCrdK8sNamespacesNamespaceMasMasIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAllMasCrdsK8sMasGet

> MASListResponse ListAllMasCrdsK8sMasGet(ctx).Namespace(namespace).Execute()

List All Mas Crds



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
	namespace := "namespace_example" // string | Filter by namespace (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.ListAllMasCrdsK8sMasGet(context.Background()).Namespace(namespace).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.ListAllMasCrdsK8sMasGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAllMasCrdsK8sMasGet`: MASListResponse
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.ListAllMasCrdsK8sMasGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAllMasCrdsK8sMasGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** | Filter by namespace | 

### Return type

[**MASListResponse**](MASListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet

> MASListResponse ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet(ctx, namespace).Execute()

List Mas Crds In Namespace



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
	namespace := "namespace_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet(context.Background(), namespace).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet`: MASListResponse
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.ListMasCrdsInNamespaceK8sNamespacesNamespaceMasGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiListMasCrdsInNamespaceK8sNamespacesNamespaceMasGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**MASListResponse**](MASListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## LivenessProbeK8sHealthzGet

> interface{} LivenessProbeK8sHealthzGet(ctx).Execute()

Liveness Probe



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
	resp, r, err := apiClient.KubernetesCRDsAPI.LivenessProbeK8sHealthzGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.LivenessProbeK8sHealthzGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `LivenessProbeK8sHealthzGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.LivenessProbeK8sHealthzGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiLivenessProbeK8sHealthzGetRequest struct via the builder pattern


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


## ReadinessProbeK8sReadyzGet

> interface{} ReadinessProbeK8sReadyzGet(ctx).Execute()

Readiness Probe



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
	resp, r, err := apiClient.KubernetesCRDsAPI.ReadinessProbeK8sReadyzGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.ReadinessProbeK8sReadyzGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReadinessProbeK8sReadyzGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.ReadinessProbeK8sReadyzGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiReadinessProbeK8sReadyzGetRequest struct via the builder pattern


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


## UpdateMasCrdK8sNamespacesNamespaceMasNamePut

> MultiAgentSystemCRD UpdateMasCrdK8sNamespacesNamespaceMasNamePut(ctx, namespace, name).MASUpdateRequest(mASUpdateRequest).Execute()

Update Mas Crd



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
	namespace := "namespace_example" // string | 
	name := "name_example" // string | 
	mASUpdateRequest := *openapiclient.NewMASUpdateRequest(*openapiclient.NewMultiAgentSystemSpecInput("Name_example")) // MASUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.UpdateMasCrdK8sNamespacesNamespaceMasNamePut(context.Background(), namespace, name).MASUpdateRequest(mASUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.UpdateMasCrdK8sNamespacesNamespaceMasNamePut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateMasCrdK8sNamespacesNamespaceMasNamePut`: MultiAgentSystemCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.UpdateMasCrdK8sNamespacesNamespaceMasNamePut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateMasCrdK8sNamespacesNamespaceMasNamePutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **mASUpdateRequest** | [**MASUpdateRequest**](MASUpdateRequest.md) |  | 

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


## UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch

> MultiAgentSystemCRD UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch(ctx, namespace, name).MASStatusUpdateRequest(mASStatusUpdateRequest).Execute()

Update Mas Status



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
	namespace := "namespace_example" // string | 
	name := "name_example" // string | 
	mASStatusUpdateRequest := *openapiclient.NewMASStatusUpdateRequest(*openapiclient.NewMultiAgentSystemStatus()) // MASStatusUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch(context.Background(), namespace, name).MASStatusUpdateRequest(mASStatusUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch`: MultiAgentSystemCRD
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.UpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 
**name** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateMasStatusK8sNamespacesNamespaceMasNameStatusPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **mASStatusUpdateRequest** | [**MASStatusUpdateRequest**](MASStatusUpdateRequest.md) |  | 

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


## WatchAllMasK8sWatchMultiagentsystemsGet

> interface{} WatchAllMasK8sWatchMultiagentsystemsGet(ctx).ResourceVersion(resourceVersion).Execute()

Watch All Mas



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
	resourceVersion := "resourceVersion_example" // string | Start watching from this version (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.WatchAllMasK8sWatchMultiagentsystemsGet(context.Background()).ResourceVersion(resourceVersion).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.WatchAllMasK8sWatchMultiagentsystemsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `WatchAllMasK8sWatchMultiagentsystemsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.WatchAllMasK8sWatchMultiagentsystemsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiWatchAllMasK8sWatchMultiagentsystemsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resourceVersion** | **string** | Start watching from this version | 

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


## WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet

> interface{} WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet(ctx, namespace).ResourceVersion(resourceVersion).Execute()

Watch Mas In Namespace



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
	namespace := "namespace_example" // string | 
	resourceVersion := "resourceVersion_example" // string | Start watching from this version (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet(context.Background(), namespace).ResourceVersion(resourceVersion).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.WatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiWatchMasInNamespaceK8sWatchNamespacesNamespaceMultiagentsystemsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **resourceVersion** | **string** | Start watching from this version | 

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


## WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet

> interface{} WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet(ctx, namespace).ResourceVersion(resourceVersion).Execute()

Watch Policies In Namespace



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
	namespace := "namespace_example" // string | 
	resourceVersion := "resourceVersion_example" // string | Start watching from this version (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.KubernetesCRDsAPI.WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet(context.Background(), namespace).ResourceVersion(resourceVersion).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `KubernetesCRDsAPI.WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `KubernetesCRDsAPI.WatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiWatchPoliciesInNamespaceK8sWatchNamespacesNamespaceZtapoliciesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **resourceVersion** | **string** | Start watching from this version | 

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

