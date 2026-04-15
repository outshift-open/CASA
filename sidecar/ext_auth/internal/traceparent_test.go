package internal_test

import (
	"encoding/hex"
	"testing"

	internal "github.com/cisco-eti/identity-auth-server/sidecar/ext_auth/internal"
	"github.com/stretchr/testify/assert"
)

func TestParseTraceParent(t *testing.T) {
	t.Parallel()

	testCases := map[string]*struct {
		raw             string
		expectedTraceID string
		expectedSpanID  string
	}{
		"should parse correctly traceparent": {
			raw:             "00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01",
			expectedTraceID: "0af7651916cd43dd8448eb211c80319c",
			expectedSpanID:  "b9c7c989f97918e1",
		},
	}

	for tn, tc := range testCases {
		t.Run(tn, func(t *testing.T) {
			t.Parallel()

			tp, err := internal.ParseTraceParent(tc.raw)

			assert.NoError(t, err)
			assert.Equal(t, tc.expectedTraceID, hex.EncodeToString(tp.TraceID[:]))
			assert.Equal(t, tc.expectedSpanID, hex.EncodeToString(tp.SpanID[:]))
		})
	}
}
