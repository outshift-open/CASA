# MASListResponse

Response model for listing MultiAgentSystems.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** |  | [optional] [default to 'zta.io/v1alpha1']
**kind** | **str** |  | [optional] [default to 'MultiAgentSystemList']
**items** | [**List[MultiAgentSystemCRD]**](MultiAgentSystemCRD.md) |  | 

## Example

```python
from identity_auth_sdk.models.mas_list_response import MASListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MASListResponse from a JSON string
mas_list_response_instance = MASListResponse.from_json(json)
# print the JSON string representation of the object
print(MASListResponse.to_json())

# convert the object into a dict
mas_list_response_dict = mas_list_response_instance.to_dict()
# create an instance of MASListResponse from a dict
mas_list_response_from_dict = MASListResponse.from_dict(mas_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


