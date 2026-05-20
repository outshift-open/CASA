# AppSpec

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Name of the application | 
**Type** | [**AppType**](AppType.md) | Type of the application | 
**BaseUrl** | [**AppSpecBaseUrl**](AppSpecBaseUrl.md) | Base URL of the application | 
**KubernetesWorkloadName** | Pointer to **NullableString** | Name of the Kubernetes workload running the app | [optional] 
**HttpRequestSchema** | Pointer to [**NullableHttpRequestSchema**](HttpRequestSchema.md) | HTTP request schema for extracting the prompt field | [optional] 

## Methods

### NewAppSpec

`func NewAppSpec(name string, type_ AppType, baseUrl AppSpecBaseUrl, ) *AppSpec`

NewAppSpec instantiates a new AppSpec object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSpecWithDefaults

`func NewAppSpecWithDefaults() *AppSpec`

NewAppSpecWithDefaults instantiates a new AppSpec object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *AppSpec) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *AppSpec) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *AppSpec) SetName(v string)`

SetName sets Name field to given value.


### GetType

`func (o *AppSpec) GetType() AppType`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *AppSpec) GetTypeOk() (*AppType, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *AppSpec) SetType(v AppType)`

SetType sets Type field to given value.


### GetBaseUrl

`func (o *AppSpec) GetBaseUrl() AppSpecBaseUrl`

GetBaseUrl returns the BaseUrl field if non-nil, zero value otherwise.

### GetBaseUrlOk

`func (o *AppSpec) GetBaseUrlOk() (*AppSpecBaseUrl, bool)`

GetBaseUrlOk returns a tuple with the BaseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBaseUrl

`func (o *AppSpec) SetBaseUrl(v AppSpecBaseUrl)`

SetBaseUrl sets BaseUrl field to given value.


### GetKubernetesWorkloadName

`func (o *AppSpec) GetKubernetesWorkloadName() string`

GetKubernetesWorkloadName returns the KubernetesWorkloadName field if non-nil, zero value otherwise.

### GetKubernetesWorkloadNameOk

`func (o *AppSpec) GetKubernetesWorkloadNameOk() (*string, bool)`

GetKubernetesWorkloadNameOk returns a tuple with the KubernetesWorkloadName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKubernetesWorkloadName

`func (o *AppSpec) SetKubernetesWorkloadName(v string)`

SetKubernetesWorkloadName sets KubernetesWorkloadName field to given value.

### HasKubernetesWorkloadName

`func (o *AppSpec) HasKubernetesWorkloadName() bool`

HasKubernetesWorkloadName returns a boolean if a field has been set.

### SetKubernetesWorkloadNameNil

`func (o *AppSpec) SetKubernetesWorkloadNameNil(b bool)`

 SetKubernetesWorkloadNameNil sets the value for KubernetesWorkloadName to be an explicit nil

### UnsetKubernetesWorkloadName
`func (o *AppSpec) UnsetKubernetesWorkloadName()`

UnsetKubernetesWorkloadName ensures that no value is present for KubernetesWorkloadName, not even an explicit nil
### GetHttpRequestSchema

`func (o *AppSpec) GetHttpRequestSchema() HttpRequestSchema`

GetHttpRequestSchema returns the HttpRequestSchema field if non-nil, zero value otherwise.

### GetHttpRequestSchemaOk

`func (o *AppSpec) GetHttpRequestSchemaOk() (*HttpRequestSchema, bool)`

GetHttpRequestSchemaOk returns a tuple with the HttpRequestSchema field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHttpRequestSchema

`func (o *AppSpec) SetHttpRequestSchema(v HttpRequestSchema)`

SetHttpRequestSchema sets HttpRequestSchema field to given value.

### HasHttpRequestSchema

`func (o *AppSpec) HasHttpRequestSchema() bool`

HasHttpRequestSchema returns a boolean if a field has been set.

### SetHttpRequestSchemaNil

`func (o *AppSpec) SetHttpRequestSchemaNil(b bool)`

 SetHttpRequestSchemaNil sets the value for HttpRequestSchema to be an explicit nil

### UnsetHttpRequestSchema
`func (o *AppSpec) UnsetHttpRequestSchema()`

UnsetHttpRequestSchema ensures that no value is present for HttpRequestSchema, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


