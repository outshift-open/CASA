package main

import (
	"context"
	"encoding/hex"
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

	authv3 "github.com/envoyproxy/go-control-plane/envoy/service/auth/v3"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/genproto/googleapis/rpc/status"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
)

var tracer trace.Tracer

func initTracer(ctx context.Context) func() {
	endpoint := os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
	if endpoint == "" {
		endpoint = "otel-collector-opentelemetry-collector:4317"
	}

	exp, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(endpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		log.Printf("Failed to create OTel exporter: %v", err)
		tracer = otel.Tracer("ext-authz-middleware")
		return func() {}
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(resource.NewWithAttributes(
			"https://opentelemetry.io/schemas/1.26.0",
			attribute.String("service.name", "ext-authz-middleware"),
		)),
	)
	otel.SetTracerProvider(tp)
	tracer = otel.Tracer("ext-authz-middleware")
	return func() { tp.Shutdown(ctx) }
}

type (
	extAuthzServerV3 struct{}
)

// Temp
var (
	reqCache   map[string]int = make(map[string]int)
	reqCacheMu sync.Mutex
)

func (s *extAuthzServerV3) Check(_ context.Context, request *authv3.CheckRequest) (*authv3.CheckResponse, error) {
	attrs := request.GetAttributes()

	httpReq := attrs.GetRequest().GetHttp()
	headers := httpReq.GetHeaders()

	ctx := context.Background()

	if tp, ok := headers["traceparent"]; ok {
		parts := strings.Split(tp, "-")
		if len(parts) == 4 {
			traceIDBytes, err1 := hex.DecodeString(parts[1])
			spanIDBytes, err2 := hex.DecodeString(parts[2])
			if err1 == nil && err2 == nil && len(traceIDBytes) == 16 && len(spanIDBytes) == 8 {
				var traceID trace.TraceID
				var spanID trace.SpanID
				copy(traceID[:], traceIDBytes)
				copy(spanID[:], spanIDBytes)
				remoteCtx := trace.ContextWithRemoteSpanContext(ctx, trace.NewSpanContext(trace.SpanContextConfig{
					TraceID:    traceID,
					SpanID:     spanID,
					TraceFlags: trace.FlagsSampled,
					Remote:     true,
				}))
				ctx = remoteCtx

				// Temp to debug distributed parallel tracing
				if !strings.HasPrefix(httpReq.GetHost(), "otel-collector") {
					reqCacheMu.Lock()
					reqCache[parts[1]]++
					reqCacheMu.Unlock()
				}
			}
		}
	}

	_, span := tracer.Start(ctx, "Check",
		trace.WithSpanKind(trace.SpanKindServer),
		trace.WithAttributes(
			attribute.String("http.method", httpReq.GetMethod()),
			attribute.String("http.path", httpReq.GetPath()),
			attribute.String("http.host", httpReq.GetHost()),
		),
	)
	defer span.End()

	l := fmt.Sprintf("%s %s%s, headers: %v, body: [%s]\n", httpReq.Method, httpReq.Host, httpReq.Path, headers, returnIfNotTooLong(string(httpReq.Body)))
	log.Printf("[HTTP][allowed]: %s", l)
	return s.allow(), nil
}

func (s *extAuthzServerV3) allow() *authv3.CheckResponse {
	return &authv3.CheckResponse{
		HttpResponse: &authv3.CheckResponse_OkResponse{
			OkResponse: &authv3.OkHttpResponse{},
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

	reqCacheMu.Lock()
	data, _ := json.MarshalIndent(reqCache, "", "  ")
	reqCacheMu.Unlock()

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
	ctx := context.Background()
	shutdown := initTracer(ctx)
	defer shutdown()

	middleware := NewExtAuthzMiddleware()
	go middleware.Run(":4000", ":4001")

	// Wait for the process to be shutdown.
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	<-sigs
}
