package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"

	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/rest"
)

const (
	inboundExtAuthHost  string = ":4100"
	outboundExtAuthHost string = ":5100"
)

func main() {
	ctx := context.Background()
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	k8sDynClient, err := createKubernetesDyncClient()
	if err != nil {
		logger.Error("Failed to create Kubernetes dynamic client", "err", err)
		os.Exit(-1)
	}

	inboundExtAuthServer, err := NewExtAuthServer(
		inboundExtAuthHost,
		NewInboundExtAuthService(k8sDynClient, "zta-sidecar"),
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

	outboundExtAuthServer, err := NewExtAuthServer(outboundExtAuthHost, &OutboundExtAuthService{})
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

func createKubernetesDyncClient() (*dynamic.DynamicClient, error) {
	config, err := rest.InClusterConfig()
	if err != nil {
		return nil, fmt.Errorf("error create K8S InCluster config: %w", err)
	}

	// clientset, err := kubernetes.NewForConfig(config)
	// if err != nil {
	// 	slog.Error("Error create K8S client", "err", err)
	// 	return nil, err
	// }

	// _, err = clientset.CoreV1().Pods("zta-sidecar").List(context.Background(), metav1.ListOptions{})
	// if err != nil {
	// 	slog.Error("Error getting PODs", "err", err)
	// 	return nil, err
	// }

	// slog.Info("Fetched PODs", "pods", pods)

	dynClient, err := dynamic.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("error create K8S dynamic client: %w", err)
	}

	return dynClient, nil
}
