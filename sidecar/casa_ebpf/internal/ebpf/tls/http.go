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

type TCPDirection int

const (
	tcpDirSend TCPDirection = 0
	tcpDirRecv TCPDirection = 1
)

type HTTPRequest struct {
	request *http.Request
}

func NewHTTPRequest(rd io.Reader) (*HTTPRequest, error) {
	reader := bufio.NewReader(rd)
	req, err := http.ReadRequest(reader)
	if err != nil {
		return nil, fmt.Errorf("failed to parse HTTP request: %w", err)
	}

	err = setRequestBodyReader(req)
	if err != nil {
		return nil, fmt.Errorf("failed to read HTTP request body: %w", err)
	}

	return &HTTPRequest{request: req}, nil
}

func (r *HTTPRequest) Body() ([]byte, error) {
	body, err := io.ReadAll(r.request.Body)
	if err != nil {
		return nil, fmt.Errorf("unable to read request body: %w", err)
	}

	r.request.Body = io.NopCloser(r.request.Body)

	return body, nil
}

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

func setRequestBodyReader(req *http.Request) error {
	rawBody, err := io.ReadAll(req.Body)
	if err != nil {
		return fmt.Errorf("failed to read raw HTTP request body: %w", err)
	}

	req.Body = io.NopCloser(bytes.NewBuffer(rawBody))

	if enc := req.Header.Get("Content-Encoding"); enc != "" && len(rawBody) > 0 {
		reader, err := getBodyDecompressor(enc, bytes.NewReader(rawBody))
		if err != nil {
			return err
		}

		req.Body = reader
		req.Header.Del("Content-Encoding")
		req.Header.Del("Content-Length")
		req.ContentLength = -1
	}

	return nil
}

func setResponseBodyReader(resp *http.Response) error {
	rawBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read raw HTTP response body: %w", err)
	}

	resp.Body = io.NopCloser(bytes.NewBuffer(rawBody))

	// http.ReadResponse does NOT auto-decompress Content-Encoding
	// (only http.Transport does, and only for gzip). Decompress manually.
	if enc := resp.Header.Get("Content-Encoding"); enc != "" && len(rawBody) > 0 {
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
