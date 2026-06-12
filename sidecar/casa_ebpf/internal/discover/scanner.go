package discover

import (
	"context"
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type Scanner struct{}

func (s *Scanner) Scan(ctx context.Context, wg *sync.WaitGroup, processMgr process.Manager) <-chan []*WatchEvent[ProcessInfo] {
	procsCh := RunProcessWatcher(ctx, wg, processMgr)
	dockerProcsCh := RunDockerProcessEnricher(ctx, procsCh, wg)
	return RunProcessFilter(ctx, dockerProcsCh, wg, processMgr)
}
