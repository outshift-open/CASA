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

package main

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
)

type PolicyTargetRef struct {
	Kind string `json:"kind"`
	Name string `json:"name"`
}

type PolicyAllowedEndpoint struct {
	Name      string `json:"name"`
	Namespace string `json:"namespace"`
	Port      int    `json:"port"`
}

type PolicyLlmEndpoint struct {
	Fqdn string `json:"fqdn"`
	Port int    `json:"port"`
}

type CASAPolicySpec struct {
	TargetRef        PolicyTargetRef         `json:"targetRef"`
	AllowedProtocols []string                `json:"allowedProtocols,omitempty"`
	AllowedEndpoints []PolicyAllowedEndpoint `json:"allowedEndpoints,omitempty"`
	LlmEndpoint      *PolicyLlmEndpoint      `json:"llmEndpoint,omitempty"`
}

type CASAPolicyStatus struct {
	Phase        string `json:"phase,omitempty"`
	LastSyncTime string `json:"lastSyncTime,omitempty"`
	Message      string `json:"message,omitempty"`
}

type CASAPolicy struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              CASAPolicySpec   `json:"spec,omitempty"`
	Status            CASAPolicyStatus `json:"status,omitempty"`
}

type CASAPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []CASAPolicy `json:"items"`
}

func (p *CASAPolicy) DeepCopyObject() runtime.Object {
	out := &CASAPolicy{}
	*out = *p
	out.Spec.AllowedProtocols = append([]string{}, p.Spec.AllowedProtocols...)
	out.Spec.AllowedEndpoints = append([]PolicyAllowedEndpoint{}, p.Spec.AllowedEndpoints...)
	if p.Spec.LlmEndpoint != nil {
		ep := *p.Spec.LlmEndpoint
		out.Spec.LlmEndpoint = &ep
	}
	return out
}

func (p *CASAPolicyList) DeepCopyObject() runtime.Object {
	out := &CASAPolicyList{}
	*out = *p
	out.Items = append([]CASAPolicy{}, p.Items...)
	return out
}
