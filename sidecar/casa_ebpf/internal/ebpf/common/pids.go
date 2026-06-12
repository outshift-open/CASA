package common

import (
	"log/slog"
	"slices"
	"sync"

	"github.com/cilium/ebpf"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/container"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

// Updating these requires updating the constants below in pid.h
// #define MAX_CONCURRENT_PIDS 3001 // estimate: 1000 concurrent processes (including children) * 3 namespaces per pid
// #define PRIME_HASH 192053 // closest prime to 3001 * 64
const (
	maxConcurrentPids = 3001
	primeHash         = 192053
)

type PIDsRegistry interface {
	AllowPID(pid process.PID, ns uint32)
	BlockPID(pid process.PID, ns uint32)
	CurrentPIDs() map[uint32][]process.PID
}

type NamespacePIDsRegistry struct {
	currentPIDs map[uint32][]process.PID
	mux         *sync.RWMutex
}

func NewNamespacePIDsRegistry() *NamespacePIDsRegistry {
	return &NamespacePIDsRegistry{
		currentPIDs: map[uint32][]process.PID{},
		mux:         &sync.RWMutex{},
	}
}

func (pf *NamespacePIDsRegistry) AllowPID(pid process.PID, ns uint32) {
	pf.mux.Lock()
	defer pf.mux.Unlock()
	pf.addPID(pid, ns)
}

func (pf *NamespacePIDsRegistry) BlockPID(pid process.PID, ns uint32) {
	pf.mux.Lock()
	defer pf.mux.Unlock()
	pf.removePID(pid, ns)
}

func (pf *NamespacePIDsRegistry) CurrentPIDs() map[uint32][]process.PID {
	pf.mux.Lock()
	defer pf.mux.Unlock()

	results := map[uint32][]process.PID{}
	for ns, pids := range pf.currentPIDs {
		results[ns] = append(results[ns], pids...)
	}

	return results
}

func (pf *NamespacePIDsRegistry) addPID(pid process.PID, ns uint32) {
	pids, err := container.FindNamespacedPids(pid)
	if err != nil {
		slog.Debug("Error looking for PIDs in namespace", "pid", pid, "err", err)
		return
	}

	pf.currentPIDs[ns] = append(pf.currentPIDs[ns], pids...)
}

func (pf *NamespacePIDsRegistry) removePID(pid process.PID, ns uint32) {
	pids, ok := pf.currentPIDs[ns]
	if !ok {
		return
	}

	pf.currentPIDs[ns] = slices.DeleteFunc(pids, func(curr process.PID) bool {
		return curr == pid
	})

	if len(pf.currentPIDs[ns]) == 0 {
		delete(pf.currentPIDs, ns)
	}
}

func pidSegmentBit(k uint64) (uint32, uint32) {
	h := uint32(k % primeHash)
	segment := h / 64
	bit := h & 63

	return segment, bit
}

func buildPIDSegments(pidsRegistry PIDsRegistry) []uint64 {
	result := make([]uint64, maxConcurrentPids)
	for nsid, pids := range pidsRegistry.CurrentPIDs() {
		for _, pid := range pids {
			// skip any pids that might've been added, but are not tracked by the kprobes
			slog.Debug("Reallowing pid", "pid", pid, "namespace", nsid)

			k := (uint64(nsid) << 32) | uint64(pid)

			segment, bit := pidSegmentBit(k)

			v := result[segment]
			v |= (1 << bit)
			result[segment] = v
		}
	}

	return result
}

func RebuildAllowedPIDs(pidsRegistry PIDsRegistry, allowedPIDsMap *ebpf.Map) {
	if allowedPIDsMap != nil {
		segs := buildPIDSegments(pidsRegistry)

		slog.Debug("number of segments in pid registry", "len", len(segs))

		for i, seg := range segs {
			err := allowedPIDsMap.Put(uint32(i), seg)
			if err != nil {
				slog.Error("Error setting up pid in BPF space, sizes of Go and BPF maps don't match", "error", err, "i", i)
			}
		}
	}
}
