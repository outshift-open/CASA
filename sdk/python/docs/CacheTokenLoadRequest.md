# CacheTokenLoadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**trace_id** | **str** |  | 
**app_host** | **str** |  | 
**app_type** | [**AppType**](AppType.md) |  | 

## Example

```python
from identity_auth_sdk.models.cache_token_load_request import CacheTokenLoadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CacheTokenLoadRequest from a JSON string
cache_token_load_request_instance = CacheTokenLoadRequest.from_json(json)
# print the JSON string representation of the object
print(CacheTokenLoadRequest.to_json())

# convert the object into a dict
cache_token_load_request_dict = cache_token_load_request_instance.to_dict()
# create an instance of CacheTokenLoadRequest from a dict
cache_token_load_request_from_dict = CacheTokenLoadRequest.from_dict(cache_token_load_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


