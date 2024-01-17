import logging
import sys
import socket
from datetime import datetime, UTC
import io
import select
import errno

logging.basicConfig(level=logging.INFO)
if not len(sys.argv) > 2:
    raise AssertionError(
        f"sample_tcp [addr] [port]\n\tinvalid input: {" ".join(sys.argv[1:])}"
    )


class WSGIServer:
    addr_f = socket.AF_INET
    sock_t = socket.SOCK_STREAM
    backlog_sz = 1024

    def __init__(self, server_addr):
        self.sock = sock = socket.socket(self.addr_f, self.sock_t)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setblocking(0)
        sock.bind(server_addr)
        sock.listen(self.backlog_sz)
        self.host, self.port = sock.getsockname()

    def set_app(self, application):
        self.application = application

    @classmethod
    def parse_req(cls, text: str):
        return text.splitlines()[0].split()

    def get_environ(self, request_data, request_method, path, server_host, server_port):
        env = {}

        # Required WSGI variables
        env["wsgi.version"] = (1, 0)
        env["wsgi.url_scheme"] = "http"
        env["wsgi.input"] = io.StringIO(request_data)
        env["wsgi.errors"] = sys.stderr
        env["wsgi.multithread"] = False
        env["wsgi.multiprocess"] = False
        env["wsgi.run_once"] = False
        # Required CGI variables
        env["REQUEST_METHOD"] = request_method
        env["PATH_INFO"] = path
        env["SERVER_NAME"] = server_host
        env["SERVER_PORT"] = str(server_port)
        return env

    def start_response(self, status, resp_headers, exc_info=None):
        dt = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S GTM")
        headers = [("Date", dt), ("Server", "WSGIServer 0.2")]
        self.headers = [status, headers + resp_headers]

    def finish_response(self, response, conn):
        status, headers = self.headers
        resp = f"HTTP/1.1 {status}\r\n"
        for header in headers:
            resp += "{0}: {1}\r\n".format(*header)
        resp += "\r\n"
        for data in response:
            resp += data.decode("utf-8")

        conn.sendall(resp.encode())

    def server_forever(self):
        rlist, wlist, elist = [self.sock], [], []

        while True:
            readables, writables, elist = select.select(rlist, wlist, elist)
            for sock in readables:
                if sock is self.sock:
                    try:
                        conn, caddr = sock.accept()
                    except IOError as e:
                        code, msg = e.args
                        if code == errno.EINTR:
                            continue
                        else:
                            raise e
                    rlist.append(conn)
                else:
                    try:
                        data = sock.recv(1024).decode("utf-8")
                    except ConnectionResetError as e:
                        data = None
                    if not data:
                        sock.close()
                        rlist.remove(sock)
                    else:
                        lines = " ".join(f"\t< {line}\n" for line in data.splitlines())
                        logging.info(f"[server] to {sock.getpeername()}\n{lines}")
                        verb, path, version = self.parse_req(data)
                        env = self.get_environ(data, verb, path, self.host, self.port)
                        result = self.application(env, self.start_response)
                        self.finish_response(result, sock)
