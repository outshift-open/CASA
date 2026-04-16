# MASListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ApiVersion** | Pointer to **string** |  | [optional] [default to "zta.io/v1alpha1"]
**Kind** | Pointer to **string** |  | [optional] [default to "MultiAgentSystemList"]
**Items** | [**[]MultiAgentSystemCRD**](MultiAgentSystemCRD.md) |  | 

## Methods

### NewMASListResponse

`func NewMASListResponse(items []MultiAgentSystemCRD, ) *MASListResponse`

NewMASListResponse instantiates a new MASListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMASListResponseWithDefaults

`func NewMASListResponseWithDefaults() *MASListResponse`

NewMASListResponseWithDefaults instantiates a new MASListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetApiVersion

`func (o *MASListResponse) GetApiVersion() string`

GetApiVersion returns the ApiVersion field if non-nil, zero value otherwise.

### GetApiVersionOk

`func (o *MASListResponse) GetApiVersionOk() (*string, bool)`

GetApiVersionOk returns a tuple with the ApiVersion field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiVersion

`func (o *MASListResponse) SetApiVersion(v string)`

SetApiVersion sets ApiVersion field to given value.

### HasApiVersion

`func (o *MASListResponse) HasApiVersion() bool`

HasApiVersion returns a boolean if a field has been set.

### GetKind

`func (o *MASListResponse) GetKind() string`

GetKind returns the Kind field if non-nil, zero value otherwise.

### GetKindOk

`func (o *MASListResponse) GetKindOk() (*string, bool)`

GetKindOk returns a tuple with the Kind field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKind

`func (o *MASListResponse) SetKind(v string)`

SetKind sets Kind field to given value.

### HasKind

`func (o *MASListResponse) HasKind() bool`

HasKind returns a boolean if a field has been set.

### GetItems

`func (o *MASListResponse) GetItems() []MultiAgentSystemCRD`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *MASListResponse) GetItemsOk() (*[]MultiAgentSystemCRD, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *MASListResponse) SetItems(v []MultiAgentSystemCRD)`

SetItems sets Items field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


