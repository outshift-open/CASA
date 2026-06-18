package discover

import (
	"context"
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/config"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type Scanner struct {
	config *config.Config
}

func NewScanner(config *config.Config) *Scanner {
	return &Scanner{
		config: config,
	}
}

func (s *Scanner) Scan(ctx context.Context, wg *sync.WaitGroup, processMgr process.Manager) <-chan []*WatchEvent[ProcessInfo] {
	procsCh := RunProcessWatcher(ctx, wg, processMgr)
	dockerProcsCh := RunDockerProcessEnricher(ctx, procsCh, wg)
	k8sProcessCh := RunK8SProcessEnricher(ctx, dockerProcsCh, wg)
	return RunProcessFilter(ctx, k8sProcessCh, wg, processMgr, s.config)
}
