# identity_auth_sdk.ScopesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_scope_scopes_post**](ScopesApi.md#create_scope_scopes_post) | **POST** /scopes | Create Scope
[**delete_scope_scopes_scope_id_delete**](ScopesApi.md#delete_scope_scopes_scope_id_delete) | **DELETE** /scopes/{scope_id} | Delete Scope
[**get_scope_scopes_scope_id_get**](ScopesApi.md#get_scope_scopes_scope_id_get) | **GET** /scopes/{scope_id} | Get Scope
[**get_scopes_scopes_get**](ScopesApi.md#get_scopes_scopes_get) | **GET** /scopes | Get Scopes
[**update_scope_scopes_scope_id_put**](ScopesApi.md#update_scope_scopes_scope_id_put) | **PUT** /scopes/{scope_id} | Update Scope


# **create_scope_scopes_post**
> ScopeViewModel create_scope_scopes_post(scope_create_request)

Create Scope

Create a new scope.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.scope_create_request import ScopeCreateRequest
from identity_auth_sdk.models.scope_view_model import ScopeViewModel
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
    api_instance = identity_auth_sdk.ScopesApi(api_client)
    scope_create_request = identity_auth_sdk.ScopeCreateRequest() # ScopeCreateRequest | 

    try:
        # Create Scope
        api_response = api_instance.create_scope_scopes_post(scope_create_request)
        print("The response of ScopesApi->create_scope_scopes_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScopesApi->create_scope_scopes_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope_create_request** | [**ScopeCreateRequest**](ScopeCreateRequest.md)|  | 

### Return type

[**ScopeViewModel**](ScopeViewModel.md)

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

# **delete_scope_scopes_scope_id_delete**
> Dict[str, object] delete_scope_scopes_scope_id_delete(scope_id)

Delete Scope

Delete a scope.

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
    api_instance = identity_auth_sdk.ScopesApi(api_client)
    scope_id = 'scope_id_example' # str | 

    try:
        # Delete Scope
        api_response = api_instance.delete_scope_scopes_scope_id_delete(scope_id)
        print("The response of ScopesApi->delete_scope_scopes_scope_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScopesApi->delete_scope_scopes_scope_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope_id** | **str**|  | 

### Return type

**Dict[str, object]**

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

# **get_scope_scopes_scope_id_get**
> ScopeViewModel get_scope_scopes_scope_id_get(scope_id)

Get Scope

Get a scope by ID.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.scope_view_model import ScopeViewModel
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
    api_instance = identity_auth_sdk.ScopesApi(api_client)
    scope_id = 'scope_id_example' # str | 

    try:
        # Get Scope
        api_response = api_instance.get_scope_scopes_scope_id_get(scope_id)
        print("The response of ScopesApi->get_scope_scopes_scope_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScopesApi->get_scope_scopes_scope_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope_id** | **str**|  | 

### Return type

[**ScopeViewModel**](ScopeViewModel.md)

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

# **get_scopes_scopes_get**
> List[ScopeViewModel] get_scopes_scopes_get()

Get Scopes

Get all scopes.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.scope_view_model import ScopeViewModel
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
    api_instance = identity_auth_sdk.ScopesApi(api_client)

    try:
        # Get Scopes
        api_response = api_instance.get_scopes_scopes_get()
        print("The response of ScopesApi->get_scopes_scopes_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScopesApi->get_scopes_scopes_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[ScopeViewModel]**](ScopeViewModel.md)

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

# **update_scope_scopes_scope_id_put**
> ScopeViewModel update_scope_scopes_scope_id_put(scope_id, scope_update_request)

Update Scope

Update an existing scope.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.scope_update_request import ScopeUpdateRequest
from identity_auth_sdk.models.scope_view_model import ScopeViewModel
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
    api_instance = identity_auth_sdk.ScopesApi(api_client)
    scope_id = 'scope_id_example' # str | 
    scope_update_request = identity_auth_sdk.ScopeUpdateRequest() # ScopeUpdateRequest | 

    try:
        # Update Scope
        api_response = api_instance.update_scope_scopes_scope_id_put(scope_id, scope_update_request)
        print("The response of ScopesApi->update_scope_scopes_scope_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScopesApi->update_scope_scopes_scope_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope_id** | **str**|  | 
 **scope_update_request** | [**ScopeUpdateRequest**](ScopeUpdateRequest.md)|  | 

### Return type

[**ScopeViewModel**](ScopeViewModel.md)

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

