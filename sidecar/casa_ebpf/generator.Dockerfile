FROM golang:1.26-alpine AS base
FROM base AS dist

WORKDIR /src

ENV PROTOC_VERSION=32.0
ENV PROTOC_X86_64_SHA256="7ca037bfe5e5cabd4255ccd21dd265f79eb82d3c010117994f5dc81d2140ee88"
ENV PROTOC_AARCH_64_SHA256="56af3fc2e43a0230802e6fadb621d890ba506c5c17a1ae1070f685fe79ba12d0"

ARG TARGETARCH

RUN apk add clang llvm20 wget unzip curl make bash git
RUN apk cache purge

# Install eBPF tools.
RUN --mount=type=cache,target=/go/pkg \
    go install github.com/cilium/ebpf/cmd/bpf2go@v0.21.0

RUN cat <<EOF > /generate.sh
#!/bin/sh
export PATH="/usr/lib/llvm20/bin:\$PATH"
export BPF2GO=/go/bin/bpf2go
export BPF_CLANG=clang
export BPF_CFLAGS="-O2 -g -Wall -Werror"
export GOCACHE=/tmp/go-build
make generate
EOF

RUN chmod +x /generate.sh

ENTRYPOINT ["/generate.sh"]
