# MultiAgentSystemUpdateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**EnabledToolChecks** | Pointer to [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 

## Methods

### NewMultiAgentSystemUpdateRequest

`func NewMultiAgentSystemUpdateRequest(name string, ) *MultiAgentSystemUpdateRequest`

NewMultiAgentSystemUpdateRequest instantiates a new MultiAgentSystemUpdateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemUpdateRequestWithDefaults

`func NewMultiAgentSystemUpdateRequestWithDefaults() *MultiAgentSystemUpdateRequest`

NewMultiAgentSystemUpdateRequestWithDefaults instantiates a new MultiAgentSystemUpdateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemUpdateRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemUpdateRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemUpdateRequest) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *MultiAgentSystemUpdateRequest) GetEnabledToolChecks() ToolCheckFlags`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystemUpdateRequest) GetEnabledToolChecksOk() (*ToolCheckFlags, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystemUpdateRequest) SetEnabledToolChecks(v ToolCheckFlags)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystemUpdateRequest) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### SetEnabledToolChecksNil

`func (o *MultiAgentSystemUpdateRequest) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *MultiAgentSystemUpdateRequest) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


