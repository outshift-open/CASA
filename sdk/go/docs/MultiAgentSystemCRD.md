# MultiAgentSystemCRD

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ApiVersion** | Pointer to **string** | API version | [optional] [default to "casa.io/v1alpha1"]
**Kind** | Pointer to **string** | Resource kind | [optional] [default to "MultiAgentSystem"]
**Metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**Spec** | [**MultiAgentSystemSpec**](MultiAgentSystemSpec.md) |  | 
**Status** | Pointer to [**NullableMultiAgentSystemStatus**](MultiAgentSystemStatus.md) | Resource status | [optional] 

## Methods

### NewMultiAgentSystemCRD

`func NewMultiAgentSystemCRD(metadata MultiAgentSystemMetadata, spec MultiAgentSystemSpec, ) *MultiAgentSystemCRD`

NewMultiAgentSystemCRD instantiates a new MultiAgentSystemCRD object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemCRDWithDefaults

`func NewMultiAgentSystemCRDWithDefaults() *MultiAgentSystemCRD`

NewMultiAgentSystemCRDWithDefaults instantiates a new MultiAgentSystemCRD object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetApiVersion

`func (o *MultiAgentSystemCRD) GetApiVersion() string`

GetApiVersion returns the ApiVersion field if non-nil, zero value otherwise.

### GetApiVersionOk

`func (o *MultiAgentSystemCRD) GetApiVersionOk() (*string, bool)`

GetApiVersionOk returns a tuple with the ApiVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiVersion

`func (o *MultiAgentSystemCRD) SetApiVersion(v string)`

SetApiVersion sets ApiVersion field to given value.

### HasApiVersion

`func (o *MultiAgentSystemCRD) HasApiVersion() bool`

HasApiVersion returns a boolean if a field has been set.

### GetKind

`func (o *MultiAgentSystemCRD) GetKind() string`

GetKind returns the Kind field if non-nil, zero value otherwise.

### GetKindOk

`func (o *MultiAgentSystemCRD) GetKindOk() (*string, bool)`

GetKindOk returns a tuple with the Kind field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKind

`func (o *MultiAgentSystemCRD) SetKind(v string)`

SetKind sets Kind field to given value.

### HasKind

`func (o *MultiAgentSystemCRD) HasKind() bool`

HasKind returns a boolean if a field has been set.

### GetMetadata

`func (o *MultiAgentSystemCRD) GetMetadata() MultiAgentSystemMetadata`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *MultiAgentSystemCRD) GetMetadataOk() (*MultiAgentSystemMetadata, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *MultiAgentSystemCRD) SetMetadata(v MultiAgentSystemMetadata)`

SetMetadata sets Metadata field to given value.


### GetSpec

`func (o *MultiAgentSystemCRD) GetSpec() MultiAgentSystemSpec`

GetSpec returns the Spec field if non-nil, zero value otherwise.

### GetSpecOk

`func (o *MultiAgentSystemCRD) GetSpecOk() (*MultiAgentSystemSpec, bool)`

GetSpecOk returns a tuple with the Spec field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSpec

`func (o *MultiAgentSystemCRD) SetSpec(v MultiAgentSystemSpec)`

SetSpec sets Spec field to given value.


### GetStatus

`func (o *MultiAgentSystemCRD) GetStatus() MultiAgentSystemStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *MultiAgentSystemCRD) GetStatusOk() (*MultiAgentSystemStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *MultiAgentSystemCRD) SetStatus(v MultiAgentSystemStatus)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *MultiAgentSystemCRD) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### SetStatusNil

`func (o *MultiAgentSystemCRD) SetStatusNil(b bool)`

 SetStatusNil sets the value for Status to be an explicit nil

### UnsetStatus
`func (o *MultiAgentSystemCRD) UnsetStatus()`

UnsetStatus ensures that no value is present for Status, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


