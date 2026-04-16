# AppViewModel

View model for App including tools and MAS relationships.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**type** | **str** |  | 
**name** | **str** |  | 
**base_url** | **str** |  | 
**tools** | [**List[ToolViewModel]**](ToolViewModel.md) |  | 
**mas_id** | **UUID** |  | 
**mas** | [**MultiAgentSystemViewModel**](MultiAgentSystemViewModel.md) |  | 

## Example

```python
from identity_auth_sdk.models.app_view_model import AppViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of AppViewModel from a JSON string
app_view_model_instance = AppViewModel.from_json(json)
# print the JSON string representation of the object
print(AppViewModel.to_json())

# convert the object into a dict
app_view_model_dict = app_view_model_instance.to_dict()
# create an instance of AppViewModel from a dict
app_view_model_from_dict = AppViewModel.from_dict(app_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


