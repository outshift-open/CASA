FROM rust:1.94.1 AS builder

RUN rustup target add wasm32-wasip1

WORKDIR /build
COPY . .
RUN cargo build --target wasm32-wasip1 --release

# Dockerfile for building "compat" variant of Wasm Image Specification.
# https://github.com/solo-io/wasm/blob/master/spec/spec-compat.md
FROM scratch

COPY --from=builder /build/target/wasm32-wasip1/release/traceparent_injector.wasm ./plugin.wasm
