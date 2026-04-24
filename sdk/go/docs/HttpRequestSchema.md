# HttpRequestSchema

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PromptFieldJsonPath** | **string** | JSONPath to the prompt field in the HTTP request body | 

## Methods

### NewHttpRequestSchema

`func NewHttpRequestSchema(promptFieldJsonPath string, ) *HttpRequestSchema`

NewHttpRequestSchema instantiates a new HttpRequestSchema object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewHttpRequestSchemaWithDefaults

`func NewHttpRequestSchemaWithDefaults() *HttpRequestSchema`

NewHttpRequestSchemaWithDefaults instantiates a new HttpRequestSchema object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPromptFieldJsonPath

`func (o *HttpRequestSchema) GetPromptFieldJsonPath() string`

GetPromptFieldJsonPath returns the PromptFieldJsonPath field if non-nil, zero value otherwise.

### GetPromptFieldJsonPathOk

`func (o *HttpRequestSchema) GetPromptFieldJsonPathOk() (*string, bool)`

GetPromptFieldJsonPathOk returns a tuple with the PromptFieldJsonPath field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPromptFieldJsonPath

`func (o *HttpRequestSchema) SetPromptFieldJsonPath(v string)`

SetPromptFieldJsonPath sets PromptFieldJsonPath field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


