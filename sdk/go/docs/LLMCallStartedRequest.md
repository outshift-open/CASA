# LLMCallStartedRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CallId** | **string** |  | 
**Prompt** | **string** |  | 
**Tools** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewLLMCallStartedRequest

`func NewLLMCallStartedRequest(callId string, prompt string, ) *LLMCallStartedRequest`

NewLLMCallStartedRequest instantiates a new LLMCallStartedRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLLMCallStartedRequestWithDefaults

`func NewLLMCallStartedRequestWithDefaults() *LLMCallStartedRequest`

NewLLMCallStartedRequestWithDefaults instantiates a new LLMCallStartedRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCallId

`func (o *LLMCallStartedRequest) GetCallId() string`

GetCallId returns the CallId field if non-nil, zero value otherwise.

### GetCallIdOk

`func (o *LLMCallStartedRequest) GetCallIdOk() (*string, bool)`

GetCallIdOk returns a tuple with the CallId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCallId

`func (o *LLMCallStartedRequest) SetCallId(v string)`

SetCallId sets CallId field to given value.


### GetPrompt

`func (o *LLMCallStartedRequest) GetPrompt() string`

GetPrompt returns the Prompt field if non-nil, zero value otherwise.

### GetPromptOk

`func (o *LLMCallStartedRequest) GetPromptOk() (*string, bool)`

GetPromptOk returns a tuple with the Prompt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPrompt

`func (o *LLMCallStartedRequest) SetPrompt(v string)`

SetPrompt sets Prompt field to given value.


### GetTools

`func (o *LLMCallStartedRequest) GetTools() string`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *LLMCallStartedRequest) GetToolsOk() (*string, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *LLMCallStartedRequest) SetTools(v string)`

SetTools sets Tools field to given value.

### HasTools

`func (o *LLMCallStartedRequest) HasTools() bool`

HasTools returns a boolean if a field has been set.

### SetToolsNil

`func (o *LLMCallStartedRequest) SetToolsNil(b bool)`

 SetToolsNil sets the value for Tools to be an explicit nil

### UnsetTools
`func (o *LLMCallStartedRequest) UnsetTools()`

UnsetTools ensures that no value is present for Tools, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


