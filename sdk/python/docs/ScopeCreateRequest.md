# ScopeCreateRequest

Request model for scope creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**mas_id** | **UUID** |  | 

## Example

```python
from identity_auth_sdk.models.scope_create_request import ScopeCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ScopeCreateRequest from a JSON string
scope_create_request_instance = ScopeCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ScopeCreateRequest.to_json())

# convert the object into a dict
scope_create_request_dict = scope_create_request_instance.to_dict()
# create an instance of ScopeCreateRequest from a dict
scope_create_request_from_dict = ScopeCreateRequest.from_dict(scope_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


