# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM rust:1.94.1 AS builder

RUN rustup target add wasm32-wasip1

WORKDIR /build
COPY . .
RUN cargo build --target wasm32-wasip1 --release

# Dockerfile for building "compat" variant of Wasm Image Specification.
# https://github.com/solo-io/wasm/blob/master/spec/spec-compat.md
FROM scratch

COPY --from=builder /build/target/wasm32-wasip1/release/llm_proxy.wasm ./plugin.wasm
