# ToolRequest

Request model for tool creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**description** | **str** |  | 
**input_schema** | **str** |  | 
**output_schema** | **str** |  | 
**scopes** | **List[str]** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.tool_request import ToolRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ToolRequest from a JSON string
tool_request_instance = ToolRequest.from_json(json)
# print the JSON string representation of the object
print(ToolRequest.to_json())

# convert the object into a dict
tool_request_dict = tool_request_instance.to_dict()
# create an instance of ToolRequest from a dict
tool_request_from_dict = ToolRequest.from_dict(tool_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


