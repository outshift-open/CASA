package main

import (
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
)

type TraceParent struct {
	// TraceID is the ID of the whole trace forest and is used to uniquely identify a distributed trace through a system.
	TraceID [16]byte

	// SpanID is is the ID of this request as known by the caller.
	SpanID [8]byte
}

func ParseTraceParent(v string) (*TraceParent, error) {
	if v == "" {
		return nil, errors.New("unable to parse an empty traceparent value")
	}

	parts := strings.Split(v, "-")
	if len(parts) != 4 {
		return nil, fmt.Errorf("traceparent %s is invalid", v)
	}

	version, err := hex.DecodeString(parts[0])
	if err != nil || len(version) != 1 {
		return nil, fmt.Errorf("traceparent %s has an invalid version", v)
	}

	traceID, err := hex.DecodeString(parts[1])
	if err != nil || len(traceID) != 16 {
		return nil, fmt.Errorf("traceparent %s has an invalid trace ID", v)
	}

	spanID, err := hex.DecodeString(parts[2])
	if err != nil || len(spanID) != 8 {
		return nil, fmt.Errorf("traceparent %s has an invalid span ID", v)
	}

	traceFlags, err := hex.DecodeString(parts[3])
	if err != nil || len(traceFlags) != 1 {
		return nil, fmt.Errorf("traceparent %s has invalid trace flags", v)
	}

	tp := TraceParent{}

	copy(tp.TraceID[:], traceID)
	copy(tp.SpanID[:], spanID)

	return &tp, nil
}
