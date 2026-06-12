package discover

import (
	"context"
	"fmt"
	"log/slog"
	"strings"
	"sync"

	"github.com/moby/moby/client"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/container"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

const (
	containerShortIDLength = 12
	composeServiceLabelKey = "com.docker.compose.service"
)

type DockerClient interface {
	IsRunning(ctx context.Context) bool
	ContainerInfo(ctx context.Context, pid process.PID) (*ContainerInfo, error)
}

type MobyDockerClient struct {
	client *client.Client
	mux    *sync.Mutex
}

func NewMobyDockerClient() DockerClient {
	return &MobyDockerClient{
		mux: &sync.Mutex{},
	}
}

func (m *MobyDockerClient) IsRunning(ctx context.Context) bool {
	m.mux.Lock()
	defer m.mux.Unlock()

	if m.client != nil {
		_, err := m.client.Ping(ctx, client.PingOptions{})
		if err != nil {
			slog.Debug("Error pinging Docker server", "err", err)
			return false
		}

		return true
	}

	if err := m.init(ctx); err != nil {
		slog.Debug("Docker not running", "err", err)
		return false
	}

	return true
}

func (m *MobyDockerClient) init(ctx context.Context) error {
	apiClient, err := client.New(client.FromEnv)
	if err != nil {
		return fmt.Errorf("failed to create Docker API client: %w", err)
	}

	result, err := apiClient.Info(ctx, client.InfoOptions{})
	if err != nil {
		return fmt.Errorf("failed to get docker info: %w", err)
	}

	slog.Info("Docker info",
		"driver", result.Info.Driver,
		"version", result.Info.ServerVersion,
		"cgroupDriver", result.Info.CgroupDriver,
		"cgroupVersion", result.Info.CgroupVersion)

	m.client = apiClient
	return nil
}

func (m *MobyDockerClient) ContainerInfo(ctx context.Context, pid process.PID) (*ContainerInfo, error) {
	info, err := container.InfoForPID(int32(pid))
	if err != nil {
		return nil, fmt.Errorf("unable to get container info from PID: %w", err)
	}

	inspectResult, err := m.client.ContainerInspect(ctx, info.ContainerID, client.ContainerInspectOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to inspect the container %s: %w", info.ContainerID, err)
	}

	inspectInfo := inspectResult.Container

	containerID := inspectInfo.ID
	if len(containerID) > containerShortIDLength {
		containerID = containerID[:containerShortIDLength]
	}

	composeSvcName := ""
	if inspectInfo.Config != nil && len(inspectInfo.Config.Labels) > 0 {
		composeSvcName = inspectInfo.Config.Labels[composeServiceLabelKey]
	}

	return &ContainerInfo{
		// some containers start with '/'. Removing it
		Name:           strings.Trim(inspectInfo.Name, "/"),
		ID:             containerID,
		ComposeService: composeSvcName,
	}, nil
}
