# ScopeViewModel

Full view model for Scope including relationships.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**name** | **str** |  | 
**mas_id** | **UUID** |  | 
**mas** | [**MultiAgentSystemViewModel**](MultiAgentSystemViewModel.md) |  | 
**tools** | [**List[ToolViewModel]**](ToolViewModel.md) |  | 

## Example

```python
from identity_auth_sdk.models.scope_view_model import ScopeViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of ScopeViewModel from a JSON string
scope_view_model_instance = ScopeViewModel.from_json(json)
# print the JSON string representation of the object
print(ScopeViewModel.to_json())

# convert the object into a dict
scope_view_model_dict = scope_view_model_instance.to_dict()
# create an instance of ScopeViewModel from a dict
scope_view_model_from_dict = ScopeViewModel.from_dict(scope_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


