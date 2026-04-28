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

package internal

import (
	"context"
	"errors"
	"net"

	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"google.golang.org/grpc"
)

type ExtAuthServer struct {
	grpcServer     *GRPCServer
	extAuthService authv3.AuthorizationServer
}

func NewExtAuthServer(host string, extAuthService authv3.AuthorizationServer) (*ExtAuthServer, error) {
	grpcServer, err := newGRPCServer(host)
	if err != nil {
		return nil, err
	}

	authv3.RegisterAuthorizationServer(grpcServer.Server, extAuthService)

	return &ExtAuthServer{
		grpcServer:     grpcServer,
		extAuthService: extAuthService,
	}, nil
}

func (s *ExtAuthServer) Run(ctx context.Context) error {
	return s.grpcServer.Run(ctx)
}

func (s *ExtAuthServer) Shutdown(ctx context.Context) error {
	return s.grpcServer.Shutdown(ctx)
}

type GRPCServer struct {
	host   string
	Server *grpc.Server
}

func newGRPCServer(host string, opts ...grpc.ServerOption) (*GRPCServer, error) {
	srv := &GRPCServer{
		host: host,
	}

	srv.Server = grpc.NewServer(opts...)

	return srv, nil
}

func (s *GRPCServer) Run(ctx context.Context) error {
	listenCfg := net.ListenConfig{}

	listener, err := listenCfg.Listen(ctx, "tcp", s.host)
	if err != nil {
		return err
	}

	return s.Server.Serve(listener)
}

func (s *GRPCServer) Shutdown(ctx context.Context) error {
	if s.Server == nil {
		return nil
	}

	return shutdownWithContext(ctx, func(ctx context.Context) error {
		s.Server.GracefulStop()
		return nil
	}, func() error {
		s.Server.Stop()
		return nil
	})
}

func shutdownWithContext(
	ctx context.Context,
	gracefulShutdownFunc func(ctx context.Context) error,
	forceShutdownFunc func() error,
) error {
	errCh := make(chan error, 1)

	go func() {
		errCh <- gracefulShutdownFunc(ctx)
	}()

	// Wait for the context to be done (timeout, cancel, ...) or shutdownFunc to complete
	select {
	case <-ctx.Done():
		err := ctx.Err()

		if forceShutdownFunc != nil {
			err = errors.Join(err, forceShutdownFunc())
		}

		return err
	case err := <-errCh:
		return err
	}
}
