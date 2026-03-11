package main

import (
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
)

type ExtAuthzMiddleware struct {
	httpServer *http.Server
}

func NewExtAuthzMiddleware() *ExtAuthzMiddleware {
	return &ExtAuthzMiddleware{}
}

func (m *ExtAuthzMiddleware) Run(httpAddr string) {
	var wg sync.WaitGroup
	wg.Add(1)
	go m.startHTTP(httpAddr, &wg)
	wg.Wait()
}

func (m *ExtAuthzMiddleware) startHTTP(addr string, wg *sync.WaitGroup) {
	defer func() {
		wg.Done()
		log.Printf("Stopped HTTP server")
	}()

	listener, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("Failed to create HTTP server: %v", err)
	}

	m.httpServer = &http.Server{Handler: m}

	log.Printf("Starting HTTP server at %s", listener.Addr())
	if err := m.httpServer.Serve(listener); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}

func (m *ExtAuthzMiddleware) ServeHTTP(resp http.ResponseWriter, req *http.Request) {
	body, err := io.ReadAll(req.Body)
	if err != nil {
		log.Printf("[HTTP] read body failed: %v", err)
	}

	l := fmt.Sprintf("%s %s%s, headers: %v, body: [%s]\n", req.Method, req.Host, req.URL, req.Header, returnIfNotTooLong(string(body)))
	log.Printf("[HTTP][allowed]: %s", l)
	resp.WriteHeader(http.StatusOK)
}

func returnIfNotTooLong(body string) string {
	// Maximum size of a header accepted by Envoy is 60KiB, so when the request body is bigger than 60KB,
	// we don't return it in a response header to avoid rejecting it by Envoy and returning 431 to the client
	if len(body) > 60000 {
		return "<too-long>"
	}
	return body
}

func main() {
	middleware := NewExtAuthzMiddleware()
	go middleware.Run(fmt.Sprintf(":%s", "4000"))

	// Wait for the process to be shutdown.
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	<-sigs
}
