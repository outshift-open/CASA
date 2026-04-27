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
	"context"
	"fmt"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
)

type KubernetesService interface {
	GetAppCredentials(ctx context.Context, appID string) (*AppClientCredential, error)
}

type kubernetesService struct {
	dynClient *dynamic.DynamicClient
	clientset *kubernetes.Clientset
	namespace string
}

func NewKubernetesService(dynClient *dynamic.DynamicClient, clientset *kubernetes.Clientset, namespace string) KubernetesService {
	return &kubernetesService{
		dynClient: dynClient,
		clientset: clientset,
		namespace: namespace,
	}
}

func (s *kubernetesService) GetAppCredentials(ctx context.Context, appID string) (*AppClientCredential, error) {
	secretName := fmt.Sprintf("%s-oauth2-credentials", appID)
	secret, err := s.clientset.CoreV1().Secrets(s.namespace).Get(ctx, secretName, metav1.GetOptions{})
	if err != nil {
		return nil, fmt.Errorf("unable to fetch client credentials from k8s secret %s: %w", secretName, err)
	}

	var clientCred AppClientCredential

	if clientID, ok := secret.Data["client_id"]; ok {
		clientCred.ClientID = string(clientID)
	}

	if clientSecret, ok := secret.Data["client_secret"]; ok {
		clientCred.ClientSecret = string(clientSecret)
	}

	if clientCred.ClientID == "" || clientCred.ClientSecret == "" {
		return nil, nil
	}

	return &clientCred, nil
}
