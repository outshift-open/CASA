package process

type Process interface {
	// Ppid returns Process ID of the process.
	PID() PID

	// Ppid returns Parent Process ID of the process.
	Ppid() (PID, error)

	// CreateTime returns created time of the process in milliseconds since the epoch, in UTC.
	CreateTime() (int64, error)

	// Exe returns executable path of the process.
	Exe() (string, error)

	// AbsoluteExe returns the absolute executable path of the process (i.e: /proc/(pid)/exe).
	AbsoluteExe() string

	// Maps get memory maps of the process with "execute" perm (e.g: on Linux from /proc/(pid)/maps)
	ExeMaps() ([]*ProcessExeMap, error)

	// FindINode finds the INode of the process
	FindINode() (uint64, error)
}
