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
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"time"

	identitysdk "github.com/cisco-eti/identity-auth-server/sdk/go"
	"github.com/cisco-eti/identity-auth-server/sidecar/ext_auth/internal"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

const (
	inboundExtAuthHost  string = ":4100"
	outboundExtAuthHost string = ":5100"
)

func main() {
	ctx := context.Background()
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	k8sDynClient, k8sClientset, err := newKubernetesClients()
	if err != nil {
		logger.Error("Failed to create Kubernetes dynamic client", "err", err)
		os.Exit(-1)
	}

	namespace := os.Getenv("K8S_NAMESPACE")
	if namespace == "" {
		logger.Error("K8S_NAMESPACE is not set", slog.Any("err", err))
		os.Exit(-1)
	}

	k8sService := internal.NewKubernetesService(k8sDynClient, k8sClientset, namespace)
	authSrvClient := internal.NewAuthServerClient(newAuthServerClient())

	inboundExtAuthServer, err := internal.NewExtAuthServer(
		inboundExtAuthHost,
		internal.NewInboundExtAuthService(namespace, authSrvClient, k8sService),
	)
	if err != nil {
		logger.Error("Failed to create the HTTP inbound ext auth server", slog.Any("err", err))
		os.Exit(-1)
	}

	defer func() {
		_ = inboundExtAuthServer.Shutdown(ctx)
	}()

	logger.Info(fmt.Sprintf("Listening on inbound HTTP requests (%s)", inboundExtAuthHost))

	go func() {
		if err := inboundExtAuthServer.Run(ctx); err != nil {
			logger.Error("Failed to run the HTTP inbound ext auth server", slog.Any("err", err))
			os.Exit(-1)
		}
	}()

	outboundExtAuthServer, err := internal.NewExtAuthServer(
		outboundExtAuthHost,
		internal.NewOutboundExtAuthService(namespace, authSrvClient, k8sService),
	)
	if err != nil {
		logger.Error("Failed to create the HTTP outbound ext auth server", slog.Any("err", err))
		os.Exit(-1)
	}

	defer func() {
		_ = outboundExtAuthServer.Shutdown(ctx)
	}()

	logger.Info(fmt.Sprintf("Listening on outbound HTTP requests (%s)", outboundExtAuthHost))

	go func() {
		if err := outboundExtAuthServer.Run(ctx); err != nil {
			logger.Error("Failed to run the HTTP outbound ext auth server", slog.Any("err", err))
			os.Exit(-1)
		}
	}()

	interrupChannel := make(chan os.Signal, 1)
	signal.Notify(interrupChannel, os.Interrupt)
	<-interrupChannel

	logger.Info("Exiting the ext auth service")
}

func newKubernetesClients() (*dynamic.DynamicClient, *kubernetes.Clientset, error) {
	config, err := rest.InClusterConfig()
	if err != nil {
		return nil, nil, fmt.Errorf("unable to create Kubernetes InCluster config: %w", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, nil, fmt.Errorf("unable to create Kubernetes clientset: %w", err)
	}

	dynClient, err := dynamic.NewForConfig(config)
	if err != nil {
		return nil, nil, fmt.Errorf("unable to create Kubernetes dynamic client: %w", err)
	}

	return dynClient, clientset, nil
}

func newAuthServerClient() *identitysdk.APIClient {
	config := identitysdk.NewConfiguration()
	config.Host = os.Getenv("AUTH_SERVER_HOST")
	config.Scheme = os.Getenv("AUTH_SERVER_SCHEME")
	config.Debug = true
	config.HTTPClient = &http.Client{Timeout: 100 * time.Second}

	return identitysdk.NewAPIClient(config)
}
