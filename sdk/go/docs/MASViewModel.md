# MASViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**Namespace** | **NullableString** |  | 
**K8sName** | **NullableString** |  | 
**EnabledToolChecks** | **NullableInt32** |  | 
**AuthorizationServerId** | **NullableString** |  | 
**CreatedAt** | **time.Time** |  | 
**Apps** | [**[]AppSummaryViewModel**](AppSummaryViewModel.md) |  | 
**Traces** | Pointer to [**NullableMASTraceStat**](MASTraceStat.md) |  | [optional] 

## Methods

### NewMASViewModel

`func NewMASViewModel(id string, name string, namespace NullableString, k8sName NullableString, enabledToolChecks NullableInt32, authorizationServerId NullableString, createdAt time.Time, apps []AppSummaryViewModel, ) *MASViewModel`

NewMASViewModel instantiates a new MASViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMASViewModelWithDefaults

`func NewMASViewModelWithDefaults() *MASViewModel`

NewMASViewModelWithDefaults instantiates a new MASViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *MASViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *MASViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *MASViewModel) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *MASViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MASViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MASViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetNamespace

`func (o *MASViewModel) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *MASViewModel) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *MASViewModel) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### SetNamespaceNil

`func (o *MASViewModel) SetNamespaceNil(b bool)`

 SetNamespaceNil sets the value for Namespace to be an explicit nil

### UnsetNamespace
`func (o *MASViewModel) UnsetNamespace()`

UnsetNamespace ensures that no value is present for Namespace, not even an explicit nil
### GetK8sName

`func (o *MASViewModel) GetK8sName() string`

GetK8sName returns the K8sName field if non-nil, zero value otherwise.

### GetK8sNameOk

`func (o *MASViewModel) GetK8sNameOk() (*string, bool)`

GetK8sNameOk returns a tuple with the K8sName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetK8sName

`func (o *MASViewModel) SetK8sName(v string)`

SetK8sName sets K8sName field to given value.


### SetK8sNameNil

`func (o *MASViewModel) SetK8sNameNil(b bool)`

 SetK8sNameNil sets the value for K8sName to be an explicit nil

### UnsetK8sName
`func (o *MASViewModel) UnsetK8sName()`

UnsetK8sName ensures that no value is present for K8sName, not even an explicit nil
### GetEnabledToolChecks

`func (o *MASViewModel) GetEnabledToolChecks() int32`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *MASViewModel) GetEnabledToolChecksOk() (*int32, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *MASViewModel) SetEnabledToolChecks(v int32)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.


### SetEnabledToolChecksNil

`func (o *MASViewModel) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *MASViewModel) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil
### GetAuthorizationServerId

`func (o *MASViewModel) GetAuthorizationServerId() string`

GetAuthorizationServerId returns the AuthorizationServerId field if non-nil, zero value otherwise.

### GetAuthorizationServerIdOk

`func (o *MASViewModel) GetAuthorizationServerIdOk() (*string, bool)`

GetAuthorizationServerIdOk returns a tuple with the AuthorizationServerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuthorizationServerId

`func (o *MASViewModel) SetAuthorizationServerId(v string)`

SetAuthorizationServerId sets AuthorizationServerId field to given value.


### SetAuthorizationServerIdNil

`func (o *MASViewModel) SetAuthorizationServerIdNil(b bool)`

 SetAuthorizationServerIdNil sets the value for AuthorizationServerId to be an explicit nil

### UnsetAuthorizationServerId
`func (o *MASViewModel) UnsetAuthorizationServerId()`

UnsetAuthorizationServerId ensures that no value is present for AuthorizationServerId, not even an explicit nil
### GetCreatedAt

`func (o *MASViewModel) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *MASViewModel) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *MASViewModel) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetApps

`func (o *MASViewModel) GetApps() []AppSummaryViewModel`

GetApps returns the Apps field if non-nil, zero value otherwise.

### GetAppsOk

`func (o *MASViewModel) GetAppsOk() (*[]AppSummaryViewModel, bool)`

GetAppsOk returns a tuple with the Apps field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApps

`func (o *MASViewModel) SetApps(v []AppSummaryViewModel)`

SetApps sets Apps field to given value.


### GetTraces

`func (o *MASViewModel) GetTraces() MASTraceStat`

GetTraces returns the Traces field if non-nil, zero value otherwise.

### GetTracesOk

`func (o *MASViewModel) GetTracesOk() (*MASTraceStat, bool)`

GetTracesOk returns a tuple with the Traces field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraces

`func (o *MASViewModel) SetTraces(v MASTraceStat)`

SetTraces sets Traces field to given value.

### HasTraces

`func (o *MASViewModel) HasTraces() bool`

HasTraces returns a boolean if a field has been set.

### SetTracesNil

`func (o *MASViewModel) SetTracesNil(b bool)`

 SetTracesNil sets the value for Traces to be an explicit nil

### UnsetTraces
`func (o *MASViewModel) UnsetTraces()`

UnsetTraces ensures that no value is present for Traces, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


