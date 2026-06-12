package llm

import (
	"fmt"
	"log/slog"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type RequestHandler struct {
	reqChan    chan *tls.HTTPRequest
	cancelChan chan bool
}

func NewRequestHandler(cancelChan chan bool) *RequestHandler {
	return &RequestHandler{
		reqChan:    make(chan *tls.HTTPRequest, 1024),
		cancelChan: cancelChan,
	}
}

func (h *RequestHandler) Chan() chan<- *tls.HTTPRequest {
	return h.reqChan
}

func (h *RequestHandler) Start() {
	for {
		select {
		case req := <-h.reqChan:
			body, err := req.Body()
			if err != nil {
				slog.Error("Failed to read http request body", "err", err)
			} else {
				slog.Info("[RequestHandler] HTTP REQUEST", "body", string(body))
			}
		case shouldCancel := <-h.cancelChan:
			slog.Debug(fmt.Sprintf("Received cancellation event [%t]", shouldCancel))
			if shouldCancel {
				return
			}
		}
	}
}
