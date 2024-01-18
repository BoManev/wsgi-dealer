from webob import Request, Response
from parse import parse
import inspect
import pdb


class API:
    def __init__(self):
        self._routes = {}

    def __call__(self, environ, start_response):
        req = Request(environ)
        res = self.handle_request(req)
        return res(environ, start_response)

    def route(self, path):
        if path in self._routes:
            raise AssertionError("{path} already exists!")

        def wrapper(handler):
            self._routes[path] = handler
            return handler

        return wrapper

    def default_response(self, response):
        response.text = "Not Found!"
        response.status_code = 404
        return response

    def get_handler(self, p):
        for path, handler in self._routes.items():
            query_params = parse(path, p)
            if query_params:
                return handler, query_params.named
        return None, None

    def handle_request(self, req: Request):
        res = Response()
        import pdb
        pdb.set_trace()
        handler, kwargs = self.get_handler(req.path)

        if req.params:
            kwargs.update(req.params)
        if not handler:
            return self.default_response(res)
        if inspect.isclass(handler):
            handler = getattr(handler(), req.method.lower(), None)
            if not handler:
                return self.default_response(res)
            handler(req, res, **kwargs)
        else:
            handler(req, res, **kwargs)
        return res


# from cgi import parse
# from html import escape

# d = parse_qs(environ['QUERY_STRING'])
# age = d.get('age', [''])[0]
# hobbies = d.get('hobbies', [])
# age = escape(age)
# hobbies = [escape(hobby) for hobby in hobbies]