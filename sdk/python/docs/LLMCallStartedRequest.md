# LLMCallStartedRequest

Request body for recording the start of an LLM call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**call_id** | **str** |  | 
**prompt** | **str** |  | 
**tools** | **str** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.llm_call_started_request import LLMCallStartedRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMCallStartedRequest from a JSON string
llm_call_started_request_instance = LLMCallStartedRequest.from_json(json)
# print the JSON string representation of the object
print(LLMCallStartedRequest.to_json())

# convert the object into a dict
llm_call_started_request_dict = llm_call_started_request_instance.to_dict()
# create an instance of LLMCallStartedRequest from a dict
llm_call_started_request_from_dict = LLMCallStartedRequest.from_dict(llm_call_started_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


