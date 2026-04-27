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

package main

import (
	identitysdk "github.com/cisco-eti/identity-auth-server/sdk/go"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
)

type BaseURL struct {
	Host   string `json:"host"`
	Scheme string `json:"scheme"`
}

type HttpRequestSchema struct {
	PromptFieldJsonPath string `json:"promptFieldJsonPath"`
}

type AppSpec struct {
	Name                   string             `json:"name"`
	Type                   string             `json:"type"`
	BaseURL                BaseURL            `json:"baseUrl"`
	KubernetesWorkloadName string             `json:"kubernetesWorkloadName"`
	HttpRequestSchema      *HttpRequestSchema `json:"httpRequestSchema,omitempty"`
}

type MASSpec struct {
	Name              string    `json:"name"`
	EnabledToolChecks []string  `json:"enabledToolChecks,omitempty"`
	Apps              []AppSpec `json:"apps,omitempty"`
	LLMHost           string    `json:"llm_host,omitempty"`
}

type MASStatus struct {
	Phase        string                       `json:"phase,omitempty"`
	AppsReady    int                          `json:"appsReady,omitempty"`
	LastSyncTime string                       `json:"lastSyncTime,omitempty"`
	Message      string                       `json:"message,omitempty"`
	Credentials  []identitysdk.AppCredentials `json:"credentials,omitempty"`
}

type MultiAgentSystem struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              MASSpec   `json:"spec,omitempty"`
	Status            MASStatus `json:"status,omitempty"`
}

type MultiAgentSystemList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []MultiAgentSystem `json:"items"`
}

func (m *MultiAgentSystem) DeepCopyObject() runtime.Object {
	out := &MultiAgentSystem{}
	*out = *m
	out.Spec.Apps = append([]AppSpec{}, m.Spec.Apps...)
	out.Spec.EnabledToolChecks = append([]string{}, m.Spec.EnabledToolChecks...)
	return out
}

func (m *MultiAgentSystemList) DeepCopyObject() runtime.Object {
	out := &MultiAgentSystemList{}
	*out = *m
	out.Items = append([]MultiAgentSystem{}, m.Items...)
	return out
}
