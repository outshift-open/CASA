# MultiAgentSystem

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Name** | **string** |  | 
**K8sName** | Pointer to **NullableString** |  | [optional] 
**EnabledToolChecks** | Pointer to [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**AuthorizationServerId** | **NullableString** |  | 
**Namespace** | **NullableString** |  | 
**CreatedAt** | Pointer to **time.Time** |  | [optional] 
**DeletedAt** | Pointer to **NullableTime** |  | [optional] 

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


### GetK8sName

`func (o *MultiAgentSystem) GetK8sName() string`

GetK8sName returns the K8sName field if non-nil, zero value otherwise.

### GetK8sNameOk

`func (o *MultiAgentSystem) GetK8sNameOk() (*string, bool)`

GetK8sNameOk returns a tuple with the K8sName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetK8sName

`func (o *MultiAgentSystem) SetK8sName(v string)`

SetK8sName sets K8sName field to given value.

### HasK8sName

`func (o *MultiAgentSystem) HasK8sName() bool`

HasK8sName returns a boolean if a field has been set.

### SetK8sNameNil

`func (o *MultiAgentSystem) SetK8sNameNil(b bool)`

 SetK8sNameNil sets the value for K8sName to be an explicit nil

### UnsetK8sName
`func (o *MultiAgentSystem) UnsetK8sName()`

UnsetK8sName ensures that no value is present for K8sName, not even an explicit nil
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

`func (o *MultiAgentSystem) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *MultiAgentSystem) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *MultiAgentSystem) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *MultiAgentSystem) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.

### GetDeletedAt

`func (o *MultiAgentSystem) GetDeletedAt() time.Time`

GetDeletedAt returns the DeletedAt field if non-nil, zero value otherwise.

### GetDeletedAtOk

`func (o *MultiAgentSystem) GetDeletedAtOk() (*time.Time, bool)`

GetDeletedAtOk returns a tuple with the DeletedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDeletedAt

`func (o *MultiAgentSystem) SetDeletedAt(v time.Time)`

SetDeletedAt sets DeletedAt field to given value.

### HasDeletedAt

`func (o *MultiAgentSystem) HasDeletedAt() bool`

HasDeletedAt returns a boolean if a field has been set.

### SetDeletedAtNil

`func (o *MultiAgentSystem) SetDeletedAtNil(b bool)`

 SetDeletedAtNil sets the value for DeletedAt to be an explicit nil

### UnsetDeletedAt
`func (o *MultiAgentSystem) UnsetDeletedAt()`

UnsetDeletedAt ensures that no value is present for DeletedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


