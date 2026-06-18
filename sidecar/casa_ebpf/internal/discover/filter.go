package discover

import (
	"context"
	"fmt"
	"log/slog"
	"path"
	"slices"
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/config"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/container"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type processFilter struct {
	inCh             <-chan []*WatchEvent[ProcessAttrs]
	outCh            chan<- []*WatchEvent[ProcessInfo]
	wg               *sync.WaitGroup
	matchedProcesses map[process.PID]ProcessInfo
	processMgr       process.Manager
	config           *config.Config
}

func RunProcessFilter(
	ctx context.Context,
	inCh <-chan []*WatchEvent[ProcessAttrs],
	wg *sync.WaitGroup,
	processMgr process.Manager,
	config *config.Config,
) <-chan []*WatchEvent[ProcessInfo] {
	outputCh := make(chan []*WatchEvent[ProcessInfo], 10)
	filter := processFilter{
		inCh:             inCh,
		outCh:            outputCh,
		wg:               wg,
		matchedProcesses: map[process.PID]ProcessInfo{},
		processMgr:       processMgr,
		config:           config,
	}

	wg.Add(1)
	go filter.Run(ctx)

	return outputCh
}

func (pf *processFilter) Run(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			slog.Debug("Context canceled.")
			pf.wg.Done()
			return
		case inEvents := <-pf.inCh:
			matches := []*WatchEvent[ProcessInfo]{}

			for _, event := range inEvents {
				switch event.Type {
				case EventCreated:
					procInfo, err := pf.newProcessInfo(&event.Obj)
					if err != nil {
						slog.Debug("Could not create process info", "pid", event.Obj.ID, "err", err)
						continue
					}

					if pf.filterProcess(&event.Obj) {
						pf.matchedProcesses[procInfo.PID] = *procInfo
						matches = append(matches, &WatchEvent[ProcessInfo]{
							Type: EventCreated,
							Obj:  *procInfo,
						})
					} else {
						// maybe the parent was a match
						if pi, ok := pf.matchedProcesses[procInfo.PPID]; ok {
							matches = append(matches, &WatchEvent[ProcessInfo]{
								Type: EventCreated,
								Obj:  pi,
							})
						}
					}
				case EventDeleted:
					if _, ok := pf.matchedProcesses[event.Obj.ID]; !ok {
						continue
					}

					matches = append(matches, &WatchEvent[ProcessInfo]{
						Type: EventDeleted,
						Obj:  pf.matchedProcesses[event.Obj.ID],
					})

					delete(pf.matchedProcesses, event.Obj.ID)
				}
			}

			if len(matches) > 0 {
				pf.outCh <- matches
			}
		}
	}
}

func (pf *processFilter) filterProcess(attrs *ProcessAttrs) bool {
	for _, criteria := range pf.config.Discovery.Criteria {
		if slices.Contains(criteria.TargetPIDs, uint32(attrs.ID)) {
			slog.Info("Process matched with PID", "pid", attrs.ID)
			return true
		}

		if attrs.ContainerInfo != nil &&
			(attrs.ContainerInfo.ID == criteria.ContainerID || pf.matchString(criteria.ContainerName, attrs.ContainerInfo.Name)) {
			slog.Info("Process matched with container info", "pid", attrs.ID)
			return true
		}

		if attrs.KubernetesInfo != nil &&
			(attrs.KubernetesInfo.Namespace == criteria.K8SNamespace || pf.matchString(criteria.K8SPodName, attrs.KubernetesInfo.PodName)) {
			slog.Info("Process matched with Kubernetes info", "pid", attrs.ID)
			return true
		}
	}

	return false
}

func (pf *processFilter) matchString(pattern string, value string) bool {
	ok, err := path.Match(pattern, value)
	if err != nil {
		return false
	}

	return ok
}

func (pf *processFilter) newProcessInfo(attrs *ProcessAttrs) (*ProcessInfo, error) {
	proc, err := pf.processMgr.Attach(attrs.ID)
	if err != nil {
		return nil, fmt.Errorf("unable to attach to process: %w", err)
	}

	ppid, _ := proc.Ppid() // we don't care about the err

	exePath, err := proc.Exe()
	if err != nil {
		return nil, fmt.Errorf("unable to get process exe path: %w", err)
	}

	ino, err := proc.FindINode()
	if err != nil {
		return nil, fmt.Errorf("unable to get process ino: %w", err)
	}

	ns, err := container.FindNamespace(int32(attrs.ID))
	if err != nil {
		return nil, fmt.Errorf("unable to find ns for pid %d: %w", attrs.ID, err)
	}

	return &ProcessInfo{
		PID:     attrs.ID,
		PPID:    process.PID(ppid),
		ExePath: exePath,
		Ino:     ino,
		Ns:      ns,
	}, nil
}
