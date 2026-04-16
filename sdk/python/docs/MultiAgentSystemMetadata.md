# MultiAgentSystemMetadata

Metadata for MultiAgentSystem CRD.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Resource name | 
**namespace** | **str** | Kubernetes namespace | 
**uid** | **str** |  | [optional] 
**resource_version** | **str** |  | [optional] 
**generation** | **int** |  | [optional] 
**labels** | **Dict[str, object]** |  | [optional] 
**annotations** | **Dict[str, object]** |  | [optional] 

## Example

```python
from identity_auth_sdk.models.multi_agent_system_metadata import MultiAgentSystemMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of MultiAgentSystemMetadata from a JSON string
multi_agent_system_metadata_instance = MultiAgentSystemMetadata.from_json(json)
# print the JSON string representation of the object
print(MultiAgentSystemMetadata.to_json())

# convert the object into a dict
multi_agent_system_metadata_dict = multi_agent_system_metadata_instance.to_dict()
# create an instance of MultiAgentSystemMetadata from a dict
multi_agent_system_metadata_from_dict = MultiAgentSystemMetadata.from_dict(multi_agent_system_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


