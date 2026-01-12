# App

Input model for creating an app.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional]
**type** | **str** |  |
**name** | **str** |  |
**base_url** | **str** |  |
**authorization_server_id** | **UUID** |  |
**client_credentials_id** | **UUID** |  |

## Example

```python
from identity_auth_sdk.models.app import App

# TODO update the JSON string below
json = "{}"
# create an instance of App from a JSON string
app_instance = App.from_json(json)
# print the JSON string representation of the object
print(App.to_json())

# convert the object into a dict
app_dict = app_instance.to_dict()
# create an instance of App from a dict
app_from_dict = App.from_dict(app_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
