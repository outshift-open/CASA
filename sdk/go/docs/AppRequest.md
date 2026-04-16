# AppRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Type** | [**AppType**](AppType.md) |  | 
**Name** | **string** |  | 
**BaseUrl** | **string** |  | 
**MasId** | **string** |  | 
**Tools** | Pointer to [**[]ToolRequest**](ToolRequest.md) |  | [optional] [default to {}]

## Methods

### NewAppRequest

`func NewAppRequest(type_ AppType, name string, baseUrl string, masId string, ) *AppRequest`

NewAppRequest instantiates a new AppRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppRequestWithDefaults

`func NewAppRequestWithDefaults() *AppRequest`

NewAppRequestWithDefaults instantiates a new AppRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetType

`func (o *AppRequest) GetType() AppType`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *AppRequest) GetTypeOk() (*AppType, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *AppRequest) SetType(v AppType)`

SetType sets Type field to given value.


### GetName

`func (o *AppRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *AppRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *AppRequest) SetName(v string)`

SetName sets Name field to given value.


### GetBaseUrl

`func (o *AppRequest) GetBaseUrl() string`

GetBaseUrl returns the BaseUrl field if non-nil, zero value otherwise.

### GetBaseUrlOk

`func (o *AppRequest) GetBaseUrlOk() (*string, bool)`

GetBaseUrlOk returns a tuple with the BaseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBaseUrl

`func (o *AppRequest) SetBaseUrl(v string)`

SetBaseUrl sets BaseUrl field to given value.


### GetMasId

`func (o *AppRequest) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *AppRequest) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *AppRequest) SetMasId(v string)`

SetMasId sets MasId field to given value.


### GetTools

`func (o *AppRequest) GetTools() []ToolRequest`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *AppRequest) GetToolsOk() (*[]ToolRequest, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *AppRequest) SetTools(v []ToolRequest)`

SetTools sets Tools field to given value.

### HasTools

`func (o *AppRequest) HasTools() bool`

HasTools returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


