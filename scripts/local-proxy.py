#!/usr/bin/env python3
"""Lightweight hostname-routing reverse proxy for local CASA development.

Routes HTTP requests by Host header to direct kubectl port-forwards.
Bypasses ingress controller throughput issues on Docker Desktop macOS
(large responses stall through port-forward SPDY tunnels with extra proxy hops).

Started by local-setup-standalone.sh Step 8.
"""
import http.server
import socketserver
import urllib.request
import sys

ROUTES = {
    "explorer.casa.outshift.ai": "http://127.0.0.1:9081",
    "banking-safe.casa.outshift.ai": "http://127.0.0.1:9082",
    "banking-compromised.casa.outshift.ai": "http://127.0.0.1:9083",
}


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_HEAD(self):
        self._proxy()

    def _proxy(self):
        host = self.headers.get("Host", "").split(":")[0]
        backend = ROUTES.get(host)
        if not backend:
            self.send_error(404, f"Unknown host: {host}")
            return

        url = backend + self.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else None

        req = urllib.request.Request(url, data=body, method=self.command)
        for key, val in self.headers.items():
            if key.lower() not in ("host", "connection", "transfer-encoding"):
                req.add_header(key, val)

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(resp.status)
            for key, val in resp.headers.items():
                if key.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(key, val)
            self.end_headers()
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        pass  # Suppress per-request logging


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9080
    server = ThreadedHTTPServer(("127.0.0.1", port), ProxyHandler)
    print(f"CASA local proxy listening on 127.0.0.1:{port}")
    server.serve_forever()
