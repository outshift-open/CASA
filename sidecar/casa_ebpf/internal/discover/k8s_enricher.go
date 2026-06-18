package discover

import (
	"context"
	"fmt"
	"log/slog"
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/container"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
)

type k8sProcessEnricher struct {
	mut              sync.RWMutex
	k8sClient        K8SClient
	k8sStore         KubeStore
	procsByContainer map[string][]ProcessAttrs
	containersByPID  map[process.PID]*container.Info
}

func RunK8SProcessEnricher(ctx context.Context, inCh <-chan []*WatchEvent[ProcessAttrs], wg *sync.WaitGroup) <-chan []*WatchEvent[ProcessAttrs] {
	outputCh := make(chan []*WatchEvent[ProcessAttrs], 10)

	store, err := NewKubeStore()
	if err != nil {
		slog.Error("Failed to create Kubernetes store, forwarding input channel", "err", err)
		return inCh
	}

	enricher := k8sProcessEnricher{
		k8sClient:        NewK8SClient(),
		k8sStore:         store,
		procsByContainer: map[string][]ProcessAttrs{},
		containersByPID:  map[process.PID]*container.Info{},
	}

	wg.Add(1)
	go enricher.Run(ctx, inCh, outputCh, wg)

	return outputCh
}

func (pe *k8sProcessEnricher) Run(
	ctx context.Context,
	inCh <-chan []*WatchEvent[ProcessAttrs],
	outCh chan<- []*WatchEvent[ProcessAttrs],
	wg *sync.WaitGroup,
) {
	podEvents, err := pe.k8sStore.Subscribe(ctx)
	if err != nil {
		slog.Error("Unable to subscribe to pod informer events", "err", err)
	}

	for {
		select {
		case <-ctx.Done():
			slog.Debug("Context canceled.")
			wg.Done()
			return
		case inEvents := <-inCh:
			if !pe.k8sClient.IsK8SEnabled(ctx) {
				// If Kubernetes is not running we skip this enricher
				outCh <- inEvents
				continue
			}

			for _, event := range inEvents {
				switch event.Type {
				case EventCreated:
					event.Obj = pe.handleCreatedProcess(event.Obj)
				case EventDeleted:
					pe.handleDeletedProcess(event.Obj)
				}
			}

			outCh <- inEvents
		case podEvent := <-podEvents:
			switch podEvent.Type {
			case EventCreated:
				slog.Info("Pod Added")
				outEvents := pe.handleCreatedPod(podEvent.Obj)
				if len(outEvents) > 0 {
					outCh <- outEvents
				}
			case EventDeleted:
				slog.Info("Pod Deleted")
				pe.handleDeletedPod(podEvent.Obj)
			}
		}
	}
}

func (pe *k8sProcessEnricher) handleCreatedProcess(proc ProcessAttrs) ProcessAttrs {
	pe.mut.Lock()
	defer pe.mut.Unlock()

	containerInfo, err := pe.getContainerInfo(proc.ID)
	if err != nil {
		slog.Debug("Unable to get process container info", "pid", proc.ID, "err", err)
		return proc
	}

	if containerInfo != nil {
		containerID := containerInfo.ContainerID

		pe.procsByContainer[containerID] = append(pe.procsByContainer[containerID], proc)

		if pod, ok := pe.k8sStore.PodByContainer(containerID); ok {
			proc.KubernetesInfo = &KubernetesInfo{
				PodName:        pod.ObjectMeta.Name,
				Namespace:      pod.ObjectMeta.Namespace,
				PodAnnotations: pod.ObjectMeta.Annotations,
				PodLabels:      pod.ObjectMeta.Labels,
			}
		}
	}

	return proc
}

func (pe *k8sProcessEnricher) handleDeletedProcess(proc ProcessAttrs) {
	pe.mut.Lock()
	defer pe.mut.Unlock()

	containerInfo, err := pe.getContainerInfo(proc.ID)
	if err != nil {
		slog.Debug("Unable to get process container info", "pid", proc.ID, "err", err)
	}

	if containerInfo != nil {
		delete(pe.procsByContainer, containerInfo.ContainerID)
	}

	delete(pe.containersByPID, proc.ID)
}

func (pe *k8sProcessEnricher) handleCreatedPod(pod *PodInfo) []*WatchEvent[ProcessAttrs] {
	pe.mut.Lock()
	defer pe.mut.Unlock()

	events := []*WatchEvent[ProcessAttrs]{}

	for _, containerID := range pod.ContainerIDs {
		if procs, ok := pe.procsByContainer[containerID]; ok {
			for _, proc := range procs {
				proc.KubernetesInfo = &KubernetesInfo{
					PodName:        pod.ObjectMeta.Name,
					Namespace:      pod.ObjectMeta.Namespace,
					PodAnnotations: pod.ObjectMeta.Annotations,
					PodLabels:      pod.ObjectMeta.Labels,
				}

				events = append(events, &WatchEvent[ProcessAttrs]{
					Type: EventCreated,
					Obj:  proc,
				})
			}
		}
	}

	return events
}

func (pe *k8sProcessEnricher) handleDeletedPod(pod *PodInfo) {
	pe.mut.Lock()
	defer pe.mut.Unlock()

	for _, containerID := range pod.ContainerIDs {
		delete(pe.procsByContainer, containerID)
	}
}

func (pe *k8sProcessEnricher) getContainerInfo(pid process.PID) (*container.Info, error) {
	if existingInfo, ok := pe.containersByPID[pid]; ok {
		return existingInfo, nil
	}

	info, err := container.InfoForPID(int32(pid))
	if err != nil {
		return nil, fmt.Errorf("unable to get container info from PID: %w", err)
	}

	pe.containersByPID[pid] = &info

	return &info, nil
}
