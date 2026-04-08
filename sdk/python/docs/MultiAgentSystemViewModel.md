# MultiAgentSystemViewModel

View model for Multi-Agent System.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**name** | **str** |  | 
**authorization_server_id** | **UUID** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_view_model import MultiAgentSystemViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemViewModel from a JSON string
multi_agent_system_view_model_instance = MultiAgentSystemViewModel.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemViewModel.to_json())

# convert the object into a dict
multi_agent_system_view_model_dict = multi_agent_system_view_model_instance.to_dict()
# create an instance of MultiAgentSystemViewModel from a dict
multi_agent_system_view_model_from_dict = MultiAgentSystemViewModel.from_dict(multi_agent_system_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


