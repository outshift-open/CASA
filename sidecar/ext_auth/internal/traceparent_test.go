// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package internal_test

import (
	"encoding/hex"
	"testing"

	internal "github.com/outshift-open/identity-auth-server/sidecar/ext_auth/internal"
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
