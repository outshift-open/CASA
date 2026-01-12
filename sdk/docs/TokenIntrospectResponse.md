# TokenIntrospectResponse

Pydantic model for the token introspection response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** |  | [optional] 
**scope** | **str** |  | [optional] 
**sub** | **str** |  | [optional] 
**act** | [**ActorClaim**](ActorClaim.md) |  | [optional] 
**other** | **Dict[str, object]** |  | [optional] 
**exp** | **int** |  | [optional] 
**user_input_id** | **str** |  | [optional] 
**app_id** | **str** |  | [optional] 
**tools** | **List[str]** |  | [optional] 
**active** | **bool** |  | 

## Example

```python
from identity_auth_sdk.models.token_introspect_response import TokenIntrospectResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TokenIntrospectResponse from a JSON string
token_introspect_response_instance = TokenIntrospectResponse.from_json(json)
# print the JSON string representation of the object
print(TokenIntrospectResponse.to_json())

# convert the object into a dict
token_introspect_response_dict = token_introspect_response_instance.to_dict()
# create an instance of TokenIntrospectResponse from a dict
token_introspect_response_from_dict = TokenIntrospectResponse.from_dict(token_introspect_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


