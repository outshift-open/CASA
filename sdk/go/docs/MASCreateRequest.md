# MASCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**Spec** | [**MultiAgentSystemSpec**](MultiAgentSystemSpec.md) |  | 

## Methods

### NewMASCreateRequest

`func NewMASCreateRequest(metadata MultiAgentSystemMetadata, spec MultiAgentSystemSpec, ) *MASCreateRequest`

NewMASCreateRequest instantiates a new MASCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMASCreateRequestWithDefaults

`func NewMASCreateRequestWithDefaults() *MASCreateRequest`

NewMASCreateRequestWithDefaults instantiates a new MASCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMetadata

`func (o *MASCreateRequest) GetMetadata() MultiAgentSystemMetadata`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *MASCreateRequest) GetMetadataOk() (*MultiAgentSystemMetadata, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *MASCreateRequest) SetMetadata(v MultiAgentSystemMetadata)`

SetMetadata sets Metadata field to given value.


### GetSpec

`func (o *MASCreateRequest) GetSpec() MultiAgentSystemSpec`

GetSpec returns the Spec field if non-nil, zero value otherwise.

### GetSpecOk

`func (o *MASCreateRequest) GetSpecOk() (*MultiAgentSystemSpec, bool)`

GetSpecOk returns a tuple with the Spec field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSpec

`func (o *MASCreateRequest) SetSpec(v MultiAgentSystemSpec)`

SetSpec sets Spec field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


