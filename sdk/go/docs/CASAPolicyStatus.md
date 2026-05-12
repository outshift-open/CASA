# CASAPolicyStatus

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Phase** | Pointer to [**CRDPhase**](CRDPhase.md) | Current phase of the policy | [optional] [default to PENDING]
**LastSyncTime** | Pointer to **time.Time** |  | [optional] 
**Message** | Pointer to **NullableString** | Human-readable status message | [optional] 

## Methods

### NewCASAPolicyStatus

`func NewCASAPolicyStatus() *CASAPolicyStatus`

NewCASAPolicyStatus instantiates a new CASAPolicyStatus object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCASAPolicyStatusWithDefaults

`func NewCASAPolicyStatusWithDefaults() *CASAPolicyStatus`

NewCASAPolicyStatusWithDefaults instantiates a new CASAPolicyStatus object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPhase

`func (o *CASAPolicyStatus) GetPhase() CRDPhase`

GetPhase returns the Phase field if non-nil, zero value otherwise.

### GetPhaseOk

`func (o *CASAPolicyStatus) GetPhaseOk() (*CRDPhase, bool)`

GetPhaseOk returns a tuple with the Phase field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPhase

`func (o *CASAPolicyStatus) SetPhase(v CRDPhase)`

SetPhase sets Phase field to given value.

### HasPhase

`func (o *CASAPolicyStatus) HasPhase() bool`

HasPhase returns a boolean if a field has been set.

### GetLastSyncTime

`func (o *CASAPolicyStatus) GetLastSyncTime() time.Time`

GetLastSyncTime returns the LastSyncTime field if non-nil, zero value otherwise.

### GetLastSyncTimeOk

`func (o *CASAPolicyStatus) GetLastSyncTimeOk() (*time.Time, bool)`

GetLastSyncTimeOk returns a tuple with the LastSyncTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastSyncTime

`func (o *CASAPolicyStatus) SetLastSyncTime(v time.Time)`

SetLastSyncTime sets LastSyncTime field to given value.

### HasLastSyncTime

`func (o *CASAPolicyStatus) HasLastSyncTime() bool`

HasLastSyncTime returns a boolean if a field has been set.

### GetMessage

`func (o *CASAPolicyStatus) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *CASAPolicyStatus) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *CASAPolicyStatus) SetMessage(v string)`

SetMessage sets Message field to given value.

### HasMessage

`func (o *CASAPolicyStatus) HasMessage() bool`

HasMessage returns a boolean if a field has been set.

### SetMessageNil

`func (o *CASAPolicyStatus) SetMessageNil(b bool)`

 SetMessageNil sets the value for Message to be an explicit nil

### UnsetMessage
`func (o *CASAPolicyStatus) UnsetMessage()`

UnsetMessage ensures that no value is present for Message, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


