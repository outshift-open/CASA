# LLMCallEndedRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CallId** | **string** |  | 
**Response** | **string** |  | 
**Tools** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewLLMCallEndedRequest

`func NewLLMCallEndedRequest(callId string, response string, ) *LLMCallEndedRequest`

NewLLMCallEndedRequest instantiates a new LLMCallEndedRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLLMCallEndedRequestWithDefaults

`func NewLLMCallEndedRequestWithDefaults() *LLMCallEndedRequest`

NewLLMCallEndedRequestWithDefaults instantiates a new LLMCallEndedRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCallId

`func (o *LLMCallEndedRequest) GetCallId() string`

GetCallId returns the CallId field if non-nil, zero value otherwise.

### GetCallIdOk

`func (o *LLMCallEndedRequest) GetCallIdOk() (*string, bool)`

GetCallIdOk returns a tuple with the CallId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCallId

`func (o *LLMCallEndedRequest) SetCallId(v string)`

SetCallId sets CallId field to given value.


### GetResponse

`func (o *LLMCallEndedRequest) GetResponse() string`

GetResponse returns the Response field if non-nil, zero value otherwise.

### GetResponseOk

`func (o *LLMCallEndedRequest) GetResponseOk() (*string, bool)`

GetResponseOk returns a tuple with the Response field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResponse

`func (o *LLMCallEndedRequest) SetResponse(v string)`

SetResponse sets Response field to given value.


### GetTools

`func (o *LLMCallEndedRequest) GetTools() string`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *LLMCallEndedRequest) GetToolsOk() (*string, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *LLMCallEndedRequest) SetTools(v string)`

SetTools sets Tools field to given value.

### HasTools

`func (o *LLMCallEndedRequest) HasTools() bool`

HasTools returns a boolean if a field has been set.

### SetToolsNil

`func (o *LLMCallEndedRequest) SetToolsNil(b bool)`

 SetToolsNil sets the value for Tools to be an explicit nil

### UnsetTools
`func (o *LLMCallEndedRequest) UnsetTools()`

UnsetTools ensures that no value is present for Tools, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


