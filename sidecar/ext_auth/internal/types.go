// Copyright 2026 Google LLC
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
	"time"
)

type CRDMetadata struct {
	UID               string
	Name              string
	Namespace         string
	CreationTimestamp time.Time
}

type MultiAgentSystemCRD struct {
	Metadata          *CRDMetadata
	Name              string
	Apps              []*AppCRD
	EnabledToolChecks []string
}

type HttpRequestSchemaCRD struct {
	PromptJsonPath string `json:"promptJsonPath,omitempty"`
}

type AppCRD struct {
	BaseURL           string                `json:"baseUrl,omitempty"`
	Name              string                `json:"name,omitempty"`
	Type              string                `json:"type,omitempty"`
	HttpRequestSchema *HttpRequestSchemaCRD `json:"httpRequestSchema,omitempty"`
}

func NewAppFromMap(m map[string]any) (*AppCRD, error) {
	bytes, err := json.Marshal(m)
	if err != nil {
		return nil, fmt.Errorf("unable to marshal App map to JSON: %w", err)
	}

	var app AppCRD

	err = json.Unmarshal(bytes, &app)
	if err != nil {
		return nil, fmt.Errorf("unable to unmarshal App JSON: %w", err)
	}

	return &app, nil
}

type AppClientCredential struct {
	ClientID     string
	ClientSecret string
}
