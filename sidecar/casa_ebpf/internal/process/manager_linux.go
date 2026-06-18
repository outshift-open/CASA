package process

import (
	"fmt"

	goprocess "github.com/shirou/gopsutil/v4/process"
)

type linuxProcessManager struct{}

func NewManager() Manager {
	return &linuxProcessManager{}
}

func (p *linuxProcessManager) ListPIDs() ([]PID, error) {
	pids, err := goprocess.Pids()
	if err != nil {
		return nil, fmt.Errorf("unable to get pids: %w", err)
	}

	results := []PID{}
	for _, pid := range pids {
		results = append(results, PID(pid))
	}

	return results, nil
}

func (p *linuxProcessManager) Attach(pid PID) (Process, error) {
	proc, err := goprocess.NewProcess(int32(pid))
	if err != nil {
		return nil, fmt.Errorf("failed to attach to process: %w", err)
	}

	return &linuxProcess{pid: pid, process: proc}, nil
}
