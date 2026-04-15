# \UserInputsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateUserInput**](UserInputsAPI.md#CreateUserInput) | **Post** /user-inputs | Create User Input
[**GetUserInputByTag**](UserInputsAPI.md#GetUserInputByTag) | **Get** /user_inputs/get_by_tag/{tag} | Get User Input By Tag



## CreateUserInput

> UserInput CreateUserInput(ctx).CreateUserInputRequest(createUserInputRequest).Execute()

Create User Input



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
	createUserInputRequest := *openapiclient.NewCreateUserInputRequest("Prompt_example", "AppId_example") // CreateUserInputRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UserInputsAPI.CreateUserInput(context.Background()).CreateUserInputRequest(createUserInputRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UserInputsAPI.CreateUserInput``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateUserInput`: UserInput
	fmt.Fprintf(os.Stdout, "Response from `UserInputsAPI.CreateUserInput`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateUserInputRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **createUserInputRequest** | [**CreateUserInputRequest**](CreateUserInputRequest.md) |  | 

### Return type

[**UserInput**](UserInput.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetUserInputByTag

> UserInput GetUserInputByTag(ctx, tag).Execute()

Get User Input By Tag



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
	tag := "tag_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UserInputsAPI.GetUserInputByTag(context.Background(), tag).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UserInputsAPI.GetUserInputByTag``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetUserInputByTag`: UserInput
	fmt.Fprintf(os.Stdout, "Response from `UserInputsAPI.GetUserInputByTag`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tag** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetUserInputByTagRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**UserInput**](UserInput.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

