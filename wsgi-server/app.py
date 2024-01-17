import time
# from server_blocking import WSGIServer
from server_nonblocking import WSGIServer
from flask import Flask
import sys

app = Flask(__name__)


@app.route("/hello")
def hello_world():
    time.sleep(0.2)
    return "Hello World"


if __name__ == "__main__":
    server = WSGIServer((sys.argv[1], int(sys.argv[2])))
    server.set_app(app)
    server.server_forever()
