package container

import "github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"

func FindNamespace(_ int32) (uint32, error) {
	// convenience method to allow unit tests compiling in Darwin
	return 0, nil
}

func FindNamespacedPids(pid process.PID) ([]process.PID, error) {
	return nil, nil
}
