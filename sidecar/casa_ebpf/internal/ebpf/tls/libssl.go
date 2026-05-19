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
	respPipes  map[uint64]*DataPipe
	responses  chan<- *HTTPResponse
}

func NewLibSSLModule(responses chan<- *HTTPResponse) *LibSSLModule {
	return &LibSSLModule{
		respPipes: make(map[uint64]*DataPipe),
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
			Entry: m.bpfObjects.UprobeSslWrite,
		},
		"SSL_write_ex": {
			Entry: m.bpfObjects.UprobeSslWriteEx,
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

		pipeKey := evt.Ssl
		if _, ok := m.respPipes[pipeKey]; !ok {
			slog.Info("Creating data pipe", "key", pipeKey)
			m.respPipes[pipeKey] = NewDataPipe()
		}

		dataPipe := m.respPipes[pipeKey]

		buf := toBytes(evt.Data[:evt.Len])
		if evt.Data[0] == 'H' && evt.Data[1] == 'T' && evt.Data[2] == 'T' && evt.Data[3] == 'P' && evt.Data[4] == '/' {
			go func() {
				slog.Info("Creating HTTP Response reader", "key", pipeKey)
				reader := bufio.NewReader(dataPipe.Reader())
				resp, err := NewHTTPResponse(reader)
				if err != nil {
					slog.Error("Failed to parse HTTP response", "err", err)
					return
				}

				m.responses <- resp
				slog.Info("event sent")

				// body, err := resp.Body()
				// if err != nil {
				// 	slog.Error("Failed to read http response body", "err", err)
				// } else {
				// 	slog.Info("http resp", "resp", resp, "body", string(body))
				// }
			}()
		}

		if evt.Done == 1 {
			// dataPipe.Close()
		} else {
			dataPipe.Writer().Write(buf)
		}

		slog.Info("Event received", "pid", evt.PidTgid, "len", evt.Len, "original_len", evt.OriginalLen, "done", evt.Done)
	}
}

func toBytes(src []int8) []byte {
	dst := make([]byte, len(src))
	for i, v := range src {
		dst[i] = byte(v)
	}

	return dst
}
