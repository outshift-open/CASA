package ebpf

import (
	"fmt"
	"io"

	"github.com/cilium/ebpf/link"
)

// TODO: to change
const (
	libPath = "/proc/37173/root/proc/5218/root/usr/lib/aarch64-linux-gnu/libssl.so.3"
	// libPath = "/proc/67843/root/proc/9615/root/usr/lib/aarch64-linux-gnu/libssl.so.3"
)

type Attacher interface {
	Attach(modules []Module) ([]io.Closer, error)
}

type attacher struct{}

func NewAttacher() Attacher {
	return &attacher{}
}

func (a *attacher) Attach(modules []Module) ([]io.Closer, error) {
	closers := []io.Closer{}

	for _, module := range modules {
		ex, err := link.OpenExecutable(libPath)
		if err != nil {
			return closers, fmt.Errorf("failed to open executable: %w", err)
		}

		if um, ok := module.(UProbesModule); ok {
			for symbol, uprobe := range um.UProbes() {
				if uprobe.Entry != nil {
					up, err := ex.Uprobe(symbol, uprobe.Entry, nil)
					if err != nil {
						return closers, fmt.Errorf("failed to create uprobe: %w", err)
					}

					closers = append(closers, up)
				}

				if uprobe.Return != nil {
					up, err := ex.Uretprobe(symbol, uprobe.Return, nil)
					if err != nil {
						return closers, fmt.Errorf("failed to create upretrobe: %w", err)
					}

					closers = append(closers, up)
				}
			}
		}
	}

	return closers, nil
}
