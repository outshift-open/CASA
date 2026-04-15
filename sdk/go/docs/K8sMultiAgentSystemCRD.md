# K8sMultiAgentSystemCRD

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**ApiVersion** | Pointer to **string** | API version | [optional] [default to "zta.io/v1alpha1"]
**Kind** | Pointer to **string** | Resource kind | [optional] [default to "MultiAgentSystem"]
**Namespace** | **string** | Kubernetes namespace | 
**Name** | **string** | Display name of the Multi-Agent System | 
**EnabledToolChecks** | Pointer to [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**MasId** | **NullableString** |  | 

## Methods

### NewK8sMultiAgentSystemCRD

`func NewK8sMultiAgentSystemCRD(namespace string, name string, masId NullableString, ) *K8sMultiAgentSystemCRD`

NewK8sMultiAgentSystemCRD instantiates a new K8sMultiAgentSystemCRD object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewK8sMultiAgentSystemCRDWithDefaults

`func NewK8sMultiAgentSystemCRDWithDefaults() *K8sMultiAgentSystemCRD`

NewK8sMultiAgentSystemCRDWithDefaults instantiates a new K8sMultiAgentSystemCRD object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *K8sMultiAgentSystemCRD) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *K8sMultiAgentSystemCRD) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *K8sMultiAgentSystemCRD) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *K8sMultiAgentSystemCRD) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *K8sMultiAgentSystemCRD) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *K8sMultiAgentSystemCRD) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetApiVersion

`func (o *K8sMultiAgentSystemCRD) GetApiVersion() string`

GetApiVersion returns the ApiVersion field if non-nil, zero value otherwise.

### GetApiVersionOk

`func (o *K8sMultiAgentSystemCRD) GetApiVersionOk() (*string, bool)`

GetApiVersionOk returns a tuple with the ApiVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiVersion

`func (o *K8sMultiAgentSystemCRD) SetApiVersion(v string)`

SetApiVersion sets ApiVersion field to given value.

### HasApiVersion

`func (o *K8sMultiAgentSystemCRD) HasApiVersion() bool`

HasApiVersion returns a boolean if a field has been set.

### GetKind

`func (o *K8sMultiAgentSystemCRD) GetKind() string`

GetKind returns the Kind field if non-nil, zero value otherwise.

### GetKindOk

`func (o *K8sMultiAgentSystemCRD) GetKindOk() (*string, bool)`

GetKindOk returns a tuple with the Kind field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKind

`func (o *K8sMultiAgentSystemCRD) SetKind(v string)`

SetKind sets Kind field to given value.

### HasKind

`func (o *K8sMultiAgentSystemCRD) HasKind() bool`

HasKind returns a boolean if a field has been set.

### GetNamespace

`func (o *K8sMultiAgentSystemCRD) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *K8sMultiAgentSystemCRD) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *K8sMultiAgentSystemCRD) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### GetName

`func (o *K8sMultiAgentSystemCRD) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *K8sMultiAgentSystemCRD) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *K8sMultiAgentSystemCRD) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *K8sMultiAgentSystemCRD) GetEnabledToolChecks() ToolCheckFlags`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *K8sMultiAgentSystemCRD) GetEnabledToolChecksOk() (*ToolCheckFlags, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *K8sMultiAgentSystemCRD) SetEnabledToolChecks(v ToolCheckFlags)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.

### HasEnabledToolChecks

`func (o *K8sMultiAgentSystemCRD) HasEnabledToolChecks() bool`

HasEnabledToolChecks returns a boolean if a field has been set.

### SetEnabledToolChecksNil

`func (o *K8sMultiAgentSystemCRD) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *K8sMultiAgentSystemCRD) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil
### GetMasId

`func (o *K8sMultiAgentSystemCRD) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *K8sMultiAgentSystemCRD) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *K8sMultiAgentSystemCRD) SetMasId(v string)`

SetMasId sets MasId field to given value.


### SetMasIdNil

`func (o *K8sMultiAgentSystemCRD) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *K8sMultiAgentSystemCRD) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


