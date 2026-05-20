# LlmCallMappingStoreRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**TraceId** | **string** |  | 
**Token** | **string** |  | 
**Request** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewLlmCallMappingStoreRequest

`func NewLlmCallMappingStoreRequest(id string, traceId string, token string, ) *LlmCallMappingStoreRequest`

NewLlmCallMappingStoreRequest instantiates a new LlmCallMappingStoreRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLlmCallMappingStoreRequestWithDefaults

`func NewLlmCallMappingStoreRequestWithDefaults() *LlmCallMappingStoreRequest`

NewLlmCallMappingStoreRequestWithDefaults instantiates a new LlmCallMappingStoreRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *LlmCallMappingStoreRequest) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *LlmCallMappingStoreRequest) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *LlmCallMappingStoreRequest) SetId(v string)`

SetId sets Id field to given value.


### GetTraceId

`func (o *LlmCallMappingStoreRequest) GetTraceId() string`

GetTraceId returns the TraceId field if non-nil, zero value otherwise.

### GetTraceIdOk

`func (o *LlmCallMappingStoreRequest) GetTraceIdOk() (*string, bool)`

GetTraceIdOk returns a tuple with the TraceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraceId

`func (o *LlmCallMappingStoreRequest) SetTraceId(v string)`

SetTraceId sets TraceId field to given value.


### GetToken

`func (o *LlmCallMappingStoreRequest) GetToken() string`

GetToken returns the Token field if non-nil, zero value otherwise.

### GetTokenOk

`func (o *LlmCallMappingStoreRequest) GetTokenOk() (*string, bool)`

GetTokenOk returns a tuple with the Token field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetToken

`func (o *LlmCallMappingStoreRequest) SetToken(v string)`

SetToken sets Token field to given value.


### GetRequest

`func (o *LlmCallMappingStoreRequest) GetRequest() string`

GetRequest returns the Request field if non-nil, zero value otherwise.

### GetRequestOk

`func (o *LlmCallMappingStoreRequest) GetRequestOk() (*string, bool)`

GetRequestOk returns a tuple with the Request field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRequest

`func (o *LlmCallMappingStoreRequest) SetRequest(v string)`

SetRequest sets Request field to given value.

### HasRequest

`func (o *LlmCallMappingStoreRequest) HasRequest() bool`

HasRequest returns a boolean if a field has been set.

### SetRequestNil

`func (o *LlmCallMappingStoreRequest) SetRequestNil(b bool)`

 SetRequestNil sets the value for Request to be an explicit nil

### UnsetRequest
`func (o *LlmCallMappingStoreRequest) UnsetRequest()`

UnsetRequest ensures that no value is present for Request, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


