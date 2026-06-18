package llm

import (
	"sync"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/ebpf/tls"
)

type CallStore interface {
	StoreRequest(req *tls.HTTPRequest)
	StoreResponse(res *tls.HTTPResponse)
	StoreTraceparent(tp *tls.TraceparentValue)
	GetRequest(conn tls.ConnectionInfo) (*tls.HTTPRequest, bool)
	GetResponse(conn tls.ConnectionInfo) (*tls.HTTPResponse, bool)
	GetTraceparent(conn tls.ConnectionInfo) (*tls.TraceparentValue, bool)
	DeleteRequest(conn tls.ConnectionInfo)
	DeleteResponse(conn tls.ConnectionInfo)
	DeleteTraceparent(conn tls.ConnectionInfo)
}

type InMemoryCallStore struct {
	tpsByConns   map[tls.ConnectionInfo]*tls.TraceparentValue
	reqsByConns  map[tls.ConnectionInfo]*tls.HTTPRequest
	respsByConns map[tls.ConnectionInfo]*tls.HTTPResponse
	mut          sync.RWMutex
}

func NewInMemoryCallStore() CallStore {
	return &InMemoryCallStore{
		tpsByConns:   map[tls.ConnectionInfo]*tls.TraceparentValue{},
		reqsByConns:  map[tls.ConnectionInfo]*tls.HTTPRequest{},
		respsByConns: map[tls.ConnectionInfo]*tls.HTTPResponse{},
	}
}

func (s *InMemoryCallStore) StoreRequest(req *tls.HTTPRequest) {
	s.mut.Lock()
	defer s.mut.Unlock()

	if req == nil {
		return
	}

	s.reqsByConns[*req.Conn()] = req
}

func (s *InMemoryCallStore) StoreResponse(res *tls.HTTPResponse) {
	s.mut.Lock()
	defer s.mut.Unlock()

	if res == nil {
		return
	}

	s.respsByConns[*res.Conn()] = res
}

func (s *InMemoryCallStore) StoreTraceparent(tp *tls.TraceparentValue) {
	s.mut.Lock()
	defer s.mut.Unlock()

	if tp == nil {
		return
	}

	s.tpsByConns[*tp.Conn] = tp
}

func (s *InMemoryCallStore) GetRequest(conn tls.ConnectionInfo) (*tls.HTTPRequest, bool) {
	s.mut.Lock()
	defer s.mut.Unlock()

	req, ok := s.reqsByConns[conn]
	return req, ok
}

func (s *InMemoryCallStore) GetResponse(conn tls.ConnectionInfo) (*tls.HTTPResponse, bool) {
	s.mut.Lock()
	defer s.mut.Unlock()

	res, ok := s.respsByConns[conn]
	return res, ok
}

func (s *InMemoryCallStore) GetTraceparent(conn tls.ConnectionInfo) (*tls.TraceparentValue, bool) {
	s.mut.Lock()
	defer s.mut.Unlock()

	tp, ok := s.tpsByConns[conn]
	return tp, ok
}

func (s *InMemoryCallStore) DeleteRequest(conn tls.ConnectionInfo) {
	s.mut.Lock()
	defer s.mut.Unlock()

	delete(s.reqsByConns, conn)
}

func (s *InMemoryCallStore) DeleteResponse(conn tls.ConnectionInfo) {
	s.mut.Lock()
	defer s.mut.Unlock()

	delete(s.respsByConns, conn)
}

func (s *InMemoryCallStore) DeleteTraceparent(conn tls.ConnectionInfo) {
	s.mut.Lock()
	defer s.mut.Unlock()

	delete(s.tpsByConns, conn)
}
