# ToolViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**Description** | **string** |  | 
**InputSchema** | **string** |  | 
**OutputSchema** | **string** |  | 
**AppId** | **NullableString** |  | 
**Scopes** | [**[]ScopeViewModelMinimal**](ScopeViewModelMinimal.md) |  | 

## Methods

### NewToolViewModel

`func NewToolViewModel(id string, name string, description string, inputSchema string, outputSchema string, appId NullableString, scopes []ScopeViewModelMinimal, ) *ToolViewModel`

NewToolViewModel instantiates a new ToolViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewToolViewModelWithDefaults

`func NewToolViewModelWithDefaults() *ToolViewModel`

NewToolViewModelWithDefaults instantiates a new ToolViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *ToolViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *ToolViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *ToolViewModel) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *ToolViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ToolViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ToolViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetDescription

`func (o *ToolViewModel) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *ToolViewModel) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *ToolViewModel) SetDescription(v string)`

SetDescription sets Description field to given value.


### GetInputSchema

`func (o *ToolViewModel) GetInputSchema() string`

GetInputSchema returns the InputSchema field if non-nil, zero value otherwise.

### GetInputSchemaOk

`func (o *ToolViewModel) GetInputSchemaOk() (*string, bool)`

GetInputSchemaOk returns a tuple with the InputSchema field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInputSchema

`func (o *ToolViewModel) SetInputSchema(v string)`

SetInputSchema sets InputSchema field to given value.


### GetOutputSchema

`func (o *ToolViewModel) GetOutputSchema() string`

GetOutputSchema returns the OutputSchema field if non-nil, zero value otherwise.

### GetOutputSchemaOk

`func (o *ToolViewModel) GetOutputSchemaOk() (*string, bool)`

GetOutputSchemaOk returns a tuple with the OutputSchema field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOutputSchema

`func (o *ToolViewModel) SetOutputSchema(v string)`

SetOutputSchema sets OutputSchema field to given value.


### GetAppId

`func (o *ToolViewModel) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *ToolViewModel) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *ToolViewModel) SetAppId(v string)`

SetAppId sets AppId field to given value.


### SetAppIdNil

`func (o *ToolViewModel) SetAppIdNil(b bool)`

 SetAppIdNil sets the value for AppId to be an explicit nil

### UnsetAppId
`func (o *ToolViewModel) UnsetAppId()`

UnsetAppId ensures that no value is present for AppId, not even an explicit nil
### GetScopes

`func (o *ToolViewModel) GetScopes() []ScopeViewModelMinimal`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *ToolViewModel) GetScopesOk() (*[]ScopeViewModelMinimal, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *ToolViewModel) SetScopes(v []ScopeViewModelMinimal)`

SetScopes sets Scopes field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


