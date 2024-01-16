from wsgiref.simple_server import make_server

class Middleware:
    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response, *args, **kwargs):
        response = self.app(environ, start_response)
        return [data[::-1] for data in response]

    # minimal implementation
    # def __call__(self, environ, start_response):
    #     response_body = b"Hello, World!"
    #     status = "200 OK"
    #     start_response(status, headers=[])
    #     return iter([response_body])


def application(environ, start_response):
    response_body = [f"{key} : {val}" for key, val in sorted(environ.items())]
    response_body = "\n".join(response_body)
    status = "200 OK"
    headers = [("CONTENT-TYPE", "text/plain")]
    # user_agent = req.headers.get("USER-AGENT", "User Agent not found")
    # user_agent = req.environ.get("HTTP_USER_AGENT", "User Agent not found")
    start_response(status, headers)
    return [response_body.encode("utf-8")]


# using the default server from std
server = make_server('localhost', 8888, Middleware(application))
server.serve_forever()
