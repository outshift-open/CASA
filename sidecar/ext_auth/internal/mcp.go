// Copyright 2026 Cisco Systems, Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
