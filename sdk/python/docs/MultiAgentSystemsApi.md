# identity_auth_sdk.MultiAgentSystemsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bind_apps_mas_mas_id_bind_apps_post**](MultiAgentSystemsApi.md#bind_apps_mas_mas_id_bind_apps_post) | **POST** /mas/{mas_id}/bind_apps | Bind Apps
[**create_mas_mas_put**](MultiAgentSystemsApi.md#create_mas_mas_put) | **PUT** /mas | Create Mas
[**delete_mas_mas_mas_id_delete**](MultiAgentSystemsApi.md#delete_mas_mas_mas_id_delete) | **DELETE** /mas/{mas_id} | Delete Mas
[**get_all_mas_mas_get**](MultiAgentSystemsApi.md#get_all_mas_mas_get) | **GET** /mas | Get All Mas
[**get_mas_apps_mas_mas_id_apps_get**](MultiAgentSystemsApi.md#get_mas_apps_mas_mas_id_apps_get) | **GET** /mas/{mas_id}/apps | Get Mas Apps
[**get_mas_by_id_mas_mas_id_get**](MultiAgentSystemsApi.md#get_mas_by_id_mas_mas_id_get) | **GET** /mas/{mas_id} | Get Mas By Id
[**update_mas_mas_mas_id_post**](MultiAgentSystemsApi.md#update_mas_mas_mas_id_post) | **POST** /mas/{mas_id} | Update Mas


# **bind_apps_mas_mas_id_bind_apps_post**
> bind_apps_mas_mas_id_bind_apps_post(mas_id, multi_agent_system_apps_binding_request)

Bind Apps

Bind a list of apps with an existing multi agent system.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system_apps_binding_request import MultiAgentSystemAppsBindingRequest
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    mas_id = 'mas_id_example' # str | 
    multi_agent_system_apps_binding_request = identity_auth_sdk.MultiAgentSystemAppsBindingRequest() # MultiAgentSystemAppsBindingRequest | 

    try:
        # Bind Apps
        api_instance.bind_apps_mas_mas_id_bind_apps_post(mas_id, multi_agent_system_apps_binding_request)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->bind_apps_mas_mas_id_bind_apps_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mas_id** | **str**|  | 
 **multi_agent_system_apps_binding_request** | [**MultiAgentSystemAppsBindingRequest**](MultiAgentSystemAppsBindingRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_mas_mas_put**
> MultiAgentSystem create_mas_mas_put(multi_agent_system_create_request)

Create Mas

Create a new multi agent system.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system import MultiAgentSystem
from identity_auth_sdk.models.multi_agent_system_create_request import MultiAgentSystemCreateRequest
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    multi_agent_system_create_request = identity_auth_sdk.MultiAgentSystemCreateRequest() # MultiAgentSystemCreateRequest | 

    try:
        # Create Mas
        api_response = api_instance.create_mas_mas_put(multi_agent_system_create_request)
        print("The response of MultiAgentSystemsApi->create_mas_mas_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->create_mas_mas_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multi_agent_system_create_request** | [**MultiAgentSystemCreateRequest**](MultiAgentSystemCreateRequest.md)|  | 

### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

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

# **delete_mas_mas_mas_id_delete**
> object delete_mas_mas_mas_id_delete(mas_id)

Delete Mas

Delete an existing multi agent system.

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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    mas_id = 'mas_id_example' # str | 

    try:
        # Delete Mas
        api_response = api_instance.delete_mas_mas_mas_id_delete(mas_id)
        print("The response of MultiAgentSystemsApi->delete_mas_mas_mas_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->delete_mas_mas_mas_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mas_id** | **str**|  | 

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

# **get_all_mas_mas_get**
> List[MultiAgentSystem] get_all_mas_mas_get()

Get All Mas

Get the list of all multi agent systems.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system import MultiAgentSystem
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)

    try:
        # Get All Mas
        api_response = api_instance.get_all_mas_mas_get()
        print("The response of MultiAgentSystemsApi->get_all_mas_mas_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->get_all_mas_mas_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[MultiAgentSystem]**](MultiAgentSystem.md)

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

# **get_mas_apps_mas_mas_id_apps_get**
> List[AppViewModel] get_mas_apps_mas_mas_id_apps_get(mas_id)

Get Mas Apps

Get all the apps related to a MAS.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.app_view_model import AppViewModel
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    mas_id = 'mas_id_example' # str | 

    try:
        # Get Mas Apps
        api_response = api_instance.get_mas_apps_mas_mas_id_apps_get(mas_id)
        print("The response of MultiAgentSystemsApi->get_mas_apps_mas_mas_id_apps_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->get_mas_apps_mas_mas_id_apps_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mas_id** | **str**|  | 

### Return type

[**List[AppViewModel]**](AppViewModel.md)

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

# **get_mas_by_id_mas_mas_id_get**
> MultiAgentSystem get_mas_by_id_mas_mas_id_get(mas_id)

Get Mas By Id

Get a multi agent system by id.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system import MultiAgentSystem
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    mas_id = 'mas_id_example' # str | 

    try:
        # Get Mas By Id
        api_response = api_instance.get_mas_by_id_mas_mas_id_get(mas_id)
        print("The response of MultiAgentSystemsApi->get_mas_by_id_mas_mas_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->get_mas_by_id_mas_mas_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mas_id** | **str**|  | 

### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

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

# **update_mas_mas_mas_id_post**
> MultiAgentSystem update_mas_mas_mas_id_post(mas_id, multi_agent_system_update_request)

Update Mas

Update an existing multi agent system instance.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.multi_agent_system import MultiAgentSystem
from identity_auth_sdk.models.multi_agent_system_update_request import MultiAgentSystemUpdateRequest
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
    api_instance = identity_auth_sdk.MultiAgentSystemsApi(api_client)
    mas_id = 'mas_id_example' # str | 
    multi_agent_system_update_request = identity_auth_sdk.MultiAgentSystemUpdateRequest() # MultiAgentSystemUpdateRequest | 

    try:
        # Update Mas
        api_response = api_instance.update_mas_mas_mas_id_post(mas_id, multi_agent_system_update_request)
        print("The response of MultiAgentSystemsApi->update_mas_mas_mas_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiAgentSystemsApi->update_mas_mas_mas_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mas_id** | **str**|  | 
 **multi_agent_system_update_request** | [**MultiAgentSystemUpdateRequest**](MultiAgentSystemUpdateRequest.md)|  | 

### Return type

[**MultiAgentSystem**](MultiAgentSystem.md)

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

