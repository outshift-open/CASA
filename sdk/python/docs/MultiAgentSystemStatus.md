# MultiAgentSystemStatus

Status of MultiAgentSystem CRD.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**phase** | [**MASPhase**](MASPhase.md) | Current phase of the MAS | [optional] 
**apps_ready** | **int** | Number of apps successfully registered | [optional] [default to 0]
**last_sync_time** | **datetime** |  | [optional] 
**message** | **str** |  | [optional] 
**credentials** | [**List[AppCredentials]**](AppCredentials.md) |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_status import MultiAgentSystemStatus

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemStatus from a JSON string
multi_agent_system_status_instance = MultiAgentSystemStatus.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemStatus.to_json())

# convert the object into a dict
multi_agent_system_status_dict = multi_agent_system_status_instance.to_dict()
# create an instance of MultiAgentSystemStatus from a dict
multi_agent_system_status_from_dict = MultiAgentSystemStatus.from_dict(multi_agent_system_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


