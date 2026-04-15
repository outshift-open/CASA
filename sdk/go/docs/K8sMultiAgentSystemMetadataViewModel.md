# K8sMultiAgentSystemMetadataViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Name** | **string** |  | 
**Uid** | Pointer to **NullableString** |  | [optional] 
**ResourceVersion** | Pointer to **NullableString** |  | [optional] 
**Generation** | Pointer to **NullableInt32** |  | [optional] 
**MasCrdId** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewK8sMultiAgentSystemMetadataViewModel

`func NewK8sMultiAgentSystemMetadataViewModel(name string, ) *K8sMultiAgentSystemMetadataViewModel`

NewK8sMultiAgentSystemMetadataViewModel instantiates a new K8sMultiAgentSystemMetadataViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewK8sMultiAgentSystemMetadataViewModelWithDefaults

`func NewK8sMultiAgentSystemMetadataViewModelWithDefaults() *K8sMultiAgentSystemMetadataViewModel`

NewK8sMultiAgentSystemMetadataViewModelWithDefaults instantiates a new K8sMultiAgentSystemMetadataViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *K8sMultiAgentSystemMetadataViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *K8sMultiAgentSystemMetadataViewModel) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *K8sMultiAgentSystemMetadataViewModel) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *K8sMultiAgentSystemMetadataViewModel) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *K8sMultiAgentSystemMetadataViewModel) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetName

`func (o *K8sMultiAgentSystemMetadataViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *K8sMultiAgentSystemMetadataViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetUid

`func (o *K8sMultiAgentSystemMetadataViewModel) GetUid() string`

GetUid returns the Uid field if non-nil, zero value otherwise.

### GetUidOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetUidOk() (*string, bool)`

GetUidOk returns a tuple with the Uid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUid

`func (o *K8sMultiAgentSystemMetadataViewModel) SetUid(v string)`

SetUid sets Uid field to given value.

### HasUid

`func (o *K8sMultiAgentSystemMetadataViewModel) HasUid() bool`

HasUid returns a boolean if a field has been set.

### SetUidNil

`func (o *K8sMultiAgentSystemMetadataViewModel) SetUidNil(b bool)`

 SetUidNil sets the value for Uid to be an explicit nil

### UnsetUid
`func (o *K8sMultiAgentSystemMetadataViewModel) UnsetUid()`

UnsetUid ensures that no value is present for Uid, not even an explicit nil
### GetResourceVersion

`func (o *K8sMultiAgentSystemMetadataViewModel) GetResourceVersion() string`

GetResourceVersion returns the ResourceVersion field if non-nil, zero value otherwise.

### GetResourceVersionOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetResourceVersionOk() (*string, bool)`

GetResourceVersionOk returns a tuple with the ResourceVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResourceVersion

`func (o *K8sMultiAgentSystemMetadataViewModel) SetResourceVersion(v string)`

SetResourceVersion sets ResourceVersion field to given value.

### HasResourceVersion

`func (o *K8sMultiAgentSystemMetadataViewModel) HasResourceVersion() bool`

HasResourceVersion returns a boolean if a field has been set.

### SetResourceVersionNil

`func (o *K8sMultiAgentSystemMetadataViewModel) SetResourceVersionNil(b bool)`

 SetResourceVersionNil sets the value for ResourceVersion to be an explicit nil

### UnsetResourceVersion
`func (o *K8sMultiAgentSystemMetadataViewModel) UnsetResourceVersion()`

UnsetResourceVersion ensures that no value is present for ResourceVersion, not even an explicit nil
### GetGeneration

`func (o *K8sMultiAgentSystemMetadataViewModel) GetGeneration() int32`

GetGeneration returns the Generation field if non-nil, zero value otherwise.

### GetGenerationOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetGenerationOk() (*int32, bool)`

GetGenerationOk returns a tuple with the Generation field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGeneration

`func (o *K8sMultiAgentSystemMetadataViewModel) SetGeneration(v int32)`

SetGeneration sets Generation field to given value.

### HasGeneration

`func (o *K8sMultiAgentSystemMetadataViewModel) HasGeneration() bool`

HasGeneration returns a boolean if a field has been set.

### SetGenerationNil

`func (o *K8sMultiAgentSystemMetadataViewModel) SetGenerationNil(b bool)`

 SetGenerationNil sets the value for Generation to be an explicit nil

### UnsetGeneration
`func (o *K8sMultiAgentSystemMetadataViewModel) UnsetGeneration()`

UnsetGeneration ensures that no value is present for Generation, not even an explicit nil
### GetMasCrdId

`func (o *K8sMultiAgentSystemMetadataViewModel) GetMasCrdId() string`

GetMasCrdId returns the MasCrdId field if non-nil, zero value otherwise.

### GetMasCrdIdOk

`func (o *K8sMultiAgentSystemMetadataViewModel) GetMasCrdIdOk() (*string, bool)`

GetMasCrdIdOk returns a tuple with the MasCrdId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasCrdId

`func (o *K8sMultiAgentSystemMetadataViewModel) SetMasCrdId(v string)`

SetMasCrdId sets MasCrdId field to given value.

### HasMasCrdId

`func (o *K8sMultiAgentSystemMetadataViewModel) HasMasCrdId() bool`

HasMasCrdId returns a boolean if a field has been set.

### SetMasCrdIdNil

`func (o *K8sMultiAgentSystemMetadataViewModel) SetMasCrdIdNil(b bool)`

 SetMasCrdIdNil sets the value for MasCrdId to be an explicit nil

### UnsetMasCrdId
`func (o *K8sMultiAgentSystemMetadataViewModel) UnsetMasCrdId()`

UnsetMasCrdId ensures that no value is present for MasCrdId, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


