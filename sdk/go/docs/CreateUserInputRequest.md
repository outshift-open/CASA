# CreateUserInputRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Prompt** | **string** |  | 
**AppId** | **string** |  | 
**Tag** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewCreateUserInputRequest

`func NewCreateUserInputRequest(prompt string, appId string, ) *CreateUserInputRequest`

NewCreateUserInputRequest instantiates a new CreateUserInputRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCreateUserInputRequestWithDefaults

`func NewCreateUserInputRequestWithDefaults() *CreateUserInputRequest`

NewCreateUserInputRequestWithDefaults instantiates a new CreateUserInputRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPrompt

`func (o *CreateUserInputRequest) GetPrompt() string`

GetPrompt returns the Prompt field if non-nil, zero value otherwise.

### GetPromptOk

`func (o *CreateUserInputRequest) GetPromptOk() (*string, bool)`

GetPromptOk returns a tuple with the Prompt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPrompt

`func (o *CreateUserInputRequest) SetPrompt(v string)`

SetPrompt sets Prompt field to given value.


### GetAppId

`func (o *CreateUserInputRequest) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *CreateUserInputRequest) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *CreateUserInputRequest) SetAppId(v string)`

SetAppId sets AppId field to given value.


### GetTag

`func (o *CreateUserInputRequest) GetTag() string`

GetTag returns the Tag field if non-nil, zero value otherwise.

### GetTagOk

`func (o *CreateUserInputRequest) GetTagOk() (*string, bool)`

GetTagOk returns a tuple with the Tag field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTag

`func (o *CreateUserInputRequest) SetTag(v string)`

SetTag sets Tag field to given value.

### HasTag

`func (o *CreateUserInputRequest) HasTag() bool`

HasTag returns a boolean if a field has been set.

### SetTagNil

`func (o *CreateUserInputRequest) SetTagNil(b bool)`

 SetTagNil sets the value for Tag to be an explicit nil

### UnsetTag
`func (o *CreateUserInputRequest) UnsetTag()`

UnsetTag ensures that no value is present for Tag, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


