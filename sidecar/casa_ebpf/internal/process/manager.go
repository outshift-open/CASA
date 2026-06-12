package process

type Manager interface {
	// ListPIDs returns a slice of process ID list which are running now.
	ListPIDs() ([]PID, error)

	// Attach creates a wrapper around an existing process.
	Attach(pid PID) (Process, error)
}
