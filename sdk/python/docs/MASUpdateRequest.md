# MASUpdateRequest

Request model for updating a MultiAgentSystem via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**MultiAgentSystemSpecInput**](MultiAgentSystemSpecInput.md) |  | 

## Example

```python
from identity_auth_sdk.models.mas_update_request import MASUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MASUpdateRequest from a JSON string
mas_update_request_instance = MASUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(MASUpdateRequest.to_json())

# convert the object into a dict
mas_update_request_dict = mas_update_request_instance.to_dict()
# create an instance of MASUpdateRequest from a dict
mas_update_request_from_dict = MASUpdateRequest.from_dict(mas_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


