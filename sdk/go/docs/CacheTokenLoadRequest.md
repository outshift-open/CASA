# CacheTokenLoadRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TraceId** | **string** |  | 
**AppHost** | **string** |  | 
**AppType** | [**AppType**](AppType.md) |  | 
**Tool** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewCacheTokenLoadRequest

`func NewCacheTokenLoadRequest(traceId string, appHost string, appType AppType, ) *CacheTokenLoadRequest`

NewCacheTokenLoadRequest instantiates a new CacheTokenLoadRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCacheTokenLoadRequestWithDefaults

`func NewCacheTokenLoadRequestWithDefaults() *CacheTokenLoadRequest`

NewCacheTokenLoadRequestWithDefaults instantiates a new CacheTokenLoadRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTraceId

`func (o *CacheTokenLoadRequest) GetTraceId() string`

GetTraceId returns the TraceId field if non-nil, zero value otherwise.

### GetTraceIdOk

`func (o *CacheTokenLoadRequest) GetTraceIdOk() (*string, bool)`

GetTraceIdOk returns a tuple with the TraceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraceId

`func (o *CacheTokenLoadRequest) SetTraceId(v string)`

SetTraceId sets TraceId field to given value.


### GetAppHost

`func (o *CacheTokenLoadRequest) GetAppHost() string`

GetAppHost returns the AppHost field if non-nil, zero value otherwise.

### GetAppHostOk

`func (o *CacheTokenLoadRequest) GetAppHostOk() (*string, bool)`

GetAppHostOk returns a tuple with the AppHost field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppHost

`func (o *CacheTokenLoadRequest) SetAppHost(v string)`

SetAppHost sets AppHost field to given value.


### GetAppType

`func (o *CacheTokenLoadRequest) GetAppType() AppType`

GetAppType returns the AppType field if non-nil, zero value otherwise.

### GetAppTypeOk

`func (o *CacheTokenLoadRequest) GetAppTypeOk() (*AppType, bool)`

GetAppTypeOk returns a tuple with the AppType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppType

`func (o *CacheTokenLoadRequest) SetAppType(v AppType)`

SetAppType sets AppType field to given value.


### GetTool

`func (o *CacheTokenLoadRequest) GetTool() string`

GetTool returns the Tool field if non-nil, zero value otherwise.

### GetToolOk

`func (o *CacheTokenLoadRequest) GetToolOk() (*string, bool)`

GetToolOk returns a tuple with the Tool field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTool

`func (o *CacheTokenLoadRequest) SetTool(v string)`

SetTool sets Tool field to given value.

### HasTool

`func (o *CacheTokenLoadRequest) HasTool() bool`

HasTool returns a boolean if a field has been set.

### SetToolNil

`func (o *CacheTokenLoadRequest) SetToolNil(b bool)`

 SetToolNil sets the value for Tool to be an explicit nil

### UnsetTool
`func (o *CacheTokenLoadRequest) UnsetTool()`

UnsetTool ensures that no value is present for Tool, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


