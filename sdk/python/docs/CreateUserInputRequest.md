# CreateUserInputRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **str** |  | 
**app_id** | **str** |  | 
**tag** | **str** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.create_user_input_request import CreateUserInputRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUserInputRequest from a JSON string
create_user_input_request_instance = CreateUserInputRequest.from_json(json)
# print the JSON string representation of the object
print(CreateUserInputRequest.to_json())

# convert the object into a dict
create_user_input_request_dict = create_user_input_request_instance.to_dict()
# create an instance of CreateUserInputRequest from a dict
create_user_input_request_from_dict = CreateUserInputRequest.from_dict(create_user_input_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


