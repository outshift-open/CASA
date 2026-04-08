# identity_auth_sdk.TracesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_traces_trace_get**](TracesApi.md#get_traces_trace_get) | **GET** /trace | Get Traces
[**trace_llm_call_end**](TracesApi.md#trace_llm_call_end) | **POST** /trace/llm/call_end | Trace Llm Call End
[**trace_llm_call_start**](TracesApi.md#trace_llm_call_start) | **POST** /trace/llm/call_start | Trace Llm Call Start


# **get_traces_trace_get**
> object get_traces_trace_get(page=page, page_size=page_size)

Get Traces

Retrieve paginated traces for all source app calls.

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
    api_instance = identity_auth_sdk.TracesApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 20 # int |  (optional) (default to 20)

    try:
        # Get Traces
        api_response = api_instance.get_traces_trace_get(page=page, page_size=page_size)
        print("The response of TracesApi->get_traces_trace_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TracesApi->get_traces_trace_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 20]

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

# **trace_llm_call_end**
> LLMCallEndedEvent trace_llm_call_end(llm_call_ended_request)

Trace Llm Call End

### Example

* Bearer Authentication (HTTPBearer):

```python
import identity_auth_sdk
from identity_auth_sdk.models.llm_call_ended_event import LLMCallEndedEvent
from identity_auth_sdk.models.llm_call_ended_request import LLMCallEndedRequest
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = identity_auth_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.TracesApi(api_client)
    llm_call_ended_request = identity_auth_sdk.LLMCallEndedRequest() # LLMCallEndedRequest | 

    try:
        # Trace Llm Call End
        api_response = api_instance.trace_llm_call_end(llm_call_ended_request)
        print("The response of TracesApi->trace_llm_call_end:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TracesApi->trace_llm_call_end: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **llm_call_ended_request** | [**LLMCallEndedRequest**](LLMCallEndedRequest.md)|  | 

### Return type

[**LLMCallEndedEvent**](LLMCallEndedEvent.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **trace_llm_call_start**
> LLMCallStartedEvent trace_llm_call_start(llm_call_started_request)

Trace Llm Call Start

### Example

* Bearer Authentication (HTTPBearer):

```python
import identity_auth_sdk
from identity_auth_sdk.models.llm_call_started_event import LLMCallStartedEvent
from identity_auth_sdk.models.llm_call_started_request import LLMCallStartedRequest
from identity_auth_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = identity_auth_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = identity_auth_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with identity_auth_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = identity_auth_sdk.TracesApi(api_client)
    llm_call_started_request = identity_auth_sdk.LLMCallStartedRequest() # LLMCallStartedRequest | 

    try:
        # Trace Llm Call Start
        api_response = api_instance.trace_llm_call_start(llm_call_started_request)
        print("The response of TracesApi->trace_llm_call_start:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TracesApi->trace_llm_call_start: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **llm_call_started_request** | [**LLMCallStartedRequest**](LLMCallStartedRequest.md)|  | 

### Return type

[**LLMCallStartedEvent**](LLMCallStartedEvent.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

