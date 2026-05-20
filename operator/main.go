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
	"fmt"
	"net/http"
	"net/url"
	"os"
	"time"

	identitysdk "github.com/outshift-open/CASA/sdk/go"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/client-go/kubernetes"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
)

func main() {
	opts := zap.Options{Development: false}
	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	authSrvClient, err := newAuthServerClient(os.Getenv("AUTH_SERVICE_URL"))
	if err != nil {
		ctrl.Log.Error(err, "unable to create auth service client")
		os.Exit(1)
	}

	scheme := runtime.NewScheme()
	_ = clientgoscheme.AddToScheme(scheme)

	// Register casa.io/v1alpha1 GroupVersion
	scheme.AddKnownTypes(schemeGroupVersion, &MultiAgentSystem{}, &MultiAgentSystemList{})
	scheme.AddKnownTypes(schemeGroupVersion, &CASAPolicy{}, &CASAPolicyList{})
	metav1.AddToGroupVersion(scheme, schemeGroupVersion)

	// Get in-cluster config
	config, err := rest.InClusterConfig()
	if err != nil {
		ctrl.Log.Error(err, "unable to get in-cluster config")
		os.Exit(1)
	}

	// Create K8s clientset for secret management
	var clientset kubernetes.Interface
	clientset, err = kubernetes.NewForConfig(config)
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

	err = NewMultiAgentSystemReconciler(mgr.GetClient(), clientset, authSrvClient).SetupWithManager(mgr)
	if err != nil {
		ctrl.Log.Error(err, "unable to create MultiAgentSystem controller")
		os.Exit(1)
	}

	err = NewCASAPolicyReconciler(mgr.GetClient(), authSrvClient).SetupWithManager(mgr)
	if err != nil {
		ctrl.Log.Error(err, "unable to create CASAPolicy controller")
		os.Exit(1)
	}

	ctrl.Log.Info("starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		ctrl.Log.Error(err, "problem running manager")
		os.Exit(1)
	}
}

func newAuthServerClient(authSrvURL string) (*identitysdk.APIClient, error) {
	u, err := url.Parse(authSrvURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse auth service URL %s: %w", authSrvURL, err)
	}

	config := identitysdk.NewConfiguration()
	config.Host = u.Host
	config.Scheme = u.Scheme
	config.HTTPClient = &http.Client{Timeout: 120 * time.Second}

	return identitysdk.NewAPIClient(config), nil
}
