# MultiAgentSystemAppsBindingRequest

Request model for binding/unbinding a list of apps to a MAS instance.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_ids** | **List[str]** |  | 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_apps_binding_request import MultiAgentSystemAppsBindingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemAppsBindingRequest from a JSON string
multi_agent_system_apps_binding_request_instance = MultiAgentSystemAppsBindingRequest.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemAppsBindingRequest.to_json())

# convert the object into a dict
multi_agent_system_apps_binding_request_dict = multi_agent_system_apps_binding_request_instance.to_dict()
# create an instance of MultiAgentSystemAppsBindingRequest from a dict
multi_agent_system_apps_binding_request_from_dict = MultiAgentSystemAppsBindingRequest.from_dict(multi_agent_system_apps_binding_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


