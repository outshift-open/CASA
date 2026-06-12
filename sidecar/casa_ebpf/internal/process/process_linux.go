package process

import (
	"fmt"
	"os"
	"syscall"

	"github.com/prometheus/procfs"
	goprocess "github.com/shirou/gopsutil/v4/process"
)

type linuxProcess struct {
	pid     PID
	process *goprocess.Process
}

// Ppid returns Process ID of the process.
func (p *linuxProcess) PID() PID {
	return p.pid
}

// Ppid returns Parent Process ID of the process.
func (p *linuxProcess) Ppid() (PID, error) {
	ppid, err := p.process.Ppid()
	if err != nil {
		return 0, err
	}

	return PID(ppid), nil
}

// CreateTime returns created time of the process in milliseconds since the epoch, in UTC.
func (p *linuxProcess) CreateTime() (int64, error) {
	return p.process.CreateTime()
}

// Exe returns executable path of the process.
func (p *linuxProcess) Exe() (string, error) {
	return p.process.Exe()
}

func (p *linuxProcess) ExeMaps() ([]*ProcessExeMap, error) {
	proc, err := procfs.NewProc(int(p.pid))
	if err != nil {
		return nil, fmt.Errorf("unable to attach to process: %w", err)
	}

	maps, err := proc.ProcMaps()
	if err != nil {
		return nil, fmt.Errorf("unable to get process memory maps: %w", err)
	}

	exeMaps := []*ProcessExeMap{}

	for _, m := range maps {
		if m.Perms.Execute {
			exeMaps = append(exeMaps, &ProcessExeMap{
				StartAddr: m.StartAddr,
				EndAddr:   m.EndAddr,
				Path:      m.Pathname,
			})
		}
	}

	return exeMaps, nil
}

func (p *linuxProcess) FindINode() (uint64, error) {
	exePath := fmt.Sprintf("/proc/%d/exe", p.pid)

	info, err := os.Stat(exePath)
	if err != nil {
		return 0, fmt.Errorf("failed to get FileInfo for executable: %w", err)
	}

	stat, ok := info.Sys().(*syscall.Stat_t)
	if !ok {
		return 0, fmt.Errorf("failed to get Stat_t for executable: %w", err)
	}

	return stat.Ino, nil
}
