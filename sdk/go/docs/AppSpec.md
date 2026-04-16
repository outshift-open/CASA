# AppSpec

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Name of the application | 
**Type** | [**AppType**](AppType.md) | Type of the application | 
**BaseUrl** | **string** | Base URL of the application | 

## Methods

### NewAppSpec

`func NewAppSpec(name string, type_ AppType, baseUrl string, ) *AppSpec`

NewAppSpec instantiates a new AppSpec object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSpecWithDefaults

`func NewAppSpecWithDefaults() *AppSpec`

NewAppSpecWithDefaults instantiates a new AppSpec object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *AppSpec) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *AppSpec) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *AppSpec) SetName(v string)`

SetName sets Name field to given value.


### GetType

`func (o *AppSpec) GetType() AppType`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *AppSpec) GetTypeOk() (*AppType, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *AppSpec) SetType(v AppType)`

SetType sets Type field to given value.


### GetBaseUrl

`func (o *AppSpec) GetBaseUrl() string`

GetBaseUrl returns the BaseUrl field if non-nil, zero value otherwise.

### GetBaseUrlOk

`func (o *AppSpec) GetBaseUrlOk() (*string, bool)`

GetBaseUrlOk returns a tuple with the BaseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBaseUrl

`func (o *AppSpec) SetBaseUrl(v string)`

SetBaseUrl sets BaseUrl field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


