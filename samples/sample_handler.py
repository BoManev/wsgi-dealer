from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class MyHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            message = "alive"
            self.wfile.write(json.dumps(message).encode())
        else:
            self.send_response(404)

httpd = HTTPServer(('localhost', 8888), MyHTTPServer)
httpd.serve_forever()