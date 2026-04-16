# AppMetadataResponse

Pydantic model for app metadata response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** |  | 
**client_name** | **str** |  | 
**grant_types** | **List[str]** |  | 
**response_types** | **List[str]** |  | 
**token_endpoint_auth_method** | **str** |  | 
**jwks_uri** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.app_metadata_response import AppMetadataResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AppMetadataResponse from a JSON string
app_metadata_response_instance = AppMetadataResponse.from_json(json)
# print the JSON string representation of the object
print(AppMetadataResponse.to_json())

# convert the object into a dict
app_metadata_response_dict = app_metadata_response_instance.to_dict()
# create an instance of AppMetadataResponse from a dict
app_metadata_response_from_dict = AppMetadataResponse.from_dict(app_metadata_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


