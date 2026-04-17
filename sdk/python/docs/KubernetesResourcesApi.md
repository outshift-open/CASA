# identity_auth_sdk.KubernetesResourcesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cache_load_token**](KubernetesResourcesApi.md#cache_load_token) | **POST** /k8s/namespaces/{namespace}/cache/load-token | Load Token
[**cache_store_token**](KubernetesResourcesApi.md#cache_store_token) | **POST** /k8s/namespaces/{namespace}/cache/store-token | Store Token
[**get_k8s_mas_by_app_host**](KubernetesResourcesApi.md#get_k8s_mas_by_app_host) | **GET** /k8s/namespaces/{namespace}/get_mas_by_app_host | Get K8S Mas By App Host
[**get_k8s_mas_by_app_workload**](KubernetesResourcesApi.md#get_k8s_mas_by_app_workload) | **GET** /k8s/namespaces/{namespace}/get_mas_by_app_workload | Get K8S Mas By App Workload


# **cache_load_token**
> TokenResponse cache_load_token(namespace, cache_token_load_request)

Load Token

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.cache_token_load_request import CacheTokenLoadRequest
from identity_auth_sdk.models.token_response import TokenResponse
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
    api_instance = identity_auth_sdk.KubernetesResourcesApi(api_client)
    namespace = 'namespace_example' # str | 
    cache_token_load_request = identity_auth_sdk.CacheTokenLoadRequest() # CacheTokenLoadRequest | 

    try:
        # Load Token
        api_response = api_instance.cache_load_token(namespace, cache_token_load_request)
        print("The response of KubernetesResourcesApi->cache_load_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesResourcesApi->cache_load_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **cache_token_load_request** | [**CacheTokenLoadRequest**](CacheTokenLoadRequest.md)|  | 

### Return type

[**TokenResponse**](TokenResponse.md)

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

# **cache_store_token**
> object cache_store_token(namespace, cache_token_store_request)

Store Token

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.cache_token_store_request import CacheTokenStoreRequest
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
    api_instance = identity_auth_sdk.KubernetesResourcesApi(api_client)
    namespace = 'namespace_example' # str | 
    cache_token_store_request = identity_auth_sdk.CacheTokenStoreRequest() # CacheTokenStoreRequest | 

    try:
        # Store Token
        api_response = api_instance.cache_store_token(namespace, cache_token_store_request)
        print("The response of KubernetesResourcesApi->cache_store_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesResourcesApi->cache_store_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **cache_token_store_request** | [**CacheTokenStoreRequest**](CacheTokenStoreRequest.md)|  | 

### Return type

**object**

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

# **get_k8s_mas_by_app_host**
> K8sMultiAgentSystemCRDViewModel get_k8s_mas_by_app_host(namespace, app_host)

Get K8S Mas By App Host

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.k8s_multi_agent_system_crd_view_model import K8sMultiAgentSystemCRDViewModel
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
    api_instance = identity_auth_sdk.KubernetesResourcesApi(api_client)
    namespace = 'namespace_example' # str | 
    app_host = 'app_host_example' # str | 

    try:
        # Get K8S Mas By App Host
        api_response = api_instance.get_k8s_mas_by_app_host(namespace, app_host)
        print("The response of KubernetesResourcesApi->get_k8s_mas_by_app_host:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesResourcesApi->get_k8s_mas_by_app_host: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **app_host** | **str**|  | 

### Return type

[**K8sMultiAgentSystemCRDViewModel**](K8sMultiAgentSystemCRDViewModel.md)

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

# **get_k8s_mas_by_app_workload**
> K8sMultiAgentSystemCRDViewModel get_k8s_mas_by_app_workload(namespace, app_workload)

Get K8S Mas By App Workload

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.k8s_multi_agent_system_crd_view_model import K8sMultiAgentSystemCRDViewModel
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
    api_instance = identity_auth_sdk.KubernetesResourcesApi(api_client)
    namespace = 'namespace_example' # str | 
    app_workload = 'app_workload_example' # str | 

    try:
        # Get K8S Mas By App Workload
        api_response = api_instance.get_k8s_mas_by_app_workload(namespace, app_workload)
        print("The response of KubernetesResourcesApi->get_k8s_mas_by_app_workload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling KubernetesResourcesApi->get_k8s_mas_by_app_workload: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | 
 **app_workload** | **str**|  | 

### Return type

[**K8sMultiAgentSystemCRDViewModel**](K8sMultiAgentSystemCRDViewModel.md)

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

