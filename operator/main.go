package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/kubernetes"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
)

const (
	finalizer = "zta.io/finalizer"
)

// ── CRD types ────────────────────────────────────────────────────────────────

type BaseURL struct {
	Host   string `json:"host"`
	Scheme string `json:"scheme"`
}

type AppSpec struct {
	Name                   string  `json:"name"`
	Type                   string  `json:"type"`
	BaseURL                BaseURL `json:"baseUrl"`
	KubernetesWorkloadName string  `json:"kubernetesWorkloadName"`
}

type MASSpec struct {
	Name                string    `json:"name"`
	AuthorizationServer string    `json:"authorizationServer"`
	EnabledToolChecks   []string  `json:"enabledToolChecks,omitempty"`
	Apps                []AppSpec `json:"apps,omitempty"`
	LLMHost             string    `json:"llm_host,omitempty"`
}

type MASStatus struct {
	Phase        string           `json:"phase,omitempty"`
	AppsReady    int              `json:"appsReady,omitempty"`
	LastSyncTime string           `json:"lastSyncTime,omitempty"`
	Message      string           `json:"message,omitempty"`
	Credentials  []AppCredentials `json:"credentials,omitempty"`
}

type MultiAgentSystem struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              MASSpec   `json:"spec,omitempty"`
	Status            MASStatus `json:"status,omitempty"`
}

type MultiAgentSystemList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []MultiAgentSystem `json:"items"`
}

func (m *MultiAgentSystem) DeepCopyObject() runtime.Object {
	out := &MultiAgentSystem{}
	*out = *m
	out.Spec.Apps = append([]AppSpec{}, m.Spec.Apps...)
	out.Spec.EnabledToolChecks = append([]string{}, m.Spec.EnabledToolChecks...)
	return out
}

func (m *MultiAgentSystemList) DeepCopyObject() runtime.Object {
	out := &MultiAgentSystemList{}
	*out = *m
	out.Items = append([]MultiAgentSystem{}, m.Items...)
	return out
}

var (
	masGVK = schema.GroupVersionKind{
		Group:   "zta.io",
		Version: "v1alpha1",
		Kind:    "MultiAgentSystem",
	}
	masGVR = schema.GroupVersionResource{
		Group:    "zta.io",
		Version:  "v1alpha1",
		Resource: "multiagentsystems",
	}
	schemeGroupVersion = schema.GroupVersion{Group: "zta.io", Version: "v1alpha1"}
)

// ── Auth-service request payload ─────────────────────────────────────────────

type MASCreateRequest struct {
	APIVersion string      `json:"apiVersion"`
	Kind       string      `json:"kind"`
	Metadata   MASMetadata `json:"metadata"`
	Spec       MASSpec     `json:"spec"`
}

type MASMetadata struct {
	Name      string `json:"name"`
	Namespace string `json:"namespace"`
}

type AppCredentials struct {
	AppName      string `json:"appName"`
	ClientID     string `json:"clientId"`
	ClientSecret string `json:"clientSecret"`
	SecretName   string `json:"secretName"`
}

// ── Reconciler ───────────────────────────────────────────────────────────────

type MultiAgentSystemReconciler struct {
	client.Client
	Scheme         *runtime.Scheme
	AuthServiceURL string
	HTTPClient     *http.Client
	K8sClient      *kubernetes.Clientset
}

func (r *MultiAgentSystemReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)

	mas := &MultiAgentSystem{}
	if err := r.Get(ctx, req.NamespacedName, mas); err != nil {
		if errors.IsNotFound(err) {
			return ctrl.Result{}, nil
		}
		return ctrl.Result{}, err
	}

	// Handle deletion via finalizer
	if !mas.DeletionTimestamp.IsZero() {
		if controllerutil.ContainsFinalizer(mas, finalizer) {
			// Delete secrets first
			if err := r.deleteSecrets(ctx, mas); err != nil {
				log.Error(err, "failed to delete secrets")
				// Continue anyway - secrets might already be gone
			}

			// Delete Istio egress resources
			if err := r.deleteIstioResources(ctx, mas); err != nil {
				log.Error(err, "failed to delete Istio resources")
				// Continue anyway
			}

			// Then delete from auth-service
			if err := r.deleteFromAuthService(ctx, mas); err != nil {
				log.Error(err, "failed to delete MAS from auth-service")
				return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
			}
			controllerutil.RemoveFinalizer(mas, finalizer)
			if err := r.Update(ctx, mas); err != nil {
				return ctrl.Result{}, err
			}
		}
		return ctrl.Result{}, nil
	}

	// Add finalizer on first reconcile
	if !controllerutil.ContainsFinalizer(mas, finalizer) {
		controllerutil.AddFinalizer(mas, finalizer)
		if err := r.Update(ctx, mas); err != nil {
			return ctrl.Result{}, err
		}
		return ctrl.Result{Requeue: true}, nil
	}

	// Register / update with auth-service
	appsReady, credentials, err := r.syncToAuthService(ctx, mas)
	if err != nil {
		log.Error(err, "failed to sync MAS with auth-service")
		if patchErr := r.patchStatus(ctx, mas, "Failed", 0, err.Error()); patchErr != nil {
			log.Error(patchErr, "failed to patch status to Failed")
		}
		return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
	}

	// Create K8s secrets for app credentials
	if err := r.createSecrets(ctx, mas, credentials); err != nil {
		log.Error(err, "failed to create secrets for app credentials")
		if patchErr := r.patchStatus(ctx, mas, "Failed", 0, fmt.Sprintf("Failed to create secrets: %v", err)); patchErr != nil {
			log.Error(patchErr, "failed to patch status to Failed")
		}
		return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
	}

	// Create Istio egress resources for LLM endpoint
	if err := r.createIstioResources(ctx, mas); err != nil {
		log.Error(err, "failed to create Istio resources")
		// Non-fatal: don't block the reconcile
	}

	if patchErr := r.patchStatus(ctx, mas, "Active", appsReady, fmt.Sprintf("Registered %d apps", appsReady)); patchErr != nil {
		log.Error(patchErr, "failed to patch status to Active")
		return ctrl.Result{}, patchErr
	}

	log.Info("MAS synced successfully", "name", mas.Name, "appsReady", appsReady)
	return ctrl.Result{}, nil
}

func (r *MultiAgentSystemReconciler) syncToAuthService(ctx context.Context, mas *MultiAgentSystem) (int, []AppCredentials, error) {
	payload := MASCreateRequest{
		APIVersion: "zta.io/v1alpha1",
		Kind:       "MultiAgentSystem",
		Metadata: MASMetadata{
			Name:      mas.Name,
			Namespace: mas.Namespace,
		},
		Spec: mas.Spec,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return 0, nil, fmt.Errorf("marshal: %w", err)
	}

	url := fmt.Sprintf("%s/k8s/namespaces/%s/mas", r.AuthServiceURL, mas.Namespace)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return 0, nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := r.HTTPClient.Do(req)
	if err != nil {
		return 0, nil, fmt.Errorf("call auth-service: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 400 {
		return 0, nil, fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(respBody))
	}

	var result struct {
		Status struct {
			AppsReady   int              `json:"appsReady"`
			Credentials []AppCredentials `json:"credentials"`
		} `json:"status"`
	}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return len(mas.Spec.Apps), nil, nil // fallback: assume all apps registered
	}
	return result.Status.AppsReady, result.Status.Credentials, nil
}

func (r *MultiAgentSystemReconciler) createSecrets(ctx context.Context, mas *MultiAgentSystem, credentials []AppCredentials) error {
	if len(credentials) == 0 {
		return nil
	}

	for _, cred := range credentials {
		secret := &corev1.Secret{
			ObjectMeta: metav1.ObjectMeta{
				Name:      cred.SecretName,
				Namespace: mas.Namespace,
				Labels: map[string]string{
					"app.kubernetes.io/managed-by": "zta-operator",
					"zta.io/mas-name":              mas.Name,
				},
			},
			Type: corev1.SecretTypeOpaque,
			StringData: map[string]string{
				"client_id":     cred.ClientID,
				"client_secret": cred.ClientSecret,
			},
		}

		// Try to create the secret
		_, err := r.K8sClient.CoreV1().Secrets(mas.Namespace).Create(ctx, secret, metav1.CreateOptions{})
		if err != nil {
			// If secret exists, update it
			if errors.IsAlreadyExists(err) {
				_, err = r.K8sClient.CoreV1().Secrets(mas.Namespace).Update(ctx, secret, metav1.UpdateOptions{})
				if err != nil {
					return fmt.Errorf("failed to update secret %s: %w", cred.SecretName, err)
				}
			} else {
				return fmt.Errorf("failed to create secret %s: %w", cred.SecretName, err)
			}
		}
	}

	return nil
}

func (r *MultiAgentSystemReconciler) deleteSecrets(ctx context.Context, mas *MultiAgentSystem) error {
	// Delete all secrets managed by this MAS
	listOptions := metav1.ListOptions{
		LabelSelector: fmt.Sprintf("zta.io/mas-name=%s", mas.Name),
	}

	secrets, err := r.K8sClient.CoreV1().Secrets(mas.Namespace).List(ctx, listOptions)
	if err != nil {
		return fmt.Errorf("failed to list secrets: %w", err)
	}

	for _, secret := range secrets.Items {
		err := r.K8sClient.CoreV1().Secrets(mas.Namespace).Delete(ctx, secret.Name, metav1.DeleteOptions{})
		if err != nil && !errors.IsNotFound(err) {
			return fmt.Errorf("failed to delete secret %s: %w", secret.Name, err)
		}
	}

	return nil
}

func (r *MultiAgentSystemReconciler) createIstioResources(ctx context.Context, mas *MultiAgentSystem) error {
	if mas.Spec.LLMHost == "" {
		return nil
	}

	seName := mas.Name + "-llm-srv-entry"
	drName := mas.Name + "-llm-dr"
	labels := map[string]string{
		"app.kubernetes.io/managed-by": "zta-operator",
		"zta.io/mas-name":              mas.Name,
	}

	se := &unstructured.Unstructured{}
	se.SetAPIVersion("networking.istio.io/v1beta1")
	se.SetKind("ServiceEntry")
	se.SetName(seName)
	se.SetNamespace(mas.Namespace)
	se.SetLabels(labels)
	_, err := controllerutil.CreateOrUpdate(ctx, r.Client, se, func() error {
		se.Object["spec"] = map[string]interface{}{
			"hosts":      []interface{}{mas.Spec.LLMHost},
			"resolution": "DNS",
			"location":   "MESH_EXTERNAL",
			"ports": []interface{}{
				map[string]interface{}{"number": int64(80), "name": "http", "protocol": "HTTP", "targetPort": int64(443)},
				map[string]interface{}{"number": int64(443), "name": "https", "protocol": "HTTPS"},
			},
		}
		return nil
	})
	if err != nil {
		return fmt.Errorf("failed to create/update ServiceEntry: %w", err)
	}

	dr := &unstructured.Unstructured{}
	dr.SetAPIVersion("networking.istio.io/v1beta1")
	dr.SetKind("DestinationRule")
	dr.SetName(drName)
	dr.SetNamespace(mas.Namespace)
	dr.SetLabels(labels)
	_, err = controllerutil.CreateOrUpdate(ctx, r.Client, dr, func() error {
		dr.Object["spec"] = map[string]interface{}{
			"host": mas.Spec.LLMHost,
			"trafficPolicy": map[string]interface{}{
				"portLevelSettings": []interface{}{
					map[string]interface{}{
						"port": map[string]interface{}{"number": int64(80)},
						"tls":  map[string]interface{}{"mode": "SIMPLE"},
					},
				},
			},
		}
		return nil
	})
	if err != nil {
		return fmt.Errorf("failed to create/update DestinationRule: %w", err)
	}

	return nil
}

func (r *MultiAgentSystemReconciler) deleteIstioResources(ctx context.Context, mas *MultiAgentSystem) error {
	se := &unstructured.Unstructured{}
	se.SetAPIVersion("networking.istio.io/v1beta1")
	se.SetKind("ServiceEntry")
	se.SetName(mas.Name + "-llm-srv-entry")
	se.SetNamespace(mas.Namespace)
	if err := r.Client.Delete(ctx, se); err != nil && !errors.IsNotFound(err) {
		return fmt.Errorf("failed to delete ServiceEntry: %w", err)
	}

	dr := &unstructured.Unstructured{}
	dr.SetAPIVersion("networking.istio.io/v1beta1")
	dr.SetKind("DestinationRule")
	dr.SetName(mas.Name + "-llm-dr")
	dr.SetNamespace(mas.Namespace)
	if err := r.Client.Delete(ctx, dr); err != nil && !errors.IsNotFound(err) {
		return fmt.Errorf("failed to delete DestinationRule: %w", err)
	}

	return nil
}

func (r *MultiAgentSystemReconciler) deleteFromAuthService(ctx context.Context, mas *MultiAgentSystem) error {
	url := fmt.Sprintf("%s/k8s/namespaces/%s/mas/%s", r.AuthServiceURL, mas.Namespace, mas.Name)
	req, err := http.NewRequestWithContext(ctx, http.MethodDelete, url, nil)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	resp, err := r.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("call auth-service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 204 && resp.StatusCode != 404 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(body))
	}
	return nil
}

func (r *MultiAgentSystemReconciler) patchStatus(ctx context.Context, mas *MultiAgentSystem, phase string, appsReady int, message string) error {
	patch := client.MergeFrom(mas.DeepCopyObject().(client.Object))
	mas.Status.Phase = phase
	mas.Status.AppsReady = appsReady
	mas.Status.Message = message
	mas.Status.LastSyncTime = time.Now().UTC().Format(time.RFC3339)
	return r.Status().Patch(ctx, mas, patch)
}

func (r *MultiAgentSystemReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&MultiAgentSystem{}).
		Complete(r)
}

// ── Main ─────────────────────────────────────────────────────────────────────

func main() {
	opts := zap.Options{Development: false}
	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	authServiceURL := os.Getenv("AUTH_SERVICE_URL")
	if authServiceURL == "" {
		authServiceURL = "http://zta-control-plane-auth-service:8000"
	}

	scheme := runtime.NewScheme()
	_ = clientgoscheme.AddToScheme(scheme)

	// Register zta.io/v1alpha1 GroupVersion
	scheme.AddKnownTypes(schemeGroupVersion, &MultiAgentSystem{}, &MultiAgentSystemList{})
	metav1.AddToGroupVersion(scheme, schemeGroupVersion)

	// Get in-cluster config
	config, err := rest.InClusterConfig()
	if err != nil {
		ctrl.Log.Error(err, "unable to get in-cluster config")
		os.Exit(1)
	}

	// Create K8s clientset for secret management
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		ctrl.Log.Error(err, "unable to create K8s clientset")
		os.Exit(1)
	}

	mgr, err := ctrl.NewManager(config, ctrl.Options{
		Scheme: scheme,
	})
	if err != nil {
		ctrl.Log.Error(err, "unable to start manager")
		os.Exit(1)
	}

	if err := (&MultiAgentSystemReconciler{
		Client:         mgr.GetClient(),
		Scheme:         mgr.GetScheme(),
		AuthServiceURL: authServiceURL,
		HTTPClient:     &http.Client{Timeout: 120 * time.Second},
		K8sClient:      clientset,
	}).SetupWithManager(mgr); err != nil {
		ctrl.Log.Error(err, "unable to create controller")
		os.Exit(1)
	}

	ctrl.Log.Info("starting manager", "authServiceURL", authServiceURL)
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		ctrl.Log.Error(err, "problem running manager")
		os.Exit(1)
	}
}
