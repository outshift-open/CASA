# MultiAgentSystem

An entity describing a multi agent system, which is a set of apps.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**name** | **str** |  | 
**enabled_tool_checks** | [**ToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**authorization_server_id** | **UUID** |  | 
**namespace** | **str** |  | 
**created_at** | **datetime** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system import MultiAgentSystem

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystem from a JSON string
multi_agent_system_instance = MultiAgentSystem.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystem.to_json())

# convert the object into a dict
multi_agent_system_dict = multi_agent_system_instance.to_dict()
# create an instance of MultiAgentSystem from a dict
multi_agent_system_from_dict = MultiAgentSystem.from_dict(multi_agent_system_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


