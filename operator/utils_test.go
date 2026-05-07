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

	"github.com/stretchr/testify/assert"
)

func TestConvertSlice_MapsEachElement(t *testing.T) {
	src := []int{1, 2, 3}
	got := ConvertSlice(src, func(v int) string { return fmt.Sprintf("%d", v) })
	assert.Equal(t, []string{"1", "2", "3"}, got)
}

func TestConvertSlice_EmptyInput(t *testing.T) {
	got := ConvertSlice([]int{}, func(v int) string { return "" })
	assert.Empty(t, got)
}

func TestDerefrence_NonNilPointer(t *testing.T) {
	v := 42
	assert.Equal(t, 42, Derefrence(&v, 0))
}

func TestDerefrence_NilPointerReturnsDefault(t *testing.T) {
	var ptr *int
	assert.Equal(t, 99, Derefrence(ptr, 99))
}
