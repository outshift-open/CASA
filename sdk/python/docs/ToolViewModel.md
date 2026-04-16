# ToolViewModel

View model for Tool including its scopes.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**input_schema** | **str** |  | 
**output_schema** | **str** |  | 
**app_id** | **UUID** |  | 
**scopes** | [**List[ScopeViewModelMinimal]**](ScopeViewModelMinimal.md) |  | 

## Example

```python
from identity_auth_sdk.models.tool_view_model import ToolViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of ToolViewModel from a JSON string
tool_view_model_instance = ToolViewModel.from_json(json)
# print the JSON string representation of the object
print(ToolViewModel.to_json())

# convert the object into a dict
tool_view_model_dict = tool_view_model_instance.to_dict()
# create an instance of ToolViewModel from a dict
tool_view_model_from_dict = ToolViewModel.from_dict(tool_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


