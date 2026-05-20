# CASAPolicyAllowedEndpoint

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Target service name | 
**Namespace** | **string** | Target service namespace | 
**Port** | **int32** | Target port number | 

## Methods

### NewCASAPolicyAllowedEndpoint

`func NewCASAPolicyAllowedEndpoint(name string, namespace string, port int32, ) *CASAPolicyAllowedEndpoint`

NewCASAPolicyAllowedEndpoint instantiates a new CASAPolicyAllowedEndpoint object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCASAPolicyAllowedEndpointWithDefaults

`func NewCASAPolicyAllowedEndpointWithDefaults() *CASAPolicyAllowedEndpoint`

NewCASAPolicyAllowedEndpointWithDefaults instantiates a new CASAPolicyAllowedEndpoint object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *CASAPolicyAllowedEndpoint) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *CASAPolicyAllowedEndpoint) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *CASAPolicyAllowedEndpoint) SetName(v string)`

SetName sets Name field to given value.


### GetNamespace

`func (o *CASAPolicyAllowedEndpoint) GetNamespace() string`

GetNamespace returns the Namespace field if non-nil, zero value otherwise.

### GetNamespaceOk

`func (o *CASAPolicyAllowedEndpoint) GetNamespaceOk() (*string, bool)`

GetNamespaceOk returns a tuple with the Namespace field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNamespace

`func (o *CASAPolicyAllowedEndpoint) SetNamespace(v string)`

SetNamespace sets Namespace field to given value.


### GetPort

`func (o *CASAPolicyAllowedEndpoint) GetPort() int32`

GetPort returns the Port field if non-nil, zero value otherwise.

### GetPortOk

`func (o *CASAPolicyAllowedEndpoint) GetPortOk() (*int32, bool)`

GetPortOk returns a tuple with the Port field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPort

`func (o *CASAPolicyAllowedEndpoint) SetPort(v int32)`

SetPort sets Port field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


