# AppSpecBaseUrl

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Host** | **string** | Host (and optional port) of the URL, e.g. my-app:8080 | 
**Scheme** | **string** | URL scheme: http or https | 

## Methods

### NewAppSpecBaseUrl

`func NewAppSpecBaseUrl(host string, scheme string, ) *AppSpecBaseUrl`

NewAppSpecBaseUrl instantiates a new AppSpecBaseUrl object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSpecBaseUrlWithDefaults

`func NewAppSpecBaseUrlWithDefaults() *AppSpecBaseUrl`

NewAppSpecBaseUrlWithDefaults instantiates a new AppSpecBaseUrl object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetHost

`func (o *AppSpecBaseUrl) GetHost() string`

GetHost returns the Host field if non-nil, zero value otherwise.

### GetHostOk

`func (o *AppSpecBaseUrl) GetHostOk() (*string, bool)`

GetHostOk returns a tuple with the Host field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHost

`func (o *AppSpecBaseUrl) SetHost(v string)`

SetHost sets Host field to given value.


### GetScheme

`func (o *AppSpecBaseUrl) GetScheme() string`

GetScheme returns the Scheme field if non-nil, zero value otherwise.

### GetSchemeOk

`func (o *AppSpecBaseUrl) GetSchemeOk() (*string, bool)`

GetSchemeOk returns a tuple with the Scheme field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScheme

`func (o *AppSpecBaseUrl) SetScheme(v string)`

SetScheme sets Scheme field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


