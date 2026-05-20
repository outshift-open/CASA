package tls

import (
	"bufio"
	"bytes"
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/cilium/ebpf/ringbuf"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/common"
	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/logger"
)

//go:generate $BPF2GO -cc $BPF_CLANG -cflags $BPF_CFLAGS -target amd64,arm64 BpfLibssl ../../../bpf/tls/libssl.c -- -I../../../bpf

type LibSSLModule struct {
	bpfObjects BpfLibsslObjects
	reqPipes   map[uint64]*DataPipe
	respPipes  map[uint64]*DataPipe
	requests   chan<- *HTTPRequest
	responses  chan<- *HTTPResponse
}

func NewLibSSLModule(requests chan<- *HTTPRequest, responses chan<- *HTTPResponse) *LibSSLModule {
	return &LibSSLModule{
		reqPipes:  make(map[uint64]*DataPipe),
		respPipes: make(map[uint64]*DataPipe),
		requests:  requests,
		responses: responses,
	}
}

func (m *LibSSLModule) Load() error {
	err := LoadBpfLibsslObjects(&m.bpfObjects, nil)
	if err != nil {
		return fmt.Errorf("failed to load eBPF program tls.Tracer: %w", err)
	}

	return nil
}

func (m *LibSSLModule) UProbes() map[string]*common.ProbeDesc {
	return map[string]*common.ProbeDesc{
		"SSL_read": {
			Entry:  m.bpfObjects.UprobeSslRead,
			Return: m.bpfObjects.UretprobeSslRead,
		},
		"SSL_read_ex": {
			Entry:  m.bpfObjects.UprobeSslReadEx,
			Return: m.bpfObjects.UretprobeSslReadEx,
		},
		"SSL_write": {
			Entry:  m.bpfObjects.UprobeSslWrite,
			Return: m.bpfObjects.UretprobeSslWrite,
		},
		"SSL_write_ex": {
			Entry:  m.bpfObjects.UprobeSslWriteEx,
			Return: m.bpfObjects.UretprobeSslWriteEx,
		},
		"SSL_free": {
			Entry: m.bpfObjects.UprobeSslFree,
		},
		"SSL_shutdown": {
			Entry: m.bpfObjects.UprobeSslShutdown,
		},
	}
}

func (m *LibSSLModule) Run(ctx context.Context) error {
	defer m.bpfObjects.Close()

	go logger.ReadDebugEventsMap(ctx, m.bpfObjects.DebugEvents, slog.With("component", "ebpf.libssl"))
	reader, err := ringbuf.NewReader(m.bpfObjects.TlsEvents)
	if err != nil {
		return fmt.Errorf("failed to create ring buffer reader: %w", err)
	}
	stop := context.AfterFunc(ctx, func() { reader.Close() })
	defer stop()

	var evt BpfLibsslTlsDataEvent
	for {
		record, err := reader.Read()
		if err != nil {
			if errors.Is(err, ringbuf.ErrClosed) {
				return fmt.Errorf("ringbuffer closed")
			}

			slog.Error("reading debug event", "err", err)
			select {
			case <-ctx.Done():
				return nil
			case <-time.After(time.Second):
			}
			continue
		}

		if err := binary.Read(bytes.NewBuffer(record.RawSample), binary.LittleEndian, &evt); err != nil {
			slog.Error("Failed to parse ringbuf event", "err", err)
			continue
		}

		var dataPipe *DataPipe
		pipeKey := evt.Ssl

		switch evt.Direction {
		case uint64(tcpDirSend):
			if _, ok := m.reqPipes[pipeKey]; !ok {
				slog.Info("Creating request data pipe", "key", pipeKey)
				m.reqPipes[pipeKey] = NewDataPipe()
			}

			dataPipe = m.reqPipes[pipeKey]
		case uint64(tcpDirRecv):
			if _, ok := m.respPipes[pipeKey]; !ok {
				slog.Info("Creating response data pipe", "key", pipeKey)
				m.respPipes[pipeKey] = NewDataPipe()
			}

			dataPipe = m.respPipes[pipeKey]
		default:
			slog.Error("Unknow TCP direction")
			continue
		}

		buf := toBytes(evt.Data[:evt.Len])

		if evt.Direction == uint64(tcpDirSend) && hasHTTPRequestStart(buf) {
			go func() {
				slog.Info("Creating HTTP Request reader", "key", pipeKey)
				reader := bufio.NewReader(dataPipe.Reader())
				req, err := NewHTTPRequest(reader)
				if err != nil {
					slog.Error("Failed to parse HTTP request", "err", err)
					return
				}

				m.requests <- req
				slog.Info("request event sent")
			}()
		} else if evt.Direction == uint64(tcpDirRecv) && hasHTTPResponseStart(buf) {
			go func() {
				slog.Info("Creating HTTP Response reader", "key", pipeKey)
				reader := bufio.NewReader(dataPipe.Reader())
				resp, err := NewHTTPResponse(reader)
				if err != nil {
					slog.Error("Failed to parse HTTP response", "err", err)
					return
				}

				m.responses <- resp
				slog.Info("response event sent")
			}()
		}

		if evt.Done == 1 {
			// dataPipe.Close()
		} else {
			dataPipe.Writer().Write(buf)
		}

		slog.Info("Event received", "pid", evt.PidTgid, "len", evt.Len, "original_len", evt.OriginalLen, "done", evt.Done, "direction", evt.Direction)
	}
}

func toBytes(src []int8) []byte {
	dst := make([]byte, len(src))
	for i, v := range src {
		dst[i] = byte(v)
	}

	return dst
}

func hasHTTPRequestStart(buf []byte) bool {
	methods := []string{
		"GET ", "POST ", "PUT ", "DELETE ", "PATCH ",
		"HEAD ", "OPTIONS ", "CONNECT ", "TRACE ",
	}

	for _, m := range methods {
		if bytes.HasPrefix(buf, []byte(m)) {
			return true
		}
	}

	return false
}

func hasHTTPResponseStart(buf []byte) bool {
	return bytes.HasPrefix(buf, []byte("HTTP/"))
}
