package ebpf

import (
	"context"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
)

type Module interface {
	Load() error
	Run(ctx context.Context) error
}

type UProbesModule interface {
	Module
	UProbes() map[string]*common.ProbeDesc
}
