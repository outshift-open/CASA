# K8sLlmCallMapping

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Namespace** | **string** |  | 
**TraceId** | **string** |  | 
**MasId** | **NullableString** |  | 
**AppId** | **NullableString** |  | 
**UserInputId** | **NullableString** |  | 
**Token** | Pointer to **NullableString** |  | [optional] 
**CreatedAt** | Pointer to **string** |  | [optional] [default to "2026-04-24T09:07:11.693086Z"]

## Methods

### NewK8sLlmCallMapping

`func NewK8sLlmCallMapping(namespace string, traceId string, masId NullableString, appId NullableString, userInputId NullableString, ) *K8sLlmCallMapping`

NewK8sLlmCallMapping instantiates a new K8sLlmCallMapping object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewK8sLlmCallMappingWithDefaults

`func NewK8sLlmCallMappingWithDefaults() *K8sLlmCallMapping`

NewK8sLlmCallMappingWithDefaults instantiates a new K8sLlmCallMapping object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *K8sLlmCallMapping) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *K8sLlmCallMapping) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *K8sLlmCallMapping) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *K8sLlmCallMapping) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *K8sLlmCallMapping) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *K8sLlmCallMapping) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetNamespace

`func (o *K8sLlmCallMapping) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *K8sLlmCallMapping) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *K8sLlmCallMapping) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### GetTraceId

`func (o *K8sLlmCallMapping) GetTraceId() string`

GetTraceId returns the TraceId field if non-nil, zero value otherwise.

### GetTraceIdOk

`func (o *K8sLlmCallMapping) GetTraceIdOk() (*string, bool)`

GetTraceIdOk returns a tuple with the TraceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTraceId

`func (o *K8sLlmCallMapping) SetTraceId(v string)`

SetTraceId sets TraceId field to given value.


### GetMasId

`func (o *K8sLlmCallMapping) GetMasId() string`

GetMasId returns the MasId field if non-nil, zero value otherwise.

### GetMasIdOk

`func (o *K8sLlmCallMapping) GetMasIdOk() (*string, bool)`

GetMasIdOk returns a tuple with the MasId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasId

`func (o *K8sLlmCallMapping) SetMasId(v string)`

SetMasId sets MasId field to given value.


### SetMasIdNil

`func (o *K8sLlmCallMapping) SetMasIdNil(b bool)`

 SetMasIdNil sets the value for MasId to be an explicit nil

### UnsetMasId
`func (o *K8sLlmCallMapping) UnsetMasId()`

UnsetMasId ensures that no value is present for MasId, not even an explicit nil
### GetAppId

`func (o *K8sLlmCallMapping) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *K8sLlmCallMapping) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *K8sLlmCallMapping) SetAppId(v string)`

SetAppId sets AppId field to given value.


### SetAppIdNil

`func (o *K8sLlmCallMapping) SetAppIdNil(b bool)`

 SetAppIdNil sets the value for AppId to be an explicit nil

### UnsetAppId
`func (o *K8sLlmCallMapping) UnsetAppId()`

UnsetAppId ensures that no value is present for AppId, not even an explicit nil
### GetUserInputId

`func (o *K8sLlmCallMapping) GetUserInputId() string`

GetUserInputId returns the UserInputId field if non-nil, zero value otherwise.

### GetUserInputIdOk

`func (o *K8sLlmCallMapping) GetUserInputIdOk() (*string, bool)`

GetUserInputIdOk returns a tuple with the UserInputId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserInputId

`func (o *K8sLlmCallMapping) SetUserInputId(v string)`

SetUserInputId sets UserInputId field to given value.


### SetUserInputIdNil

`func (o *K8sLlmCallMapping) SetUserInputIdNil(b bool)`

 SetUserInputIdNil sets the value for UserInputId to be an explicit nil

### UnsetUserInputId
`func (o *K8sLlmCallMapping) UnsetUserInputId()`

UnsetUserInputId ensures that no value is present for UserInputId, not even an explicit nil
### GetToken

`func (o *K8sLlmCallMapping) GetToken() string`

GetToken returns the Token field if non-nil, zero value otherwise.

### GetTokenOk

`func (o *K8sLlmCallMapping) GetTokenOk() (*string, bool)`

GetTokenOk returns a tuple with the Token field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetToken

`func (o *K8sLlmCallMapping) SetToken(v string)`

SetToken sets Token field to given value.

### HasToken

`func (o *K8sLlmCallMapping) HasToken() bool`

HasToken returns a boolean if a field has been set.

### SetTokenNil

`func (o *K8sLlmCallMapping) SetTokenNil(b bool)`

 SetTokenNil sets the value for Token to be an explicit nil

### UnsetToken
`func (o *K8sLlmCallMapping) UnsetToken()`

UnsetToken ensures that no value is present for Token, not even an explicit nil
### GetCreatedAt

`func (o *K8sLlmCallMapping) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *K8sLlmCallMapping) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *K8sLlmCallMapping) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.

### HasCreatedAt

`func (o *K8sLlmCallMapping) HasCreatedAt() bool`

HasCreatedAt returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


