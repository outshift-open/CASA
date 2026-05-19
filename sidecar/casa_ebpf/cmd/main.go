package main

import (
	"context"
	"log"
	"log/slog"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/cilium/ebpf/rlimit"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/llm"
)

func main() {
	// Remove resource limits for kernels <5.11.
	err := rlimit.RemoveMemlock()
	if err != nil {
		log.Fatal("Removing memlock:", err)
	}

	attacher := ebpf.NewAttacher()

	cancelChan := make(chan bool, 1)
	wg := sync.WaitGroup{}

	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)
	defer stop()

	respHandler := llm.NewResponseHandler(cancelChan, &wg)

	module := tls.NewLibSSLModule(respHandler.Chan())

	err = module.Load()
	if err != nil {
		slog.Error("Failed to load eBPF program", "err", err)
		os.Exit(1)
	}

	closers, err := attacher.Attach([]ebpf.Module{module})
	if err != nil {
		slog.Error("Failed to attach eBPF module", "err", err)
		os.Exit(1)
	}
	defer func() {
		for _, closer := range closers {
			closer.Close()
		}
	}()

	go func() {
		err := module.Run(ctx)
		if err != nil {
			slog.Error("Failed to run eBPF program", "err", err)
		}
	}()
	go respHandler.Start()

	slog.Info("running, press Ctrl+C to stop")

	<-ctx.Done()

	wg.Wait()

	slog.Info("shutting down")
}
