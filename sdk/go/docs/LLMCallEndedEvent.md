# LLMCallEndedEvent

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
**Response** | **string** |  | 
**Tools** | **NullableString** |  | 

## Methods

### NewLLMCallEndedEvent

`func NewLLMCallEndedEvent(userInputId string, callId string, token string, appId string, response string, tools NullableString, ) *LLMCallEndedEvent`

NewLLMCallEndedEvent instantiates a new LLMCallEndedEvent object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLLMCallEndedEventWithDefaults

`func NewLLMCallEndedEventWithDefaults() *LLMCallEndedEvent`

NewLLMCallEndedEventWithDefaults instantiates a new LLMCallEndedEvent object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *LLMCallEndedEvent) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *LLMCallEndedEvent) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *LLMCallEndedEvent) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *LLMCallEndedEvent) HasId() bool`

HasId returns a boolean if a field has been set.

### GetUserInputId

`func (o *LLMCallEndedEvent) GetUserInputId() string`

GetUserInputId returns the UserInputId field if non-nil, zero value otherwise.

### GetUserInputIdOk

`func (o *LLMCallEndedEvent) GetUserInputIdOk() (*string, bool)`

GetUserInputIdOk returns a tuple with the UserInputId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserInputId

`func (o *LLMCallEndedEvent) SetUserInputId(v string)`

SetUserInputId sets UserInputId field to given value.


### GetCreatedAt

`func (o *LLMCallEndedEvent) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *LLMCallEndedEvent) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *LLMCallEndedEvent) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *LLMCallEndedEvent) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.

### GetCallId

`func (o *LLMCallEndedEvent) GetCallId() string`

GetCallId returns the CallId field if non-nil, zero value otherwise.

### GetCallIdOk

`func (o *LLMCallEndedEvent) GetCallIdOk() (*string, bool)`

GetCallIdOk returns a tuple with the CallId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCallId

`func (o *LLMCallEndedEvent) SetCallId(v string)`

SetCallId sets CallId field to given value.


### GetToken

`func (o *LLMCallEndedEvent) GetToken() string`

GetToken returns the Token field if non-nil, zero value otherwise.

### GetTokenOk

`func (o *LLMCallEndedEvent) GetTokenOk() (*string, bool)`

GetTokenOk returns a tuple with the Token field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetToken

`func (o *LLMCallEndedEvent) SetToken(v string)`

SetToken sets Token field to given value.


### GetAppId

`func (o *LLMCallEndedEvent) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *LLMCallEndedEvent) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *LLMCallEndedEvent) SetAppId(v string)`

SetAppId sets AppId field to given value.


### GetMasId

`func (o *LLMCallEndedEvent) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *LLMCallEndedEvent) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *LLMCallEndedEvent) SetMasId(v string)`

SetMasId sets MasId field to given value.

### HasMasId

`func (o *LLMCallEndedEvent) HasMasId() bool`

HasMasId returns a boolean if a field has been set.

### SetMasIdNil

`func (o *LLMCallEndedEvent) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *LLMCallEndedEvent) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetResponse

`func (o *LLMCallEndedEvent) GetResponse() string`

GetResponse returns the Response field if non-nil, zero value otherwise.

### GetResponseOk

`func (o *LLMCallEndedEvent) GetResponseOk() (*string, bool)`

GetResponseOk returns a tuple with the Response field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResponse

`func (o *LLMCallEndedEvent) SetResponse(v string)`

SetResponse sets Response field to given value.


### GetTools

`func (o *LLMCallEndedEvent) GetTools() string`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *LLMCallEndedEvent) GetToolsOk() (*string, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *LLMCallEndedEvent) SetTools(v string)`

SetTools sets Tools field to given value.


### SetToolsNil

`func (o *LLMCallEndedEvent) SetToolsNil(b bool)`

 SetToolsNil sets the value for Tools to be an explicit nil

### UnsetTools
`func (o *LLMCallEndedEvent) UnsetTools()`

UnsetTools ensures that no value is present for Tools, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


