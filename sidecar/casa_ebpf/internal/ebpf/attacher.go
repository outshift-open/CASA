package ebpf

import (
	"errors"
	"fmt"
	"io"
	"log/slog"
	"os"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/cilium/ebpf/link"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/container"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type Attacher interface {
	LoadModules(pinPath *string) error
	AttachToProcess(pid process.PID, ns uint32) error
	DetachFromProcess(pid process.PID, ns uint32) error
	DetachAll() error
}

type attacher struct {
	modules     []Module
	processMgr  process.Manager
	libRefs     map[uint64]*LibRef
	libsPerProc map[process.PID][]uint64
	closers     []io.Closer
}

func NewAttacher(modules []Module, processMgr process.Manager) Attacher {
	return &attacher{
		modules:     modules,
		processMgr:  processMgr,
		libRefs:     map[uint64]*LibRef{},
		libsPerProc: map[process.PID][]uint64{},
		closers:     []io.Closer{},
	}
}

func (a *attacher) LoadModules(pinPath *string) error {
	errCount := 0
	for _, module := range a.modules {
		err := module.Load(pinPath)
		if err != nil {
			slog.Warn("Unable to load module", "err", err)
			errCount++
			continue
		}

		if kp, ok := module.(KProbesModule); ok {
			err := a.attachKProbes(kp)
			if err != nil {
				return fmt.Errorf("unable to attach kprobe module: %w", err)
			}
		}

		if som, ok := module.(SockOpsModule); ok {
			err := a.attachSockOps(som)
			if err != nil {
				slog.Warn("unable to attach sock ops module", "err", err)
				continue
			}
		}
	}

	if len(a.modules) == errCount {
		return errors.New("failed to attach all ebpf modules")
	}

	return nil
}

func (a *attacher) attachKProbes(module KProbesModule) error {
	for symbol, kprobe := range module.KProbes() {
		if kprobe.Entry != nil {
			kp, err := link.Kprobe(symbol, kprobe.Entry, nil)
			if err != nil {
				return fmt.Errorf("failed to attach kprobe %s: %w", symbol, err)
			}

			a.addCloser(kp)
		}

		if kprobe.Return != nil {
			kp, err := link.Kretprobe(symbol, kprobe.Return, nil)
			if err != nil {
				return fmt.Errorf("failed to attach kretprobe %s: %w", symbol, err)
			}

			a.addCloser(kp)
		}
	}

	return nil
}

func (a *attacher) attachSockOps(module SockOpsModule) error {
	cgroupPath, err := findCgroupPath()
	if err != nil {
		return fmt.Errorf("unable to get cgroup path: %w", err)
	}

	for _, sockOp := range module.SockOps() {
		slog.Info("Attaching sock ops", "path", cgroupPath)

		l, err := link.AttachCgroup(link.CgroupOptions{
			Path:    cgroupPath,
			Program: sockOp.Program,
			Attach:  sockOp.AttachAs,
		})
		if err != nil {
			slog.Warn("Unable to attach sock ops", "err", err)
			continue
		}

		a.addCloser(l)
	}

	return nil
}

func (a *attacher) addCloser(closer io.Closer) {
	a.closers = append(a.closers, closer)
}

func findCgroupPath() (string, error) {
	cgroupPath := "/sys/fs/cgroup"

	isCgroupV2Enabled, err := container.IsCgroupV2Enabled()
	if err != nil {
		return "", err
	}

	if !isCgroupV2Enabled {
		cgroupPath = filepath.Join(cgroupPath, "unified")
	}

	return cgroupPath, nil
}

type libUProbes struct {
	libPath string
	uprobes []map[string]*common.ProbeDesc // multiple probes can be attached to one function
}

func (a *attacher) getUProbesForProcess(pid process.PID, ns uint32, maps []*process.ProcessExeMap, exeIno uint64, exePath string) map[uint64]*libUProbes {
	modules := map[uint64]*libUProbes{}

	for _, module := range a.modules {
		module.AllowPID(pid, ns)
		if um, ok := module.(UProbesModule); ok {
			for libName, uprobes := range um.UProbes() {
				binIno := exeIno
				binPath := exePath

				libMap, ok := a.matchUProbeLibMap(libName, maps)
				if ok {
					// This is a robust way to find the lib/exe binary, especially in Docker where libMap.Path is relative.
					libPath := fmt.Sprintf("/proc/%d/map_files/%x-%x", pid, libMap.StartAddr, libMap.EndAddr)

					libStat, err := os.Stat(libPath)
					if err == nil {
						stat, ok := libStat.Sys().(*syscall.Stat_t)
						if ok {
							binIno = stat.Ino
							binPath = libPath
						}
					}
				}

				if binIno == exeIno {
					slog.Debug(fmt.Sprintf("%s not linked, trying to find the symbols in the executable", libName))
				}

				mod, ok := modules[binIno]
				if ok {
					mod.uprobes = append(mod.uprobes, uprobes)
				} else {
					modules[binIno] = &libUProbes{libPath: binPath, uprobes: []map[string]*common.ProbeDesc{uprobes}}
				}
			}
		}
	}

	return modules
}

func (a *attacher) AttachToProcess(pid process.PID, ns uint32) error {
	proc, err := a.processMgr.Attach(pid)
	if err != nil {
		return fmt.Errorf("unable to attach to process: %w", err)
	}

	maps, err := proc.ExeMaps()
	if err != nil {
		return fmt.Errorf("failed to get process maps: %w", err)
	}

	exeIno, err := proc.FindINode()
	if err != nil {
		return fmt.Errorf("failed to get exe INode: %w", err)
	}

	exePath := proc.AbsoluteExe()

	procUprobes := a.getUProbesForProcess(pid, ns, maps, exeIno, exePath)

	for libIno, lib := range procUprobes {
		if ref, ok := a.libRefs[libIno]; ok {
			slog.Debug("shared module library already linked", "lib", lib.libPath, "ino", libIno)
			ref.AddRef()
			continue
		}

		ref := NewLibRef(libIno)

		exe, err := link.OpenExecutable(lib.libPath)
		if err != nil {
			return fmt.Errorf("failed to open executable: %w", err)
		}

		for _, uprobes := range lib.uprobes {
			ref.AddClosers(a.attachUprobes(exe, uprobes))
		}

		a.libRefs[libIno] = ref
		a.libsPerProc[pid] = append(a.libsPerProc[pid], libIno)
	}

	return nil
}

func (a *attacher) attachUprobes(exe *link.Executable, uprobes map[string]*common.ProbeDesc) []io.Closer {
	closers := []io.Closer{}

	for symbol, uprobe := range uprobes {
		cc, err := a.attachUprobe(exe, symbol, uprobe)
		if err != nil {
			for _, closer := range cc {
				closer.Close()
			}

			slog.Debug("Error attaching uprobe", "func", symbol, "err", err)
		} else {
			closers = append(closers, cc...)
		}
	}

	return closers
}

func (a *attacher) attachUprobe(exe *link.Executable, symbol string, uprobe *common.ProbeDesc) ([]io.Closer, error) {
	closers := []io.Closer{}

	if uprobe.Entry != nil {
		up, err := exe.Uprobe(symbol, uprobe.Entry, nil)
		if err != nil {
			return closers, fmt.Errorf("failed to create uprobe: %w", err)
		}

		closers = append(closers, up)
	}

	if uprobe.Return != nil {
		up, err := exe.Uretprobe(symbol, uprobe.Return, nil)
		if err != nil {
			return closers, fmt.Errorf("failed to create upretrobe: %w", err)
		}

		closers = append(closers, up)
	}

	return closers, nil
}

func (a *attacher) DetachFromProcess(pid process.PID, ns uint32) error {
	libInos, ok := a.libsPerProc[pid]
	if ok {
		for _, ino := range libInos {
			libRef, libOk := a.libRefs[ino]
			if !libOk {
				continue
			}

			libRef.RemoveRef()

			// If no other processes are using the same library then close all its uprobe links
			if !libRef.IsReferenced() {
				for _, closer := range libRef.Closers() {
					closer.Close()
				}
			}
		}

		delete(a.libsPerProc, pid)
	}

	for _, module := range a.modules {
		module.BlockPID(pid, ns)
	}

	return nil
}

func (a *attacher) DetachAll() error {
	for ino, ref := range a.libRefs {
		slog.Debug("Closing the links to library uprobes", "ino", ino)
		for _, closer := range ref.Closers() {
			_ = closer.Close()
		}
	}

	a.libRefs = map[uint64]*LibRef{}
	a.libsPerProc = map[process.PID][]uint64{}

	for _, closer := range a.closers {
		_ = closer.Close()
	}

	return nil
}

func (a *attacher) matchUProbeLibMap(name string, maps []*process.ProcessExeMap) (*process.ProcessExeMap, bool) {
	for _, m := range maps {
		if strings.Contains(m.Path, string(filepath.Separator)+name) {
			return m, true
		}
	}

	return nil, false
}
