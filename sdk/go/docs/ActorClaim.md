# ActorClaim

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Sub** | **string** |  | 
**Act** | Pointer to [**NullableActorClaim**](ActorClaim.md) |  | [optional] 

## Methods

### NewActorClaim

`func NewActorClaim(sub string, ) *ActorClaim`

NewActorClaim instantiates a new ActorClaim object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewActorClaimWithDefaults

`func NewActorClaimWithDefaults() *ActorClaim`

NewActorClaimWithDefaults instantiates a new ActorClaim object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSub

`func (o *ActorClaim) GetSub() string`

GetSub returns the Sub field if non-nil, zero value otherwise.

### GetSubOk

`func (o *ActorClaim) GetSubOk() (*string, bool)`

GetSubOk returns a tuple with the Sub field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSub

`func (o *ActorClaim) SetSub(v string)`

SetSub sets Sub field to given value.


### GetAct

`func (o *ActorClaim) GetAct() ActorClaim`

GetAct returns the Act field if non-nil, zero value otherwise.

### GetActOk

`func (o *ActorClaim) GetActOk() (*ActorClaim, bool)`

GetActOk returns a tuple with the Act field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAct

`func (o *ActorClaim) SetAct(v ActorClaim)`

SetAct sets Act field to given value.

### HasAct

`func (o *ActorClaim) HasAct() bool`

HasAct returns a boolean if a field has been set.

### SetActNil

`func (o *ActorClaim) SetActNil(b bool)`

 SetActNil sets the value for Act to be an explicit nil

### UnsetAct
`func (o *ActorClaim) UnsetAct()`

UnsetAct ensures that no value is present for Act, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


