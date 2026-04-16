# MASStatusUpdateRequest

Request model for updating MAS status (used by operator).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**MultiAgentSystemStatus**](MultiAgentSystemStatus.md) |  | 

## Example

```python
from identity_auth_sdk.models.mas_status_update_request import MASStatusUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MASStatusUpdateRequest from a JSON string
mas_status_update_request_instance = MASStatusUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(MASStatusUpdateRequest.to_json())

# convert the object into a dict
mas_status_update_request_dict = mas_status_update_request_instance.to_dict()
# create an instance of MASStatusUpdateRequest from a dict
mas_status_update_request_from_dict = MASStatusUpdateRequest.from_dict(mas_status_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


