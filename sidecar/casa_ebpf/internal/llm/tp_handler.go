package llm

import (
	"fmt"
	"log/slog"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type TraceparentHandler struct {
	tpChan     chan *tls.TraceparentValue
	cancelChan chan bool
	store      CallStore
}

func NewTraceparentHandler(cancelChan chan bool, store CallStore) *TraceparentHandler {
	return &TraceparentHandler{
		tpChan:     make(chan *tls.TraceparentValue, 1024),
		cancelChan: cancelChan,
		store:      store,
	}
}

func (h *TraceparentHandler) Chan() chan<- *tls.TraceparentValue {
	return h.tpChan
}

func (h *TraceparentHandler) Start() {
	for {
		select {
		case tp := <-h.tpChan:
			h.store.StoreTraceparent(tp)

			slog.Info("++++++ TP ++++++", "trace_id", tp.TraceID, "span_id", tp.SpanID)
			conn := *tp.Conn

			req, ok := h.store.GetRequest(conn)
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
