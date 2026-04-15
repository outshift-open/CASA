# MultiAgentSystem

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Name** | **string** |  | 
**EnabledToolChecks** | Pointer to [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**AuthorizationServerId** | **NullableString** |  | 
**Namespace** | **NullableString** |  | 
**CreatedAt** | Pointer to **string** |  | [optional] [default to "2026-04-15T15:18:00.589239Z"]

## Methods

### NewMultiAgentSystem

`func NewMultiAgentSystem(name string, authorizationServerId NullableString, namespace NullableString, ) *MultiAgentSystem`

NewMultiAgentSystem instantiates a new MultiAgentSystem object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemWithDefaults

`func NewMultiAgentSystemWithDefaults() *MultiAgentSystem`

NewMultiAgentSystemWithDefaults instantiates a new MultiAgentSystem object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *MultiAgentSystem) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *MultiAgentSystem) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *MultiAgentSystem) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *MultiAgentSystem) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *MultiAgentSystem) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *MultiAgentSystem) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetName

`func (o *MultiAgentSystem) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystem) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystem) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *MultiAgentSystem) GetEnabledToolChecks() ToolCheckFlags`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MultiAgentSystem) GetEnabledToolChecksOk() (*ToolCheckFlags, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MultiAgentSystem) SetEnabledToolChecks(v ToolCheckFlags)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *MultiAgentSystem) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### SetEnabledToolChecksNil

`func (o *MultiAgentSystem) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *MultiAgentSystem) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil
### GetAuthorizationServerId

`func (o *MultiAgentSystem) GetAuthorizationServerId() string`

GetAuthorizationServerId returns the AuthorizationServerId field if non-nil, zero value otherwise.

### GetAuthorizationServerIdOk

`func (o *MultiAgentSystem) GetAuthorizationServerIdOk() (*string, bool)`

GetAuthorizationServerIdOk returns a tuple with the AuthorizationServerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuthorizationServerId

`func (o *MultiAgentSystem) SetAuthorizationServerId(v string)`

SetAuthorizationServerId sets AuthorizationServerId field to given value.


### SetAuthorizationServerIdNil

`func (o *MultiAgentSystem) SetAuthorizationServerIdNil(b bool)`

 SetAuthorizationServerIdNil sets the value for AuthorizationServerId to be an explicit nil

### UnsetAuthorizationServerId
`func (o *MultiAgentSystem) UnsetAuthorizationServerId()`

UnsetAuthorizationServerId ensures that no value is present for AuthorizationServerId, not even an explicit nil
### GetNamespace

`func (o *MultiAgentSystem) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *MultiAgentSystem) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *MultiAgentSystem) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### SetNamespaceNil

`func (o *MultiAgentSystem) SetNamespaceNil(b bool)`

 SetNamespaceNil sets the value for Namespace to be an explicit nil

### UnsetNamespace
`func (o *MultiAgentSystem) UnsetNamespace()`

UnsetNamespace ensures that no value is present for Namespace, not even an explicit nil
### GetCreatedAt

`func (o *MultiAgentSystem) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *MultiAgentSystem) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *MultiAgentSystem) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *MultiAgentSystem) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


