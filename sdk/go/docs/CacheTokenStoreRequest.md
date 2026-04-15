# CacheTokenStoreRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TraceId** | **string** |  | 
**AppHost** | **string** |  | 
**AppType** | [**AppType**](AppType.md) |  | 
**AccessToken** | **string** |  | 

## Methods

### NewCacheTokenStoreRequest

`func NewCacheTokenStoreRequest(traceId string, appHost string, appType AppType, accessToken string, ) *CacheTokenStoreRequest`

NewCacheTokenStoreRequest instantiates a new CacheTokenStoreRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCacheTokenStoreRequestWithDefaults

`func NewCacheTokenStoreRequestWithDefaults() *CacheTokenStoreRequest`

NewCacheTokenStoreRequestWithDefaults instantiates a new CacheTokenStoreRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTraceId

`func (o *CacheTokenStoreRequest) GetTraceId() string`

GetTraceId returns the TraceId field if non-nil, zero value otherwise.

### GetTraceIdOk

`func (o *CacheTokenStoreRequest) GetTraceIdOk() (*string, bool)`

GetTraceIdOk returns a tuple with the TraceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraceId

`func (o *CacheTokenStoreRequest) SetTraceId(v string)`

SetTraceId sets TraceId field to given value.


### GetAppHost

`func (o *CacheTokenStoreRequest) GetAppHost() string`

GetAppHost returns the AppHost field if non-nil, zero value otherwise.

### GetAppHostOk

`func (o *CacheTokenStoreRequest) GetAppHostOk() (*string, bool)`

GetAppHostOk returns a tuple with the AppHost field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppHost

`func (o *CacheTokenStoreRequest) SetAppHost(v string)`

SetAppHost sets AppHost field to given value.


### GetAppType

`func (o *CacheTokenStoreRequest) GetAppType() AppType`

GetAppType returns the AppType field if non-nil, zero value otherwise.

### GetAppTypeOk

`func (o *CacheTokenStoreRequest) GetAppTypeOk() (*AppType, bool)`

GetAppTypeOk returns a tuple with the AppType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppType

`func (o *CacheTokenStoreRequest) SetAppType(v AppType)`

SetAppType sets AppType field to given value.


### GetAccessToken

`func (o *CacheTokenStoreRequest) GetAccessToken() string`

GetAccessToken returns the AccessToken field if non-nil, zero value otherwise.

### GetAccessTokenOk

`func (o *CacheTokenStoreRequest) GetAccessTokenOk() (*string, bool)`

GetAccessTokenOk returns a tuple with the AccessToken field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccessToken

`func (o *CacheTokenStoreRequest) SetAccessToken(v string)`

SetAccessToken sets AccessToken field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


