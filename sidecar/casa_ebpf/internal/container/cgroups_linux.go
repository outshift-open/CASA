package container

import (
	"syscall"

	"golang.org/x/sys/unix"
)

func IsCgroupV2Enabled() (bool, error) {
	cgroupPath := "/sys/fs/cgroup"

	var st syscall.Statfs_t

	err := syscall.Statfs(cgroupPath, &st)
	if err != nil {
		return false, err
	}

	isEnabled := st.Type == unix.CGROUP2_SUPER_MAGIC
	return isEnabled, nil
}
