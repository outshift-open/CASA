package ebpf

import (
	"fmt"
	"io"
	"log/slog"
	"os"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/cilium/ebpf/link"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type Attacher interface {
	AttachToProcess(pid process.PID, ns uint32) error
	DetachFromProcess(pid process.PID, ns uint32) error
	DetachAll() error
}

type attacher struct {
	modules     []Module
	processMgr  process.Manager
	libRefs     map[uint64]*LibRef
	libsPerProc map[process.PID][]uint64
}

func NewAttacher(modules []Module, processMgr process.Manager) Attacher {
	return &attacher{
		modules:     modules,
		processMgr:  processMgr,
		libRefs:     map[uint64]*LibRef{},
		libsPerProc: map[process.PID][]uint64{},
	}
}

type libUProbes struct {
	libPath string
	uprobes map[string]*common.ProbeDesc
}

func (a *attacher) getUProbesForProcess(pid process.PID, ns uint32, maps []*process.ProcessExeMap, exeIno uint64) map[uint64]*libUProbes {
	modules := map[uint64]*libUProbes{}

	for _, module := range a.modules {
		module.AllowPID(pid, ns)
		if um, ok := module.(UProbesModule); ok {
			for libName, uprobes := range um.UProbes() {
				libMap, ok := a.matchUProbeLibMap(libName, maps)
				if !ok {
					slog.Debug(fmt.Sprintf("Ignoring library %s", libName))
					continue
				}

				libIno := exeIno

				// This is a robust way to find the lib/exe binary, especially in Docker where libMap.Path is relative.
				libPath := fmt.Sprintf("/proc/%d/map_files/%x-%x", pid, libMap.StartAddr, libMap.EndAddr)

				libStat, err := os.Stat(libPath)
				if err == nil {
					stat, ok := libStat.Sys().(*syscall.Stat_t)
					if ok {
						libIno = stat.Ino
					}
				}

				modules[libIno] = &libUProbes{libPath: libPath, uprobes: uprobes}
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

	procUprobes := a.getUProbesForProcess(pid, ns, maps, exeIno)

	for libIno, lib := range procUprobes {
		if ref, ok := a.libRefs[libIno]; ok {
			slog.Debug("shared module library already linked", "lib", lib.libPath, "ino", libIno)
			ref.AddRef()
			continue
		}

		ref := NewLibRef(libIno)

		ex, err := link.OpenExecutable(lib.libPath)
		if err != nil {
			return fmt.Errorf("failed to open executable: %w", err)
		}

		for symbol, uprobe := range lib.uprobes {
			closers, err := a.attachUprobe(ex, symbol, uprobe)
			if err != nil {
				for _, closer := range closers {
					closer.Close()
				}

				slog.Debug("Error attaching uprobe", "func", symbol, "err", err)
			} else {
				ref.AddClosers(closers)
			}
		}

		a.libRefs[libIno] = ref
		a.libsPerProc[pid] = append(a.libsPerProc[pid], libIno)
	}

	return nil
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
			closer.Close()
		}
	}

	a.libRefs = map[uint64]*LibRef{}
	a.libsPerProc = map[process.PID][]uint64{}

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
