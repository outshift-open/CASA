# MetricsSnapshot

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TotalMas** | **int32** |  | 
**TokenRequests** | **int32** |  | 
**McpCallsAllowed** | **int32** |  | 
**McpCallsDenied** | **int32** |  | 
**TotalMcpCalls** | **int32** |  | 
**DeterministicBlocks** | **int32** |  | 
**AiPoweredBlocks** | **int32** |  | 
**BlockReasons** | [**[]BlockReasonStat**](BlockReasonStat.md) |  | 

## Methods

### NewMetricsSnapshot

`func NewMetricsSnapshot(totalMas int32, tokenRequests int32, mcpCallsAllowed int32, mcpCallsDenied int32, totalMcpCalls int32, deterministicBlocks int32, aiPoweredBlocks int32, blockReasons []BlockReasonStat, ) *MetricsSnapshot`

NewMetricsSnapshot instantiates a new MetricsSnapshot object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMetricsSnapshotWithDefaults

`func NewMetricsSnapshotWithDefaults() *MetricsSnapshot`

NewMetricsSnapshotWithDefaults instantiates a new MetricsSnapshot object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTotalMas

`func (o *MetricsSnapshot) GetTotalMas() int32`

GetTotalMas returns the TotalMas field if non-nil, zero value otherwise.

### GetTotalMasOk

`func (o *MetricsSnapshot) GetTotalMasOk() (*int32, bool)`

GetTotalMasOk returns a tuple with the TotalMas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalMas

`func (o *MetricsSnapshot) SetTotalMas(v int32)`

SetTotalMas sets TotalMas field to given value.


### GetTokenRequests

`func (o *MetricsSnapshot) GetTokenRequests() int32`

GetTokenRequests returns the TokenRequests field if non-nil, zero value otherwise.

### GetTokenRequestsOk

`func (o *MetricsSnapshot) GetTokenRequestsOk() (*int32, bool)`

GetTokenRequestsOk returns a tuple with the TokenRequests field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTokenRequests

`func (o *MetricsSnapshot) SetTokenRequests(v int32)`

SetTokenRequests sets TokenRequests field to given value.


### GetMcpCallsAllowed

`func (o *MetricsSnapshot) GetMcpCallsAllowed() int32`

GetMcpCallsAllowed returns the McpCallsAllowed field if non-nil, zero value otherwise.

### GetMcpCallsAllowedOk

`func (o *MetricsSnapshot) GetMcpCallsAllowedOk() (*int32, bool)`

GetMcpCallsAllowedOk returns a tuple with the McpCallsAllowed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMcpCallsAllowed

`func (o *MetricsSnapshot) SetMcpCallsAllowed(v int32)`

SetMcpCallsAllowed sets McpCallsAllowed field to given value.


### GetMcpCallsDenied

`func (o *MetricsSnapshot) GetMcpCallsDenied() int32`

GetMcpCallsDenied returns the McpCallsDenied field if non-nil, zero value otherwise.

### GetMcpCallsDeniedOk

`func (o *MetricsSnapshot) GetMcpCallsDeniedOk() (*int32, bool)`

GetMcpCallsDeniedOk returns a tuple with the McpCallsDenied field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMcpCallsDenied

`func (o *MetricsSnapshot) SetMcpCallsDenied(v int32)`

SetMcpCallsDenied sets McpCallsDenied field to given value.


### GetTotalMcpCalls

`func (o *MetricsSnapshot) GetTotalMcpCalls() int32`

GetTotalMcpCalls returns the TotalMcpCalls field if non-nil, zero value otherwise.

### GetTotalMcpCallsOk

`func (o *MetricsSnapshot) GetTotalMcpCallsOk() (*int32, bool)`

GetTotalMcpCallsOk returns a tuple with the TotalMcpCalls field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalMcpCalls

`func (o *MetricsSnapshot) SetTotalMcpCalls(v int32)`

SetTotalMcpCalls sets TotalMcpCalls field to given value.


### GetDeterministicBlocks

`func (o *MetricsSnapshot) GetDeterministicBlocks() int32`

GetDeterministicBlocks returns the DeterministicBlocks field if non-nil, zero value otherwise.

### GetDeterministicBlocksOk

`func (o *MetricsSnapshot) GetDeterministicBlocksOk() (*int32, bool)`

GetDeterministicBlocksOk returns a tuple with the DeterministicBlocks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDeterministicBlocks

`func (o *MetricsSnapshot) SetDeterministicBlocks(v int32)`

SetDeterministicBlocks sets DeterministicBlocks field to given value.


### GetAiPoweredBlocks

`func (o *MetricsSnapshot) GetAiPoweredBlocks() int32`

GetAiPoweredBlocks returns the AiPoweredBlocks field if non-nil, zero value otherwise.

### GetAiPoweredBlocksOk

`func (o *MetricsSnapshot) GetAiPoweredBlocksOk() (*int32, bool)`

GetAiPoweredBlocksOk returns a tuple with the AiPoweredBlocks field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiPoweredBlocks

`func (o *MetricsSnapshot) SetAiPoweredBlocks(v int32)`

SetAiPoweredBlocks sets AiPoweredBlocks field to given value.


### GetBlockReasons

`func (o *MetricsSnapshot) GetBlockReasons() []BlockReasonStat`

GetBlockReasons returns the BlockReasons field if non-nil, zero value otherwise.

### GetBlockReasonsOk

`func (o *MetricsSnapshot) GetBlockReasonsOk() (*[]BlockReasonStat, bool)`

GetBlockReasonsOk returns a tuple with the BlockReasons field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBlockReasons

`func (o *MetricsSnapshot) SetBlockReasons(v []BlockReasonStat)`

SetBlockReasons sets BlockReasons field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


