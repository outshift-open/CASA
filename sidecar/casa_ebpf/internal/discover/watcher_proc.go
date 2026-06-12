package discover

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

const (
	defaultPollInterval  = 5 * time.Second
	defaultMinProcessAge = 5 * time.Second
)

type processWatcher struct {
	procs        map[process.PID]ProcessAttrs
	pollInterval time.Duration
	outputCh     chan<- []*WatchEvent[ProcessAttrs]
	wg           *sync.WaitGroup
	processMgr   process.Manager
}

func RunProcessWatcher(ctx context.Context, wg *sync.WaitGroup, processMgr process.Manager) <-chan []*WatchEvent[ProcessAttrs] {
	outputCh := make(chan []*WatchEvent[ProcessAttrs], 10)
	watcher := processWatcher{
		procs:        map[process.PID]ProcessAttrs{},
		pollInterval: defaultPollInterval,
		outputCh:     outputCh,
		wg:           wg,
		processMgr:   processMgr,
	}

	wg.Add(1)
	go watcher.run(ctx)

	return outputCh
}

func (pw *processWatcher) run(ctx context.Context) {
	for {
		procs, err := pw.enumerateProcesses()
		if err != nil {
			slog.Error("Error getting the list of processes", "err", err)
		} else {
			events := []*WatchEvent[ProcessAttrs]{}
			readyProcs := map[process.PID]ProcessAttrs{}

			// take only processes who are old enough to be used
			for pid, proc := range procs {
				if pw.isProcessOldEnough(&proc) {
					readyProcs[pid] = proc
				}
			}

			// add events for created procs
			for pid, proc := range readyProcs {
				if _, ok := pw.procs[pid]; !ok {
					events = append(events, &WatchEvent[ProcessAttrs]{Type: EventCreated, Obj: proc})
					slog.Debug("Process added", "pid", pid)
				}
			}

			// add events for removed procs
			for pid, proc := range pw.procs {
				if _, ok := readyProcs[pid]; !ok {
					events = append(events, &WatchEvent[ProcessAttrs]{Type: EventDeleted, Obj: proc})
					slog.Debug("Process removed", "pid", pid)
				}
			}

			if len(events) > 0 {
				pw.outputCh <- events
			}

			pw.procs = readyProcs
		}

		select {
		case <-ctx.Done():
			slog.Debug("Context canceled.")
			pw.wg.Done()
			return
		case <-time.After(pw.pollInterval):
			// enumerate again
		}
	}
}

func (pw *processWatcher) isProcessOldEnough(proc *ProcessAttrs) bool {
	processAge := time.Since(proc.StartedTime)
	return processAge >= defaultMinProcessAge
}

func (pw *processWatcher) enumerateProcesses() (map[process.PID]ProcessAttrs, error) {
	pids, err := pw.processMgr.ListPIDs()
	if err != nil {
		return nil, fmt.Errorf("unable to get pids: %w", err)
	}

	procs := make(map[process.PID]ProcessAttrs, len(pids))

	for _, pid := range pids {
		proc, err := pw.processMgr.Attach(pid)
		if err != nil {
			return nil, fmt.Errorf("failed to attach to process: %w", err)
		}

		createTime, err := proc.CreateTime()
		if err != nil {
			return nil, fmt.Errorf("failed to fetch create time for process: %w", err)
		}

		procs[pid] = ProcessAttrs{ID: pid, StartedTime: time.UnixMilli(createTime)}
	}

	return procs, nil
}
