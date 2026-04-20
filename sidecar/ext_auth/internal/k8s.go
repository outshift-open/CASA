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
