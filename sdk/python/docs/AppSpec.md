# AppSpec

Application specification within a MultiAgentSystem.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the application | 
**type** | [**AppType**](AppType.md) | Type of the application | 
**base_url** | **str** | Base URL of the application | 

## Example

```python
from identity_auth_sdk.models.app_spec import AppSpec

# TODO update the JSON string below
json = "{}"
# create an instance of AppSpec from a JSON string
app_spec_instance = AppSpec.from_json(json)
# print the JSON string representation of the object
print(AppSpec.to_json())

# convert the object into a dict
app_spec_dict = app_spec_instance.to_dict()
# create an instance of AppSpec from a dict
app_spec_from_dict = AppSpec.from_dict(app_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


