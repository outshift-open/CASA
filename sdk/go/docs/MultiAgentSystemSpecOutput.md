# MultiAgentSystemSpecOutput

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Display name of the Multi-Agent System | 
**EnabledToolChecks** | Pointer to [**[]ToolCheckType**](ToolCheckType.md) | List of enabled tool check types | [optional] 
**Apps** | Pointer to [**[]AppSpec**](AppSpec.md) | List of applications in this MAS | [optional] 

## Methods

### NewMultiAgentSystemSpecOutput

`func NewMultiAgentSystemSpecOutput(name string, ) *MultiAgentSystemSpecOutput`

NewMultiAgentSystemSpecOutput instantiates a new MultiAgentSystemSpecOutput object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemSpecOutputWithDefaults

`func NewMultiAgentSystemSpecOutputWithDefaults() *MultiAgentSystemSpecOutput`

NewMultiAgentSystemSpecOutputWithDefaults instantiates a new MultiAgentSystemSpecOutput object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemSpecOutput) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemSpecOutput) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemSpecOutput) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *MultiAgentSystemSpecOutput) GetEnabledToolChecks() []ToolCheckType`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystemSpecOutput) GetEnabledToolChecksOk() (*[]ToolCheckType, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystemSpecOutput) SetEnabledToolChecks(v []ToolCheckType)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystemSpecOutput) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### GetApps

`func (o *MultiAgentSystemSpecOutput) GetApps() []AppSpec`

GetApps returns the Apps field if non-nil, zero value otherwise.

### GetAppsOk

`func (o *MultiAgentSystemSpecOutput) GetAppsOk() (*[]AppSpec, bool)`

GetAppsOk returns a tuple with the Apps field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApps

`func (o *MultiAgentSystemSpecOutput) SetApps(v []AppSpec)`

SetApps sets Apps field to given value.

### HasApps

`func (o *MultiAgentSystemSpecOutput) HasApps() bool`

HasApps returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


