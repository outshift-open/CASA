# K8sMultiAgentSystemMetadataViewModel

View model for MultiAgentSystem metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**name** | **str** |  | 
**uid** | **str** |  | [optional] 
**resource_version** | **str** |  | [optional] 
**generation** | **int** |  | [optional] 
**mas_crd_id** | **UUID** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.k8s_multi_agent_system_metadata_view_model import K8sMultiAgentSystemMetadataViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of K8sMultiAgentSystemMetadataViewModel from a JSON string
k8s_multi_agent_system_metadata_view_model_instance = K8sMultiAgentSystemMetadataViewModel.from_json(json)
# print the JSON string representation of the object
print(K8sMultiAgentSystemMetadataViewModel.to_json())

# convert the object into a dict
k8s_multi_agent_system_metadata_view_model_dict = k8s_multi_agent_system_metadata_view_model_instance.to_dict()
# create an instance of K8sMultiAgentSystemMetadataViewModel from a dict
k8s_multi_agent_system_metadata_view_model_from_dict = K8sMultiAgentSystemMetadataViewModel.from_dict(k8s_multi_agent_system_metadata_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


