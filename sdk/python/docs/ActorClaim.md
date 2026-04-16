# ActorClaim

Pydantic model for the JWT 'act' (actor) claim.  Represents an actor in a delegation chain. Can be nested to represent a chain of delegation where the outermost act claim represents the current actor and nested act claims represent prior actors.  As per RFC 8693, for access control decisions, only the top-level claims and the current actor (outermost act claim) should be considered.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sub** | **str** |  | 
**act** | [**ActorClaim**](ActorClaim.md) |  | [optional] 

## Example

```python
from identity_auth_sdk.models.actor_claim import ActorClaim

# TODO update the JSON string below
json = "{}"
# create an instance of ActorClaim from a JSON string
actor_claim_instance = ActorClaim.from_json(json)
# print the JSON string representation of the object
print(ActorClaim.to_json())

# convert the object into a dict
actor_claim_dict = actor_claim_instance.to_dict()
# create an instance of ActorClaim from a dict
actor_claim_from_dict = ActorClaim.from_dict(actor_claim_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


