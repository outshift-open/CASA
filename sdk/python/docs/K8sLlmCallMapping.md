# K8sLlmCallMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**namespace** | **str** |  | 
**trace_id** | **str** |  | 
**mas_id** | **UUID** |  | 
**app_id** | **UUID** |  | 
**user_input_id** | **UUID** |  | 
**created_at** | **datetime** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.k8s_llm_call_mapping import K8sLlmCallMapping

# TODO update the JSON string below
json = "{}"
# create an instance of K8sLlmCallMapping from a JSON string
k8s_llm_call_mapping_instance = K8sLlmCallMapping.from_json(json)
# print the JSON string representation of the object
print(K8sLlmCallMapping.to_json())

# convert the object into a dict
k8s_llm_call_mapping_dict = k8s_llm_call_mapping_instance.to_dict()
# create an instance of K8sLlmCallMapping from a dict
k8s_llm_call_mapping_from_dict = K8sLlmCallMapping.from_dict(k8s_llm_call_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


