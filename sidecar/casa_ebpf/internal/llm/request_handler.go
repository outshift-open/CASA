package llm

import (
	"fmt"
	"log/slog"
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type RequestHandler struct {
	reqChan    chan *tls.HTTPRequest
	cancelChan chan bool
	wg         *sync.WaitGroup
}

func NewRequestHandler(cancelChan chan bool, wg *sync.WaitGroup) *RequestHandler {
	return &RequestHandler{
		reqChan:    make(chan *tls.HTTPRequest, 1024),
		cancelChan: cancelChan,
		wg:         wg,
	}
}

func (h *RequestHandler) Chan() chan<- *tls.HTTPRequest {
	return h.reqChan
}

func (h *RequestHandler) Start() {
	h.wg.Add(1)

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
				h.wg.Done()
				return
			}
		}
	}
}
