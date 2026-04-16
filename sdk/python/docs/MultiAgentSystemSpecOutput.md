# MultiAgentSystemSpecOutput

Specification for MultiAgentSystem CRD.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Display name of the Multi-Agent System | 
**enabled_tool_checks** | [**List[ToolCheckType]**](ToolCheckType.md) | List of enabled tool check types | [optional] 
**apps** | [**List[AppSpec]**](AppSpec.md) | List of applications in this MAS | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_spec_output import MultiAgentSystemSpecOutput

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemSpecOutput from a JSON string
multi_agent_system_spec_output_instance = MultiAgentSystemSpecOutput.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemSpecOutput.to_json())

# convert the object into a dict
multi_agent_system_spec_output_dict = multi_agent_system_spec_output_instance.to_dict()
# create an instance of MultiAgentSystemSpecOutput from a dict
multi_agent_system_spec_output_from_dict = MultiAgentSystemSpecOutput.from_dict(multi_agent_system_spec_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


