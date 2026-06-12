package discover

import (
	"context"
	"sync"
	"time"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type ContainerInfo struct {
	ID             string
	Name           string
	ComposeService string
}

type ProcessAttrs struct {
	ID            process.PID
	StartedTime   time.Time
	ContainerInfo *ContainerInfo
}

type ProcessInfo struct {
	PID     process.PID
	PPID    process.PID
	ExePath string
	Ino     uint64
	Ns      uint32
}

type WatchEventType int

const (
	EventCreated = WatchEventType(iota)
	EventDeleted
)

type WatchEvent[T any] struct {
	Type WatchEventType
	Obj  T
}

type ProcessEnricher interface {
	Run(
		ctx context.Context,
		inCh <-chan []*WatchEvent[ProcessAttrs],
		outCh chan<- []*WatchEvent[ProcessAttrs],
		wg *sync.WaitGroup,
	)
}
