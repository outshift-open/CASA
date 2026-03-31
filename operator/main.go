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

	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
)

const (
	finalizer = "zta.io/finalizer"
)

// ── CRD types ────────────────────────────────────────────────────────────────

type AppSpec struct {
	Name    string `json:"name"`
	Type    string `json:"type"`
	BaseURL string `json:"baseUrl"`
}

type MASSpec struct {
	Name                string    `json:"name"`
	AuthorizationServer string    `json:"authorizationServer"`
	EnabledToolChecks   []string  `json:"enabledToolChecks,omitempty"`
	Apps                []AppSpec `json:"apps,omitempty"`
}

type MASStatus struct {
	Phase       string `json:"phase,omitempty"`
	AppsReady   int    `json:"appsReady,omitempty"`
	LastSyncTime string `json:"lastSyncTime,omitempty"`
	Message     string `json:"message,omitempty"`
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

// ── Reconciler ───────────────────────────────────────────────────────────────

type MultiAgentSystemReconciler struct {
	client.Client
	Scheme         *runtime.Scheme
	AuthServiceURL string
	HTTPClient     *http.Client
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
	appsReady, err := r.syncToAuthService(ctx, mas)
	if err != nil {
		log.Error(err, "failed to sync MAS with auth-service")
		if patchErr := r.patchStatus(ctx, mas, "Failed", 0, err.Error()); patchErr != nil {
			log.Error(patchErr, "failed to patch status to Failed")
		}
		return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
	}

	if patchErr := r.patchStatus(ctx, mas, "Active", appsReady, fmt.Sprintf("Registered %d apps", appsReady)); patchErr != nil {
		log.Error(patchErr, "failed to patch status to Active")
		return ctrl.Result{}, patchErr
	}

	log.Info("MAS synced successfully", "name", mas.Name, "appsReady", appsReady)
	return ctrl.Result{}, nil
}

func (r *MultiAgentSystemReconciler) syncToAuthService(ctx context.Context, mas *MultiAgentSystem) (int, error) {
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
		return 0, fmt.Errorf("marshal: %w", err)
	}

	url := fmt.Sprintf("%s/k8s/namespaces/%s/mas", r.AuthServiceURL, mas.Namespace)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return 0, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := r.HTTPClient.Do(req)
	if err != nil {
		return 0, fmt.Errorf("call auth-service: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 400 {
		return 0, fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(respBody))
	}

	var result struct {
		Status struct {
			AppsReady int `json:"appsReady"`
		} `json:"status"`
	}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return len(mas.Spec.Apps), nil // fallback: assume all apps registered
	}
	return result.Status.AppsReady, nil
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
	_ = metav1.AddMetaToScheme(scheme)
	scheme.AddKnownTypeWithName(masGVK, &MultiAgentSystem{})
	scheme.AddKnownTypeWithName(
		schema.GroupVersionKind{Group: "zta.io", Version: "v1alpha1", Kind: "MultiAgentSystemList"},
		&MultiAgentSystemList{},
	)

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
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
		HTTPClient:     &http.Client{Timeout: 30 * time.Second},
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
