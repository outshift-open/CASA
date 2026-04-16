# K8sAppSpecViewModel

View model for application specification data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**name** | **str** |  | 
**type** | [**AppType**](AppType.md) |  | 
**url_host** | **str** |  | 
**url_scheme** | **str** |  | 
**prompt_field_json_path** | **str** |  | [optional] 
**kubernetes_workload_name** | **str** |  | [optional] 
**mas_crd_id** | **UUID** |  | [optional] 
**app_id** | **UUID** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.k8s_app_spec_view_model import K8sAppSpecViewModel

# TODO update the JSON string below
json = "{}"
# create an instance of K8sAppSpecViewModel from a JSON string
k8s_app_spec_view_model_instance = K8sAppSpecViewModel.from_json(json)
# print the JSON string representation of the object
print(K8sAppSpecViewModel.to_json())

# convert the object into a dict
k8s_app_spec_view_model_dict = k8s_app_spec_view_model_instance.to_dict()
# create an instance of K8sAppSpecViewModel from a dict
k8s_app_spec_view_model_from_dict = K8sAppSpecViewModel.from_dict(k8s_app_spec_view_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


