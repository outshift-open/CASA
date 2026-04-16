# K8sMultiAgentSystemCRDViewModel

View model for a complete MultiAgentSystem CRD.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**api_version** | **str** |  | 
**kind** | **str** |  | 
**namespace** | **str** |  | 
**mas_metadata** | [**K8sMultiAgentSystemMetadataViewModel**](K8sMultiAgentSystemMetadataViewModel.md) |  | [optional] 
**name** | **str** |  | 
**enabled_tool_checks** | [**ToolCheckFlags**](ToolCheckFlags.md) |  | 
**app_specs** | [**List[K8sAppSpecViewModel]**](K8sAppSpecViewModel.md) |  | [optional] [default to []]
**mas_id** | **UUID** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.k8s_multi_agent_system_crd_view_model import K8sMultiAgentSystemCRDViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of K8sMultiAgentSystemCRDViewModel from a JSON string
k8s_multi_agent_system_crd_view_model_instance = K8sMultiAgentSystemCRDViewModel.from_json(json)
# print the JSON string representation of the object
print(K8sMultiAgentSystemCRDViewModel.to_json())

# convert the object into a dict
k8s_multi_agent_system_crd_view_model_dict = k8s_multi_agent_system_crd_view_model_instance.to_dict()
# create an instance of K8sMultiAgentSystemCRDViewModel from a dict
k8s_multi_agent_system_crd_view_model_from_dict = K8sMultiAgentSystemCRDViewModel.from_dict(k8s_multi_agent_system_crd_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


