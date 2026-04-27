// Copyright 2026 Google LLC
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
	"fmt"
	"io"
	"time"

	identitysdk "github.com/outshift-open/identity-auth-server/sdk/go"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/kubernetes"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
)

const (
	finalizer = "casa.io/finalizer"
)

var (
	schemeGroupVersion = schema.GroupVersion{Group: "casa.io", Version: "v1alpha1"}
)

type MultiAgentSystemReconciler struct {
	client.Client
	k8sClient     *kubernetes.Clientset
	authSrvClient *identitysdk.APIClient
}

func NewMultiAgentSystemReconciler(
	client client.Client,
	k8sClient *kubernetes.Clientset,
	authSrvClient *identitysdk.APIClient,
) *MultiAgentSystemReconciler {
	return &MultiAgentSystemReconciler{
		Client:        client,
		k8sClient:     k8sClient,
		authSrvClient: authSrvClient,
	}
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

func (r *MultiAgentSystemReconciler) syncToAuthService(ctx context.Context, mas *MultiAgentSystem) (int, []identitysdk.AppCredentials, error) {
	result, resp, err := r.authSrvClient.KubernetesCRDsAPI.CreateMasCrd(ctx, mas.Namespace).MASCreateRequest(identitysdk.MASCreateRequest{
		Metadata: identitysdk.MultiAgentSystemMetadata{
			Name:      mas.Name,
			Namespace: mas.Namespace,
		},
		Spec: identitysdk.MultiAgentSystemSpec{
			Name: mas.Spec.Name,
			EnabledToolChecks: ConvertSlice(mas.Spec.EnabledToolChecks, func(check string) identitysdk.ToolCheckType {
				return identitysdk.ToolCheckType(check)
			}),
			LlmHost: *identitysdk.NewNullableString(&mas.Spec.LLMHost),
			Apps: ConvertSlice(mas.Spec.Apps, func(app AppSpec) identitysdk.AppSpec {
				var httpRequestSchema *identitysdk.HttpRequestSchema
				if app.HttpRequestSchema != nil {
					httpRequestSchema = &identitysdk.HttpRequestSchema{
						PromptFieldJsonPath: app.HttpRequestSchema.PromptFieldJsonPath,
					}
				}

				return identitysdk.AppSpec{
					Name:                   app.Name,
					Type:                   identitysdk.AppType(app.Type),
					BaseUrl:                identitysdk.AppSpecBaseUrl(app.BaseURL),
					KubernetesWorkloadName: *identitysdk.NewNullableString(&app.KubernetesWorkloadName),
					HttpRequestSchema:      *identitysdk.NewNullableHttpRequestSchema(httpRequestSchema),
				}
			}),
		},
	}).Execute()
	if err != nil {
		return 0, nil, fmt.Errorf("call auth-service: %w", err)
	}

	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		respBody, _ := io.ReadAll(resp.Body)
		return 0, nil, fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(respBody))
	}

	return int(Derefrence(result.GetStatus().AppsReady, 0)), result.GetStatus().Credentials, nil
}

func (r *MultiAgentSystemReconciler) createSecrets(ctx context.Context, mas *MultiAgentSystem, credentials []identitysdk.AppCredentials) error {
	if len(credentials) == 0 {
		return nil
	}

	for _, cred := range credentials {
		secret := &corev1.Secret{
			ObjectMeta: metav1.ObjectMeta{
				Name:      cred.SecretName,
				Namespace: mas.Namespace,
				Labels: map[string]string{
					"app.kubernetes.io/managed-by": "casa-operator",
					"casa.io/mas-name":              mas.Name,
				},
			},
			Type: corev1.SecretTypeOpaque,
			StringData: map[string]string{
				"client_id":     cred.ClientId,
				"client_secret": cred.ClientSecret,
			},
		}

		// Try to create the secret
		_, err := r.k8sClient.CoreV1().Secrets(mas.Namespace).Create(ctx, secret, metav1.CreateOptions{})
		if err != nil {
			// If secret exists, update it
			if errors.IsAlreadyExists(err) {
				_, err = r.k8sClient.CoreV1().Secrets(mas.Namespace).Update(ctx, secret, metav1.UpdateOptions{})
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
		LabelSelector: fmt.Sprintf("casa.io/mas-name=%s", mas.Name),
	}

	secrets, err := r.k8sClient.CoreV1().Secrets(mas.Namespace).List(ctx, listOptions)
	if err != nil {
		return fmt.Errorf("failed to list secrets: %w", err)
	}

	for _, secret := range secrets.Items {
		err := r.k8sClient.CoreV1().Secrets(mas.Namespace).Delete(ctx, secret.Name, metav1.DeleteOptions{})
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
		"app.kubernetes.io/managed-by": "casa-operator",
		"casa.io/mas-name":              mas.Name,
	}

	se := &unstructured.Unstructured{}
	se.SetAPIVersion("networking.istio.io/v1beta1")
	se.SetKind("ServiceEntry")
	se.SetName(seName)
	se.SetNamespace(mas.Namespace)
	se.SetLabels(labels)
	_, err := controllerutil.CreateOrUpdate(ctx, r.Client, se, func() error {
		se.Object["spec"] = map[string]any{
			"hosts":      []any{mas.Spec.LLMHost},
			"resolution": "DNS",
			"location":   "MESH_EXTERNAL",
			"ports": []any{
				map[string]any{"number": int64(80), "name": "http", "protocol": "HTTP", "targetPort": int64(443)},
				map[string]any{"number": int64(443), "name": "https", "protocol": "HTTPS"},
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
		dr.Object["spec"] = map[string]any{
			"host": mas.Spec.LLMHost,
			"trafficPolicy": map[string]any{
				"portLevelSettings": []any{
					map[string]any{
						"port": map[string]any{"number": int64(80)},
						"tls":  map[string]any{"mode": "SIMPLE"},
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
	resp, err := r.authSrvClient.KubernetesCRDsAPI.DeleteMasCrd(ctx, mas.Namespace, mas.Name).Execute()
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
