# MultiAgentSystemCRD

Complete MultiAgentSystem Custom Resource Definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | API version | [optional] [default to 'zta.io/v1alpha1']
**kind** | **str** | Resource kind | [optional] [default to 'MultiAgentSystem']
**metadata** | [**MultiAgentSystemMetadata**](MultiAgentSystemMetadata.md) |  | 
**spec** | [**MultiAgentSystemSpecOutput**](MultiAgentSystemSpecOutput.md) |  | 
**status** | [**MultiAgentSystemStatus**](MultiAgentSystemStatus.md) |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_crd import MultiAgentSystemCRD

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemCRD from a JSON string
multi_agent_system_crd_instance = MultiAgentSystemCRD.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemCRD.to_json())

# convert the object into a dict
multi_agent_system_crd_dict = multi_agent_system_crd_instance.to_dict()
# create an instance of MultiAgentSystemCRD from a dict
multi_agent_system_crd_from_dict = MultiAgentSystemCRD.from_dict(multi_agent_system_crd_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


