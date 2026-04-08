# identity_auth_sdk.AppsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_app_apps_post**](AppsApi.md#create_app_apps_post) | **POST** /apps | Create App
[**delete_app_apps_app_id_delete**](AppsApi.md#delete_app_apps_app_id_delete) | **DELETE** /apps/{app_id} | Delete App
[**get_app_apps_app_id_get**](AppsApi.md#get_app_apps_app_id_get) | **GET** /apps/{app_id} | Get App
[**get_apps_apps_get**](AppsApi.md#get_apps_apps_get) | **GET** /apps | Get Apps
[**update_app_apps_app_id_put**](AppsApi.md#update_app_apps_app_id_put) | **PUT** /apps/{app_id} | Update App


# **create_app_apps_post**
> AppViewModel create_app_apps_post(app_request)

Create App

Create a new App.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.app_request import AppRequest
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
    api_instance = identity_auth_sdk.AppsApi(api_client)
    app_request = identity_auth_sdk.AppRequest() # AppRequest | 

    try:
        # Create App
        api_response = api_instance.create_app_apps_post(app_request)
        print("The response of AppsApi->create_app_apps_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->create_app_apps_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_request** | [**AppRequest**](AppRequest.md)|  | 

### Return type

[**AppViewModel**](AppViewModel.md)

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

# **delete_app_apps_app_id_delete**
> Dict[str, object] delete_app_apps_app_id_delete(app_id)

Delete App

Delete an App.

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
    api_instance = identity_auth_sdk.AppsApi(api_client)
    app_id = 'app_id_example' # str | 

    try:
        # Delete App
        api_response = api_instance.delete_app_apps_app_id_delete(app_id)
        print("The response of AppsApi->delete_app_apps_app_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->delete_app_apps_app_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  | 

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

# **get_app_apps_app_id_get**
> AppViewModel get_app_apps_app_id_get(app_id)

Get App

Get an App by ID.

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
    api_instance = identity_auth_sdk.AppsApi(api_client)
    app_id = 'app_id_example' # str | 

    try:
        # Get App
        api_response = api_instance.get_app_apps_app_id_get(app_id)
        print("The response of AppsApi->get_app_apps_app_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->get_app_apps_app_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  | 

### Return type

[**AppViewModel**](AppViewModel.md)

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

# **get_apps_apps_get**
> List[AppViewModel] get_apps_apps_get()

Get Apps

Get all Apps.

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
    api_instance = identity_auth_sdk.AppsApi(api_client)

    try:
        # Get Apps
        api_response = api_instance.get_apps_apps_get()
        print("The response of AppsApi->get_apps_apps_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->get_apps_apps_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_app_apps_app_id_put**
> AppViewModel update_app_apps_app_id_put(app_id, app_request)

Update App

Update an existing App.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.app_request import AppRequest
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
    api_instance = identity_auth_sdk.AppsApi(api_client)
    app_id = 'app_id_example' # str | 
    app_request = identity_auth_sdk.AppRequest() # AppRequest | 

    try:
        # Update App
        api_response = api_instance.update_app_apps_app_id_put(app_id, app_request)
        print("The response of AppsApi->update_app_apps_app_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->update_app_apps_app_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  | 
 **app_request** | [**AppRequest**](AppRequest.md)|  | 

### Return type

[**AppViewModel**](AppViewModel.md)

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

