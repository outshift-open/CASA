# MultiAgentSystemUpdateRequest

Request model for updating an existing MAS instance.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**enabled_tool_checks** | [**ToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_update_request import MultiAgentSystemUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemUpdateRequest from a JSON string
multi_agent_system_update_request_instance = MultiAgentSystemUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemUpdateRequest.to_json())

# convert the object into a dict
multi_agent_system_update_request_dict = multi_agent_system_update_request_instance.to_dict()
# create an instance of MultiAgentSystemUpdateRequest from a dict
multi_agent_system_update_request_from_dict = MultiAgentSystemUpdateRequest.from_dict(multi_agent_system_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


