# UserInput

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Prompt** | **string** |  | 
**CreatedAt** | Pointer to **string** |  | [optional] [default to "2026-04-24T09:07:11.019131Z"]
**AppId** | **NullableString** |  | 
**Tag** | **NullableString** |  | 

## Methods

### NewUserInput

`func NewUserInput(prompt string, appId NullableString, tag NullableString, ) *UserInput`

NewUserInput instantiates a new UserInput object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewUserInputWithDefaults

`func NewUserInputWithDefaults() *UserInput`

NewUserInputWithDefaults instantiates a new UserInput object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *UserInput) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *UserInput) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *UserInput) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *UserInput) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *UserInput) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *UserInput) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetPrompt

`func (o *UserInput) GetPrompt() string`

GetPrompt returns the Prompt field if non-nil, zero value otherwise.

### GetPromptOk

`func (o *UserInput) GetPromptOk() (*string, bool)`

GetPromptOk returns a tuple with the Prompt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPrompt

`func (o *UserInput) SetPrompt(v string)`

SetPrompt sets Prompt field to given value.


### GetCreatedAt

`func (o *UserInput) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *UserInput) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *UserInput) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *UserInput) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.

### GetAppId

`func (o *UserInput) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *UserInput) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *UserInput) SetAppId(v string)`

SetAppId sets AppId field to given value.


### SetAppIdNil

`func (o *UserInput) SetAppIdNil(b bool)`

 SetAppIdNil sets the value for AppId to be an explicit nil

### UnsetAppId
`func (o *UserInput) UnsetAppId()`

UnsetAppId ensures that no value is present for AppId, not even an explicit nil
### GetTag

`func (o *UserInput) GetTag() string`

GetTag returns the Tag field if non-nil, zero value otherwise.

### GetTagOk

`func (o *UserInput) GetTagOk() (*string, bool)`

GetTagOk returns a tuple with the Tag field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTag

`func (o *UserInput) SetTag(v string)`

SetTag sets Tag field to given value.


### SetTagNil

`func (o *UserInput) SetTagNil(b bool)`

 SetTagNil sets the value for Tag to be an explicit nil

### UnsetTag
`func (o *UserInput) UnsetTag()`

UnsetTag ensures that no value is present for Tag, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


