# AppSpecBaseUrl

Base URL split into host and scheme, matching the CRD schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host** | **str** | Host (and optional port) of the URL, e.g. my-app:8080 | 
**scheme** | **str** | URL scheme: http or https | 

## Example

```python
from identity_auth_sdk.models.app_spec_base_url import AppSpecBaseUrl

# TODO update the JSON string below
json = "{}"
# create an instance of AppSpecBaseUrl from a JSON string
app_spec_base_url_instance = AppSpecBaseUrl.from_json(json)
# print the JSON string representation of the object
print(AppSpecBaseUrl.to_json())

# convert the object into a dict
app_spec_base_url_dict = app_spec_base_url_instance.to_dict()
# create an instance of AppSpecBaseUrl from a dict
app_spec_base_url_from_dict = AppSpecBaseUrl.from_dict(app_spec_base_url_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


