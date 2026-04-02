package main

import (
	// "github.com/google/uuid"

	"github.com/proxy-wasm/proxy-wasm-go-sdk/proxywasm"
	"github.com/proxy-wasm/proxy-wasm-go-sdk/proxywasm/types"
	// "go.opentelemetry.io/otel"
	// "go.opentelemetry.io/otel/propagation"
)

func main() {}
func init() {
	proxywasm.SetVMContext(&vmContext{})
}

const (
	traceParentHTTPHeader = "traceparent"
)

type vmContext struct {
	types.DefaultVMContext
}

func (*vmContext) NewPluginContext(contextID uint32) types.PluginContext {
	return &pluginContext{}
}

type pluginContext struct {
	types.DefaultPluginContext
}

func (*pluginContext) NewHttpContext(contextID uint32) types.HttpContext {
	return &httpContext{
		contextID: contextID,
	}
}

func (*pluginContext) OnPluginStart(pluginConfigurationSize int) types.OnPluginStartStatus {
	return types.OnPluginStartStatusOK
}

type httpContext struct {
	types.DefaultHttpContext
	contextID uint32
}

func (*httpContext) OnHttpRequestHeaders(numHeaders int, endOfStream bool) types.Action {
	tp, err := proxywasm.GetHttpRequestHeader(traceParentHTTPHeader)
	if err != nil || tp == "" {
		v := generateTraceParent()
		err := proxywasm.ReplaceHttpRequestHeader(traceParentHTTPHeader, v)
		if err != nil {
			proxywasm.LogCritical("failed to set request header: traceparent")
		}
	}

	return types.ActionContinue
}

func generateTraceParent() string {
	// tracer := otel.Tracer(uuid.NewString())
	// ctx, span := tracer.Start(context.Background(), uuid.NewString())
	// defer span.End()

	// carrier := propagation.MapCarrier{}

	// traceCtx := propagation.TraceContext{}
	// traceCtx.Inject(ctx, carrier)

	// return carrier.Get("traceparent")

	// traceID := make([]byte, 16)
	// spanID := make([]byte, 8)

	// _, err := rand.Read(traceID)
	// if err != nil {
	// 	return ""
	// }

	// _, err = rand.Read(spanID)
	// if err != nil {
	// 	return ""
	// }

	// return fmt.Sprintf("00-%s-%s-01",
	// 	hex.EncodeToString(traceID),
	// 	hex.EncodeToString(spanID),
	// )
	return "test"
}
