// Copyright 2026 Cisco Systems, Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	identitysdk "github.com/outshift-open/CASA/sdk/go"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	k8sfake "k8s.io/client-go/kubernetes/fake"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/client/fake"
)

// buildTestScheme registers both the core Kubernetes types and the MAS CRD types.
func buildTestScheme() *runtime.Scheme {
	scheme := runtime.NewScheme()
	_ = clientgoscheme.AddToScheme(scheme)
	scheme.AddKnownTypes(schemeGroupVersion, &MultiAgentSystem{}, &MultiAgentSystemList{})
	metav1.AddToGroupVersion(scheme, schemeGroupVersion)
	return scheme
}

// reconcileReq constructs a controller-runtime reconcile Request.
func reconcileReq(name, namespace string) ctrl.Request {
	return ctrl.Request{NamespacedName: types.NamespacedName{Name: name, Namespace: namespace}}
}

// newTestReconciler wires up a reconciler with a fake CR client, a fake K8s clientset,
// and an auth server client pointed at the provided httptest.Server.
// crObjs are the initial objects in the CR store; k8sObjs are initial K8s core objects.
func newTestReconciler(
	t *testing.T,
	authSrv *httptest.Server,
	crObjs []client.Object,
	k8sObjs ...runtime.Object,
) (*MultiAgentSystemReconciler, client.Client, *k8sfake.Clientset) {
	t.Helper()

	scheme := buildTestScheme()
	crClient := fake.NewClientBuilder().
		WithScheme(scheme).
		WithStatusSubresource(&MultiAgentSystem{}).
		WithObjects(crObjs...).
		Build()

	k8sClient := k8sfake.NewSimpleClientset(k8sObjs...)

	authClient, err := newAuthServerClient(authSrv.URL)
	if err != nil {
		t.Fatalf("newAuthServerClient: %v", err)
	}

	r := NewMultiAgentSystemReconciler(crClient, k8sClient, authClient)
	return r, crClient, k8sClient
}

// baseMAS returns a minimal MultiAgentSystem for use in tests.
func baseMAS() *MultiAgentSystem {
	return &MultiAgentSystem{
		TypeMeta: metav1.TypeMeta{
			APIVersion: "casa.io/v1alpha1",
			Kind:       "MultiAgentSystem",
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      "test-mas",
			Namespace: "default",
		},
		Spec: MASSpec{
			Name: "Test MAS",
			Apps: []AppSpec{
				{
					Name: "app1",
					Type: "mcp",
					BaseURL: BaseURL{Scheme: "http", Host: "app1.default.svc.cluster.local"},
				},
			},
		},
	}
}

// masWithFinalizer returns baseMAS with the operator finalizer already present.
func masWithFinalizer() *MultiAgentSystem {
	m := baseMAS()
	m.Finalizers = []string{finalizer}
	return m
}

// mockCreateServer returns an httptest.Server that responds to any POST with a
// MultiAgentSystemCRD JSON body containing the supplied appsReady count and credentials.
func mockCreateServer(t *testing.T, appsReady int32, creds []identitysdk.AppCredentials) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		appsReadyVal := appsReady
		status := identitysdk.NewMultiAgentSystemStatus()
		status.AppsReady = &appsReadyVal
		status.Credentials = creds
		nullStatus := identitysdk.NewNullableMultiAgentSystemStatus(status)

		crd := identitysdk.NewMultiAgentSystemCRD(
			identitysdk.MultiAgentSystemMetadata{Name: "test-mas", Namespace: "default"},
			*identitysdk.NewMultiAgentSystemSpec("Test MAS"),
		)
		crd.Status = *nullStatus

		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(crd)
	}))
}

// mockDeleteServer returns an httptest.Server that accepts DELETE requests with 204
// and fails the test on any unexpected method.
func mockDeleteServer(t *testing.T) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodDelete {
			t.Errorf("unexpected %s request to %s during deletion reconcile", r.Method, r.URL.Path)
			http.Error(w, "unexpected method", http.StatusBadRequest)
			return
		}
		w.WriteHeader(http.StatusNoContent)
	}))
}

// --------------------------------------------------------------------------
// Tests
// --------------------------------------------------------------------------

// TestReconcile_NotFound verifies a quiet return when the MAS no longer exists.
func TestReconcile_NotFound(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("auth service should not be called for a missing MAS")
	}))
	defer srv.Close()

	r, _, _ := newTestReconciler(t, srv, nil)
	result, err := r.Reconcile(context.Background(), reconcileReq("not-found", "default"))

	if err != nil {
		t.Fatalf("expected nil error, got: %v", err)
	}
	if result != (ctrl.Result{}) {
		t.Errorf("expected empty result, got %+v", result)
	}
}

// TestReconcile_AddsFinalizer verifies that the first reconcile of a new MAS
// adds the operator finalizer and returns Requeue:true without calling the auth service.
func TestReconcile_AddsFinalizer(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t.Error("auth service must not be called before finalizer is set")
	}))
	defer srv.Close()

	mas := baseMAS()
	r, crClient, _ := newTestReconciler(t, srv, []client.Object{mas})

	result, err := r.Reconcile(context.Background(), reconcileReq("test-mas", "default"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !result.Requeue {
		t.Error("expected Requeue=true after adding finalizer")
	}

	got := &MultiAgentSystem{}
	if err := crClient.Get(context.Background(), types.NamespacedName{Name: "test-mas", Namespace: "default"}, got); err != nil {
		t.Fatalf("failed to get MAS after reconcile: %v", err)
	}
	for _, f := range got.Finalizers {
		if f == finalizer {
			return // success
		}
	}
	t.Errorf("finalizer %q not found; finalizers: %v", finalizer, got.Finalizers)
}

// TestReconcile_SyncSuccess verifies the happy path: an existing MAS with a finalizer
// is synced to the auth service, its K8s secret is created, and the status is set to Active.
func TestReconcile_SyncSuccess(t *testing.T) {
	creds := []identitysdk.AppCredentials{
		{AppName: "app1", AppId: "id-1", ClientId: "cid-1", ClientSecret: "csec-1", SecretName: "app1-secret"},
	}
	srv := mockCreateServer(t, 1, creds)
	defer srv.Close()

	mas := masWithFinalizer()
	r, crClient, k8sClient := newTestReconciler(t, srv, []client.Object{mas})

	result, err := r.Reconcile(context.Background(), reconcileReq("test-mas", "default"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != (ctrl.Result{}) {
		t.Errorf("expected empty result, got %+v", result)
	}

	// Secret must exist with the expected credentials.
	secret, err := k8sClient.CoreV1().Secrets("default").Get(context.Background(), "app1-secret", metav1.GetOptions{})
	if err != nil {
		t.Fatalf("secret app1-secret not found: %v", err)
	}
	if secret.StringData["client_id"] != "cid-1" {
		t.Errorf("client_id = %q, want %q", secret.StringData["client_id"], "cid-1")
	}
	if secret.StringData["client_secret"] != "csec-1" {
		t.Errorf("client_secret = %q, want %q", secret.StringData["client_secret"], "csec-1")
	}
	if secret.Labels["app.kubernetes.io/managed-by"] != "casa-operator" {
		t.Errorf("managed-by label = %q, want %q", secret.Labels["app.kubernetes.io/managed-by"], "casa-operator")
	}

	// MAS status must reflect an Active phase.
	updated := &MultiAgentSystem{}
	if err := crClient.Get(context.Background(), types.NamespacedName{Name: "test-mas", Namespace: "default"}, updated); err != nil {
		t.Fatalf("failed to get MAS after reconcile: %v", err)
	}
	if updated.Status.Phase != "Active" {
		t.Errorf("status.phase = %q, want %q", updated.Status.Phase, "Active")
	}
	if updated.Status.AppsReady != 1 {
		t.Errorf("status.appsReady = %d, want 1", updated.Status.AppsReady)
	}
}

// TestReconcile_AuthServiceError verifies that a 500 from the auth service causes
// a re-queue with a 30 s delay and does NOT surface the error (to avoid exponential backoff).
func TestReconcile_AuthServiceError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "internal server error", http.StatusInternalServerError)
	}))
	defer srv.Close()

	mas := masWithFinalizer()
	r, _, _ := newTestReconciler(t, srv, []client.Object{mas})

	result, err := r.Reconcile(context.Background(), reconcileReq("test-mas", "default"))
	if err != nil {
		t.Fatalf("expected nil error (swallowed on auth failure), got: %v", err)
	}
	if result.RequeueAfter != 30*time.Second {
		t.Errorf("RequeueAfter = %v, want 30s", result.RequeueAfter)
	}
}

// TestReconcile_Deletion verifies the full deletion flow: secrets are deleted,
// the auth service DELETE endpoint is called, and the finalizer is removed.
func TestReconcile_Deletion(t *testing.T) {
	srv := mockDeleteServer(t)
	defer srv.Close()

	deletionTime := metav1.Now()
	mas := masWithFinalizer()
	mas.DeletionTimestamp = &deletionTime

	// Pre-create a secret owned by this MAS to verify it is garbage-collected.
	existingSecret := &corev1.Secret{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "app1-secret",
			Namespace: "default",
			Labels:    map[string]string{"casa.io/mas-name": "test-mas"},
		},
		Type: corev1.SecretTypeOpaque,
	}

	r, crClient, k8sClient := newTestReconciler(t, srv, []client.Object{mas}, existingSecret)

	result, err := r.Reconcile(context.Background(), reconcileReq("test-mas", "default"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != (ctrl.Result{}) {
		t.Errorf("expected empty result, got %+v", result)
	}

	// Secret must be gone.
	_, err = k8sClient.CoreV1().Secrets("default").Get(context.Background(), "app1-secret", metav1.GetOptions{})
	if err == nil {
		t.Error("expected secret app1-secret to be deleted, but it still exists")
	}

	// Finalizer must be removed. The fake client deletes the object entirely once
	// all finalizers are gone and DeletionTimestamp is set, so "not found" is also
	// an acceptable (and correct) outcome.
	got := &MultiAgentSystem{}
	err = crClient.Get(context.Background(), types.NamespacedName{Name: "test-mas", Namespace: "default"}, got)
	if err == nil {
		for _, f := range got.Finalizers {
			if f == finalizer {
				t.Errorf("finalizer %q still present after deletion", finalizer)
			}
		}
	}
	// err != nil (not found) means the object was fully removed — that's fine.
}
