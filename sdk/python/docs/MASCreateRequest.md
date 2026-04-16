# MASCreateRequest

Request model for creating a MultiAgentSystem via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**spec** | [**MultiAgentSystemSpecInput**](MultiAgentSystemSpecInput.md) |  | 

## Example

```python
from identity_auth_sdk.models.mas_create_request import MASCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MASCreateRequest from a JSON string
mas_create_request_instance = MASCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MASCreateRequest.to_json())

# convert the object into a dict
mas_create_request_dict = mas_create_request_instance.to_dict()
# create an instance of MASCreateRequest from a dict
mas_create_request_from_dict = MASCreateRequest.from_dict(mas_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


