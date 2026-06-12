FROM golang:1.26-alpine AS builder

ARG TARGETARCH

ENV GOARCH=$TARGETARCH

WORKDIR /src

# avoids redownloading the whole Go dependencies on each local build
RUN go env -w GOCACHE=/go-cache
RUN go env -w GOMODCACHE=/gomod-cache

USER root

RUN apk update && apk add make bpftool

RUN go install github.com/go-delve/delve/cmd/dlv@latest

# Copy the Go Modules manifests
# COPY go.mod go.mod

# RUN go mod download
COPY . .

RUN GOOS=linux GOARCH=arm64 make debug

ENTRYPOINT [ "dlv", "--listen=:2345", "--headless=true", "--api-version=2", "--accept-multiclient", "--log", "exec", "bin/casa_ebpf" ]
