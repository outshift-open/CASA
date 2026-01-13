# identity_auth_sdk.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**app_metadata**](DefaultApi.md#app_metadata) | **GET** /{app_id}/oauth2/client-metadata.json | App Metadata
[**create_app_apps_post**](DefaultApi.md#create_app_apps_post) | **POST** /apps | Create App
[**health_check_health_get**](DefaultApi.md#health_check_health_get) | **GET** /health | Health Check
[**introspect**](DefaultApi.md#introspect) | **POST** /oauth2/introspect | Introspect
[**token**](DefaultApi.md#token) | **POST** /{app_id}/oauth2/token | Token
[**token_exchange**](DefaultApi.md#token_exchange) | **POST** /{app_id}/oauth2/token_exchange | Token Exchange


# **app_metadata**
> AppMetadataResponse app_metadata(app_id)

App Metadata

Generate a new token based on the request parameters.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.app_metadata_response import AppMetadataResponse
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
    api_instance = identity_auth_sdk.DefaultApi(api_client)
    app_id = 'app_id_example' # str |

    try:
        # App Metadata
        api_response = api_instance.app_metadata(app_id)
        print("The response of DefaultApi->app_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->app_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  |

### Return type

[**AppMetadataResponse**](AppMetadataResponse.md)

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

# **create_app_apps_post**
> App create_app_apps_post(app_request)

Create App

Create a new App.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.app import App
from identity_auth_sdk.models.app_request import AppRequest
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
    api_instance = identity_auth_sdk.DefaultApi(api_client)
    app_request = identity_auth_sdk.AppRequest() # AppRequest |

    try:
        # Create App
        api_response = api_instance.create_app_apps_post(app_request)
        print("The response of DefaultApi->create_app_apps_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_app_apps_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_request** | [**AppRequest**](AppRequest.md)|  |

### Return type

[**App**](App.md)

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

# **health_check_health_get**
> Dict[str, object] health_check_health_get()

Health Check

Health check endpoint.

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
    api_instance = identity_auth_sdk.DefaultApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_health_get()
        print("The response of DefaultApi->health_check_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_check_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **introspect**
> TokenIntrospectResponse introspect(token, tools=tools)

Introspect

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.token_introspect_response import TokenIntrospectResponse
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
    api_instance = identity_auth_sdk.DefaultApi(api_client)
    token = 'token_example' # str |
    tools = ['tools_example'] # List[str] |  (optional)

    try:
        # Introspect
        api_response = api_instance.introspect(token, tools=tools)
        print("The response of DefaultApi->introspect:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->introspect: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  |
 **tools** | [**List[str]**](str.md)|  | [optional]

### Return type

[**TokenIntrospectResponse**](TokenIntrospectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **token**
> TokenResponse token(app_id, client_id, client_secret, user_input)

Token

Generate a new token based on the request parameters.

### Example


```python
import identity_auth_sdk
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
    api_instance = identity_auth_sdk.DefaultApi(api_client)
    app_id = 'app_id_example' # str |
    client_id = 'client_id_example' # str |
    client_secret = 'client_secret_example' # str |
    user_input = 'user_input_example' # str |

    try:
        # Token
        api_response = api_instance.token(app_id, client_id, client_secret, user_input)
        print("The response of DefaultApi->token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  |
 **client_id** | **str**|  |
 **client_secret** | **str**|  |
 **user_input** | **str**|  |

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **token_exchange**
> TokenResponse token_exchange(app_id, client_id, client_secret, subject_token, subject_token_type, scope=scope, mcp_server_url=mcp_server_url, tools=tools)

Token Exchange

Do a token exchange for an app.

### Example


```python
import identity_auth_sdk
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
    api_instance = identity_auth_sdk.DefaultApi(api_client)
    app_id = 'app_id_example' # str |
    client_id = 'client_id_example' # str |
    client_secret = 'client_secret_example' # str |
    subject_token = 'subject_token_example' # str |
    subject_token_type = 'subject_token_type_example' # str |
    scope = 'scope_example' # str |  (optional)
    mcp_server_url = 'mcp_server_url_example' # str |  (optional)
    tools = ['tools_example'] # List[str] |  (optional)

    try:
        # Token Exchange
        api_response = api_instance.token_exchange(app_id, client_id, client_secret, subject_token, subject_token_type, scope=scope, mcp_server_url=mcp_server_url, tools=tools)
        print("The response of DefaultApi->token_exchange:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->token_exchange: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  |
 **client_id** | **str**|  |
 **client_secret** | **str**|  |
 **subject_token** | **str**|  |
 **subject_token_type** | **str**|  |
 **scope** | **str**|  | [optional]
 **mcp_server_url** | **str**|  | [optional]
 **tools** | [**List[str]**](str.md)|  | [optional]

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
