# MultiAgentSystemCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**EnabledToolChecks** | Pointer to [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**Namespace** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewMultiAgentSystemCreateRequest

`func NewMultiAgentSystemCreateRequest(name string, ) *MultiAgentSystemCreateRequest`

NewMultiAgentSystemCreateRequest instantiates a new MultiAgentSystemCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemCreateRequestWithDefaults

`func NewMultiAgentSystemCreateRequestWithDefaults() *MultiAgentSystemCreateRequest`

NewMultiAgentSystemCreateRequestWithDefaults instantiates a new MultiAgentSystemCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemCreateRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemCreateRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemCreateRequest) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *MultiAgentSystemCreateRequest) GetEnabledToolChecks() ToolCheckFlags`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystemCreateRequest) GetEnabledToolChecksOk() (*ToolCheckFlags, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystemCreateRequest) SetEnabledToolChecks(v ToolCheckFlags)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystemCreateRequest) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### SetEnabledToolChecksNil

`func (o *MultiAgentSystemCreateRequest) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *MultiAgentSystemCreateRequest) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil
### GetNamespace

`func (o *MultiAgentSystemCreateRequest) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *MultiAgentSystemCreateRequest) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *MultiAgentSystemCreateRequest) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.

### HasNamespace

`func (o *MultiAgentSystemCreateRequest) HasNamespace() bool`

HasNamespace returns a boolean if a field has been set.

### SetNamespaceNil

`func (o *MultiAgentSystemCreateRequest) SetNamespaceNil(b bool)`

 SetNamespaceNil sets the value for Namespace to be an explicit nil

### UnsetNamespace
`func (o *MultiAgentSystemCreateRequest) UnsetNamespace()`

UnsetNamespace ensures that no value is present for Namespace, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


