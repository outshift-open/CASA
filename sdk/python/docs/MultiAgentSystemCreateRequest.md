# MultiAgentSystemCreateRequest

Request model for MAS creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**enabled_tool_checks** | [**ToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**namespace** | **str** |  | [optional] 
**k8s_name** | **str** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_create_request import MultiAgentSystemCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemCreateRequest from a JSON string
multi_agent_system_create_request_instance = MultiAgentSystemCreateRequest.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemCreateRequest.to_json())

# convert the object into a dict
multi_agent_system_create_request_dict = multi_agent_system_create_request_instance.to_dict()
# create an instance of MultiAgentSystemCreateRequest from a dict
multi_agent_system_create_request_from_dict = MultiAgentSystemCreateRequest.from_dict(multi_agent_system_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


