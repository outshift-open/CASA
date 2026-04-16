# K8sAppSpecViewModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **NullableString** |  | [optional] 
**Name** | **string** |  | 
**Type** | [**AppType**](AppType.md) |  | 
**UrlHost** | **string** |  | 
**UrlScheme** | **string** |  | 
**PromptFieldJsonPath** | Pointer to **NullableString** |  | [optional] 
**KubernetesWorkloadName** | Pointer to **NullableString** |  | [optional] 
**MasCrdId** | Pointer to **NullableString** |  | [optional] 
**AppId** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewK8sAppSpecViewModel

`func NewK8sAppSpecViewModel(name string, type_ AppType, urlHost string, urlScheme string, ) *K8sAppSpecViewModel`

NewK8sAppSpecViewModel instantiates a new K8sAppSpecViewModel object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewK8sAppSpecViewModelWithDefaults

`func NewK8sAppSpecViewModelWithDefaults() *K8sAppSpecViewModel`

NewK8sAppSpecViewModelWithDefaults instantiates a new K8sAppSpecViewModel object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *K8sAppSpecViewModel) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *K8sAppSpecViewModel) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *K8sAppSpecViewModel) SetId(v string)`

SetId sets Id field to given value.

### HasId

`func (o *K8sAppSpecViewModel) HasId() bool`

HasId returns a boolean if a field has been set.

### SetIdNil

`func (o *K8sAppSpecViewModel) SetIdNil(b bool)`

 SetIdNil sets the value for Id to be an explicit nil

### UnsetId
`func (o *K8sAppSpecViewModel) UnsetId()`

UnsetId ensures that no value is present for Id, not even an explicit nil
### GetName

`func (o *K8sAppSpecViewModel) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *K8sAppSpecViewModel) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *K8sAppSpecViewModel) SetName(v string)`

SetName sets Name field to given value.


### GetType

`func (o *K8sAppSpecViewModel) GetType() AppType`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *K8sAppSpecViewModel) GetTypeOk() (*AppType, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *K8sAppSpecViewModel) SetType(v AppType)`

SetType sets Type field to given value.


### GetUrlHost

`func (o *K8sAppSpecViewModel) GetUrlHost() string`

GetUrlHost returns the UrlHost field if non-nil, zero value otherwise.

### GetUrlHostOk

`func (o *K8sAppSpecViewModel) GetUrlHostOk() (*string, bool)`

GetUrlHostOk returns a tuple with the UrlHost field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUrlHost

`func (o *K8sAppSpecViewModel) SetUrlHost(v string)`

SetUrlHost sets UrlHost field to given value.


### GetUrlScheme

`func (o *K8sAppSpecViewModel) GetUrlScheme() string`

GetUrlScheme returns the UrlScheme field if non-nil, zero value otherwise.

### GetUrlSchemeOk

`func (o *K8sAppSpecViewModel) GetUrlSchemeOk() (*string, bool)`

GetUrlSchemeOk returns a tuple with the UrlScheme field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUrlScheme

`func (o *K8sAppSpecViewModel) SetUrlScheme(v string)`

SetUrlScheme sets UrlScheme field to given value.


### GetPromptFieldJsonPath

`func (o *K8sAppSpecViewModel) GetPromptFieldJsonPath() string`

GetPromptFieldJsonPath returns the PromptFieldJsonPath field if non-nil, zero value otherwise.

### GetPromptFieldJsonPathOk

`func (o *K8sAppSpecViewModel) GetPromptFieldJsonPathOk() (*string, bool)`

GetPromptFieldJsonPathOk returns a tuple with the PromptFieldJsonPath field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPromptFieldJsonPath

`func (o *K8sAppSpecViewModel) SetPromptFieldJsonPath(v string)`

SetPromptFieldJsonPath sets PromptFieldJsonPath field to given value.

### HasPromptFieldJsonPath

`func (o *K8sAppSpecViewModel) HasPromptFieldJsonPath() bool`

HasPromptFieldJsonPath returns a boolean if a field has been set.

### SetPromptFieldJsonPathNil

`func (o *K8sAppSpecViewModel) SetPromptFieldJsonPathNil(b bool)`

 SetPromptFieldJsonPathNil sets the value for PromptFieldJsonPath to be an explicit nil

### UnsetPromptFieldJsonPath
`func (o *K8sAppSpecViewModel) UnsetPromptFieldJsonPath()`

UnsetPromptFieldJsonPath ensures that no value is present for PromptFieldJsonPath, not even an explicit nil
### GetKubernetesWorkloadName

`func (o *K8sAppSpecViewModel) GetKubernetesWorkloadName() string`

GetKubernetesWorkloadName returns the KubernetesWorkloadName field if non-nil, zero value otherwise.

### GetKubernetesWorkloadNameOk

`func (o *K8sAppSpecViewModel) GetKubernetesWorkloadNameOk() (*string, bool)`

GetKubernetesWorkloadNameOk returns a tuple with the KubernetesWorkloadName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKubernetesWorkloadName

`func (o *K8sAppSpecViewModel) SetKubernetesWorkloadName(v string)`

SetKubernetesWorkloadName sets KubernetesWorkloadName field to given value.

### HasKubernetesWorkloadName

`func (o *K8sAppSpecViewModel) HasKubernetesWorkloadName() bool`

HasKubernetesWorkloadName returns a boolean if a field has been set.

### SetKubernetesWorkloadNameNil

`func (o *K8sAppSpecViewModel) SetKubernetesWorkloadNameNil(b bool)`

 SetKubernetesWorkloadNameNil sets the value for KubernetesWorkloadName to be an explicit nil

### UnsetKubernetesWorkloadName
`func (o *K8sAppSpecViewModel) UnsetKubernetesWorkloadName()`

UnsetKubernetesWorkloadName ensures that no value is present for KubernetesWorkloadName, not even an explicit nil
### GetMasCrdId

`func (o *K8sAppSpecViewModel) GetMasCrdId() string`

GetMasCrdId returns the MasCrdId field if non-nil, zero value otherwise.

### GetMasCrdIdOk

`func (o *K8sAppSpecViewModel) GetMasCrdIdOk() (*string, bool)`

GetMasCrdIdOk returns a tuple with the MasCrdId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMasCrdId

`func (o *K8sAppSpecViewModel) SetMasCrdId(v string)`

SetMasCrdId sets MasCrdId field to given value.

### HasMasCrdId

`func (o *K8sAppSpecViewModel) HasMasCrdId() bool`

HasMasCrdId returns a boolean if a field has been set.

### SetMasCrdIdNil

`func (o *K8sAppSpecViewModel) SetMasCrdIdNil(b bool)`

 SetMasCrdIdNil sets the value for MasCrdId to be an explicit nil

### UnsetMasCrdId
`func (o *K8sAppSpecViewModel) UnsetMasCrdId()`

UnsetMasCrdId ensures that no value is present for MasCrdId, not even an explicit nil
### GetAppId

`func (o *K8sAppSpecViewModel) GetAppId() string`

GetAppId returns the AppId field if non-nil, zero value otherwise.

### GetAppIdOk

`func (o *K8sAppSpecViewModel) GetAppIdOk() (*string, bool)`

GetAppIdOk returns a tuple with the AppId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAppId

`func (o *K8sAppSpecViewModel) SetAppId(v string)`

SetAppId sets AppId field to given value.

### HasAppId

`func (o *K8sAppSpecViewModel) HasAppId() bool`

HasAppId returns a boolean if a field has been set.

### SetAppIdNil

`func (o *K8sAppSpecViewModel) SetAppIdNil(b bool)`

 SetAppIdNil sets the value for AppId to be an explicit nil

### UnsetAppId
`func (o *K8sAppSpecViewModel) UnsetAppId()`

UnsetAppId ensures that no value is present for AppId, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


