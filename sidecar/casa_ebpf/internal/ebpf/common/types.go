package common

import "github.com/cilium/ebpf"

type ProbeDesc struct {
	Entry  *ebpf.Program
	Return *ebpf.Program
}
