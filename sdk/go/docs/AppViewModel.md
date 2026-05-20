# AppViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Type** | **string** |  | 
**Name** | **string** |  | 
**BaseUrl** | **string** |  | 
**Tools** | [**[]ToolViewModel**](ToolViewModel.md) |  | 
**MasId** | **NullableString** |  | 
**Mas** | [**NullableMultiAgentSystemViewModel**](MultiAgentSystemViewModel.md) |  | 
**ClientIdMetadataUrl** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewAppViewModel

`func NewAppViewModel(id string, type_ string, name string, baseUrl string, tools []ToolViewModel, masId NullableString, mas NullableMultiAgentSystemViewModel, ) *AppViewModel`

NewAppViewModel instantiates a new AppViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppViewModelWithDefaults

`func NewAppViewModelWithDefaults() *AppViewModel`

NewAppViewModelWithDefaults instantiates a new AppViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *AppViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *AppViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *AppViewModel) SetId(v string)`

SetId sets Id field to given value.


### GetType

`func (o *AppViewModel) GetType() string`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *AppViewModel) GetTypeOk() (*string, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *AppViewModel) SetType(v string)`

SetType sets Type field to given value.


### GetName

`func (o *AppViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *AppViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *AppViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetBaseUrl

`func (o *AppViewModel) GetBaseUrl() string`

GetBaseUrl returns the BaseUrl field if non-nil, zero value otherwise.

### GetBaseUrlOk

`func (o *AppViewModel) GetBaseUrlOk() (*string, bool)`

GetBaseUrlOk returns a tuple with the BaseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBaseUrl

`func (o *AppViewModel) SetBaseUrl(v string)`

SetBaseUrl sets BaseUrl field to given value.


### GetTools

`func (o *AppViewModel) GetTools() []ToolViewModel`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *AppViewModel) GetToolsOk() (*[]ToolViewModel, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *AppViewModel) SetTools(v []ToolViewModel)`

SetTools sets Tools field to given value.


### GetMasId

`func (o *AppViewModel) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *AppViewModel) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *AppViewModel) SetMasId(v string)`

SetMasId sets MasId field to given value.


### SetMasIdNil

`func (o *AppViewModel) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *AppViewModel) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetMas

`func (o *AppViewModel) GetMas() MultiAgentSystemViewModel`

GetMas returns the Mas field if non-nil, zero value otherwise.

### GetMasOk

`func (o *AppViewModel) GetMasOk() (*MultiAgentSystemViewModel, bool)`

GetMasOk returns a tuple with the Mas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMas

`func (o *AppViewModel) SetMas(v MultiAgentSystemViewModel)`

SetMas sets Mas field to given value.


### SetMasNil

`func (o *AppViewModel) SetMasNil(b bool)`

 SetMasNil sets the value for Mas to be an explicit nil

### UnsetMas
`func (o *AppViewModel) UnsetMas()`

UnsetMas ensures that no value is present for Mas, not even an explicit nil
### GetClientIdMetadataUrl

`func (o *AppViewModel) GetClientIdMetadataUrl() string`

GetClientIdMetadataUrl returns the ClientIdMetadataUrl field if non-nil, zero value otherwise.

### GetClientIdMetadataUrlOk

`func (o *AppViewModel) GetClientIdMetadataUrlOk() (*string, bool)`

GetClientIdMetadataUrlOk returns a tuple with the ClientIdMetadataUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientIdMetadataUrl

`func (o *AppViewModel) SetClientIdMetadataUrl(v string)`

SetClientIdMetadataUrl sets ClientIdMetadataUrl field to given value.

### HasClientIdMetadataUrl

`func (o *AppViewModel) HasClientIdMetadataUrl() bool`

HasClientIdMetadataUrl returns a boolean if a field has been set.

### SetClientIdMetadataUrlNil

`func (o *AppViewModel) SetClientIdMetadataUrlNil(b bool)`

 SetClientIdMetadataUrlNil sets the value for ClientIdMetadataUrl to be an explicit nil

### UnsetClientIdMetadataUrl
`func (o *AppViewModel) UnsetClientIdMetadataUrl()`

UnsetClientIdMetadataUrl ensures that no value is present for ClientIdMetadataUrl, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


