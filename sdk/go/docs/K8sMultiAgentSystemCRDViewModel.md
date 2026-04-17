# K8sMultiAgentSystemCRDViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**ApiVersion** | **string** |  | 
**Kind** | **string** |  | 
**Namespace** | **string** |  | 
**MasMetadata** | Pointer to [**NullableK8sMultiAgentSystemMetadataViewModel**](K8sMultiAgentSystemMetadataViewModel.md) |  | [optional] 
**Name** | **string** |  | 
**EnabledToolChecks** | [**NullableToolCheckFlags**](ToolCheckFlags.md) |  | 
**LlmHost** | **NullableString** |  | 
**AppSpecs** | Pointer to [**[]K8sAppSpecViewModel**](K8sAppSpecViewModel.md) |  | [optional] [default to {}]
**MasId** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewK8sMultiAgentSystemCRDViewModel

`func NewK8sMultiAgentSystemCRDViewModel(apiVersion string, kind string, namespace string, name string, enabledToolChecks NullableToolCheckFlags, llmHost NullableString, ) *K8sMultiAgentSystemCRDViewModel`

NewK8sMultiAgentSystemCRDViewModel instantiates a new K8sMultiAgentSystemCRDViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewK8sMultiAgentSystemCRDViewModelWithDefaults

`func NewK8sMultiAgentSystemCRDViewModelWithDefaults() *K8sMultiAgentSystemCRDViewModel`

NewK8sMultiAgentSystemCRDViewModelWithDefaults instantiates a new K8sMultiAgentSystemCRDViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *K8sMultiAgentSystemCRDViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *K8sMultiAgentSystemCRDViewModel) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *K8sMultiAgentSystemCRDViewModel) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *K8sMultiAgentSystemCRDViewModel) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *K8sMultiAgentSystemCRDViewModel) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetApiVersion

`func (o *K8sMultiAgentSystemCRDViewModel) GetApiVersion() string`

GetApiVersion returns the ApiVersion field if non-nil, zero value otherwise.

### GetApiVersionOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetApiVersionOk() (*string, bool)`

GetApiVersionOk returns a tuple with the ApiVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiVersion

`func (o *K8sMultiAgentSystemCRDViewModel) SetApiVersion(v string)`

SetApiVersion sets ApiVersion field to given value.


### GetKind

`func (o *K8sMultiAgentSystemCRDViewModel) GetKind() string`

GetKind returns the Kind field if non-nil, zero value otherwise.

### GetKindOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetKindOk() (*string, bool)`

GetKindOk returns a tuple with the Kind field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKind

`func (o *K8sMultiAgentSystemCRDViewModel) SetKind(v string)`

SetKind sets Kind field to given value.


### GetNamespace

`func (o *K8sMultiAgentSystemCRDViewModel) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *K8sMultiAgentSystemCRDViewModel) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### GetMasMetadata

`func (o *K8sMultiAgentSystemCRDViewModel) GetMasMetadata() K8sMultiAgentSystemMetadataViewModel`

GetMasMetadata returns the MasMetadata field if non-nil, zero value otherwise.

### GetMasMetadataOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetMasMetadataOk() (*K8sMultiAgentSystemMetadataViewModel, bool)`

GetMasMetadataOk returns a tuple with the MasMetadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasMetadata

`func (o *K8sMultiAgentSystemCRDViewModel) SetMasMetadata(v K8sMultiAgentSystemMetadataViewModel)`

SetMasMetadata sets MasMetadata field to given value.

### HasMasMetadata

`func (o *K8sMultiAgentSystemCRDViewModel) HasMasMetadata() bool`

HasMasMetadata returns a boolean if a field has been set.

### SetMasMetadataNil

`func (o *K8sMultiAgentSystemCRDViewModel) SetMasMetadataNil(b bool)`

 SetMasMetadataNil sets the value for MasMetadata to be an explicit nil

### UnsetMasMetadata
`func (o *K8sMultiAgentSystemCRDViewModel) UnsetMasMetadata()`

UnsetMasMetadata ensures that no value is present for MasMetadata, not even an explicit nil
### GetName

`func (o *K8sMultiAgentSystemCRDViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *K8sMultiAgentSystemCRDViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetEnabledToolChecks

`func (o *K8sMultiAgentSystemCRDViewModel) GetEnabledToolChecks() ToolCheckFlags`

GetEnabledToolChecks returns the EnabledToolChecks field if non-nil, zero value otherwise.

### GetEnabledToolChecksOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetEnabledToolChecksOk() (*ToolCheckFlags, bool)`

GetEnabledToolChecksOk returns a tuple with the EnabledToolChecks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabledToolChecks

`func (o *K8sMultiAgentSystemCRDViewModel) SetEnabledToolChecks(v ToolCheckFlags)`

SetEnabledToolChecks sets EnabledToolChecks field to given value.


### SetEnabledToolChecksNil

`func (o *K8sMultiAgentSystemCRDViewModel) SetEnabledToolChecksNil(b bool)`

 SetEnabledToolChecksNil sets the value for EnabledToolChecks to be an explicit nil

### UnsetEnabledToolChecks
`func (o *K8sMultiAgentSystemCRDViewModel) UnsetEnabledToolChecks()`

UnsetEnabledToolChecks ensures that no value is present for EnabledToolChecks, not even an explicit nil
### GetLlmHost

`func (o *K8sMultiAgentSystemCRDViewModel) GetLlmHost() string`

GetLlmHost returns the LlmHost field if non-nil, zero value otherwise.

### GetLlmHostOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetLlmHostOk() (*string, bool)`

GetLlmHostOk returns a tuple with the LlmHost field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLlmHost

`func (o *K8sMultiAgentSystemCRDViewModel) SetLlmHost(v string)`

SetLlmHost sets LlmHost field to given value.


### SetLlmHostNil

`func (o *K8sMultiAgentSystemCRDViewModel) SetLlmHostNil(b bool)`

 SetLlmHostNil sets the value for LlmHost to be an explicit nil

### UnsetLlmHost
`func (o *K8sMultiAgentSystemCRDViewModel) UnsetLlmHost()`

UnsetLlmHost ensures that no value is present for LlmHost, not even an explicit nil
### GetAppSpecs

`func (o *K8sMultiAgentSystemCRDViewModel) GetAppSpecs() []K8sAppSpecViewModel`

GetAppSpecs returns the AppSpecs field if non-nil, zero value otherwise.

### GetAppSpecsOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetAppSpecsOk() (*[]K8sAppSpecViewModel, bool)`

GetAppSpecsOk returns a tuple with the AppSpecs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppSpecs

`func (o *K8sMultiAgentSystemCRDViewModel) SetAppSpecs(v []K8sAppSpecViewModel)`

SetAppSpecs sets AppSpecs field to given value.

### HasAppSpecs

`func (o *K8sMultiAgentSystemCRDViewModel) HasAppSpecs() bool`

HasAppSpecs returns a boolean if a field has been set.

### GetMasId

`func (o *K8sMultiAgentSystemCRDViewModel) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *K8sMultiAgentSystemCRDViewModel) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *K8sMultiAgentSystemCRDViewModel) SetMasId(v string)`

SetMasId sets MasId field to given value.

### HasMasId

`func (o *K8sMultiAgentSystemCRDViewModel) HasMasId() bool`

HasMasId returns a boolean if a field has been set.

### SetMasIdNil

`func (o *K8sMultiAgentSystemCRDViewModel) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *K8sMultiAgentSystemCRDViewModel) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


