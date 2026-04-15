# CacheTokenStoreRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**trace_id** | **str** |  | 
**app_host** | **str** |  | 
**app_type** | [**AppType**](AppType.md) |  | 
**access_token** | **str** |  | 

## Example

```python
from identity_auth_sdk.models.cache_token_store_request import CacheTokenStoreRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CacheTokenStoreRequest from a JSON string
cache_token_store_request_instance = CacheTokenStoreRequest.from_json(json)
# print the JSON string representation of the object
print(CacheTokenStoreRequest.to_json())

# convert the object into a dict
cache_token_store_request_dict = cache_token_store_request_instance.to_dict()
# create an instance of CacheTokenStoreRequest from a dict
cache_token_store_request_from_dict = CacheTokenStoreRequest.from_dict(cache_token_store_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


