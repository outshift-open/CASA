# MultiAgentSystemMetadata

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Resource name | 
**Namespace** | **string** | Kubernetes namespace | 
**Uid** | Pointer to **NullableString** | Kubernetes UID | [optional] 
**ResourceVersion** | Pointer to **NullableString** | Resource version | [optional] 
**Generation** | Pointer to **NullableInt32** | Generation number | [optional] 
**Labels** | Pointer to **map[string]interface{}** | Resource labels | [optional] 
**Annotations** | Pointer to **map[string]interface{}** | Resource annotations | [optional] 

## Methods

### NewMultiAgentSystemMetadata

`func NewMultiAgentSystemMetadata(name string, namespace string, ) *MultiAgentSystemMetadata`

NewMultiAgentSystemMetadata instantiates a new MultiAgentSystemMetadata object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemMetadataWithDefaults

`func NewMultiAgentSystemMetadataWithDefaults() *MultiAgentSystemMetadata`

NewMultiAgentSystemMetadataWithDefaults instantiates a new MultiAgentSystemMetadata object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *MultiAgentSystemMetadata) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *MultiAgentSystemMetadata) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *MultiAgentSystemMetadata) SetName(v string)`

SetName sets Name field to given value.


### GetNamespace

`func (o *MultiAgentSystemMetadata) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *MultiAgentSystemMetadata) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *MultiAgentSystemMetadata) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### GetUid

`func (o *MultiAgentSystemMetadata) GetUid() string`

GetUid returns the Uid field if non-nil, zero value otherwise.

### GetUidOk

`func (o *MultiAgentSystemMetadata) GetUidOk() (*string, bool)`

GetUidOk returns a tuple with the Uid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUid

`func (o *MultiAgentSystemMetadata) SetUid(v string)`

SetUid sets Uid field to given value.

### HasUid

`func (o *MultiAgentSystemMetadata) HasUid() bool`

HasUid returns a boolean if a field has been set.

### SetUidNil

`func (o *MultiAgentSystemMetadata) SetUidNil(b bool)`

 SetUidNil sets the value for Uid to be an explicit nil

### UnsetUid
`func (o *MultiAgentSystemMetadata) UnsetUid()`

UnsetUid ensures that no value is present for Uid, not even an explicit nil
### GetResourceVersion

`func (o *MultiAgentSystemMetadata) GetResourceVersion() string`

GetResourceVersion returns the ResourceVersion field if non-nil, zero value otherwise.

### GetResourceVersionOk

`func (o *MultiAgentSystemMetadata) GetResourceVersionOk() (*string, bool)`

GetResourceVersionOk returns a tuple with the ResourceVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResourceVersion

`func (o *MultiAgentSystemMetadata) SetResourceVersion(v string)`

SetResourceVersion sets ResourceVersion field to given value.

### HasResourceVersion

`func (o *MultiAgentSystemMetadata) HasResourceVersion() bool`

HasResourceVersion returns a boolean if a field has been set.

### SetResourceVersionNil

`func (o *MultiAgentSystemMetadata) SetResourceVersionNil(b bool)`

 SetResourceVersionNil sets the value for ResourceVersion to be an explicit nil

### UnsetResourceVersion
`func (o *MultiAgentSystemMetadata) UnsetResourceVersion()`

UnsetResourceVersion ensures that no value is present for ResourceVersion, not even an explicit nil
### GetGeneration

`func (o *MultiAgentSystemMetadata) GetGeneration() int32`

GetGeneration returns the Generation field if non-nil, zero value otherwise.

### GetGenerationOk

`func (o *MultiAgentSystemMetadata) GetGenerationOk() (*int32, bool)`

GetGenerationOk returns a tuple with the Generation field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGeneration

`func (o *MultiAgentSystemMetadata) SetGeneration(v int32)`

SetGeneration sets Generation field to given value.

### HasGeneration

`func (o *MultiAgentSystemMetadata) HasGeneration() bool`

HasGeneration returns a boolean if a field has been set.

### SetGenerationNil

`func (o *MultiAgentSystemMetadata) SetGenerationNil(b bool)`

 SetGenerationNil sets the value for Generation to be an explicit nil

### UnsetGeneration
`func (o *MultiAgentSystemMetadata) UnsetGeneration()`

UnsetGeneration ensures that no value is present for Generation, not even an explicit nil
### GetLabels

`func (o *MultiAgentSystemMetadata) GetLabels() map[string]interface{}`

GetLabels returns the Labels field if non-nil, zero value otherwise.

### GetLabelsOk

`func (o *MultiAgentSystemMetadata) GetLabelsOk() (*map[string]interface{}, bool)`

GetLabelsOk returns a tuple with the Labels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLabels

`func (o *MultiAgentSystemMetadata) SetLabels(v map[string]interface{})`

SetLabels sets Labels field to given value.

### HasLabels

`func (o *MultiAgentSystemMetadata) HasLabels() bool`

HasLabels returns a boolean if a field has been set.

### SetLabelsNil

`func (o *MultiAgentSystemMetadata) SetLabelsNil(b bool)`

 SetLabelsNil sets the value for Labels to be an explicit nil

### UnsetLabels
`func (o *MultiAgentSystemMetadata) UnsetLabels()`

UnsetLabels ensures that no value is present for Labels, not even an explicit nil
### GetAnnotations

`func (o *MultiAgentSystemMetadata) GetAnnotations() map[string]interface{}`

GetAnnotations returns the Annotations field if non-nil, zero value otherwise.

### GetAnnotationsOk

`func (o *MultiAgentSystemMetadata) GetAnnotationsOk() (*map[string]interface{}, bool)`

GetAnnotationsOk returns a tuple with the Annotations field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAnnotations

`func (o *MultiAgentSystemMetadata) SetAnnotations(v map[string]interface{})`

SetAnnotations sets Annotations field to given value.

### HasAnnotations

`func (o *MultiAgentSystemMetadata) HasAnnotations() bool`

HasAnnotations returns a boolean if a field has been set.

### SetAnnotationsNil

`func (o *MultiAgentSystemMetadata) SetAnnotationsNil(b bool)`

 SetAnnotationsNil sets the value for Annotations to be an explicit nil

### UnsetAnnotations
`func (o *MultiAgentSystemMetadata) UnsetAnnotations()`

UnsetAnnotations ensures that no value is present for Annotations, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


