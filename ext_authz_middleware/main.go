package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"

	corev3 "github.com/envoyproxy/go-control-plane/envoy/config/core/v3"
	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"github.com/google/uuid"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
)

type (
	extAuthzServerV3 struct{}
)

// Temp
var reqCache map[string]int = make(map[string]int)

func (s *extAuthzServerV3) Check(_ context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()
	headersToRet := []*corev3.HeaderValueOption{}

	// Temp
	if _, ok := headers["traceparent"]; !ok {
		spanID := uuid.New()
		traceparent := fmt.Sprintf("00-%s-%s-01", strings.ReplaceAll(uuid.NewString(), "-", ""), fmt.Sprintf("%x", spanID[:8]))
		headersToRet = append(headersToRet, &corev3.HeaderValueOption{
			Header: &corev3.HeaderValue{
				Key:   "traceparent",
				Value: traceparent,
			},
		})
		headers["traceparent"] = traceparent
	}

	if !strings.HasPrefix(httpReq.GetHost(), "otel-collector") {
		for hn, hv := range headers {
			if hn == "traceparent" {
				traceID := strings.Split(hv, "-")[1]
				count := 0
				if c, ok := reqCache[traceID]; ok {
					count = c
				}

				reqCache[traceID] = count + 1
			}
		}
	}

	l := fmt.Sprintf("%s %s%s, headers: %v, body: [%s]\n", httpReq.Method, httpReq.Host, httpReq.Path, headers, returnIfNotTooLong(string(httpReq.Body)))
	log.Printf("[HTTP][allowed]: %s", l)
	return s.allow(headersToRet), nil
}

func (s *extAuthzServerV3) allow(headers []*corev3.HeaderValueOption) *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{
				Headers: headers,
			},
		},
		Status: &status.Status{Code: int32(codes.OK)},
	}
}

type ExtAuthzMiddleware struct {
	httpServer *http.Server
	grpcServer *grpc.Server
	grpcV3     *extAuthzServerV3
}

func NewExtAuthzMiddleware() *ExtAuthzMiddleware {
	return &ExtAuthzMiddleware{
		grpcV3: &extAuthzServerV3{},
	}
}

func (m *ExtAuthzMiddleware) Run(httpAddr, grpcAddr string) {
	var wg sync.WaitGroup
	wg.Add(2)
	go m.startHTTP(httpAddr, &wg)
	go m.startGrpc(grpcAddr, &wg)
	wg.Wait()
}

func (m *ExtAuthzMiddleware) startHTTP(addr string, wg *sync.WaitGroup) {
	defer func() {
		wg.Done()
		log.Printf("Stopped HTTP server")
	}()

	listener, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("Failed to create HTTP server: %v", err)
	}

	m.httpServer = &http.Server{Handler: m}

	log.Printf("Starting HTTP server at %s", listener.Addr())
	if err := m.httpServer.Serve(listener); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}

func (m *ExtAuthzMiddleware) startGrpc(addr string, wg *sync.WaitGroup) {
	defer func() {
		wg.Done()
		log.Printf("Stopped HTTP server")
	}()

	listen, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	m.grpcServer = grpc.NewServer()
	authv3.RegisterAuthorizationServer(m.grpcServer, m.grpcV3)

	log.Printf("server listening at %v", listen.Addr())
	if err := m.grpcServer.Serve(listen); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func (m *ExtAuthzMiddleware) ServeHTTP(resp http.ResponseWriter, req *http.Request) {
	body, err := io.ReadAll(req.Body)
	if err != nil {
		log.Printf("[HTTP] read body failed: %v", err)
	}

	data, _ := json.MarshalIndent(reqCache, "", "  ")

	l := fmt.Sprintf("%s %s%s, headers: %v, body: [%s]\n", req.Method, req.Host, req.URL, req.Header, returnIfNotTooLong(string(body)))
	log.Printf("[HTTP][allowed]: %s", l)
	resp.Header().Set("Content-Type", "application/json")
	resp.WriteHeader(http.StatusOK)
	resp.Write(data)

}

func returnIfNotTooLong(body string) string {
	// Maximum size of a header accepted by Envoy is 60KiB, so when the request body is bigger than 60KB,
	// we don't return it in a response header to avoid rejecting it by Envoy and returning 431 to the client
	if len(body) > 60000 {
		return "<too-long>"
	}
	return body
}

func main() {
	middleware := NewExtAuthzMiddleware()
	go middleware.Run(":4000", ":4001")

	// Wait for the process to be shutdown.
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	<-sigs
}
