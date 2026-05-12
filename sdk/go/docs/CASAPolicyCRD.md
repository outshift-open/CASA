# CASAPolicyCRD

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ApiVersion** | Pointer to **string** | API version | [optional] [default to "casa.io/v1alpha1"]
**Kind** | Pointer to **string** | Resource kind | [optional] [default to "CASAPolicy"]
**Metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**Spec** | [**CASAPolicySpec**](CASAPolicySpec.md) |  | 
**Status** | Pointer to [**NullableCASAPolicyStatus**](CASAPolicyStatus.md) | Resource status | [optional] 

## Methods

### NewCASAPolicyCRD

`func NewCASAPolicyCRD(metadata MultiAgentSystemMetadata, spec CASAPolicySpec, ) *CASAPolicyCRD`

NewCASAPolicyCRD instantiates a new CASAPolicyCRD object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCASAPolicyCRDWithDefaults

`func NewCASAPolicyCRDWithDefaults() *CASAPolicyCRD`

NewCASAPolicyCRDWithDefaults instantiates a new CASAPolicyCRD object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetApiVersion

`func (o *CASAPolicyCRD) GetApiVersion() string`

GetApiVersion returns the ApiVersion field if non-nil, zero value otherwise.

### GetApiVersionOk

`func (o *CASAPolicyCRD) GetApiVersionOk() (*string, bool)`

GetApiVersionOk returns a tuple with the ApiVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiVersion

`func (o *CASAPolicyCRD) SetApiVersion(v string)`

SetApiVersion sets ApiVersion field to given value.

### HasApiVersion

`func (o *CASAPolicyCRD) HasApiVersion() bool`

HasApiVersion returns a boolean if a field has been set.

### GetKind

`func (o *CASAPolicyCRD) GetKind() string`

GetKind returns the Kind field if non-nil, zero value otherwise.

### GetKindOk

`func (o *CASAPolicyCRD) GetKindOk() (*string, bool)`

GetKindOk returns a tuple with the Kind field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKind

`func (o *CASAPolicyCRD) SetKind(v string)`

SetKind sets Kind field to given value.

### HasKind

`func (o *CASAPolicyCRD) HasKind() bool`

HasKind returns a boolean if a field has been set.

### GetMetadata

`func (o *CASAPolicyCRD) GetMetadata() MultiAgentSystemMetadata`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *CASAPolicyCRD) GetMetadataOk() (*MultiAgentSystemMetadata, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *CASAPolicyCRD) SetMetadata(v MultiAgentSystemMetadata)`

SetMetadata sets Metadata field to given value.


### GetSpec

`func (o *CASAPolicyCRD) GetSpec() CASAPolicySpec`

GetSpec returns the Spec field if non-nil, zero value otherwise.

### GetSpecOk

`func (o *CASAPolicyCRD) GetSpecOk() (*CASAPolicySpec, bool)`

GetSpecOk returns a tuple with the Spec field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSpec

`func (o *CASAPolicyCRD) SetSpec(v CASAPolicySpec)`

SetSpec sets Spec field to given value.


### GetStatus

`func (o *CASAPolicyCRD) GetStatus() CASAPolicyStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *CASAPolicyCRD) GetStatusOk() (*CASAPolicyStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *CASAPolicyCRD) SetStatus(v CASAPolicyStatus)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *CASAPolicyCRD) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### SetStatusNil

`func (o *CASAPolicyCRD) SetStatusNil(b bool)`

 SetStatusNil sets the value for Status to be an explicit nil

### UnsetStatus
`func (o *CASAPolicyCRD) UnsetStatus()`

UnsetStatus ensures that no value is present for Status, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


