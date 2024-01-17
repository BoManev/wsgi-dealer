import socket
import io
import sys
import logging
from datetime import datetime, UTC

logging.basicConfig(level=logging.INFO)
if not len(sys.argv) > 2:
    raise AssertionError(
        f"sample_tcp [addr] [port]\n\tinvalid input: {" ".join(sys.argv[1:])}"
    )


class WSGIServer:
    addr_f = socket.AF_INET
    sock_t = socket.SOCK_STREAM
    backlog_sz = 1

    def __init__(self, server_addr):
        self.sock = sock = socket.socket(self.addr_f, self.sock_t)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_addr)
        sock.listen(self.backlog_sz)
        self.host, self.port = sock.getsockname()

    def set_app(self, application):
        self.application = application

    def parse_req(self, text: str):
        (self.verb, self.path, self.version) = (
            text.splitlines()[0].rstrip("\r\n").split()
        )

    def handle_req(self, start_response):
        self.req_data = data = self.conn.recv(1024).decode("utf-8")
        lines = " ".join(f"\t< {line}\n" for line in data.splitlines())
        logging.info(f"[server] from {self.caddr}\n{lines}")

        if data:
            self.parse_req(data)
            env = self.get_environ()
            response = self.application(env, start_response)
            self.finish_response(response)

    def server_forever(self):
        while True:
            self.conn, self.caddr = self.sock.accept()
            conn = self.conn
            with conn:

                def start_response(status, headers):
                    dt = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    more_headers = [("Server", "WSGIServer 0.2"), ("Date", dt)]
                    response = f"HTTP/1.1 {status}\r\n"
                    for header in more_headers + headers:
                        response += "{0}: {1}\r\n".format(*header)
                    response += "\r\n"
                    conn.sendall(response.encode("utf-8"))

                self.handle_req(start_response)

    def get_environ(self):
        env = {}

        # Required WSGI variables
        env["wsgi.version"] = (1, 0)
        env["wsgi.url_scheme"] = "http"
        env["wsgi.input"] = io.StringIO(self.req_data)
        env["wsgi.errors"] = sys.stderr
        env["wsgi.multithread"] = False
        env["wsgi.multiprocess"] = False
        env["wsgi.run_once"] = False
        # Required CGI variables
        env["REQUEST_METHOD"] = self.verb
        env["PATH_INFO"] = self.path
        env["SERVER_NAME"] = self.host
        env["SERVER_PORT"] = str(self.port)
        return env

    def finish_response(self, result):
        try:
            response = ""
            for data in result:
                response += data.decode("utf-8")
            lines = " ".join(f"\t< {line}\n" for line in data.splitlines())
            logging.info(f"[server] to {self.caddr}\n{lines}")
            response_bytes = response.encode()
            self.conn.sendall(response_bytes)
        finally:
            logging.info("ALL GOOD")
