package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
)

const (
	inboundExtAuthHost  string = ":4100"
	outboundExtAuthHost string = ":5100"
)

func main() {
	ctx := context.Background()
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	inboundExtAuthServer, err := NewExtAuthServer(inboundExtAuthHost, &InboundExtAuthService{})
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
