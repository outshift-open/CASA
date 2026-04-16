# ScopeViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**MasId** | **NullableString** |  | 
**Mas** | [**NullableMultiAgentSystemViewModel**](MultiAgentSystemViewModel.md) |  | 
**Tools** | [**[]ToolViewModel**](ToolViewModel.md) |  | 

## Methods

### NewScopeViewModel

`func NewScopeViewModel(id string, name string, masId NullableString, mas NullableMultiAgentSystemViewModel, tools []ToolViewModel, ) *ScopeViewModel`

NewScopeViewModel instantiates a new ScopeViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewScopeViewModelWithDefaults

`func NewScopeViewModelWithDefaults() *ScopeViewModel`

NewScopeViewModelWithDefaults instantiates a new ScopeViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *ScopeViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *ScopeViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *ScopeViewModel) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *ScopeViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ScopeViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ScopeViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetMasId

`func (o *ScopeViewModel) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *ScopeViewModel) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *ScopeViewModel) SetMasId(v string)`

SetMasId sets MasId field to given value.


### SetMasIdNil

`func (o *ScopeViewModel) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *ScopeViewModel) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetMas

`func (o *ScopeViewModel) GetMas() MultiAgentSystemViewModel`

GetMas returns the Mas field if non-nil, zero value otherwise.

### GetMasOk

`func (o *ScopeViewModel) GetMasOk() (*MultiAgentSystemViewModel, bool)`

GetMasOk returns a tuple with the Mas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMas

`func (o *ScopeViewModel) SetMas(v MultiAgentSystemViewModel)`

SetMas sets Mas field to given value.


### SetMasNil

`func (o *ScopeViewModel) SetMasNil(b bool)`

 SetMasNil sets the value for Mas to be an explicit nil

### UnsetMas
`func (o *ScopeViewModel) UnsetMas()`

UnsetMas ensures that no value is present for Mas, not even an explicit nil
### GetTools

`func (o *ScopeViewModel) GetTools() []ToolViewModel`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *ScopeViewModel) GetToolsOk() (*[]ToolViewModel, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *ScopeViewModel) SetTools(v []ToolViewModel)`

SetTools sets Tools field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


