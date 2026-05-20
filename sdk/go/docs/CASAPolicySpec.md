# CASAPolicySpec

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TargetRef** | [**CASAPolicyTargetRef**](CASAPolicyTargetRef.md) | Workload this policy applies to | 
**AllowedProtocols** | Pointer to **[]string** | Protocols allowed for this workload: mcp, a2a, http | [optional] 
**AllowedEndpoints** | Pointer to [**[]CASAPolicyAllowedEndpoint**](CASAPolicyAllowedEndpoint.md) | K8s services this workload may communicate with | [optional] 
**LlmEndpoint** | Pointer to [**NullableCASAPolicyLlmEndpoint**](CASAPolicyLlmEndpoint.md) | Allowed external LLM endpoint | [optional] 

## Methods

### NewCASAPolicySpec

`func NewCASAPolicySpec(targetRef CASAPolicyTargetRef, ) *CASAPolicySpec`

NewCASAPolicySpec instantiates a new CASAPolicySpec object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCASAPolicySpecWithDefaults

`func NewCASAPolicySpecWithDefaults() *CASAPolicySpec`

NewCASAPolicySpecWithDefaults instantiates a new CASAPolicySpec object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTargetRef

`func (o *CASAPolicySpec) GetTargetRef() CASAPolicyTargetRef`

GetTargetRef returns the TargetRef field if non-nil, zero value otherwise.

### GetTargetRefOk

`func (o *CASAPolicySpec) GetTargetRefOk() (*CASAPolicyTargetRef, bool)`

GetTargetRefOk returns a tuple with the TargetRef field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetRef

`func (o *CASAPolicySpec) SetTargetRef(v CASAPolicyTargetRef)`

SetTargetRef sets TargetRef field to given value.


### GetAllowedProtocols

`func (o *CASAPolicySpec) GetAllowedProtocols() []string`

GetAllowedProtocols returns the AllowedProtocols field if non-nil, zero value otherwise.

### GetAllowedProtocolsOk

`func (o *CASAPolicySpec) GetAllowedProtocolsOk() (*[]string, bool)`

GetAllowedProtocolsOk returns a tuple with the AllowedProtocols field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllowedProtocols

`func (o *CASAPolicySpec) SetAllowedProtocols(v []string)`

SetAllowedProtocols sets AllowedProtocols field to given value.

### HasAllowedProtocols

`func (o *CASAPolicySpec) HasAllowedProtocols() bool`

HasAllowedProtocols returns a boolean if a field has been set.

### GetAllowedEndpoints

`func (o *CASAPolicySpec) GetAllowedEndpoints() []CASAPolicyAllowedEndpoint`

GetAllowedEndpoints returns the AllowedEndpoints field if non-nil, zero value otherwise.

### GetAllowedEndpointsOk

`func (o *CASAPolicySpec) GetAllowedEndpointsOk() (*[]CASAPolicyAllowedEndpoint, bool)`

GetAllowedEndpointsOk returns a tuple with the AllowedEndpoints field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllowedEndpoints

`func (o *CASAPolicySpec) SetAllowedEndpoints(v []CASAPolicyAllowedEndpoint)`

SetAllowedEndpoints sets AllowedEndpoints field to given value.

### HasAllowedEndpoints

`func (o *CASAPolicySpec) HasAllowedEndpoints() bool`

HasAllowedEndpoints returns a boolean if a field has been set.

### GetLlmEndpoint

`func (o *CASAPolicySpec) GetLlmEndpoint() CASAPolicyLlmEndpoint`

GetLlmEndpoint returns the LlmEndpoint field if non-nil, zero value otherwise.

### GetLlmEndpointOk

`func (o *CASAPolicySpec) GetLlmEndpointOk() (*CASAPolicyLlmEndpoint, bool)`

GetLlmEndpointOk returns a tuple with the LlmEndpoint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLlmEndpoint

`func (o *CASAPolicySpec) SetLlmEndpoint(v CASAPolicyLlmEndpoint)`

SetLlmEndpoint sets LlmEndpoint field to given value.

### HasLlmEndpoint

`func (o *CASAPolicySpec) HasLlmEndpoint() bool`

HasLlmEndpoint returns a boolean if a field has been set.

### SetLlmEndpointNil

`func (o *CASAPolicySpec) SetLlmEndpointNil(b bool)`

 SetLlmEndpointNil sets the value for LlmEndpoint to be an explicit nil

### UnsetLlmEndpoint
`func (o *CASAPolicySpec) UnsetLlmEndpoint()`

UnsetLlmEndpoint ensures that no value is present for LlmEndpoint, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


