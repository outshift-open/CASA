# identity_auth_sdk.UserInputsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_user_input**](UserInputsApi.md#create_user_input) | **POST** /user-inputs | Create User Input
[**get_user_input_by_tag**](UserInputsApi.md#get_user_input_by_tag) | **GET** /user_inputs/get_by_tag/{tag} | Get User Input By Tag


# **create_user_input**
> UserInput create_user_input(create_user_input_request)

Create User Input

Create a new User Input.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.create_user_input_request import CreateUserInputRequest
from identity_auth_sdk.models.user_input import UserInput
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
    api_instance = identity_auth_sdk.UserInputsApi(api_client)
    create_user_input_request = identity_auth_sdk.CreateUserInputRequest() # CreateUserInputRequest | 

    try:
        # Create User Input
        api_response = api_instance.create_user_input(create_user_input_request)
        print("The response of UserInputsApi->create_user_input:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserInputsApi->create_user_input: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_user_input_request** | [**CreateUserInputRequest**](CreateUserInputRequest.md)|  | 

### Return type

[**UserInput**](UserInput.md)

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

# **get_user_input_by_tag**
> UserInput get_user_input_by_tag(tag)

Get User Input By Tag

Get a UserInput by tag.

### Example


```python
import identity_auth_sdk
from identity_auth_sdk.models.user_input import UserInput
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
    api_instance = identity_auth_sdk.UserInputsApi(api_client)
    tag = 'tag_example' # str | 

    try:
        # Get User Input By Tag
        api_response = api_instance.get_user_input_by_tag(tag)
        print("The response of UserInputsApi->get_user_input_by_tag:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserInputsApi->get_user_input_by_tag: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tag** | **str**|  | 

### Return type

[**UserInput**](UserInput.md)

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

