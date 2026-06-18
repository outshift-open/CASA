package llm

import (
	"fmt"
	"log/slog"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type RequestHandler struct {
	reqChan    chan *tls.HTTPRequest
	cancelChan chan bool
	store      CallStore
}

func NewRequestHandler(cancelChan chan bool, store CallStore) *RequestHandler {
	return &RequestHandler{
		reqChan:    make(chan *tls.HTTPRequest, 1024),
		cancelChan: cancelChan,
		store:      store,
	}
}

func (h *RequestHandler) Chan() chan<- *tls.HTTPRequest {
	return h.reqChan
}

func (h *RequestHandler) Start() {
	for {
		select {
		case req := <-h.reqChan:
			h.store.StoreRequest(req)

			body, err := req.Body()
			if err != nil {
				slog.Error("Failed to read http request body", "err", err)
			} else {
				slog.Info("[RequestHandler] HTTP REQUEST", "body", string(body), "headers", req.Headers())
			}

			tp, ok := h.store.GetTraceparent(*req.Conn())
			if ok {
				h.store.DeleteRequest(*req.Conn())

				// TODO: call the auth API to store it
				slog.Info("Sending the LLM call request to CASA Auth server", "tp", tp.TraceID, "span", tp.SpanID)
			}
		case shouldCancel := <-h.cancelChan:
			slog.Debug(fmt.Sprintf("Received cancellation event [%t]", shouldCancel))
			if shouldCancel {
				return
			}
		}
	}
}
