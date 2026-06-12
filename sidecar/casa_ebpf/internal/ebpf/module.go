package ebpf

import (
	"context"
	"io"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type Module interface {
	Load(pinPath *string) error
	Run(ctx context.Context) error

	// AllowPID notifies the module to accept events from the process with the
	// provided PID. The module should discard events from processes whose PID
	// has not been allowed before.
	AllowPID(pid process.PID, ns uint32)

	// BlockPID notifies the module to stop accepting events from the process
	// with the provided PID.
	BlockPID(pid process.PID, ns uint32)
}

type UProbesModule interface {
	Module
	UProbes() common.LibUProbeDescs
}

type LibRef struct {
	ino     uint64
	count   int
	closers []io.Closer
}

func NewLibRef(ino uint64) *LibRef {
	return &LibRef{
		ino:     ino,
		count:   1,
		closers: []io.Closer{},
	}
}

func (r *LibRef) AddRef() {
	r.count++
}

func (r *LibRef) RemoveRef() {
	r.count--
}

func (r *LibRef) IsReferenced() bool {
	return r.count > 0
}

func (r *LibRef) Closers() []io.Closer {
	return r.closers
}

func (r *LibRef) Ino() uint64 {
	return r.Ino()
}

func (r *LibRef) AddClosers(closers []io.Closer) {
	r.closers = append(r.closers, closers...)
}
