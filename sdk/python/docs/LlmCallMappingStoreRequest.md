# LlmCallMappingStoreRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**trace_id** | **str** |  | 
**token** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.llm_call_mapping_store_request import LlmCallMappingStoreRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LlmCallMappingStoreRequest from a JSON string
llm_call_mapping_store_request_instance = LlmCallMappingStoreRequest.from_json(json)
# print the JSON string representation of the object
print(LlmCallMappingStoreRequest.to_json())

# convert the object into a dict
llm_call_mapping_store_request_dict = llm_call_mapping_store_request_instance.to_dict()
# create an instance of LlmCallMappingStoreRequest from a dict
llm_call_mapping_store_request_from_dict = LlmCallMappingStoreRequest.from_dict(llm_call_mapping_store_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


