# LLMCallStartedEvent

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **string** |  | [optional] 
**UserInputId** | **string** |  | 
**CreatedAt** | Pointer to **string** |  | [optional] 
**CallId** | **string** |  | 
**Token** | **string** |  | 
**AppId** | **string** |  | 
**MasId** | Pointer to **NullableString** |  | [optional] 
**Prompt** | **string** |  | 
**Tools** | **NullableString** |  | 

## Methods

### NewLLMCallStartedEvent

`func NewLLMCallStartedEvent(userInputId string, callId string, token string, appId string, prompt string, tools NullableString, ) *LLMCallStartedEvent`

NewLLMCallStartedEvent instantiates a new LLMCallStartedEvent object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLLMCallStartedEventWithDefaults

`func NewLLMCallStartedEventWithDefaults() *LLMCallStartedEvent`

NewLLMCallStartedEventWithDefaults instantiates a new LLMCallStartedEvent object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *LLMCallStartedEvent) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *LLMCallStartedEvent) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *LLMCallStartedEvent) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *LLMCallStartedEvent) HasId() bool`

HasId returns a boolean if a field has been set.

### GetUserInputId

`func (o *LLMCallStartedEvent) GetUserInputId() string`

GetUserInputId returns the UserInputId field if non-nil, zero value otherwise.

### GetUserInputIdOk

`func (o *LLMCallStartedEvent) GetUserInputIdOk() (*string, bool)`

GetUserInputIdOk returns a tuple with the UserInputId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserInputId

`func (o *LLMCallStartedEvent) SetUserInputId(v string)`

SetUserInputId sets UserInputId field to given value.


### GetCreatedAt

`func (o *LLMCallStartedEvent) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *LLMCallStartedEvent) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *LLMCallStartedEvent) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *LLMCallStartedEvent) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.

### GetCallId

`func (o *LLMCallStartedEvent) GetCallId() string`

GetCallId returns the CallId field if non-nil, zero value otherwise.

### GetCallIdOk

`func (o *LLMCallStartedEvent) GetCallIdOk() (*string, bool)`

GetCallIdOk returns a tuple with the CallId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCallId

`func (o *LLMCallStartedEvent) SetCallId(v string)`

SetCallId sets CallId field to given value.


### GetToken

`func (o *LLMCallStartedEvent) GetToken() string`

GetToken returns the Token field if non-nil, zero value otherwise.

### GetTokenOk

`func (o *LLMCallStartedEvent) GetTokenOk() (*string, bool)`

GetTokenOk returns a tuple with the Token field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetToken

`func (o *LLMCallStartedEvent) SetToken(v string)`

SetToken sets Token field to given value.


### GetAppId

`func (o *LLMCallStartedEvent) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *LLMCallStartedEvent) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *LLMCallStartedEvent) SetAppId(v string)`

SetAppId sets AppId field to given value.


### GetMasId

`func (o *LLMCallStartedEvent) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *LLMCallStartedEvent) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *LLMCallStartedEvent) SetMasId(v string)`

SetMasId sets MasId field to given value.

### HasMasId

`func (o *LLMCallStartedEvent) HasMasId() bool`

HasMasId returns a boolean if a field has been set.

### SetMasIdNil

`func (o *LLMCallStartedEvent) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *LLMCallStartedEvent) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetPrompt

`func (o *LLMCallStartedEvent) GetPrompt() string`

GetPrompt returns the Prompt field if non-nil, zero value otherwise.

### GetPromptOk

`func (o *LLMCallStartedEvent) GetPromptOk() (*string, bool)`

GetPromptOk returns a tuple with the Prompt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPrompt

`func (o *LLMCallStartedEvent) SetPrompt(v string)`

SetPrompt sets Prompt field to given value.


### GetTools

`func (o *LLMCallStartedEvent) GetTools() string`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *LLMCallStartedEvent) GetToolsOk() (*string, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *LLMCallStartedEvent) SetTools(v string)`

SetTools sets Tools field to given value.


### SetToolsNil

`func (o *LLMCallStartedEvent) SetToolsNil(b bool)`

 SetToolsNil sets the value for Tools to be an explicit nil

### UnsetTools
`func (o *LLMCallStartedEvent) UnsetTools()`

UnsetTools ensures that no value is present for Tools, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


