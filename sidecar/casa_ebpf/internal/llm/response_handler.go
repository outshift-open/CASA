package llm

import (
	"fmt"
	"log/slog"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type ResponseHandler struct {
	respChan   chan *tls.HTTPResponse
	cancelChan chan bool
	store      CallStore
}

func NewResponseHandler(cancelChan chan bool, store CallStore) *ResponseHandler {
	return &ResponseHandler{
		respChan:   make(chan *tls.HTTPResponse, 1024),
		cancelChan: cancelChan,
		store:      store,
	}
}

func (h *ResponseHandler) Chan() chan<- *tls.HTTPResponse {
	return h.respChan
}

func (h *ResponseHandler) Start() {
	for {
		select {
		case resp := <-h.respChan:
			h.store.StoreResponse(resp)

			body, err := resp.Body()
			if err != nil {
				slog.Error("Failed to read http response body", "err", err)
			} else {
				slog.Info("[ResponseHandler] HTTP RESPONSE", "body", string(body[:10]))
			}

			conn := *resp.Conn()

			tp, ok := h.store.GetTraceparent(conn)
			if ok {
				h.store.DeleteResponse(conn)
				h.store.DeleteTraceparent(conn)

				// TODO: call the auth API to store it
				slog.Info("Sending the LLM call response to CASA Auth server", "tp", tp.TraceID, "span", tp.SpanID)
			}
		case shouldCancel := <-h.cancelChan:
			slog.Debug(fmt.Sprintf("Received cancellation event [%t]", shouldCancel))
			if shouldCancel {
				return
			}
		}
	}
}
