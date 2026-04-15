package internal

import (
	"context"
	"errors"
	"fmt"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
)

const (
	podMASAnnotationKey string = "zta.io/mas"
)

type KubernetesService interface {
	GetMasK8sDefinition(ctx context.Context) (*MultiAgentSystemCRD, error)
	GetMasResourceByName(ctx context.Context, name string) (*MultiAgentSystemCRD, error)
	GetMasCRFromService(ctx context.Context, svcName string) (*MultiAgentSystemCRD, error)
	GetAppCredentials(ctx context.Context, appID string) (*AppClientCredential, error)
}

type kubernetesService struct {
	dynClient *dynamic.DynamicClient
	clientset *kubernetes.Clientset
	namespace string
}

func NewKubernetesService(dynClient *dynamic.DynamicClient, clientset *kubernetes.Clientset, namespace string) KubernetesService {
	return &kubernetesService{
		dynClient: dynClient,
		clientset: clientset,
		namespace: namespace,
	}
}

func (s *kubernetesService) GetMasK8sDefinition(ctx context.Context) (*MultiAgentSystemCRD, error) {
	// fetch the list of MAS CRs
	gvr := schema.GroupVersionResource{
		Group:    "zta.io",
		Version:  "v1alpha1",
		Resource: "multiagentsystems",
	}

	resource, err := s.dynClient.
		Resource(gvr).
		Namespace(s.namespace).
		List(ctx, metav1.ListOptions{})
	if err != nil {
		return nil, fmt.Errorf("unable to list the MAS CRDs: %w", err)
	}

	if len(resource.Items) == 0 {
		return nil, errors.New("no MultiAgentSystem resource found")
	}

	// TODO: pass the metadata.name as a parameter later
	// get the first one in the list
	masDef := resource.Items[0]

	name, _, _ := unstructured.NestedString(masDef.Object, "spec", "name")
	enabledToolChecks, _, _ := unstructured.NestedStringSlice(
		masDef.Object,
		"spec",
		"enabledToolChecks",
	)

	masCRD := &MultiAgentSystemCRD{
		Metadata: &CRDMetadata{
			UID:               string(masDef.GetUID()),
			Name:              masDef.GetName(),
			Namespace:         masDef.GetNamespace(),
			CreationTimestamp: masDef.GetCreationTimestamp().Time,
		},
		Name:              name,
		EnabledToolChecks: enabledToolChecks,
		Apps:              []*AppCRD{},
	}

	apps, _, _ := unstructured.NestedSlice(masDef.Object, "spec", "apps")
	for _, payload := range apps {
		appMap, ok := payload.(map[string]any)
		if ok {
			app, err := NewAppFromMap(appMap)
			if err != nil {
				return nil, fmt.Errorf("unable to create App: %w", err)
			}

			masCRD.Apps = append(masCRD.Apps, app)
		}
	}

	return masCRD, nil
}

func (s *kubernetesService) GetMasCRFromService(ctx context.Context, svcName string) (*MultiAgentSystemCRD, error) {
	servicesClient := s.clientset.CoreV1().Services(s.namespace)
	svc, err := servicesClient.Get(ctx, svcName, metav1.GetOptions{})
	if err != nil {
		return nil, fmt.Errorf("unable to get k8s service %s: %w", svcName, err)
	}

	selector := labels.SelectorFromSet(svc.Spec.Selector).String()

	pods, err := s.clientset.CoreV1().Pods(s.namespace).List(ctx, metav1.ListOptions{
		LabelSelector: selector,
		Limit:         1,
	})
	if err != nil {
		return nil, fmt.Errorf("unable to fetch pods with selector %s: %w", selector, err)
	}

	if len(pods.Items) == 0 {
		return nil, fmt.Errorf("no pods found with selector %s", selector)
	}

	masName := pods.Items[0].Annotations[podMASAnnotationKey]

	return s.GetMasResourceByName(ctx, masName)
}

func (s *kubernetesService) GetMasResourceByName(ctx context.Context, name string) (*MultiAgentSystemCRD, error) {
	// fetch the list of MAS CRs
	gvr := schema.GroupVersionResource{
		Group:    "zta.io",
		Version:  "v1alpha1",
		Resource: "multiagentsystems",
	}

	resource, err := s.dynClient.
		Resource(gvr).
		Namespace(s.namespace).
		Get(ctx, name, metav1.GetOptions{})
	if err != nil {
		return nil, fmt.Errorf("unable to get MAS resource by name %s: %w", name, err)
	}

	enabledToolChecks, _, _ := unstructured.NestedStringSlice(
		resource.Object,
		"spec",
		"enabledToolChecks",
	)

	masCRD := &MultiAgentSystemCRD{
		Metadata: &CRDMetadata{
			UID:               string(resource.GetUID()),
			Name:              resource.GetName(),
			Namespace:         resource.GetNamespace(),
			CreationTimestamp: resource.GetCreationTimestamp().Time,
		},
		Name:              name,
		EnabledToolChecks: enabledToolChecks,
		Apps:              []*AppCRD{},
	}

	apps, _, _ := unstructured.NestedSlice(resource.Object, "spec", "apps")
	for _, payload := range apps {
		appMap, ok := payload.(map[string]any)
		if ok {
			app, err := NewAppFromMap(appMap)
			if err != nil {
				return nil, fmt.Errorf("unable to create App: %w", err)
			}

			masCRD.Apps = append(masCRD.Apps, app)
		}
	}

	return masCRD, nil
}

func (s *kubernetesService) GetAppCredentials(ctx context.Context, appID string) (*AppClientCredential, error) {
	secretName := fmt.Sprintf("%s-oauth2-credentials", appID)
	secret, err := s.clientset.CoreV1().Secrets(s.namespace).Get(ctx, secretName, metav1.GetOptions{})
	if err != nil {
		return nil, fmt.Errorf("unable to fetch client credentials from k8s secret %s: %w", secretName, err)
	}

	var clientCred AppClientCredential

	if clientID, ok := secret.Data["client_id"]; ok {
		clientCred.ClientID = string(clientID)
	}

	if clientSecret, ok := secret.Data["client_secret"]; ok {
		clientCred.ClientSecret = string(clientSecret)
	}

	if clientCred.ClientID == "" || clientCred.ClientSecret == "" {
		return nil, nil
	}

	return &clientCred, nil
}
