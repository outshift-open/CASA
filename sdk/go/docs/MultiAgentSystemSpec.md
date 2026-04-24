# MultiAgentSystemSpec

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Display name of the Multi-Agent System | 
**AuthorizationServer** | Pointer to **string** | Keycloak realm name for this MAS | [optional] [default to ""]
**EnabledToolChecks** | Pointer to [**[]ToolCheckType**](ToolCheckType.md) | List of enabled tool check types | [optional] 
**Apps** | Pointer to [**[]AppSpec**](AppSpec.md) | List of applications in this MAS | [optional] 
**LlmHost** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewMultiAgentSystemSpec

`func NewMultiAgentSystemSpec(name string, ) *MultiAgentSystemSpec`

NewMultiAgentSystemSpec instantiates a new MultiAgentSystemSpec object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemSpecWithDefaults

`func NewMultiAgentSystemSpecWithDefaults() *MultiAgentSystemSpec`

NewMultiAgentSystemSpecWithDefaults instantiates a new MultiAgentSystemSpec object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemSpec) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemSpec) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemSpec) SetName(v string)`

SetName sets Name field to given value.


### GetAuthorizationServer

`func (o *MultiAgentSystemSpec) GetAuthorizationServer() string`

GetAuthorizationServer returns the AuthorizationServer field if non-nil, zero value otherwise.

### GetAuthorizationServerOk

`func (o *MultiAgentSystemSpec) GetAuthorizationServerOk() (*string, bool)`

GetAuthorizationServerOk returns a tuple with the AuthorizationServer field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuthorizationServer

`func (o *MultiAgentSystemSpec) SetAuthorizationServer(v string)`

SetAuthorizationServer sets AuthorizationServer field to given value.

### HasAuthorizationServer

`func (o *MultiAgentSystemSpec) HasAuthorizationServer() bool`

HasAuthorizationServer returns a boolean if a field has been set.

### GetEnabledToolChecks

`func (o *MultiAgentSystemSpec) GetEnabledToolChecks() []ToolCheckType`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystemSpec) GetEnabledToolChecksOk() (*[]ToolCheckType, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystemSpec) SetEnabledToolChecks(v []ToolCheckType)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystemSpec) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### GetApps

`func (o *MultiAgentSystemSpec) GetApps() []AppSpec`

GetApps returns the Apps field if non-nil, zero value otherwise.

### GetAppsOk

`func (o *MultiAgentSystemSpec) GetAppsOk() (*[]AppSpec, bool)`

GetAppsOk returns a tuple with the Apps field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApps

`func (o *MultiAgentSystemSpec) SetApps(v []AppSpec)`

SetApps sets Apps field to given value.

### HasApps

`func (o *MultiAgentSystemSpec) HasApps() bool`

HasApps returns a boolean if a field has been set.

### GetLlmHost

`func (o *MultiAgentSystemSpec) GetLlmHost() string`

GetLlmHost returns the LlmHost field if non-nil, zero value otherwise.

### GetLlmHostOk

`func (o *MultiAgentSystemSpec) GetLlmHostOk() (*string, bool)`

GetLlmHostOk returns a tuple with the LlmHost field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLlmHost

`func (o *MultiAgentSystemSpec) SetLlmHost(v string)`

SetLlmHost sets LlmHost field to given value.

### HasLlmHost

`func (o *MultiAgentSystemSpec) HasLlmHost() bool`

HasLlmHost returns a boolean if a field has been set.

### SetLlmHostNil

`func (o *MultiAgentSystemSpec) SetLlmHostNil(b bool)`

 SetLlmHostNil sets the value for LlmHost to be an explicit nil

### UnsetLlmHost
`func (o *MultiAgentSystemSpec) UnsetLlmHost()`

UnsetLlmHost ensures that no value is present for LlmHost, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


