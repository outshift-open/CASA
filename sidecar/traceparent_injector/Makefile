OUT_DIR ?= out
WASM := $(OUT_DIR)/plugin.wasm

build:
	env GOOS=wasip1 GOARCH=wasm go build -buildmode=c-shared -o $(WASM) main.go
.PHONY: build

clean:
	rm -rf $(OUT_DIR)
