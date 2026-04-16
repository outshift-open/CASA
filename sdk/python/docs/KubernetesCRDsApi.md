# identity_auth_sdk.KubernetesCRDsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_mas_crd_k8s_namespaces_namespace_mas_post**](KubernetesCRDsApi.md#create_mas_crd_k8s_namespaces_namespace_mas_post) | **POST** /k8s/namespaces/{namespace}/mas | Create Mas Crd
[**delete_mas_crd_k8s_namespaces_namespace_mas_name_delete**](KubernetesCRDsApi.md#delete_mas_crd_k8s_namespaces_namespace_mas_name_delete) | **DELETE** /k8s/namespaces/{namespace}/mas/{name} | Delete Mas Crd
[**get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get**](KubernetesCRDsApi.md#get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get) | **GET** /k8s/namespaces/{namespace}/mas/{mas_id} | Get Mas Crd
[**list_all_mas_crds_k8s_mas_get**](KubernetesCRDsApi.md#list_all_mas_crds_k8s_mas_get) | **GET** /k8s/mas | List All Mas Crds
[**list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get**](KubernetesCRDsApi.md#list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get) | **GET** /k8s/namespaces/{namespace}/mas | List Mas Crds In Namespace
[**liveness_probe_k8s_healthz_get**](KubernetesCRDsApi.md#liveness_probe_k8s_healthz_get) | **GET** /k8s/healthz | Liveness Probe
[**readiness_probe_k8s_readyz_get**](KubernetesCRDsApi.md#readiness_probe_k8s_readyz_get) | **GET** /k8s/readyz | Readiness Probe
[**update_mas_crd_k8s_namespaces_namespace_mas_name_put**](KubernetesCRDsApi.md#update_mas_crd_k8s_namespaces_namespace_mas_name_put) | **PUT** /k8s/namespaces/{namespace}/mas/{name} | Update Mas Crd
[**update_mas_status_k8s_namespaces_namespace_mas_name_status_patch**](KubernetesCRDsApi.md#update_mas_status_k8s_namespaces_namespace_mas_name_status_patch) | **PATCH** /k8s/namespaces/{namespace}/mas/{name}/status | Update Mas Status
[**watch_all_mas_k8s_watch_multiagentsystems_get**](KubernetesCRDsApi.md#watch_all_mas_k8s_watch_multiagentsystems_get) | **GET** /k8s/watch/multiagentsystems | Watch All Mas
[**watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get**](KubernetesCRDsApi.md#watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get) | **GET** /k8s/watch/namespaces/{namespace}/multiagentsystems | Watch Mas In Namespace
[**watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get**](KubernetesCRDsApi.md#watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get) | **GET** /k8s/watch/namespaces/{namespace}/ztapolicies | Watch Policies In Namespace


# **create_mas_crd_k8s_namespaces_namespace_mas_post**
> MultiAgentSystemCRD create_mas_crd_k8s_namespaces_namespace_mas_post(namespace, mas_create_request)

Create Mas Crd

Create a new MultiAgentSystem CRD.

This endpoint is used by kubectl or Kubernetes operators to create a new
Multi-Agent System through the CRD API.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.mas_create_request import MASCreateRequest
from identity_auth_sdk.models.multi_agent_system_crd import MultiAgentSystemCRD
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    mas_create_request = identity_auth_sdk.MASCreateRequest() # MASCreateRequest | 

    try:
        # Create Mas Crd
        api_response = api_instance.create_mas_crd_k8s_namespaces_namespace_mas_post(namespace, mas_create_request)
        print("The response of KubernetesCRDsApi->create_mas_crd_k8s_namespaces_namespace_mas_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->create_mas_crd_k8s_namespaces_namespace_mas_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **mas_create_request** | [**MASCreateRequest**](MASCreateRequest.md)|  | 

### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_mas_crd_k8s_namespaces_namespace_mas_name_delete**
> delete_mas_crd_k8s_namespaces_namespace_mas_name_delete(namespace, name)

Delete Mas Crd

Delete a MultiAgentSystem CRD.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    name = 'name_example' # str | 

    try:
        # Delete Mas Crd
        api_instance.delete_mas_crd_k8s_namespaces_namespace_mas_name_delete(namespace, name)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->delete_mas_crd_k8s_namespaces_namespace_mas_name_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get**
> MultiAgentSystemCRD get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get(namespace, mas_id)

Get Mas Crd

Get a MultiAgentSystem CRD by namespace and name.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system_crd import MultiAgentSystemCRD
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    mas_id = 'mas_id_example' # str | 

    try:
        # Get Mas Crd
        api_response = api_instance.get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get(namespace, mas_id)
        print("The response of KubernetesCRDsApi->get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->get_mas_crd_k8s_namespaces_namespace_mas_mas_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **mas_id** | **str**|  | 

### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_all_mas_crds_k8s_mas_get**
> MASListResponse list_all_mas_crds_k8s_mas_get(namespace=namespace)

List All Mas Crds

List all MultiAgentSystem CRDs across all namespaces or filtered by namespace.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.mas_list_response import MASListResponse
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | Filter by namespace (optional)

    try:
        # List All Mas Crds
        api_response = api_instance.list_all_mas_crds_k8s_mas_get(namespace=namespace)
        print("The response of KubernetesCRDsApi->list_all_mas_crds_k8s_mas_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->list_all_mas_crds_k8s_mas_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**| Filter by namespace | [optional] 

### Return type

[**MASListResponse**](MASListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get**
> MASListResponse list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get(namespace)

List Mas Crds In Namespace

List all MultiAgentSystem CRDs in a specific namespace.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.mas_list_response import MASListResponse
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 

    try:
        # List Mas Crds In Namespace
        api_response = api_instance.list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get(namespace)
        print("The response of KubernetesCRDsApi->list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->list_mas_crds_in_namespace_k8s_namespaces_namespace_mas_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 

### Return type

[**MASListResponse**](MASListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **liveness_probe_k8s_healthz_get**
> object liveness_probe_k8s_healthz_get()

Liveness Probe

Liveness probe endpoint.

Returns 200 if the service is alive and should not be restarted.
This is a lightweight check.

Example:
    curl http://localhost:3000/k8s/healthz

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)

    try:
        # Liveness Probe
        api_response = api_instance.liveness_probe_k8s_healthz_get()
        print("The response of KubernetesCRDsApi->liveness_probe_k8s_healthz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->liveness_probe_k8s_healthz_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **readiness_probe_k8s_readyz_get**
> object readiness_probe_k8s_readyz_get()

Readiness Probe

Readiness probe endpoint.

Returns 200 if the service is ready to receive traffic.
Checks database connectivity and other dependencies.

Example:
    curl http://localhost:3000/k8s/readyz

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)

    try:
        # Readiness Probe
        api_response = api_instance.readiness_probe_k8s_readyz_get()
        print("The response of KubernetesCRDsApi->readiness_probe_k8s_readyz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->readiness_probe_k8s_readyz_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_mas_crd_k8s_namespaces_namespace_mas_name_put**
> MultiAgentSystemCRD update_mas_crd_k8s_namespaces_namespace_mas_name_put(namespace, name, mas_update_request)

Update Mas Crd

Update a MultiAgentSystem CRD spec.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.mas_update_request import MASUpdateRequest
from identity_auth_sdk.models.multi_agent_system_crd import MultiAgentSystemCRD
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    name = 'name_example' # str | 
    mas_update_request = identity_auth_sdk.MASUpdateRequest() # MASUpdateRequest | 

    try:
        # Update Mas Crd
        api_response = api_instance.update_mas_crd_k8s_namespaces_namespace_mas_name_put(namespace, name, mas_update_request)
        print("The response of KubernetesCRDsApi->update_mas_crd_k8s_namespaces_namespace_mas_name_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->update_mas_crd_k8s_namespaces_namespace_mas_name_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **name** | **str**|  | 
 **mas_update_request** | [**MASUpdateRequest**](MASUpdateRequest.md)|  | 

### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_mas_status_k8s_namespaces_namespace_mas_name_status_patch**
> MultiAgentSystemCRD update_mas_status_k8s_namespaces_namespace_mas_name_status_patch(namespace, name, mas_status_update_request)

Update Mas Status

Update a MultiAgentSystem CRD status (typically called by operator).

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.mas_status_update_request import MASStatusUpdateRequest
from identity_auth_sdk.models.multi_agent_system_crd import MultiAgentSystemCRD
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    name = 'name_example' # str | 
    mas_status_update_request = identity_auth_sdk.MASStatusUpdateRequest() # MASStatusUpdateRequest | 

    try:
        # Update Mas Status
        api_response = api_instance.update_mas_status_k8s_namespaces_namespace_mas_name_status_patch(namespace, name, mas_status_update_request)
        print("The response of KubernetesCRDsApi->update_mas_status_k8s_namespaces_namespace_mas_name_status_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->update_mas_status_k8s_namespaces_namespace_mas_name_status_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **name** | **str**|  | 
 **mas_status_update_request** | [**MASStatusUpdateRequest**](MASStatusUpdateRequest.md)|  | 

### Return type

[**MultiAgentSystemCRD**](MultiAgentSystemCRD.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **watch_all_mas_k8s_watch_multiagentsystems_get**
> object watch_all_mas_k8s_watch_multiagentsystems_get(resource_version=resource_version)

Watch All Mas

Watch all MultiAgentSystem CRDs across all namespaces.

Example:
    curl -N http://localhost:3000/k8s/watch/multiagentsystems

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    resource_version = 'resource_version_example' # str | Start watching from this version (optional)

    try:
        # Watch All Mas
        api_response = api_instance.watch_all_mas_k8s_watch_multiagentsystems_get(resource_version=resource_version)
        print("The response of KubernetesCRDsApi->watch_all_mas_k8s_watch_multiagentsystems_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->watch_all_mas_k8s_watch_multiagentsystems_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_version** | **str**| Start watching from this version | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get**
> object watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get(namespace, resource_version=resource_version)

Watch Mas In Namespace

Watch MultiAgentSystem CRDs in a specific namespace.

This endpoint streams Server-Sent Events (SSE) for real-time updates.
Operators can use this to react to CRD changes immediately.

Example:
    curl -N http://localhost:3000/k8s/watch/namespaces/default/multiagentsystems

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    resource_version = 'resource_version_example' # str | Start watching from this version (optional)

    try:
        # Watch Mas In Namespace
        api_response = api_instance.watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get(namespace, resource_version=resource_version)
        print("The response of KubernetesCRDsApi->watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->watch_mas_in_namespace_k8s_watch_namespaces_namespace_multiagentsystems_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **resource_version** | **str**| Start watching from this version | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get**
> object watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get(namespace, resource_version=resource_version)

Watch Policies In Namespace

Watch ZTAPolicy CRDs in a specific namespace.

Example:
    curl -N http://localhost:3000/k8s/watch/namespaces/production-mas/ztapolicies

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.KubernetesCRDsApi(api_client)
    namespace = 'namespace_example' # str | 
    resource_version = 'resource_version_example' # str | Start watching from this version (optional)

    try:
        # Watch Policies In Namespace
        api_response = api_instance.watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get(namespace, resource_version=resource_version)
        print("The response of KubernetesCRDsApi->watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesCRDsApi->watch_policies_in_namespace_k8s_watch_namespaces_namespace_ztapolicies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **resource_version** | **str**| Start watching from this version | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

