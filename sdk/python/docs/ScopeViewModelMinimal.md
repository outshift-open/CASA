# ScopeViewModelMinimal

Minimal view model for Scope with only essential fields (used in Tool.scopes).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**name** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.scope_view_model_minimal import ScopeViewModelMinimal

# TODO update the JSON string below
json = "{}"
# create an instance of ScopeViewModelMinimal from a JSON string
scope_view_model_minimal_instance = ScopeViewModelMinimal.from_json(json)
# print the JSON string representation of the object
print(ScopeViewModelMinimal.to_json())

# convert the object into a dict
scope_view_model_minimal_dict = scope_view_model_minimal_instance.to_dict()
# create an instance of ScopeViewModelMinimal from a dict
scope_view_model_minimal_from_dict = ScopeViewModelMinimal.from_dict(scope_view_model_minimal_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


