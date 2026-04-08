# ScopeUpdateRequest

Request model for scope updates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.scope_update_request import ScopeUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ScopeUpdateRequest from a JSON string
scope_update_request_instance = ScopeUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ScopeUpdateRequest.to_json())

# convert the object into a dict
scope_update_request_dict = scope_update_request_instance.to_dict()
# create an instance of ScopeUpdateRequest from a dict
scope_update_request_from_dict = ScopeUpdateRequest.from_dict(scope_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


