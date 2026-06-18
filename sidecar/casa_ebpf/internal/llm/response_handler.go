package llm

import (
	"fmt"
	"log/slog"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type ResponseHandler struct {
	respChan   chan *tls.HTTPResponse
	cancelChan chan bool
}

func NewResponseHandler(cancelChan chan bool) *ResponseHandler {
	return &ResponseHandler{
		respChan:   make(chan *tls.HTTPResponse, 1024),
		cancelChan: cancelChan,
	}
}

func (h *ResponseHandler) Chan() chan<- *tls.HTTPResponse {
	return h.respChan
}

func (h *ResponseHandler) Start() {
	for {
		select {
		case resp := <-h.respChan:
			body, err := resp.Body()
			if err != nil {
				slog.Error("Failed to read http response body", "err", err)
			} else {
				slog.Info("[ResponseHandler] HTTP RESPONSE", "body", string(body[:10]))
			}
			// TODO: call the auth API to store it
		case shouldCancel := <-h.cancelChan:
			slog.Debug(fmt.Sprintf("Received cancellation event [%t]", shouldCancel))
			if shouldCancel {
				return
			}
		}
	}
}
