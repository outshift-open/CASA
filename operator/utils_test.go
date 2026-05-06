// Copyright 2026 Cisco Systems, Inc. and its affiliates
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

package main

import (
	"fmt"
	"testing"
)

func TestConvertSlice_MapsEachElement(t *testing.T) {
	src := []int{1, 2, 3}
	got := ConvertSlice(src, func(v int) string { return fmt.Sprintf("%d", v) })
	want := []string{"1", "2", "3"}

	if len(got) != len(want) {
		t.Fatalf("len = %d, want %d", len(got), len(want))
	}
	for i := range want {
		if got[i] != want[i] {
			t.Errorf("[%d] = %q, want %q", i, got[i], want[i])
		}
	}
}

func TestConvertSlice_EmptyInput(t *testing.T) {
	got := ConvertSlice([]int{}, func(v int) string { return "" })
	if len(got) != 0 {
		t.Fatalf("expected empty slice, got len %d", len(got))
	}
}

func TestDerefrence_NonNilPointer(t *testing.T) {
	v := 42
	if got := Derefrence(&v, 0); got != 42 {
		t.Errorf("got %d, want 42", got)
	}
}

func TestDerefrence_NilPointerReturnsDefault(t *testing.T) {
	var ptr *int
	if got := Derefrence(ptr, 99); got != 99 {
		t.Errorf("got %d, want 99 (default)", got)
	}
}
