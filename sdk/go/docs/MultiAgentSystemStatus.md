# MultiAgentSystemStatus

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Phase** | Pointer to [**MASPhase**](MASPhase.md) | Current phase of the MAS | [optional] [default to PENDING]
**AppsReady** | Pointer to **int32** | Number of apps successfully registered | [optional] [default to 0]
**LastSyncTime** | Pointer to **time.Time** |  | [optional] 
**Message** | Pointer to **NullableString** |  | [optional] 
**Credentials** | Pointer to [**[]AppCredentials**](AppCredentials.md) |  | [optional] 

## Methods

### NewMultiAgentSystemStatus

`func NewMultiAgentSystemStatus() *MultiAgentSystemStatus`

NewMultiAgentSystemStatus instantiates a new MultiAgentSystemStatus object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiAgentSystemStatusWithDefaults

`func NewMultiAgentSystemStatusWithDefaults() *MultiAgentSystemStatus`

NewMultiAgentSystemStatusWithDefaults instantiates a new MultiAgentSystemStatus object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPhase

`func (o *MultiAgentSystemStatus) GetPhase() MASPhase`

GetPhase returns the Phase field if non-nil, zero value otherwise.

### GetPhaseOk

`func (o *MultiAgentSystemStatus) GetPhaseOk() (*MASPhase, bool)`

GetPhaseOk returns a tuple with the Phase field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPhase

`func (o *MultiAgentSystemStatus) SetPhase(v MASPhase)`

SetPhase sets Phase field to given value.

### HasPhase

`func (o *MultiAgentSystemStatus) HasPhase() bool`

HasPhase returns a boolean if a field has been set.

### GetAppsReady

`func (o *MultiAgentSystemStatus) GetAppsReady() int32`

GetAppsReady returns the AppsReady field if non-nil, zero value otherwise.

### GetAppsReadyOk

`func (o *MultiAgentSystemStatus) GetAppsReadyOk() (*int32, bool)`

GetAppsReadyOk returns a tuple with the AppsReady field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppsReady

`func (o *MultiAgentSystemStatus) SetAppsReady(v int32)`

SetAppsReady sets AppsReady field to given value.

### HasAppsReady

`func (o *MultiAgentSystemStatus) HasAppsReady() bool`

HasAppsReady returns a boolean if a field has been set.

### GetLastSyncTime

`func (o *MultiAgentSystemStatus) GetLastSyncTime() time.Time`

GetLastSyncTime returns the LastSyncTime field if non-nil, zero value otherwise.

### GetLastSyncTimeOk

`func (o *MultiAgentSystemStatus) GetLastSyncTimeOk() (*time.Time, bool)`

GetLastSyncTimeOk returns a tuple with the LastSyncTime field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastSyncTime

`func (o *MultiAgentSystemStatus) SetLastSyncTime(v time.Time)`

SetLastSyncTime sets LastSyncTime field to given value.

### HasLastSyncTime

`func (o *MultiAgentSystemStatus) HasLastSyncTime() bool`

HasLastSyncTime returns a boolean if a field has been set.

### GetMessage

`func (o *MultiAgentSystemStatus) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *MultiAgentSystemStatus) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *MultiAgentSystemStatus) SetMessage(v string)`

SetMessage sets Message field to given value.

### HasMessage

`func (o *MultiAgentSystemStatus) HasMessage() bool`

HasMessage returns a boolean if a field has been set.

### SetMessageNil

`func (o *MultiAgentSystemStatus) SetMessageNil(b bool)`

 SetMessageNil sets the value for Message to be an explicit nil

### UnsetMessage
`func (o *MultiAgentSystemStatus) UnsetMessage()`

UnsetMessage ensures that no value is present for Message, not even an explicit nil
### GetCredentials

`func (o *MultiAgentSystemStatus) GetCredentials() []AppCredentials`

GetCredentials returns the Credentials field if non-nil, zero value otherwise.

### GetCredentialsOk

`func (o *MultiAgentSystemStatus) GetCredentialsOk() (*[]AppCredentials, bool)`

GetCredentialsOk returns a tuple with the Credentials field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCredentials

`func (o *MultiAgentSystemStatus) SetCredentials(v []AppCredentials)`

SetCredentials sets Credentials field to given value.

### HasCredentials

`func (o *MultiAgentSystemStatus) HasCredentials() bool`

HasCredentials returns a boolean if a field has been set.

### SetCredentialsNil

`func (o *MultiAgentSystemStatus) SetCredentialsNil(b bool)`

 SetCredentialsNil sets the value for Credentials to be an explicit nil

### UnsetCredentials
`func (o *MultiAgentSystemStatus) UnsetCredentials()`

UnsetCredentials ensures that no value is present for Credentials, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


