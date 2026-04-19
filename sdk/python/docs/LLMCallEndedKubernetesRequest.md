# LLMCallEndedKubernetesRequest

Request body for recording the end of an LLM call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**call_id** | **str** |  | 
**response** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.llm_call_ended_kubernetes_request import LLMCallEndedKubernetesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMCallEndedKubernetesRequest from a JSON string
llm_call_ended_kubernetes_request_instance = LLMCallEndedKubernetesRequest.from_json(json)
# print the JSON string representation of the object
print(LLMCallEndedKubernetesRequest.to_json())

# convert the object into a dict
llm_call_ended_kubernetes_request_dict = llm_call_ended_kubernetes_request_instance.to_dict()
# create an instance of LLMCallEndedKubernetesRequest from a dict
llm_call_ended_kubernetes_request_from_dict = LLMCallEndedKubernetesRequest.from_dict(llm_call_ended_kubernetes_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


