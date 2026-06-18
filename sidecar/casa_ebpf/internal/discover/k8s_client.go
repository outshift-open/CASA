package discover

import (
	"context"
	"fmt"
	"log/slog"

	"k8s.io/client-go/rest"
)

type K8SClient interface {
	IsK8SEnabled(ctx context.Context) bool
}

type k8sClient struct{}

func NewK8SClient() K8SClient {
	return &k8sClient{}
}

func (c *k8sClient) IsK8SEnabled(ctx context.Context) bool {
	// TODO: lock
	// We autodetect that we are in a kubernetes if we can properly load a K8s configuration file
	_, err := loadKubeConfig()
	if err != nil {
		slog.Debug("kubeconfig can't be detected. Assuming we are not in Kubernetes", "error", err)
		return false
	}

	return true
}

func loadKubeConfig() (*rest.Config, error) {
	// use in-cluster config for now
	config, err := rest.InClusterConfig()
	if err != nil {
		return nil, fmt.Errorf("can't access kubernetes using InClusterConfig: %w", err)
	}

	return config, nil
}
