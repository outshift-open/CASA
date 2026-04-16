# MultiAgentSystemSpecInput

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Display name of the Multi-Agent System | 
**EnabledToolChecks** | Pointer to [**[]ToolCheckType**](ToolCheckType.md) | List of enabled tool check types | [optional] 
**Apps** | Pointer to [**[]AppSpec**](AppSpec.md) | List of applications in this MAS | [optional] 

## Methods

### NewMultiAgentSystemSpecInput

`func NewMultiAgentSystemSpecInput(name string, ) *MultiAgentSystemSpecInput`

NewMultiAgentSystemSpecInput instantiates a new MultiAgentSystemSpecInput object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemSpecInputWithDefaults

`func NewMultiAgentSystemSpecInputWithDefaults() *MultiAgentSystemSpecInput`

NewMultiAgentSystemSpecInputWithDefaults instantiates a new MultiAgentSystemSpecInput object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemSpecInput) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemSpecInput) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemSpecInput) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *MultiAgentSystemSpecInput) GetEnabledToolChecks() []ToolCheckType`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystemSpecInput) GetEnabledToolChecksOk() (*[]ToolCheckType, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystemSpecInput) SetEnabledToolChecks(v []ToolCheckType)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystemSpecInput) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### GetApps

`func (o *MultiAgentSystemSpecInput) GetApps() []AppSpec`

GetApps returns the Apps field if non-nil, zero value otherwise.

### GetAppsOk

`func (o *MultiAgentSystemSpecInput) GetAppsOk() (*[]AppSpec, bool)`

GetAppsOk returns a tuple with the Apps field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApps

`func (o *MultiAgentSystemSpecInput) SetApps(v []AppSpec)`

SetApps sets Apps field to given value.

### HasApps

`func (o *MultiAgentSystemSpecInput) HasApps() bool`

HasApps returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


