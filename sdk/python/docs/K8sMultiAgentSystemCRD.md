# K8sMultiAgentSystemCRD

Complete MultiAgentSystem Custom Resource Definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**api_version** | **str** | API version | [optional] [default to 'zta.io/v1alpha1']
**kind** | **str** | Resource kind | [optional] [default to 'MultiAgentSystem']
**namespace** | **str** | Kubernetes namespace | 
**name** | **str** | Display name of the Multi-Agent System | 
**enabled_tool_checks** | [**ToolCheckFlags**](ToolCheckFlags.md) |  | [optional] 
**mas_id** | **UUID** |  | 

## Example

```python
from identity_auth_sdk.models.k8s_multi_agent_system_crd import K8sMultiAgentSystemCRD

# TODO update the JSON string below
json = "{}"
# create an instance of K8sMultiAgentSystemCRD from a JSON string
k8s_multi_agent_system_crd_instance = K8sMultiAgentSystemCRD.from_json(json)
# print the JSON string representation of the object
print(K8sMultiAgentSystemCRD.to_json())

# convert the object into a dict
k8s_multi_agent_system_crd_dict = k8s_multi_agent_system_crd_instance.to_dict()
# create an instance of K8sMultiAgentSystemCRD from a dict
k8s_multi_agent_system_crd_from_dict = K8sMultiAgentSystemCRD.from_dict(k8s_multi_agent_system_crd_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


