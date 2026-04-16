# AppMetadataResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ClientId** | **string** |  | 
**ClientName** | **string** |  | 
**GrantTypes** | **[]string** |  | 
**ResponseTypes** | **[]string** |  | 
**TokenEndpointAuthMethod** | **string** |  | 
**JwksUri** | **string** |  | 

## Methods

### NewAppMetadataResponse

`func NewAppMetadataResponse(clientId string, clientName string, grantTypes []string, responseTypes []string, tokenEndpointAuthMethod string, jwksUri string, ) *AppMetadataResponse`

NewAppMetadataResponse instantiates a new AppMetadataResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppMetadataResponseWithDefaults

`func NewAppMetadataResponseWithDefaults() *AppMetadataResponse`

NewAppMetadataResponseWithDefaults instantiates a new AppMetadataResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetClientId

`func (o *AppMetadataResponse) GetClientId() string`

GetClientId returns the ClientId field if non-nil, zero value otherwise.

### GetClientIdOk

`func (o *AppMetadataResponse) GetClientIdOk() (*string, bool)`

GetClientIdOk returns a tuple with the ClientId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientId

`func (o *AppMetadataResponse) SetClientId(v string)`

SetClientId sets ClientId field to given value.


### GetClientName

`func (o *AppMetadataResponse) GetClientName() string`

GetClientName returns the ClientName field if non-nil, zero value otherwise.

### GetClientNameOk

`func (o *AppMetadataResponse) GetClientNameOk() (*string, bool)`

GetClientNameOk returns a tuple with the ClientName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClientName

`func (o *AppMetadataResponse) SetClientName(v string)`

SetClientName sets ClientName field to given value.


### GetGrantTypes

`func (o *AppMetadataResponse) GetGrantTypes() []string`

GetGrantTypes returns the GrantTypes field if non-nil, zero value otherwise.

### GetGrantTypesOk

`func (o *AppMetadataResponse) GetGrantTypesOk() (*[]string, bool)`

GetGrantTypesOk returns a tuple with the GrantTypes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGrantTypes

`func (o *AppMetadataResponse) SetGrantTypes(v []string)`

SetGrantTypes sets GrantTypes field to given value.


### GetResponseTypes

`func (o *AppMetadataResponse) GetResponseTypes() []string`

GetResponseTypes returns the ResponseTypes field if non-nil, zero value otherwise.

### GetResponseTypesOk

`func (o *AppMetadataResponse) GetResponseTypesOk() (*[]string, bool)`

GetResponseTypesOk returns a tuple with the ResponseTypes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResponseTypes

`func (o *AppMetadataResponse) SetResponseTypes(v []string)`

SetResponseTypes sets ResponseTypes field to given value.


### GetTokenEndpointAuthMethod

`func (o *AppMetadataResponse) GetTokenEndpointAuthMethod() string`

GetTokenEndpointAuthMethod returns the TokenEndpointAuthMethod field if non-nil, zero value otherwise.

### GetTokenEndpointAuthMethodOk

`func (o *AppMetadataResponse) GetTokenEndpointAuthMethodOk() (*string, bool)`

GetTokenEndpointAuthMethodOk returns a tuple with the TokenEndpointAuthMethod field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTokenEndpointAuthMethod

`func (o *AppMetadataResponse) SetTokenEndpointAuthMethod(v string)`

SetTokenEndpointAuthMethod sets TokenEndpointAuthMethod field to given value.


### GetJwksUri

`func (o *AppMetadataResponse) GetJwksUri() string`

GetJwksUri returns the JwksUri field if non-nil, zero value otherwise.

### GetJwksUriOk

`func (o *AppMetadataResponse) GetJwksUriOk() (*string, bool)`

GetJwksUriOk returns a tuple with the JwksUri field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJwksUri

`func (o *AppMetadataResponse) SetJwksUri(v string)`

SetJwksUri sets JwksUri field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


