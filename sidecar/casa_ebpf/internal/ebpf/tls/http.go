package tls

import (
	"bufio"
	"bytes"
	"compress/flate"
	"compress/gzip"
	"fmt"
	"io"
	"net/http"
)

type HTTPResponse struct {
	response *http.Response
}

func NewHTTPResponse(rd io.Reader) (*HTTPResponse, error) {
	reader := bufio.NewReader(rd)
	resp, err := http.ReadResponse(reader, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to parse HTTP response: %w", err)
	}

	err = setResponseBodyReader(resp)
	if err != nil {
		return nil, fmt.Errorf("failed to read HTTP response body: %w", err)
	}

	// slog.Info("http resp", "resp", resp, "body", string(body))

	return &HTTPResponse{
		response: resp,
	}, nil
}

func (r *HTTPResponse) Body() ([]byte, error) {
	body, err := io.ReadAll(r.response.Body)
	if err != nil {
		return nil, fmt.Errorf("unable to read response body: %w", err)
	}

	r.response.Body = io.NopCloser(r.response.Body)

	return body, nil
}

func setResponseBodyReader(resp *http.Response) error {
	rawBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read raw HTTP response body: %w", err)
	}

	resp.Body = io.NopCloser(bytes.NewBuffer(rawBody))

	// http.ReadResponse does NOT auto-decompress Content-Encoding
	// (only http.Transport does, and only for gzip). Decompress manually.
	// body := rawBody
	if enc := resp.Header.Get("Content-Encoding"); enc != "" && len(rawBody) > 0 {
		// dec, err := decompressBody(enc, rawBody)
		// if err != nil {
		// 	return nil, fmt.Errorf("decompress error (enc=%s, truncated body?): %w", enc, err)
		// }
		// body = dec

		reader, err := getBodyDecompressor(enc, bytes.NewReader(rawBody))
		if err != nil {
			return err
		}

		resp.Body = reader
		resp.Header.Del("Content-Encoding")
		resp.Header.Del("Content-Length")
		resp.ContentLength = -1
		resp.Uncompressed = true

	}

	return nil
}

func getBodyDecompressor(encoding string, rawReader io.Reader) (io.ReadCloser, error) {
	var (
		reader io.ReadCloser
		err    error
	)

	switch encoding {
	case "gzip":
		var gr *gzip.Reader
		gr, err = gzip.NewReader(rawReader)
		reader = gr
	case "deflate":
		fr := flate.NewReader(rawReader)
		reader = fr
	default:
		return nil, fmt.Errorf("unsupported HTTP content encoding %s", encoding)
	}

	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP response body decompressor: %w", err)
	}

	return reader, nil
}

// func decompressBody(encoding string, b []byte) ([]byte, error) {
// 	var (
// 		reader  io.Reader
// 		closeFn func()
// 		err     error
// 	)

// 	switch encoding {
// 	case "gzip":
// 		var gr *gzip.Reader
// 		gr, err = gzip.NewReader(bytes.NewReader(b))
// 		reader = gr
// 		closeFn = func() { _ = gr.Close() }
// 	case "deflate":
// 		fr := flate.NewReader(bytes.NewReader(b))
// 		reader = fr
// 		closeFn = func() { _ = fr.Close() }
// 	default:
// 		return b, nil
// 	}

// 	if err != nil {
// 		return nil, err
// 	}
// 	if closeFn != nil {
// 		defer closeFn()
// 	}

// 	body, err := io.ReadAll(reader)
// 	if err != nil {
// 		return nil, err
// 	}

// 	return body, nil
// }
