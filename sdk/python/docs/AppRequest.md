# AppRequest

Request model for app creation and updates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**AppType**](AppType.md) |  | 
**name** | **str** |  | 
**base_url** | **str** |  | 
**mas_id** | **str** |  | 
**tools** | [**List[ToolRequest]**](ToolRequest.md) |  | [optional] [default to []]

## Example

```python
from identity_auth_sdk.models.app_request import AppRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AppRequest from a JSON string
app_request_instance = AppRequest.from_json(json)
# print the JSON string representation of the object
print(AppRequest.to_json())

# convert the object into a dict
app_request_dict = app_request_instance.to_dict()
# create an instance of AppRequest from a dict
app_request_from_dict = AppRequest.from_dict(app_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


