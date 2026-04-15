package internal

import (
	"encoding/json"
	"fmt"
	"log/slog"

	"github.com/modelcontextprotocol/go-sdk/jsonrpc"
	"github.com/modelcontextprotocol/go-sdk/mcp"
)

const (
	mcpMethodCallTool string = "tools/call"
)

func GetMCPToolFromRequest(reqBody string) (string, error) {
	mcpMsg, err := jsonrpc.DecodeMessage([]byte(reqBody))
	if err != nil {
		slog.Error("Failed to decode MCP message", "err", err)
		return "", fmt.Errorf("unable to decode MCP message: %w", err)
	}

	mcpReq, ok := mcpMsg.(*jsonrpc.Request)
	if !ok {
		return "", nil
	}

	if mcpReq.Method != mcpMethodCallTool {
		return "", nil
	}

	var callToolReq mcp.CallToolParams

	err = json.Unmarshal(mcpReq.Params, &callToolReq)
	if err != nil {
		slog.Error("Failed to unmarshal the MCP call tool request", "err", err)
		return "", fmt.Errorf("unable to unmarshal the MCP call tool request: %w", err)
	}

	return callToolReq.Name, nil
}
