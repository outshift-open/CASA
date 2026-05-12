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
	"fmt"
	"io"
	"time"

	identitysdk "github.com/outshift-open/CASA/sdk/go"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
)

type CASAPolicyReconciler struct {
	client.Client
	authSrvClient *identitysdk.APIClient
}

func NewCASAPolicyReconciler(
	c client.Client,
	authSrvClient *identitysdk.APIClient,
) *CASAPolicyReconciler {
	return &CASAPolicyReconciler{
		Client:        c,
		authSrvClient: authSrvClient,
	}
}

func (r *CASAPolicyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)

	policy := &CASAPolicy{}
	if err := r.Get(ctx, req.NamespacedName, policy); err != nil {
		if errors.IsNotFound(err) {
			return ctrl.Result{}, nil
		}
		return ctrl.Result{}, err
	}

	// Handle deletion via finalizer
	if !policy.DeletionTimestamp.IsZero() {
		if controllerutil.ContainsFinalizer(policy, finalizer) {
			if err := r.deletePolicyIstioResources(ctx, policy); err != nil {
				log.Error(err, "failed to delete Istio resources for policy")
				// Continue anyway
			}

			if err := r.deleteFromAuthService(ctx, policy); err != nil {
				log.Error(err, "failed to delete CASAPolicy from auth-service")
				return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
			}

			controllerutil.RemoveFinalizer(policy, finalizer)
			if err := r.Update(ctx, policy); err != nil {
				return ctrl.Result{}, err
			}
		}
		return ctrl.Result{}, nil
	}

	// Add finalizer on first reconcile
	if !controllerutil.ContainsFinalizer(policy, finalizer) {
		controllerutil.AddFinalizer(policy, finalizer)
		if err := r.Update(ctx, policy); err != nil {
			return ctrl.Result{}, err
		}
		return ctrl.Result{Requeue: true}, nil
	}

	// Sync to auth-service
	if err := r.syncToAuthService(ctx, policy); err != nil {
		log.Error(err, "failed to sync CASAPolicy with auth-service")
		if patchErr := r.patchPolicyStatus(ctx, policy, "Failed", err.Error()); patchErr != nil {
			log.Error(patchErr, "failed to patch status to Failed")
		}
		return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
	}

	// Create Istio resources
	if err := r.createPolicyIstioResources(ctx, policy); err != nil {
		log.Error(err, "failed to create Istio resources for policy")
		// Non-fatal: don't block the reconcile
	}

	if patchErr := r.patchPolicyStatus(ctx, policy, "Active", fmt.Sprintf("Policy synced for workload %s", policy.Spec.TargetRef.Name)); patchErr != nil {
		log.Error(patchErr, "failed to patch status to Active")
		return ctrl.Result{}, patchErr
	}

	log.Info("CASAPolicy synced successfully", "name", policy.Name, "workload", policy.Spec.TargetRef.Name)
	return ctrl.Result{}, nil
}

func (r *CASAPolicyReconciler) syncToAuthService(ctx context.Context, policy *CASAPolicy) error {
	allowedEndpoints := ConvertSlice(policy.Spec.AllowedEndpoints, func(ep PolicyAllowedEndpoint) identitysdk.CASAPolicyAllowedEndpoint {
		return identitysdk.CASAPolicyAllowedEndpoint{
			Name:      ep.Name,
			Namespace: ep.Namespace,
			Port:      int32(ep.Port),
		}
	})

	spec := identitysdk.CASAPolicySpec{
		TargetRef: identitysdk.CASAPolicyTargetRef{
			Kind: policy.Spec.TargetRef.Kind,
			Name: policy.Spec.TargetRef.Name,
		},
		AllowedProtocols: policy.Spec.AllowedProtocols,
		AllowedEndpoints: allowedEndpoints,
	}

	if policy.Spec.LlmEndpoint != nil {
		llmEp := identitysdk.NewCASAPolicyLlmEndpoint(policy.Spec.LlmEndpoint.Fqdn, int32(policy.Spec.LlmEndpoint.Port))
		spec.LlmEndpoint = *identitysdk.NewNullableCASAPolicyLlmEndpoint(llmEp)
	}

	result, resp, err := r.authSrvClient.KubernetesCRDsAPI.CreatePolicyCrd(ctx, policy.Namespace).
		CASAPolicyCreateRequest(identitysdk.CASAPolicyCreateRequest{
			Metadata: identitysdk.MultiAgentSystemMetadata{
				Name:      policy.Name,
				Namespace: policy.Namespace,
			},
			Spec: spec,
		}).Execute()
	if err != nil {
		return fmt.Errorf("call auth-service: %w", err)
	}

	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(respBody))
	}

	_ = result
	return nil
}

func (r *CASAPolicyReconciler) deleteFromAuthService(ctx context.Context, policy *CASAPolicy) error {
	resp, err := r.authSrvClient.KubernetesCRDsAPI.DeletePolicyCrd(ctx, policy.Namespace, policy.Name).Execute()
	if resp != nil {
		defer resp.Body.Close()
		if resp.StatusCode == 404 || resp.StatusCode == 204 {
			return nil
		}
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("auth-service returned %d: %s", resp.StatusCode, string(body))
	}
	if err != nil {
		return fmt.Errorf("call auth-service: %w", err)
	}
	return nil
}

func (r *CASAPolicyReconciler) createPolicyIstioResources(ctx context.Context, policy *CASAPolicy) error {
	labels := map[string]string{
		"app.kubernetes.io/managed-by": "casa-operator",
		"casa.io/policy-name":          policy.Name,
	}

	// Build egress hosts: cluster services from allowedEndpoints
	// Istio requires FQDN in egress hosts; short names are rejected by the validation webhook.
	egressHosts := []any{}
	for _, ep := range policy.Spec.AllowedEndpoints {
		egressHosts = append(egressHosts, fmt.Sprintf("%s/%s.%s.svc.cluster.local", ep.Namespace, ep.Name, ep.Namespace))
	}
	// Always include istio-system for telemetry
	egressHosts = append(egressHosts, "istio-system/*")

	// Add LLM endpoint host if set (requires a ServiceEntry in the same namespace)
	if policy.Spec.LlmEndpoint != nil {
		egressHosts = append(egressHosts, fmt.Sprintf("./%s", policy.Spec.LlmEndpoint.Fqdn))
	}

	// Sidecar to restrict egress for the target workload
	sidecar := &unstructured.Unstructured{}
	sidecar.SetAPIVersion("networking.istio.io/v1beta1")
	sidecar.SetKind("Sidecar")
	sidecar.SetName(policy.Name + "-sidecar")
	sidecar.SetNamespace(policy.Namespace)
	sidecar.SetLabels(labels)
	_, err := controllerutil.CreateOrUpdate(ctx, r.Client, sidecar, func() error {
		sidecar.Object["spec"] = map[string]any{
			"workloadSelector": map[string]any{
				"labels": map[string]any{
					"app": policy.Spec.TargetRef.Name,
				},
			},
			"egress": []any{
				map[string]any{"hosts": egressHosts},
			},
		}
		return nil
	})
	if err != nil {
		return fmt.Errorf("failed to create/update Sidecar: %w", err)
	}

	// ServiceEntry + DestinationRule for the external LLM endpoint (if set)
	if policy.Spec.LlmEndpoint != nil {
		if err := r.createLlmIstioResources(ctx, policy, labels); err != nil {
			return err
		}
	}

	return nil
}

func (r *CASAPolicyReconciler) createLlmIstioResources(ctx context.Context, policy *CASAPolicy, labels map[string]string) error {
	llm := policy.Spec.LlmEndpoint
	seName := policy.Name + "-llm-srv-entry"
	drName := policy.Name + "-llm-dr"

	se := &unstructured.Unstructured{}
	se.SetAPIVersion("networking.istio.io/v1beta1")
	se.SetKind("ServiceEntry")
	se.SetName(seName)
	se.SetNamespace(policy.Namespace)
	se.SetLabels(labels)
	_, err := controllerutil.CreateOrUpdate(ctx, r.Client, se, func() error {
		se.Object["spec"] = map[string]any{
			"hosts":      []any{llm.Fqdn},
			"resolution": "DNS",
			"location":   "MESH_EXTERNAL",
			"ports": []any{
				map[string]any{"number": int64(80), "name": "http", "protocol": "HTTP", "targetPort": int64(llm.Port)},
				map[string]any{"number": int64(llm.Port), "name": "https", "protocol": "HTTPS"},
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
	dr.SetNamespace(policy.Namespace)
	dr.SetLabels(labels)
	_, err = controllerutil.CreateOrUpdate(ctx, r.Client, dr, func() error {
		dr.Object["spec"] = map[string]any{
			"host": llm.Fqdn,
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

func (r *CASAPolicyReconciler) deletePolicyIstioResources(ctx context.Context, policy *CASAPolicy) error {
	sidecar := &unstructured.Unstructured{}
	sidecar.SetAPIVersion("networking.istio.io/v1beta1")
	sidecar.SetKind("Sidecar")
	sidecar.SetName(policy.Name + "-sidecar")
	sidecar.SetNamespace(policy.Namespace)
	if err := r.Client.Delete(ctx, sidecar); err != nil && !errors.IsNotFound(err) {
		return fmt.Errorf("failed to delete Sidecar: %w", err)
	}

	se := &unstructured.Unstructured{}
	se.SetAPIVersion("networking.istio.io/v1beta1")
	se.SetKind("ServiceEntry")
	se.SetName(policy.Name + "-llm-srv-entry")
	se.SetNamespace(policy.Namespace)
	if err := r.Client.Delete(ctx, se); err != nil && !errors.IsNotFound(err) {
		return fmt.Errorf("failed to delete ServiceEntry: %w", err)
	}

	dr := &unstructured.Unstructured{}
	dr.SetAPIVersion("networking.istio.io/v1beta1")
	dr.SetKind("DestinationRule")
	dr.SetName(policy.Name + "-llm-dr")
	dr.SetNamespace(policy.Namespace)
	if err := r.Client.Delete(ctx, dr); err != nil && !errors.IsNotFound(err) {
		return fmt.Errorf("failed to delete DestinationRule: %w", err)
	}

	return nil
}

func (r *CASAPolicyReconciler) patchPolicyStatus(ctx context.Context, policy *CASAPolicy, phase string, message string) error {
	patch := client.MergeFrom(policy.DeepCopyObject().(client.Object))
	policy.Status.Phase = phase
	policy.Status.Message = message
	policy.Status.LastSyncTime = time.Now().UTC().Format(time.RFC3339)
	return r.Status().Patch(ctx, policy, patch)
}

func (r *CASAPolicyReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&CASAPolicy{}).
		Complete(r)
}
