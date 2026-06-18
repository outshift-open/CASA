package logger

import (
	"context"
	"errors"
	"io"
	"log/slog"
	"time"
	"unsafe"

	"github.com/cilium/ebpf"
	"github.com/cilium/ebpf/ringbuf"
	"golang.org/x/sys/unix"
)

//go:generate $BPF2GO -cc $BPF_CLANG -cflags $BPF_CFLAGS -type log_info_t -target amd64,arm64 BpfLogger ../../../bpf/logger/logger.c -- -I../../../bpf

type BPFLogInfo BpfLoggerLogInfoT

type BPFLogger struct {
	bpfObjects BpfLoggerObjects
	closers    []io.Closer
	log        *slog.Logger
}

type Event struct {
	Log string
}

func New() *BPFLogger {
	log := slog.With("component", "BPFLogger")
	return &BPFLogger{
		log: log,
	}
}

func reinterpretCast[T any](b []byte) (*T, error) {
	var zero T

	if len(b) < int(unsafe.Sizeof(zero)) {
		return nil, errors.New("byte slice too short")
	}

	return (*T)(unsafe.Pointer(unsafe.SliceData(b))), nil
}

func logDebugEvent(log *slog.Logger, record *ringbuf.Record) {
	event, err := reinterpretCast[BPFLogInfo](record.RawSample)
	if err != nil {
		log.Info("failed to decode debug event", "error", err)
		return
	}
	log.Info(unix.ByteSliceToString(event.Log[:]),
		"pid", event.Pid,
		"comm", unix.ByteSliceToString(event.Comm[:]))
}

// ReadDebugEventsMap can be used by any subsystem that loads BPF programs including
// bpf_dbg.h but doesn't go through the main appolly pipeline (e.g. statsolly, netolly).
// This is a blocking function. Callers should invoke it with `go ReadDebugEventsMap(..)`.
func ReadDebugEventsMap(ctx context.Context, debugEventsMap *ebpf.Map, log *slog.Logger) {
	if debugEventsMap == nil {
		return
	}

	reader, err := ringbuf.NewReader(debugEventsMap)
	if err != nil {
		log.Error("failed to create debug events reader", "error", err)
		return
	}
	stop := context.AfterFunc(ctx, func() { reader.Close() })
	defer stop()

	record := ringbuf.Record{}

	for {
		err := reader.ReadInto(&record)
		if err != nil {
			if errors.Is(err, ringbuf.ErrClosed) {
				return
			}
			log.Error("reading debug event", "error", err)
			// Back off so a persistent error (e.g. invalid FD) doesn't spin the CPU.
			select {
			case <-ctx.Done():
				return
			case <-time.After(time.Second):
			}
			continue
		}
		logDebugEvent(log, &record)
	}
}
