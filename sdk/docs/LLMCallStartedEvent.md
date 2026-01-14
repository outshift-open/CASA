# LLMCallStartedEvent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional]
**user_input_id** | **str** |  |
**created_at** | **datetime** |  | [optional]
**call_id** | **str** |  |
**token** | **str** |  |
**app_id** | **str** |  |
**prompt** | **str** |  |
**tools** | **str** |  |

## Example

```python
from identity_auth_sdk.models.llm_call_started_event import LLMCallStartedEvent

# TODO update the JSON string below
json = "{}"
# create an instance of LLMCallStartedEvent from a JSON string
llm_call_started_event_instance = LLMCallStartedEvent.from_json(json)
# print the JSON string representation of the object
print(LLMCallStartedEvent.to_json())

# convert the object into a dict
llm_call_started_event_dict = llm_call_started_event_instance.to_dict()
# create an instance of LLMCallStartedEvent from a dict
llm_call_started_event_from_dict = LLMCallStartedEvent.from_dict(llm_call_started_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
