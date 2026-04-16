# UserInput

User Input model containing the user input prompt.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | [optional] 
**prompt** | **str** |  | 
**created_at** | **datetime** |  | [optional] 
**app_id** | **UUID** |  | 
**tag** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.user_input import UserInput

# TODO update the JSON string below
json = "{}"
# create an instance of UserInput from a JSON string
user_input_instance = UserInput.from_json(json)
# print the JSON string representation of the object
print(UserInput.to_json())

# convert the object into a dict
user_input_dict = user_input_instance.to_dict()
# create an instance of UserInput from a dict
user_input_from_dict = UserInput.from_dict(user_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


