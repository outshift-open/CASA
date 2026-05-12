# TokenIntrospectResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ClientId** | Pointer to **NullableString** |  | [optional] 
**Scope** | Pointer to **NullableString** |  | [optional] 
**Sub** | Pointer to **NullableString** |  | [optional] 
**Act** | Pointer to [**NullableActorClaim**](ActorClaim.md) |  | [optional] 
**Other** | Pointer to **map[string]interface{}** | Resource annotations | [optional] 
**Exp** | Pointer to **NullableInt32** |  | [optional] 
**UserInputId** | Pointer to **NullableString** |  | [optional] 
**AppId** | Pointer to **NullableString** |  | [optional] 
**MasId** | Pointer to **NullableString** |  | [optional] 
**Tools** | Pointer to **[]string** |  | [optional] 
**Active** | **bool** |  | 

## Methods

### NewTokenIntrospectResponse

`func NewTokenIntrospectResponse(active bool, ) *TokenIntrospectResponse`

NewTokenIntrospectResponse instantiates a new TokenIntrospectResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTokenIntrospectResponseWithDefaults

`func NewTokenIntrospectResponseWithDefaults() *TokenIntrospectResponse`

NewTokenIntrospectResponseWithDefaults instantiates a new TokenIntrospectResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetClientId

`func (o *TokenIntrospectResponse) GetClientId() string`

GetClientId returns the ClientId field if non-nil, zero value otherwise.

### GetClientIdOk

`func (o *TokenIntrospectResponse) GetClientIdOk() (*string, bool)`

GetClientIdOk returns a tuple with the ClientId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientId

`func (o *TokenIntrospectResponse) SetClientId(v string)`

SetClientId sets ClientId field to given value.

### HasClientId

`func (o *TokenIntrospectResponse) HasClientId() bool`

HasClientId returns a boolean if a field has been set.

### SetClientIdNil

`func (o *TokenIntrospectResponse) SetClientIdNil(b bool)`

 SetClientIdNil sets the value for ClientId to be an explicit nil

### UnsetClientId
`func (o *TokenIntrospectResponse) UnsetClientId()`

UnsetClientId ensures that no value is present for ClientId, not even an explicit nil
### GetScope

`func (o *TokenIntrospectResponse) GetScope() string`

GetScope returns the Scope field if non-nil, zero value otherwise.

### GetScopeOk

`func (o *TokenIntrospectResponse) GetScopeOk() (*string, bool)`

GetScopeOk returns a tuple with the Scope field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScope

`func (o *TokenIntrospectResponse) SetScope(v string)`

SetScope sets Scope field to given value.

### HasScope

`func (o *TokenIntrospectResponse) HasScope() bool`

HasScope returns a boolean if a field has been set.

### SetScopeNil

`func (o *TokenIntrospectResponse) SetScopeNil(b bool)`

 SetScopeNil sets the value for Scope to be an explicit nil

### UnsetScope
`func (o *TokenIntrospectResponse) UnsetScope()`

UnsetScope ensures that no value is present for Scope, not even an explicit nil
### GetSub

`func (o *TokenIntrospectResponse) GetSub() string`

GetSub returns the Sub field if non-nil, zero value otherwise.

### GetSubOk

`func (o *TokenIntrospectResponse) GetSubOk() (*string, bool)`

GetSubOk returns a tuple with the Sub field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSub

`func (o *TokenIntrospectResponse) SetSub(v string)`

SetSub sets Sub field to given value.

### HasSub

`func (o *TokenIntrospectResponse) HasSub() bool`

HasSub returns a boolean if a field has been set.

### SetSubNil

`func (o *TokenIntrospectResponse) SetSubNil(b bool)`

 SetSubNil sets the value for Sub to be an explicit nil

### UnsetSub
`func (o *TokenIntrospectResponse) UnsetSub()`

UnsetSub ensures that no value is present for Sub, not even an explicit nil
### GetAct

`func (o *TokenIntrospectResponse) GetAct() ActorClaim`

GetAct returns the Act field if non-nil, zero value otherwise.

### GetActOk

`func (o *TokenIntrospectResponse) GetActOk() (*ActorClaim, bool)`

GetActOk returns a tuple with the Act field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAct

`func (o *TokenIntrospectResponse) SetAct(v ActorClaim)`

SetAct sets Act field to given value.

### HasAct

`func (o *TokenIntrospectResponse) HasAct() bool`

HasAct returns a boolean if a field has been set.

### SetActNil

`func (o *TokenIntrospectResponse) SetActNil(b bool)`

 SetActNil sets the value for Act to be an explicit nil

### UnsetAct
`func (o *TokenIntrospectResponse) UnsetAct()`

UnsetAct ensures that no value is present for Act, not even an explicit nil
### GetOther

`func (o *TokenIntrospectResponse) GetOther() map[string]interface{}`

GetOther returns the Other field if non-nil, zero value otherwise.

### GetOtherOk

`func (o *TokenIntrospectResponse) GetOtherOk() (*map[string]interface{}, bool)`

GetOtherOk returns a tuple with the Other field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOther

`func (o *TokenIntrospectResponse) SetOther(v map[string]interface{})`

SetOther sets Other field to given value.

### HasOther

`func (o *TokenIntrospectResponse) HasOther() bool`

HasOther returns a boolean if a field has been set.

### SetOtherNil

`func (o *TokenIntrospectResponse) SetOtherNil(b bool)`

 SetOtherNil sets the value for Other to be an explicit nil

### UnsetOther
`func (o *TokenIntrospectResponse) UnsetOther()`

UnsetOther ensures that no value is present for Other, not even an explicit nil
### GetExp

`func (o *TokenIntrospectResponse) GetExp() int32`

GetExp returns the Exp field if non-nil, zero value otherwise.

### GetExpOk

`func (o *TokenIntrospectResponse) GetExpOk() (*int32, bool)`

GetExpOk returns a tuple with the Exp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExp

`func (o *TokenIntrospectResponse) SetExp(v int32)`

SetExp sets Exp field to given value.

### HasExp

`func (o *TokenIntrospectResponse) HasExp() bool`

HasExp returns a boolean if a field has been set.

### SetExpNil

`func (o *TokenIntrospectResponse) SetExpNil(b bool)`

 SetExpNil sets the value for Exp to be an explicit nil

### UnsetExp
`func (o *TokenIntrospectResponse) UnsetExp()`

UnsetExp ensures that no value is present for Exp, not even an explicit nil
### GetUserInputId

`func (o *TokenIntrospectResponse) GetUserInputId() string`

GetUserInputId returns the UserInputId field if non-nil, zero value otherwise.

### GetUserInputIdOk

`func (o *TokenIntrospectResponse) GetUserInputIdOk() (*string, bool)`

GetUserInputIdOk returns a tuple with the UserInputId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserInputId

`func (o *TokenIntrospectResponse) SetUserInputId(v string)`

SetUserInputId sets UserInputId field to given value.

### HasUserInputId

`func (o *TokenIntrospectResponse) HasUserInputId() bool`

HasUserInputId returns a boolean if a field has been set.

### SetUserInputIdNil

`func (o *TokenIntrospectResponse) SetUserInputIdNil(b bool)`

 SetUserInputIdNil sets the value for UserInputId to be an explicit nil

### UnsetUserInputId
`func (o *TokenIntrospectResponse) UnsetUserInputId()`

UnsetUserInputId ensures that no value is present for UserInputId, not even an explicit nil
### GetAppId

`func (o *TokenIntrospectResponse) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *TokenIntrospectResponse) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *TokenIntrospectResponse) SetAppId(v string)`

SetAppId sets AppId field to given value.

### HasAppId

`func (o *TokenIntrospectResponse) HasAppId() bool`

HasAppId returns a boolean if a field has been set.

### SetAppIdNil

`func (o *TokenIntrospectResponse) SetAppIdNil(b bool)`

 SetAppIdNil sets the value for AppId to be an explicit nil

### UnsetAppId
`func (o *TokenIntrospectResponse) UnsetAppId()`

UnsetAppId ensures that no value is present for AppId, not even an explicit nil
### GetMasId

`func (o *TokenIntrospectResponse) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *TokenIntrospectResponse) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *TokenIntrospectResponse) SetMasId(v string)`

SetMasId sets MasId field to given value.

### HasMasId

`func (o *TokenIntrospectResponse) HasMasId() bool`

HasMasId returns a boolean if a field has been set.

### SetMasIdNil

`func (o *TokenIntrospectResponse) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *TokenIntrospectResponse) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetTools

`func (o *TokenIntrospectResponse) GetTools() []string`

GetTools returns the Tools field if non-nil, zero value otherwise.

### GetToolsOk

`func (o *TokenIntrospectResponse) GetToolsOk() (*[]string, bool)`

GetToolsOk returns a tuple with the Tools field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTools

`func (o *TokenIntrospectResponse) SetTools(v []string)`

SetTools sets Tools field to given value.

### HasTools

`func (o *TokenIntrospectResponse) HasTools() bool`

HasTools returns a boolean if a field has been set.

### SetToolsNil

`func (o *TokenIntrospectResponse) SetToolsNil(b bool)`

 SetToolsNil sets the value for Tools to be an explicit nil

### UnsetTools
`func (o *TokenIntrospectResponse) UnsetTools()`

UnsetTools ensures that no value is present for Tools, not even an explicit nil
### GetActive

`func (o *TokenIntrospectResponse) GetActive() bool`

GetActive returns the Active field if non-nil, zero value otherwise.

### GetActiveOk

`func (o *TokenIntrospectResponse) GetActiveOk() (*bool, bool)`

GetActiveOk returns a tuple with the Active field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActive

`func (o *TokenIntrospectResponse) SetActive(v bool)`

SetActive sets Active field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


