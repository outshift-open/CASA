# LLMCallEndedRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**call_id** | **str** |  |
**response** | **str** |  |
**tools** | **str** |  | [optional]

## Example

```python
from identity_auth_sdk.models.llm_call_ended_request import LLMCallEndedRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LLMCallEndedRequest from a JSON string
llm_call_ended_request_instance = LLMCallEndedRequest.from_json(json)
# print the JSON string representation of the object
print(LLMCallEndedRequest.to_json())

# convert the object into a dict
llm_call_ended_request_dict = llm_call_ended_request_instance.to_dict()
# create an instance of LLMCallEndedRequest from a dict
llm_call_ended_request_from_dict = LLMCallEndedRequest.from_dict(llm_call_ended_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
