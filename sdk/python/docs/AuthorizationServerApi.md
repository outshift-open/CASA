# identity_auth_sdk.AuthorizationServerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**app_metadata**](AuthorizationServerApi.md#app_metadata) | **GET** /{app_id}/oauth2/client-metadata.json | App Metadata
[**health_check_health_get**](AuthorizationServerApi.md#health_check_health_get) | **GET** /health | Health Check
[**introspect**](AuthorizationServerApi.md#introspect) | **POST** /oauth2/introspect | Introspect
[**token**](AuthorizationServerApi.md#token) | **POST** /{app_id}/oauth2/token | Token
[**token_exchange**](AuthorizationServerApi.md#token_exchange) | **POST** /{app_id}/oauth2/token_exchange | Token Exchange


# **app_metadata**
> AppMetadataResponse app_metadata(app_id)

App Metadata

Get an Application client metadata.

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
    api_instance = identity_auth_sdk.AuthorizationServerApi(api_client)
    app_id = 'app_id_example' # str | 

    try:
        # App Metadata
        api_response = api_instance.app_metadata(app_id)
        print("The response of AuthorizationServerApi->app_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationServerApi->app_metadata: %s\n" % e)
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
    api_instance = identity_auth_sdk.AuthorizationServerApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_health_get()
        print("The response of AuthorizationServerApi->health_check_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationServerApi->health_check_health_get: %s\n" % e)
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

Introspect a token and evaluate it against the requested tools.

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
    api_instance = identity_auth_sdk.AuthorizationServerApi(api_client)
    token = 'token_example' # str | 
    tools = ['tools_example'] # List[str] |  (optional)

    try:
        # Introspect
        api_response = api_instance.introspect(token, tools=tools)
        print("The response of AuthorizationServerApi->introspect:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationServerApi->introspect: %s\n" % e)
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
> TokenResponse token(app_id, client_id, client_secret, user_input=user_input, user_input_id=user_input_id)

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
    api_instance = identity_auth_sdk.AuthorizationServerApi(api_client)
    app_id = 'app_id_example' # str | 
    client_id = 'client_id_example' # str | 
    client_secret = 'client_secret_example' # str | 
    user_input = 'user_input_example' # str |  (optional)
    user_input_id = 'user_input_id_example' # str |  (optional)

    try:
        # Token
        api_response = api_instance.token(app_id, client_id, client_secret, user_input=user_input, user_input_id=user_input_id)
        print("The response of AuthorizationServerApi->token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationServerApi->token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**|  | 
 **client_id** | **str**|  | 
 **client_secret** | **str**|  | 
 **user_input** | **str**|  | [optional] 
 **user_input_id** | **str**|  | [optional] 

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
    api_instance = identity_auth_sdk.AuthorizationServerApi(api_client)
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
        print("The response of AuthorizationServerApi->token_exchange:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationServerApi->token_exchange: %s\n" % e)
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

