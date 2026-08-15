from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BACKEND = "http://127.0.0.1:8001"
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class SmokeProxy(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def _proxy_api(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None
        headers = {}
        for key in ("Cookie", "Content-Type", "X-CSRFToken", "Accept"):
            if self.headers.get(key):
                headers[key] = self.headers[key]
        request = Request(f"{BACKEND}{self.path}", data=body, headers=headers, method=self.command)
        try:
            with urlopen(request, timeout=10) as response:
                self._write_response(response.status, response.headers, response.read())
        except HTTPError as error:
            self._write_response(error.code, error.headers, error.read())

    def _write_response(self, status, headers, body):
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() in {"connection", "content-length", "transfer-encoding", "content-encoding"}:
                continue
            if key.lower() == "set-cookie":
                self.send_header(key, value.split("; Domain=", 1)[0])
            else:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy_api()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy_api()
        else:
            self.send_error(405)

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self._proxy_api()
        else:
            self.send_error(405)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8000), SmokeProxy).serve_forever()
