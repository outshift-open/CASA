# AppCredentials

OAuth2 credentials for an application.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_name** | **str** | Name of the application | 
**app_id** | **str** | Application UUID | 
**client_id** | **str** | OAuth2 client ID | 
**client_secret** | **str** | OAuth2 client secret | 
**secret_name** | **str** | Name of the K8s secret to create | 

## Example

```python
from identity_auth_sdk.models.app_credentials import AppCredentials

# TODO update the JSON string below
json = "{}"
# create an instance of AppCredentials from a JSON string
app_credentials_instance = AppCredentials.from_json(json)
# print the JSON string representation of the object
print(AppCredentials.to_json())

# convert the object into a dict
app_credentials_dict = app_credentials_instance.to_dict()
# create an instance of AppCredentials from a dict
app_credentials_from_dict = AppCredentials.from_dict(app_credentials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


