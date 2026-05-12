# MASTraceStat

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**MasId** | **string** |  | 
**Traces** | **int32** |  | 
**Allowed** | **int32** |  | 
**Denied** | **int32** |  | 

## Methods

### NewMASTraceStat

`func NewMASTraceStat(masId string, traces int32, allowed int32, denied int32, ) *MASTraceStat`

NewMASTraceStat instantiates a new MASTraceStat object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMASTraceStatWithDefaults

`func NewMASTraceStatWithDefaults() *MASTraceStat`

NewMASTraceStatWithDefaults instantiates a new MASTraceStat object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMasId

`func (o *MASTraceStat) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *MASTraceStat) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *MASTraceStat) SetMasId(v string)`

SetMasId sets MasId field to given value.


### GetTraces

`func (o *MASTraceStat) GetTraces() int32`

GetTraces returns the Traces field if non-nil, zero value otherwise.

### GetTracesOk

`func (o *MASTraceStat) GetTracesOk() (*int32, bool)`

GetTracesOk returns a tuple with the Traces field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraces

`func (o *MASTraceStat) SetTraces(v int32)`

SetTraces sets Traces field to given value.


### GetAllowed

`func (o *MASTraceStat) GetAllowed() int32`

GetAllowed returns the Allowed field if non-nil, zero value otherwise.

### GetAllowedOk

`func (o *MASTraceStat) GetAllowedOk() (*int32, bool)`

GetAllowedOk returns a tuple with the Allowed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllowed

`func (o *MASTraceStat) SetAllowed(v int32)`

SetAllowed sets Allowed field to given value.


### GetDenied

`func (o *MASTraceStat) GetDenied() int32`

GetDenied returns the Denied field if non-nil, zero value otherwise.

### GetDeniedOk

`func (o *MASTraceStat) GetDeniedOk() (*int32, bool)`

GetDeniedOk returns a tuple with the Denied field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDenied

`func (o *MASTraceStat) SetDenied(v int32)`

SetDenied sets Denied field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


