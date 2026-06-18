package main

import (
	"context"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"path"
	"sync"
	"syscall"

	"github.com/cilium/ebpf/rlimit"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/config"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/discover"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"

	ebpfcommon "github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/llm"
)

func main() {
	// Remove resource limits for kernels <5.11.
	err := rlimit.RemoveMemlock()
	if err != nil {
		slog.Error("Error removing memlock", "err", err)
		os.Exit(-1)
	}

	configPath := flag.String("config", "", "path to the configuration file")
	flag.Parse()

	if cfg := os.Getenv("CASA_EBPF_CONFIG_PATH"); cfg != "" {
		configPath = &cfg
	}

	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		slog.Error("Failed to load config", "err", err)
		os.Exit(-1)
	}

	slog.Info("Configuration loaded", "path", *configPath)

	cancelChan := make(chan bool, 1)
	wg := sync.WaitGroup{}
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)
	defer stop()

	pidsRegistry := ebpfcommon.NewNamespacePIDsRegistry()

	pinPath, err := makeBPFFSPath("/sys/fs/bpf/")
	if err != nil {
		slog.Error("Failed to create bpffs path", "err", err)
		os.Exit(-1)
	}

	reqHandler := llm.NewRequestHandler(cancelChan)
	respHandler := llm.NewResponseHandler(cancelChan)

	module := tls.NewLibSSLModule(pidsRegistry, reqHandler.Chan(), respHandler.Chan())

	processMgr := process.NewManager()

	attacher := ebpf.NewAttacher([]ebpf.Module{module}, processMgr)

	err = attacher.LoadModules(&pinPath)
	if err != nil {
		slog.Error("Failed to load all eBPF modules", "err", err)
		os.Exit(1)
	}

	scanner := discover.NewScanner(cfg)
	processEventsCh := scanner.Scan(ctx, &wg, processMgr)

	wg.Go(func() {
		err := module.Run(ctx)
		if err != nil {
			slog.Error("Failed to run eBPF program", "err", err)
		}
	})
	wg.Go(reqHandler.Start)
	wg.Go(respHandler.Start)

	wg.Go(func() {
		for {
			select {
			case <-ctx.Done():
				slog.Debug("Context canceled.")
				return
			case processEvents := <-processEventsCh:
				for _, event := range processEvents {
					switch event.Type {
					case discover.EventCreated:
						err := attacher.AttachToProcess(event.Obj.PID, event.Obj.Ns)
						if err != nil {
							slog.Error("Failed to attach eBPF module", "pid", event.Obj.PID, "err", err)
							continue
						}

					case discover.EventDeleted:
						slog.Info("Process deleted")
						attacher.DetachFromProcess(event.Obj.PID, event.Obj.Ns)
					}
				}
			}
		}
	})

	defer func() {
		_ = attacher.DetachAll()
	}()

	slog.Info("running, press Ctrl+C to stop")

	<-ctx.Done()

	wg.Wait()

	slog.Info("shutting down")
}

func makeBPFFSPath(bpfFsPath string) (string, error) {
	pinPath := path.Join(bpfFsPath, "casa")

	if err := os.MkdirAll(pinPath, 0o1700); err != nil {
		return "", fmt.Errorf("creating bpffs casa path: %w", err)
	}

	return pinPath, nil
}
