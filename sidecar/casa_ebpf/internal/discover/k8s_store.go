package discover

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"strings"
	"sync"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/cache"
)

type ObjectMeta struct {
	Name        string
	Namespace   string
	Labels      map[string]string
	Annotations map[string]string
}

type PodInfo struct {
	ObjectMeta   *ObjectMeta
	ContainerIDs []string
}

type KubeStore interface {
	Subscribe(ctx context.Context) (<-chan WatchEvent[*PodInfo], error)
	PodByContainer(containerID string) (*PodInfo, bool)
}

type kubeStore struct {
	mut             sync.RWMutex
	factory         informers.SharedInformerFactory
	podInformer     cache.SharedIndexInformer
	outputCh        chan WatchEvent[*PodInfo]
	podsByContainer map[string]*PodInfo
}

func NewKubeStore() (KubeStore, error) {
	config, err := loadKubeConfig()
	if err != nil {
		return nil, fmt.Errorf("unable to load Kubernetes config: %w", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("unable to create Kubernetes clientset: %w", err)
	}

	factory := informers.NewSharedInformerFactoryWithOptions(clientset, 0, informers.WithNamespace(""))
	podInformer := factory.Core().V1().Pods().Informer()

	return &kubeStore{
		factory:         factory,
		podInformer:     podInformer,
		outputCh:        make(chan WatchEvent[*PodInfo], 100),
		podsByContainer: map[string]*PodInfo{},
	}, nil
}

func (s *kubeStore) Subscribe(ctx context.Context) (<-chan WatchEvent[*PodInfo], error) {
	_, err := s.podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj any) {
			pod, ok := obj.(*corev1.Pod)
			if !ok {
				return
			}

			s.addObjectMeta(pod)

			s.outputCh <- WatchEvent[*PodInfo]{
				Type: EventCreated,
				Obj:  s.newPodInfo(pod),
			}
		},
		UpdateFunc: func(oldObj, newObj any) {
			pod, ok := newObj.(*corev1.Pod)
			if !ok {
				return
			}

			s.updateObjectMeta(pod)

			s.outputCh <- WatchEvent[*PodInfo]{
				Type: EventCreated,
				Obj:  s.newPodInfo(pod),
			}
		},
		DeleteFunc: func(obj any) {
			pod, ok := obj.(*corev1.Pod)
			if !ok {
				return
			}

			s.deleteObjectMeta(pod)

			s.outputCh <- WatchEvent[*PodInfo]{
				Type: EventDeleted,
				Obj:  s.newPodInfo(pod),
			}
		},
	})
	if err != nil {
		return s.outputCh, fmt.Errorf("failed to subscribe to pod informer events: %w", err)
	}

	s.factory.Start(ctx.Done())

	// Wait for the initial cache sync, this will give us the PODs already in K8S.
	if !cache.WaitForCacheSync(ctx.Done(), s.podInformer.HasSynced) {
		return s.outputCh, errors.New("timed out waiting for caches to sync")
	}

	slog.Info("Informer has synced. Watching for Pod events...")

	return s.outputCh, nil
}

func (s *kubeStore) PodByContainer(containerID string) (*PodInfo, bool) {
	pod, ok := s.podsByContainer[containerID]
	return pod, ok
}

func (s *kubeStore) addObjectMeta(pod *corev1.Pod) {
	s.mut.Lock()
	defer s.mut.Unlock()

	s.unlockedAddObjectMeta(pod)
}

func (s *kubeStore) updateObjectMeta(pod *corev1.Pod) {
	s.mut.Lock()
	defer s.mut.Unlock()

	s.unlockedDeleteObjectMeta(pod)
	s.unlockedAddObjectMeta(pod)
}

func (s *kubeStore) unlockedAddObjectMeta(pod *corev1.Pod) {
	for _, container := range pod.Status.ContainerStatuses {
		s.podsByContainer[container.ContainerID] = s.newPodInfo(pod)
	}
}

func (s *kubeStore) deleteObjectMeta(pod *corev1.Pod) {
	s.mut.Lock()
	defer s.mut.Unlock()

	s.unlockedDeleteObjectMeta(pod)
}

func (s *kubeStore) unlockedDeleteObjectMeta(pod *corev1.Pod) {
	for _, container := range pod.Status.ContainerStatuses {
		delete(s.podsByContainer, container.ContainerID)
	}
}

func (s *kubeStore) newPodInfo(pod *corev1.Pod) *PodInfo {
	return &PodInfo{
		ObjectMeta: &ObjectMeta{
			Name:        pod.ObjectMeta.Name,
			Namespace:   pod.ObjectMeta.Namespace,
			Labels:      pod.ObjectMeta.Labels,
			Annotations: pod.ObjectMeta.Annotations,
		},
		ContainerIDs: s.getContainerIDs(pod),
	}
}

func (s *kubeStore) getContainerIDs(pod *corev1.Pod) []string {
	ids := []string{}

	for _, ctn := range pod.Status.ContainerStatuses {
		containerID := rmContainerIDSchema(ctn.ContainerID)
		ids = append(ids, containerID)
	}

	return ids
}

// rmContainerIDSchema extracts the hex ID of a container ID that is provided in the form:
// containerd://40c03570b6f4c30bc8d69923d37ee698f5cfcced92c7b7df1c47f6f7887378a9
func rmContainerIDSchema(containerID string) string {
	if parts := strings.SplitN(containerID, "://", 2); len(parts) > 1 {
		return parts[1]
	}
	return containerID
}
