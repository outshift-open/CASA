# CASAPolicyCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**Spec** | [**CASAPolicySpec**](CASAPolicySpec.md) |  | 

## Methods

### NewCASAPolicyCreateRequest

`func NewCASAPolicyCreateRequest(metadata MultiAgentSystemMetadata, spec CASAPolicySpec, ) *CASAPolicyCreateRequest`

NewCASAPolicyCreateRequest instantiates a new CASAPolicyCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCASAPolicyCreateRequestWithDefaults

`func NewCASAPolicyCreateRequestWithDefaults() *CASAPolicyCreateRequest`

NewCASAPolicyCreateRequestWithDefaults instantiates a new CASAPolicyCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMetadata

`func (o *CASAPolicyCreateRequest) GetMetadata() MultiAgentSystemMetadata`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *CASAPolicyCreateRequest) GetMetadataOk() (*MultiAgentSystemMetadata, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *CASAPolicyCreateRequest) SetMetadata(v MultiAgentSystemMetadata)`

SetMetadata sets Metadata field to given value.


### GetSpec

`func (o *CASAPolicyCreateRequest) GetSpec() CASAPolicySpec`

GetSpec returns the Spec field if non-nil, zero value otherwise.

### GetSpecOk

`func (o *CASAPolicyCreateRequest) GetSpecOk() (*CASAPolicySpec, bool)`

GetSpecOk returns a tuple with the Spec field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSpec

`func (o *CASAPolicyCreateRequest) SetSpec(v CASAPolicySpec)`

SetSpec sets Spec field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


