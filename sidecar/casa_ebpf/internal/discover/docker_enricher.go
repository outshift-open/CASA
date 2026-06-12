package discover

import (
	"context"
	"log/slog"
	"sync"
)

type dockerProcessEnricher struct {
	dockerClient DockerClient
}

func RunDockerProcessEnricher(ctx context.Context, inCh <-chan []*WatchEvent[ProcessAttrs], wg *sync.WaitGroup) <-chan []*WatchEvent[ProcessAttrs] {
	outputCh := make(chan []*WatchEvent[ProcessAttrs], 10)
	enricher := dockerProcessEnricher{
		dockerClient: NewMobyDockerClient(),
	}

	wg.Add(1)
	go enricher.Run(ctx, inCh, outputCh, wg)

	return outputCh
}

func (pe *dockerProcessEnricher) Run(
	ctx context.Context,
	inCh <-chan []*WatchEvent[ProcessAttrs],
	outCh chan<- []*WatchEvent[ProcessAttrs],
	wg *sync.WaitGroup,
) {
	for {
		select {
		case <-ctx.Done():
			slog.Debug("Context canceled.")
			wg.Done()
			return
		case inEvents := <-inCh:
			if !pe.dockerClient.IsRunning(ctx) {
				// If no docker is running we skip this enricher
				outCh <- inEvents
				continue
			}

			for _, event := range inEvents {
				switch event.Type {
				case EventCreated:
					info, err := pe.dockerClient.ContainerInfo(ctx, event.Obj.ID)
					if err != nil {
						slog.Debug("PID is not a Docker container", "pid", event.Obj.ID, "err", err)
						continue
					}

					event.Obj.ContainerInfo = info
				case EventDeleted:
					continue
				}
			}

			outCh <- inEvents
		}
	}
}
