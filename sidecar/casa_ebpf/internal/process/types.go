package process

type PID uint32

// ProcessExeMap contains the process memory-mappings with execute perm
type ProcessExeMap struct {
	// The start address of current mapping.
	StartAddr uintptr

	// The end address of the current mapping
	EndAddr uintptr

	// The file or psuedofile (or empty==anonymous)
	Path string
}
