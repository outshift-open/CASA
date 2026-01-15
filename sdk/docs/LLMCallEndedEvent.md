# LLMCallEndedEvent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional]
**user_input_id** | **str** |  |
**created_at** | **datetime** |  | [optional]
**call_id** | **str** |  |
**token** | **str** |  |
**app_id** | **str** |  |
**response** | **str** |  |
**tools** | **str** |  |

## Example

```python
from identity_auth_sdk.models.llm_call_ended_event import LLMCallEndedEvent

# TODO update the JSON string below
json = "{}"
# create an instance of LLMCallEndedEvent from a JSON string
llm_call_ended_event_instance = LLMCallEndedEvent.from_json(json)
# print the JSON string representation of the object
print(LLMCallEndedEvent.to_json())

# convert the object into a dict
llm_call_ended_event_dict = llm_call_ended_event_instance.to_dict()
# create an instance of LLMCallEndedEvent from a dict
llm_call_ended_event_from_dict = LLMCallEndedEvent.from_dict(llm_call_ended_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
