import socket
import sys
import logging
import random
import string

logging.basicConfig(level=logging.INFO)
if not len(sys.argv) > 2:
    raise AssertionError(
        f"sample_tcp [addr] [port]\n\tinvalid input: {" ".join(sys.argv[1:])}"
    )


def basic():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    saddr = (sys.argv[1], int(sys.argv[2]))
    sock.bind(saddr)
    sock.listen(1)

    while True:
        logging.info("[server] accepting...")
        conn, caddr = sock.accept()

        try:
            logging.info(f"[server] connection from {caddr}")
            c = random.choice(string.ascii_letters)
            conn.sendall(bytes(c, "utf-8"))
        finally:
            conn.close()


class TCPEcho(object):
    addr_f = socket.AF_INET
    sock_t = socket.SOCK_STREAM
    backlog_sz = 1
    recv_sz = 1024
    sentinel = "\\exit"

    def __init__(self, saddr):
        self.sock = sock = socket.socket(self.addr_f, self.sock_t)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(saddr)
        sock.listen(self.backlog_sz)
        self.host, self.port = sock.getsockname()

    def reply_once(self):
        while True:
            conn, caddr = self.sock.accept()
            data = conn.recv(1024).decode("utf-8").strip()
            logging.info(f"[server] got {data}")
            conn.sendall(bytes(f"[echo] {data}\n", "utf-8"))
            conn.close()

    def reply_many(self):
        conn, caddr = self.sock.accept()
        while True:
            data = conn.recv(1024).decode("utf-8").strip()
            if data == self.sentinel:
                break
            logging.info(f"[server] got {data}")
            conn.sendall(bytes(f"[echo] {data}\n", "utf-8"))
        conn.close()
        self.sock.close()


if __name__ == "__main__":
    # basic()

    server = TCPEcho((sys.argv[1], int(sys.argv[2])))
    # server.reply_once()
    server.reply_many()
